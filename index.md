---
layout: home
---

<div class="home-intro">
  <h1>💕 欢迎来到我们的赛博小家 💕</h1>
  <p>这里记录着我的生活、想法和对Z的无尽爱意</p>
  <p>每一个美好的点滴被我悄悄珍藏在这里</p>
  <p>这里不写坏情绪，只写饱满的喜欢</p>
  <!-- 情侣头像 -->
  <div class="couple-avatars">
    <div class="avatar-container" onclick="showBubble('midouzha')">
      <img src="{{ '/assets/sheep_head.webp' | relative_url }}" alt="Midouzha" class="avatar-img">
      <div class="avatar-label">Midouzha</div>
      <!-- 气泡容器 -->
      <div id="bubble-midouzha" class="speech-bubble midouzha-bubble"></div>
    </div>
    <div class="love-heart">💕</div>
    <div class="avatar-container" onclick="showBubble('z')">
      <img src="{{ '/assets/z_con.jpg' | relative_url }}" alt="Z" class="avatar-img">
      <div class="avatar-label">Z</div>
      <!-- 气泡容器 -->
      <div id="bubble-z" class="speech-bubble z-bubble"></div>
    </div>
  </div>
  
  <!-- 倒计时小工具 -->
  <div class="countdown-widget">
    <div class="countdown-title">with周洋洋已经</div>
    <div id="countdown-days" class="countdown-days">-- 天</div>
  </div>
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

// 气泡特效功能
var midouzhaTexts = ['姐姐~', '喜欢姐姐~', '姐姐最漂亮啦💕', '好想姐姐', '求求姐姐啦','爱你宝贝！','想抱抱姐姐'];
var zTexts = ['爱你喔~', '嘻嘻', '好嘟💕', '嗯哼~', '哼哼哼','怎么啦','嗷~'];

function showBubble(target) {
  var bubbleId = 'bubble-' + target;
  var bubble = document.getElementById(bubbleId);
  var texts = target === 'midouzha' ? midouzhaTexts : zTexts;
  var avatarContainer = bubble.parentElement;
  
  // 随机选择文字
  var randomText = texts[Math.floor(Math.random() * texts.length)];
  
  // 设置气泡文字
  bubble.textContent = randomText;
  
  // 添加头像点击反馈效果
  avatarContainer.style.transform = 'scale(0.95)';
  setTimeout(function() {
    avatarContainer.style.transform = '';
  }, 150);
  
  // 显示气泡
  bubble.classList.add('show');
  
  // 1.5秒后隐藏气泡（稍微延长显示时间）
  setTimeout(function() {
    bubble.classList.remove('show');
  }, 1500);
}
</script>

---
