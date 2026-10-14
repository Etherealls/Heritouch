<template>
  <view class="create">
    <!-- 页面说明 -->
    <view class="page-intro">
      <text class="page-intro-title">AI 互动创作</text>
      <text class="page-intro-sub">输入灵感，AI 帮你生成非遗纹样、科普剧本与风格画作</text>
    </view>

    <!-- 三个功能大卡片 -->
    <view class="feature-list">
      <view class="feature-item card" @click="goPattern">
        <view class="feature-icon" style="background: linear-gradient(135deg, #b03a2e, #d45a4a)">
          <text>✂️</text>
        </view>
        <view class="flex-1">
          <text class="feature-name">非遗纹样生成</text>
          <text class="feature-desc">剪纸 / 漆器 / 玉雕 / 蓝印花布风格，一键生成创意图案</text>
        </view>
        <text class="feature-arrow">›</text>
      </view>

      <view class="feature-item card" @click="goScript">
        <view class="feature-icon" style="background: linear-gradient(135deg, #c9a063, #ddc08f)">
          <text>📜</text>
        </view>
        <view class="flex-1">
          <text class="feature-name">科普剧本生成</text>
          <text class="feature-desc">选定主题与时长，自动生成多场景非遗科普小剧本</text>
        </view>
        <text class="feature-arrow">›</text>
      </view>

      <view class="feature-item card" @click="goPainting">
        <view class="feature-icon" style="background: linear-gradient(135deg, #3f6f6a, #5d8a85)">
          <text>🖌️</text>
        </view>
        <view class="flex-1">
          <text class="feature-name">非遗风格画作</text>
          <text class="feature-desc">漆画 / 水墨 / 年画 / 刺绣风格，支持文生图与图生图</text>
        </view>
        <text class="feature-arrow">›</text>
      </view>
    </view>

    <!-- 我的作品入口行 -->
    <view class="my-works card" @click="goWorks">
      <view class="my-works-icon">
        <text>🗂️</text>
      </view>
      <text class="flex-1 my-works-text">我的作品</text>
      <text class="feature-arrow">›</text>
    </view>

    <!-- 合规提示 -->
    <view class="compliance">
      <text class="compliance-icon">🛡️</text>
      <text class="compliance-text">AI 生成内容将标注“AI 创作”标识，仅作学习交流使用</text>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
/* ---------- 页面跳转 ---------- */

/* 纹样生成页 */
function goPattern() {
  uni.navigateTo({ url: '/pages/create/pattern' })
}

/* 剧本生成页 */
function goScript() {
  uni.navigateTo({ url: '/pages/create/script' })
}

/* 画作生成页 */
function goPainting() {
  uni.navigateTo({ url: '/pages/create/painting' })
}

/* 我的作品页 */
function goWorks() {
  uni.navigateTo({ url: '/pages/profile/works' })
}
</script>

<style lang="scss" scoped>
.create {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
  padding-top: calc(40rpx + constant(safe-area-inset-top));
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

/* ---------- 页面说明 ---------- */
.page-intro {
  padding: 8rpx 0 36rpx;
}
.page-intro-title {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
  color: $ink;
  letter-spacing: 1rpx;
}
.page-intro-sub {
  display: block;
  font-size: 24rpx;
  color: $ink-light;
  margin-top: 12rpx;
  line-height: 1.6;
}

/* ---------- 功能大卡片 ---------- */
.feature-list {
  margin-bottom: 32rpx;
}
.feature-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 24rpx;
  padding: 36rpx 32rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
  transition: transform 0.1s ease;
  &:active { transform: scale(0.99); }
}
.feature-icon {
  width: 104rpx;
  height: 104rpx;
  border-radius: 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 52rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
  box-shadow: $shadow-xs;
}
.feature-name {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $ink;
}
.feature-desc {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 10rpx;
  line-height: 1.55;
}
.feature-arrow {
  font-size: 44rpx;
  color: $ink-faint;
  margin-left: 16rpx;
  flex-shrink: 0;
}

/* ---------- 我的作品入口 ---------- */
.my-works {
  display: flex;
  flex-direction: row;
  align-items: center;
  min-height: 112rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.my-works-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 20rpx;
  background: $primary-bg;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  margin-right: 20rpx;
}
.my-works-text {
  font-size: 30rpx;
  font-weight: 600;
  color: $ink;
}

/* ---------- 合规提示 ---------- */
.compliance {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-top: 32rpx;
  background: #fdf6e8;
  border: 1rpx solid #f0e2c4;
  border-radius: $radius-md;
  padding: 24rpx 28rpx;
}
.compliance-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}
.compliance-text {
  flex: 1;
  font-size: 22rpx;
  color: #9a7b3a;
  line-height: 1.6;
}

.bottom-gap {
  height: 60rpx;
}
</style>
