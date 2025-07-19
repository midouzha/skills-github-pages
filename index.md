---
layout: home
---

<div class="page-widgets-container">
  <!-- 左侧小工具：倒计时 -->
  <div class="side-widget left-widget">
    <div class="countdown-title">with周洋洋已经</div>
    <div id="countdown-days" class="countdown-days">-- 天</div>
  </div>

  <div class="main-content-area">
    <div class="home-intro">
  <h1>💕 欢迎来到我们的赛博小家 💕</h1>
  <p>这里记录着我们的生活、想法和对Z的无尽爱意</p>
  <p>每一个美好的瞬间都被我悄悄珍藏在这里</p>
  
  <!-- 情侣头像 -->
  <div class="couple-avatars">
    <div class="avatar-container">
      <img src="{{ '/assets/sheep_head.webp' | relative_url }}" alt="Midouzha" class="avatar-img">
      <div class="avatar-label">Midouzha</div>
    </div>
    <div class="love-heart">💕</div>
    <div class="avatar-container">
      <img src="{{ '/assets/z_con.jpg' | relative_url }}" alt="Z" class="avatar-img">
      <div class="avatar-label">Z</div>
    </div>
  </div>
</div>

<!-- 倒计时小工具 -->
<div class="countdown-card">
  <div class="countdown-title">with周洋洋已经</div>
  <div id="countdown-days" class="countdown-days">-- 天</div>
</div>

<script>
// 纯前端倒计时，Jekyll+GitHub Pages兼容
function updateCountdown() {
  var startDate = new Date('2025-05-26T00:00:00');
  var now = new Date();
  var diffTime = now - startDate;
  var days = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  document.getElementById('countdown-days').textContent = days + ' 天';
}
updateCountdown();
setInterval(updateCountdown, 60 * 60 * 1000);
</script>

    </div>
  </div>

  <!-- 右侧可扩展小工具区域（预留）-->
  <div class="side-widget right-widget"></div>
</div>

<script>
// 倒计时小工具脚本
function updateCountdown() {
  const startDate = new Date('2025-05-26T00:00:00');
  const now = new Date();
  const diffTime = now - startDate;
  const days = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  document.getElementById('countdown-days').textContent = days + ' 天';
}
updateCountdown();
setInterval(updateCountdown, 60 * 60 * 1000); // 每小时刷新一次
</script>

---
