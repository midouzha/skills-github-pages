---
title: "Image Test"
date: 2025-07-18
---

# 测试不同的图片显示方式

## 方式1: 绝对路径
![周洋洋](/assets/zhouyangyang.jpg)

## 方式2: Jekyll relative_url 过滤器
![周洋洋]({{ "/assets/zhouyangyang.jpg" | relative_url }})

## 方式3: Jekyll site.baseurl
![周洋洋]({{ site.baseurl }}/assets/zhouyangyang.jpg)

## 方式4: HTML img 标签
<img src="/assets/zhouyangyang.jpg" alt="周洋洋" width="300">

## 方式5: 相对路径（从根目录）
![周洋洋](./assets/zhouyangyang.jpg)

## 方式6: GitHub仓库原始文件链接
![周洋洋](https://raw.githubusercontent.com/midouzha/skills-github-pages/main/assets/zhouyangyang.jpg)
