---
title: This is Midouzha's first website
layout: home
---

<!-- 浮动爱心装饰 -->
<div class="floating-hearts" id="floating-hearts"></div>

<div class="home-intro">
  <h1>💕 欢迎来到我的个人网站 💕</h1>
  <p>这里记录着我的生活、想法和对Z的无尽爱意</p>
  <p>愿每一个美好的瞬间都被珍藏在这里</p>
  <a href="{{ '/assets/zhouyangyang.jpg' | relative_url }}" class="btn" target="_blank">✨ 查看我的照片 ✨</a>
</div>

## ✨ 最新文章

---

<div class="decorative-quote scroll-animation">
  <p style="font-style: italic; color: #7f8c8d; text-align: center; font-size: 1.1rem; line-height: 1.6;">
    某人想我的话，不妨偶尔来转转，万一更新了呢，那是我也想你的证明
  </p>
</div>

<script>
// 创建浮动爱心
function createFloatingHearts() {
  const heartsContainer = document.getElementById('floating-hearts');
  const heartSymbols = ['💕', '💖', '💗', '💝', '💘', '💞', '💓', '💟'];
  
  function createHeart() {
    const heart = document.createElement('div');
    heart.className = 'heart';
    heart.innerHTML = heartSymbols[Math.floor(Math.random() * heartSymbols.length)];
    heart.style.left = Math.random() * 100 + 'vw';
    heart.style.fontSize = (Math.random() * 10 + 15) + 'px';
    heart.style.animationDuration = (Math.random() * 3 + 4) + 's';
    heart.style.animationDelay = Math.random() * 2 + 's';
    
    heartsContainer.appendChild(heart);
    
    // 动画结束后移除元素
    setTimeout(() => {
      if (heart.parentNode) {
        heart.parentNode.removeChild(heart);
      }
    }, 8000);
  }
  
  // 定期创建爱心
  setInterval(createHeart, 800);
}

// 滚动动画
function handleScrollAnimation() {
  const elements = document.querySelectorAll('.scroll-animation');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate');
      }
    });
  }, {
    threshold: 0.1
  });
  
  elements.forEach(element => {
    observer.observe(element);
  });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  createFloatingHearts();
  handleScrollAnimation();
  
  // 为主页添加入场动画延迟
  setTimeout(() => {
    document.querySelector('.home-intro').style.animationDelay = '0s';
  }, 100);
});
</script>
