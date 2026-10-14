<template>
  <view class="index">
    <!-- 顶部品牌区（自定义导航） -->
    <view class="brand">
      <!-- 状态栏占位 -->
      <view class="status-bar"></view>
      <view class="brand-row">
        <view class="brand-logo">
          <text class="brand-logo-text">遗</text>
        </view>
        <view class="flex-1">
          <text class="brand-title">Heritouch 非遗</text>
          <text class="brand-slogan">可查询 · 可互动 · 可创作 · 可游玩</text>
        </view>
      </view>
      <!-- 搜索框 -->
      <view class="search-box" @click="goList">
        <text class="search-icon">🔍</text>
        <text class="search-placeholder">搜索非遗项目 / 传承人 / 关键词</text>
      </view>
    </view>

    <!-- 分类金刚区（横滑） -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">非遗分类</text>
        <text class="section-more" @click="goList">全部 ›</text>
      </view>
      <scroll-view scroll-x class="cat-scroll" :show-scrollbar="false" :enable-flex="true">
        <view class="cat-row">
          <view
            class="cat-item"
            v-for="c in categories"
            :key="c.id"
            @click="goList({ category: c.name })"
          >
            <view class="cat-icon" :style="{ background: catGradient(c.id) }">
              <text>{{ c.icon }}</text>
            </view>
            <text class="cat-name">{{ c.name }}</text>
            <text class="cat-count">{{ c.count }} 项</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 精选非遗横滑卡片 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">精选非遗</text>
        <text class="section-more" @click="goList">更多 ›</text>
      </view>
      <scroll-view scroll-x class="feature-scroll" :show-scrollbar="false" :enable-flex="true" v-if="featured.length">
        <view class="feature-row">
          <view
            class="feature-card"
            v-for="p in featured"
            :key="p.id"
            @click="goDetail(p.id)"
          >
            <view class="feature-cover" :style="{ background: coverGradient(p.id) }">
              <text class="feature-cover-text">{{ p.name.slice(0, 2) }}</text>
              <view class="feature-level">{{ p.level }}</view>
            </view>
            <view class="feature-body">
              <text class="feature-name text-ellipsis">{{ p.name }}</text>
              <text class="feature-intro text-ellipsis-2">{{ p.intro }}</text>
            </view>
          </view>
        </view>
      </scroll-view>
      <view class="card loading-card" v-else>
        <text class="loading-text">正在加载精选非遗…</text>
      </view>
    </view>

    <!-- 四大功能入口网格 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">探索更多</text>
      </view>
      <view class="entry-grid">
        <view class="entry-card" @click="switchTab('/pages/atlas/atlas')">
          <view class="entry-icon" style="background: linear-gradient(135deg, #b03a2e, #d45a4a)">
            <text>🕸️</text>
          </view>
          <text class="entry-name">非遗图谱</text>
          <text class="entry-desc">关系网络一眼看清</text>
        </view>
        <view class="entry-card" @click="switchTab('/pages/create/create')">
          <view class="entry-icon" style="background: linear-gradient(135deg, #c9a063, #ddc08f)">
            <text>🎨</text>
          </view>
          <text class="entry-name">AI 创作</text>
          <text class="entry-desc">纹样剧本画作生成</text>
        </view>
        <view class="entry-card" @click="goGuide">
          <view class="entry-icon" style="background: linear-gradient(135deg, #3f6f6a, #5d8a85)">
            <text>🎧</text>
          </view>
          <text class="entry-name">智能导览</text>
          <text class="entry-desc">语音讲解与问答</text>
        </view>
        <view class="entry-card" @click="switchTab('/pages/game/game')">
          <view class="entry-icon" style="background: linear-gradient(135deg, #3d3529, #5c5344)">
            <text>🎮</text>
          </view>
          <text class="entry-name">科普闯关</text>
          <text class="entry-desc">答题闯关当大师</text>
        </view>
      </view>
    </view>

    <!-- 底部非遗小知识卡片 -->
    <view class="section">
      <view class="knowledge">
        <view class="knowledge-header">
          <text class="knowledge-badge">非遗小知识</text>
        </view>
        <text class="knowledge-text">{{ knowledge.text }}</text>
        <text class="knowledge-source">—— {{ knowledge.source }}</text>
      </view>
    </view>

    <!-- 底部留白 -->
    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getCategories, getProjectList } from '@/api/heritage'

const categories = ref([])
const featured = ref([])
const knowledge = ref({
  text: '扬州剪纸以"细、秀、雅、活"著称，早期多用作刺绣底样，因此又称"剪纸绣样"，2006 年列入第一批国家级非物质文化遗产名录。',
  source: '《扬州非遗名录》'
})

function coverGradient(id) {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)',
    'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    'linear-gradient(135deg, #c9a063, #ddc08f)',
    'linear-gradient(135deg, #3d3529, #5c5344)'
  ]
  return palettes[(Number(id) || 0) % palettes.length]
}

function catGradient(id) {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)',
    'linear-gradient(135deg, #c9a063, #ddc08f)',
    'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    'linear-gradient(135deg, #8c9a5b, #a8b678)',
    'linear-gradient(135deg, #9c6b9e, #b98cb9)',
    'linear-gradient(135deg, #d98e2b, #e8ac5e)',
    'linear-gradient(135deg, #3d3529, #5c5344)'
  ]
  return palettes[(Number(id) - 1) % palettes.length] || palettes[0]
}

function goList(query) {
  const q = query ? '?' + Object.keys(query).map((k) => k + '=' + encodeURIComponent(query[k])).join('&') : ''
  uni.navigateTo({ url: '/pages/heritage/list' + q })
}

function goDetail(id) {
  uni.navigateTo({ url: '/pages/heritage/detail?id=' + id })
}

function goGuide() {
  uni.navigateTo({ url: '/pages/guide/guide?id=1' })
}

function switchTab(url) {
  uni.switchTab({ url })
}

async function loadData() {
  try {
    const [cats, list] = await Promise.all([getCategories(), getProjectList({ page: 1, size: 6 })])
    categories.value = cats || []
    featured.value = (list && list.list) || []
  } catch (e) {
    uni.showToast({ title: '数据加载失败', icon: 'none' })
  }
}

onShow(loadData)
</script>

<style lang="scss" scoped>
.index {
  min-height: 100vh;
  background: $paper;
  padding-bottom: 60rpx;
}

/* ---------- 品牌区 ---------- */
.brand {
  background: linear-gradient(165deg, #b03a2e 0%, #943025 55%, #7c241c 100%);
  padding: 0 40rpx 72rpx;
  border-radius: 0 0 48rpx 48rpx;
  position: relative;
  overflow: hidden;
}
/* 品牌区装饰光斑，增加层次 */
.brand::after {
  content: '';
  position: absolute;
  top: -120rpx;
  right: -80rpx;
  width: 320rpx;
  height: 320rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
}
.status-bar {
  height: 60rpx;
}
.brand-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: relative;
  z-index: 1;
}
.brand-logo {
  width: 92rpx;
  height: 92rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, 0.96);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
  box-shadow: 0 8rpx 20rpx rgba(0, 0, 0, 0.16);
}
.brand-logo-text {
  font-size: 52rpx;
  font-weight: 700;
  color: $primary;
}
.brand-title {
  display: block;
  font-size: 42rpx;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2rpx;
  line-height: 1.3;
}
.brand-slogan {
  display: block;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 10rpx;
  letter-spacing: 3rpx;
}

.search-box {
  margin-top: 40rpx;
  height: 88rpx;
  border-radius: $radius-pill;
  background: #fff;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.14);
  position: relative;
  z-index: 1;
}
.search-icon {
  font-size: 28rpx;
  margin-right: 16rpx;
  color: $ink-light;
}
.search-placeholder {
  font-size: 26rpx;
  color: $ink-faint;
}

/* ---------- 通用区块 ---------- */
.section {
  padding: 0 40rpx;
  margin-top: 48rpx;
}
.section-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28rpx;
}
.section-more {
  font-size: 24rpx;
  color: $ink-light;
  padding: 8rpx 0;
}

/* ---------- 分类金刚区 ---------- */
.cat-scroll {
  width: 100%;
}
.cat-row {
  display: flex;
  flex-direction: row;
  padding-bottom: 8rpx;
  width: max-content;
}
.cat-item {
  display: flex;
  flex-direction: column;
  width: 156rpx;
  align-items: center;
  margin-right: 28rpx;
  flex-shrink: 0;
}
.cat-icon {
  width: 104rpx;
  height: 104rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 46rpx;
  box-shadow: $shadow-card;
  margin-bottom: 14rpx;
}
.cat-name {
  font-size: 24rpx;
  color: $ink;
  font-weight: 600;
  line-height: 1.4;
}
.cat-count {
  font-size: 20rpx;
  color: $ink-light;
  margin-top: 4rpx;
}

/* ---------- 精选非遗横滑 ---------- */
.feature-scroll {
  width: 100%;
}
.feature-row {
  display: flex;
  flex-direction: row;
  padding-bottom: 12rpx;
  width: max-content;
}
.feature-card {
  width: 320rpx;
  margin-right: 28rpx;
  background: $card;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
  overflow: hidden;
  flex-shrink: 0;
}
.feature-cover {
  height: 208rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.feature-cover-text {
  font-size: 68rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.94);
  letter-spacing: 8rpx;
  text-shadow: 0 4rpx 14rpx rgba(0, 0, 0, 0.2);
}
.feature-level {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  font-size: 18rpx;
  color: #fff;
  background: rgba(0, 0, 0, 0.28);
  border-radius: $radius-pill;
  padding: 6rpx 16rpx;
}
.feature-body {
  padding: 22rpx 26rpx 26rpx;
}
.feature-name {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
}
.feature-intro {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.55;
  margin-top: 8rpx;
  min-height: 68rpx;
}

/* ---------- 四大功能入口 ---------- */
.entry-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
}
.entry-card {
  background: $card;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
  padding: 30rpx 28rpx;
  transition: transform 0.1s ease;
  &:active { transform: scale(0.98); }
}
.entry-icon {
  width: 84rpx;
  height: 84rpx;
  border-radius: 26rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-bottom: 18rpx;
}
.entry-name {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
}
.entry-desc {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 8rpx;
}

/* ---------- 小知识卡片 ---------- */
.knowledge {
  background: linear-gradient(135deg, #fdf9f0, #f6efe0);
  border: 1rpx solid $border;
  border-radius: $radius-xl;
  padding: 32rpx;
}
.knowledge-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 18rpx;
}
.knowledge-badge {
  font-size: 22rpx;
  color: #fff;
  background: linear-gradient(135deg, $gold, $gold-deep);
  border-radius: $radius-pill;
  padding: 8rpx 22rpx;
  font-weight: 600;
}
.knowledge-text {
  font-size: 26rpx;
  color: $ink;
  line-height: 1.8;
}
.knowledge-source {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  text-align: right;
  margin-top: 16rpx;
}

/* ---------- 其他 ---------- */
.loading-card {
  display: flex;
  padding: 60rpx;
  align-items: center;
}
.loading-text {
  font-size: 26rpx;
  color: $ink-light;
}
.bottom-gap {
  height: 40rpx;
}
</style>
