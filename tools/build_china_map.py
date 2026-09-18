#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把中国省级 GeoJSON 转换成旅行地图页面用的 SVG 路径数据。

用法：
    python tools/build_china_map.py            # 只生成 assets/china-map-data.js
    python tools/build_china_map.py --preview  # 额外输出一张 PNG 预览，方便肉眼检查

数据源：阿里云 DataV 的全国省级边界（含港澳台与九段线）。
首次运行会自动下载到 tools/.cache/ 并缓存，之后离线可重复运行。

输出：assets/china-map-data.js，浏览器里通过 <script> 直接加载，
      不依赖任何外部 CDN，GitHub Pages 上开箱即用。
"""

import argparse
import json
import math
import os
import urllib.request

SRC_URL = "https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "tools", ".cache", "china-100000-full.json")
PREVIEW = os.path.join(ROOT, "tools", ".cache", "preview.png")
OUT = os.path.join(ROOT, "assets", "china-map-data.js")

# 视图画布尺寸（SVG viewBox 单位），实际渲染尺寸由页面 CSS 决定
VIEW_W = 1000.0
MARGIN = 6.0

# 每单位面积小于该值的碎岛会被丢弃，避免路径数据过大
MIN_RING_AREA = float(os.environ.get("MIN_RING_AREA", "0.45"))
# 每个省至少保留面积最大的 N 个岛屿（海南的南海诸岛很多，靠这条兜底）
KEEP_TOP_RINGS = 14
# 小于该面积的小岛在真实比例下不足一个像素，改成同位置的小方块，
# 这样南海诸岛、沿海小岛在图上仍然是看得见、点得到的点
ISLET_AREA = float(os.environ.get("ISLET_AREA", "6.0"))
ISLET_HALF = 1.6  # 方块半径（画布单位）

# 九段线单独成一条不可交互的装饰路径
NINE_DASH_ID = "100000_JD"

# 简化容差（画布单位），越大越省体积、越失真
TOLERANCE = float(os.environ.get("TOLERANCE", "0.55"))

# 省份分区，只用于页面上的分组展示
REGIONS = {
    "110000": "华北", "120000": "华北", "130000": "华北", "140000": "华北", "150000": "华北",
    "210000": "东北", "220000": "东北", "230000": "东北",
    "310000": "华东", "320000": "华东", "330000": "华东", "340000": "华东",
    "350000": "华东", "360000": "华东", "370000": "华东", "710000": "华东",
    "410000": "华中", "420000": "华中", "430000": "华中",
    "440000": "华南", "450000": "华南", "460000": "华南", "810000": "华南", "820000": "华南",
    "500000": "西南", "510000": "西南", "520000": "西南", "530000": "西南", "540000": "西南",
    "610000": "西北", "620000": "西北", "630000": "西北", "640000": "西北", "650000": "西北",
}

# 名称里需要剥掉的行政后缀，顺序敏感（先长后短）
SUFFIXES = ("维吾尔自治区", "壮族自治区", "回族自治区", "特别行政区", "自治区", "省", "市")


def short_name(name):
    """北京市 -> 北京，新疆维吾尔自治区 -> 新疆"""
    for suf in SUFFIXES:
        if name.endswith(suf) and len(name) > len(suf):
            return name[: -len(suf)]
    return name


def make_albers(phi1=25.0, phi2=47.0, lam0=105.0, phi0=35.0):
    """中国常用的 Albers 等积圆锥投影，避免墨卡托把北方拉得过高。"""
    p1, p2, l0, p0 = map(math.radians, (phi1, phi2, lam0, phi0))
    n = (math.sin(p1) + math.sin(p2)) / 2.0
    c = math.cos(p1) ** 2 + 2.0 * n * math.sin(p1)
    rho0 = math.sqrt(c - 2.0 * n * math.sin(p0)) / n

    def project(lon, lat):
        lam, phi = math.radians(lon), math.radians(lat)
        rho = math.sqrt(max(c - 2.0 * n * math.sin(phi), 0.0)) / n
        theta = n * (lam - l0)
        # y 轴在投影里向北为正，这里先不翻转，统一在缩放阶段处理
        return rho * math.sin(theta), rho0 - rho * math.cos(theta)

    return project


def simplify(points, tol):
    """Douglas-Peucker 简化，输入输出都是 (x, y) 列表。"""
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        if last <= first + 1:
            continue
        ax, ay = points[first]
        bx, by = points[last]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        far, far_dist = -1, -1.0
        for i in range(first + 1, last):
            px, py = points[i]
            if norm == 0:
                dist = math.hypot(px - ax, py - ay)
            else:
                dist = abs(dy * px - dx * py + bx * ay - by * ax) / norm
            if dist > far_dist:
                far, far_dist = i, dist
        if far_dist > tol:
            keep[far] = True
            stack.append((first, far))
            stack.append((far, last))
    return [p for p, k in zip(points, keep) if k]


def ring_area(points):
    """鞋带公式，返回绝对面积。"""
    s = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def dash_segment(points):
    """细长的九段线虚线段改用中心线表示（主成分分析取两端点）。

    按多边形直接画会因线宽不足一个画布单位而塌陷，画成带描边的线段更稳。
    """
    n = len(points)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    sxx = sum((p[0] - cx) ** 2 for p in points)
    syy = sum((p[1] - cy) ** 2 for p in points)
    sxy = sum((p[0] - cx) * (p[1] - cy) for p in points)

    theta = 0.5 * math.atan2(2 * sxy, sxx - syy)
    ux, uy = math.cos(theta), math.sin(theta)
    ts = [(p[0] - cx) * ux + (p[1] - cy) * uy for p in points]
    t_min, t_max = min(ts), max(ts)
    span = (t_max - t_min) or 1.0

    def mean_of(selected):
        return (sum(p[0] for p in selected) / len(selected),
                sum(p[1] for p in selected) / len(selected))

    head = [p for p, t in zip(points, ts) if t - t_min <= span * 0.25]
    tail = [p for p, t in zip(points, ts) if t_max - t <= span * 0.25]
    return mean_of(head), mean_of(tail)


def iter_rings(geometry):
    """把 Polygon / MultiPolygon 统一成一个个外环（忽略内环，省级区划的内环极少）。"""
    if not geometry:
        return
    if geometry["type"] == "Polygon":
        for ring in geometry["coordinates"]:
            yield ring
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            for ring in polygon:
                yield ring


def load_source():
    if not os.path.exists(CACHE):
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        print("下载数据源 …")
        with urllib.request.urlopen(SRC_URL, timeout=120) as resp:
            raw = resp.read()
        with open(CACHE, "wb") as fh:
            fh.write(raw)
    with open(CACHE, encoding="utf-8") as fh:
        return json.load(fh)


def path_d(points):
    """点列表 -> 紧凑的 SVG path（M 后面接隐式 lineto）。"""
    head = "M%d %d" % points[0]
    rest = " ".join("%d %d" % p for p in points[1:])
    return head + (" " + rest if rest else "") + "Z"


def build():
    data = load_source()
    project = make_albers()

    # ---- 第一遍：投影所有外环，算出整体包围盒 ----
    raw = []  # [(adcode, name, props, [投影后的环, ...]), ...]
    for feature in data["features"]:
        props = feature["properties"]
        rings = [[project(lon, lat) for lon, lat in ring]
                 for ring in iter_rings(feature["geometry"])]
        raw.append((str(props.get("adcode", "")), props.get("name") or "", props, rings))

    xs = [p[0] for _, _, _, rings in raw for ring in rings for p in ring]
    ys = [p[1] for _, _, _, rings in raw for ring in rings for p in ring]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)

    scale = (VIEW_W - 2 * MARGIN) / (max_x - min_x)
    view_h = round((max_y - min_y) * scale + 2 * MARGIN, 1)

    def to_canvas(pt):
        x = MARGIN + (pt[0] - min_x) * scale
        y = MARGIN + (max_y - pt[1]) * scale  # SVG 的 y 轴向下，翻转一次
        return x, y

    # ---- 第二遍：简化、筛碎岛、量化成整数坐标 ----
    provinces, nine_dash, dropped = [], [], 0
    islet_total = 0
    south_sea = None  # 南海诸岛点群的中心，页面用来放"南海诸岛"标注
    preview_rings = []  # [(adcode, [画布坐标环, ...]), ...] 仅用于预览渲染

    for adcode, name, props, rings in raw:
        canvas_rings = [[to_canvas(p) for p in ring] for ring in rings]

        if adcode == NINE_DASH_ID:
            for ring in canvas_rings:
                (x1, y1), (x2, y2) = dash_segment(ring)
                nine_dash.append("M%d %dL%d %d" % (round(x1), round(y1), round(x2), round(y2)))
            continue

        simplified = []
        islets = []  # 小到画不出形状的岛，用方块点代替
        for ring in canvas_rings:
            if len(ring) >= 4 and ring_area(ring) < ISLET_AREA:
                rx = [p[0] for p in ring]
                ry = [p[1] for p in ring]
                islets.append(((min(rx) + max(rx)) / 2.0, (min(ry) + max(ry)) / 2.0))
                continue

            pts = simplify(ring, TOLERANCE)
            # 去掉量化后重复的点
            quant = []
            for x, y in pts:
                node = (int(round(x)), int(round(y)))
                if not quant or quant[-1] != node:
                    quant.append(node)
            if len(quant) > 1 and quant[0] == quant[-1]:
                quant.pop()
            if len(quant) >= 3:
                simplified.append((ring_area(quant), quant))

        simplified.sort(key=lambda item: item[0], reverse=True)
        kept = []
        for index, (area, pts) in enumerate(simplified):
            if index < KEEP_TOP_RINGS or area >= MIN_RING_AREA:
                kept.append(pts)
            else:
                dropped += 1

        islet_total += len(islets)
        for cx, cy in islets:
            x0, y0 = int(round(cx - ISLET_HALF)), int(round(cy - ISLET_HALF))
            x1, y1 = int(round(cx + ISLET_HALF)), int(round(cy + ISLET_HALF))
            kept.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])

        if adcode == "460000" and islets:
            south_sea = [
                round(sum(p[0] for p in islets) / len(islets)),
                round(sum(p[1] for p in islets) / len(islets)),
            ]

        if not kept:
            continue

        center = props.get("centroid") or props.get("center")
        if center:
            cx, cy = to_canvas(project(center[0], center[1]))
        else:
            cx, cy = kept[0][0]
        provinces.append({
            "id": adcode,
            "name": name,
            "short": short_name(name),
            "region": REGIONS.get(adcode, "其他"),
            "center": [int(round(cx)), int(round(cy))],
            "d": " ".join(path_d(pts) for pts in kept),
        })
        preview_rings.append((adcode, kept))

    provinces.sort(key=lambda p: p["id"])

    payload = {
        "viewBox": "0 0 %d %s" % (int(VIEW_W), view_h),
        "provinces": provinces,
        "nineDash": " ".join(nine_dash),
    }
    if south_sea:
        payload["southSea"] = {"x": south_sea[0], "y": south_sea[1]}
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("// 由 tools/build_china_map.py 生成，请勿手工修改。\n")
        fh.write("// 数据源：阿里云 DataV 全国省级边界（Albers 投影 + Douglas-Peucker 简化）\n")
        fh.write("window.CHINA_MAP_DATA = %s;\n" % body)

    size_kb = os.path.getsize(OUT) / 1024.0
    print("省份 %d 个，丢弃碎岛 %d 个，小岛转点 %d 个，九段线 %d 段"
          % (len(provinces), dropped, islet_total, len(nine_dash)))
    print("viewBox = %s，输出 %.1f KB -> %s" % (payload["viewBox"], size_kb, os.path.relpath(OUT, ROOT)))
    return payload, preview_rings


def draw_preview(payload, preview_rings):
    """把生成结果画成 PNG，用来肉眼确认版图是否正确。"""
    from PIL import Image, ImageDraw

    _, _, vw, vh = payload["viewBox"].split()
    vw, vh = int(vw), float(vh)
    ratio = 2  # 2 倍超采样，线条看得清
    img = Image.new("RGB", (int(vw) * ratio, int(vh * ratio)), (240, 245, 255))
    draw = ImageDraw.Draw(img)

    # 挑几个省涂成"已点亮"，确认填充效果
    lit = {"530000", "440000", "310000", "110000", "650000"}
    for adcode, rings in preview_rings:
        fill = (162, 89, 230) if adcode in lit else (236, 230, 247)
        for pts in rings:
            if len(pts) >= 3:
                draw.polygon([(x * ratio, y * ratio) for x, y in pts],
                             fill=fill, outline=(255, 255, 255))

    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    img.save(PREVIEW)
    print("预览图 -> %s" % os.path.relpath(PREVIEW, ROOT))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成中国省级旅行地图数据")
    parser.add_argument("--preview", action="store_true", help="额外渲染一张 PNG 预览图")
    args = parser.parse_args()

    result, rings = build()
    if args.preview:
        draw_preview(result, rings)
