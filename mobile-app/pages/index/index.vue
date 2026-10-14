<template>
  <view class="index">
    <!-- 顶部品牌区（自定义导航，渐变朱砂红背景） -->
    <view class="brand">
      <view class="brand-row">
        <!-- 印章 Logo 色块 -->
        <view class="brand-logo">
          <text class="brand-logo-text">遗</text>
        </view>
        <view class="flex-1">
          <view class="brand-title-row">
            <text class="brand-title">Heritouch 非遗</text>
          </view>
          <text class="brand-slogan">可查询 · 可互动 · 可创作 · 可游玩</text>
        </view>
      </view>
      <!-- 搜索框（点击跳转名录页） -->
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
            class="feature-card card"
            v-for="p in featured"
            :key="p.id"
            @click="goDetail(p.id)"
          >
            <!-- 渐变色块封面占位（无图片资源） -->
            <view class="feature-cover" :style="{ background: coverGradient(p.id) }">
              <text class="feature-cover-text">{{ p.name.slice(0, 2) }}</text>
              <view class="feature-level">{{ p.level }}</view>
            </view>
            <text class="feature-name text-ellipsis">{{ p.name }}</text>
            <text class="feature-intro text-ellipsis-2">{{ p.intro }}</text>
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
        <view class="entry-card card" @click="switchTab('/pages/atlas/atlas')">
          <view class="entry-icon" style="background: linear-gradient(135deg, #b03a2e, #d45a4a)">
            <text>🕸️</text>
          </view>
          <text class="entry-name">非遗图谱</text>
          <text class="entry-desc">关系网络一眼看清</text>
        </view>
        <view class="entry-card card" @click="switchTab('/pages/create/create')">
          <view class="entry-icon" style="background: linear-gradient(135deg, #c9a063, #ddc08f)">
            <text>🎨</text>
          </view>
          <text class="entry-name">AI 创作</text>
          <text class="entry-desc">纹样剧本画作生成</text>
        </view>
        <view class="entry-card card" @click="goGuide">
          <view class="entry-icon" style="background: linear-gradient(135deg, #3f6f6a, #5d8a85)">
            <text>🎧</text>
          </view>
          <text class="entry-name">智能导览</text>
          <text class="entry-desc">语音讲解与问答</text>
        </view>
        <view class="entry-card card" @click="switchTab('/pages/game/game')">
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
      <view class="knowledge card">
        <view class="knowledge-header">
          <text class="knowledge-badge">非遗小知识</text>
        </view>
        <text class="knowledge-text">{{ knowledge.text }}</text>
        <text class="knowledge-source">—— {{ knowledge.source }}</text>
      </view>
    </view>

    <!-- 底部留白（tabBar 安全区） -->
    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getCategories, getProjectList } from '@/api/heritage'

/* ---------- 数据 ---------- */
const categories = ref([])
const featured = ref([])
// 每日非遗小知识（静态文案，可按日期轮换）
const knowledge = ref({
  text: '扬州剪纸以“细、秀、雅、活”著称，早期多用作刺绣底样，因此又称“剪纸绣样”，2006 年列入第一批国家级非物质文化遗产名录。',
  source: '《扬州非遗名录》'
})

/* ---------- 工具函数 ---------- */

/* 按 id 生成渐变色系（朱砂红/黛青/泥金/墨色轮换，规避不存在的图片资源） */
function coverGradient(id) {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)', // 朱砂红
    'linear-gradient(135deg, #3f6f6a, #5d8a85)', // 黛青
    'linear-gradient(135deg, #c9a063, #ddc08f)', // 泥金
    'linear-gradient(135deg, #3d3529, #5c5344)' // 墨色
  ]
  return palettes[(Number(id) || 0) % palettes.length]
}

/* 分类图标底色（按分类 id 轮换色系） */
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

/* ---------- 页面跳转 ---------- */

/* 跳转名录页（可带筛选参数，非 tab 页用 navigateTo） */
function goList(query) {
  const q = query ? '?' + Object.keys(query).map((k) => k + '=' + encodeURIComponent(query[k])).join('&') : ''
  uni.navigateTo({ url: '/pages/heritage/list' + q })
}

/* 跳转项目详情 */
function goDetail(id) {
  uni.navigateTo({ url: '/pages/heritage/detail?id=' + id })
}

/* 智能导览入口（演示项目 id=1 扬州剪纸） */
function goGuide() {
  uni.navigateTo({ url: '/pages/guide/guide?id=1' })
}

/* tab 页之间切换 */
function switchTab(url) {
  uni.switchTab({ url })
}

/* ---------- 生命周期 ---------- */

/* 页面显示时刷新数据（从其他 tab 返回也能更新） */
async function loadData() {
  try {
    const [cats, list] = await Promise.all([getCategories(), getProjectList({ page: 1, size: 6 })])
    categories.value = cats || []
    featured.value = (list && list.list) || []
  } catch (e) {
    uni.showToast({ title: '数据加载失败', icon: 'none' })
  }
}

// onShow：tab 页每次展示都刷新，保证数据最新
onShow(loadData)
</script>

<style lang="scss" scoped>
.index {
  min-height: 100vh;
  background: $paper;
  padding-bottom: 40rpx;
}

/* ---------- 品牌区 ---------- */
.brand {
  background: linear-gradient(160deg, #b03a2e 0%, #8e2b21 60%, #7a241c 100%);
  padding: 24rpx 32rpx 72rpx;
  border-radius: 0 0 40rpx 40rpx;
}
.brand-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding-top: 24rpx;
}
.brand-logo {
  width: 88rpx;
  height: 88rpx;
  border-radius: 16rpx;
  background: $card;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
  box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.18);
}
.brand-logo-text {
  font-size: 48rpx;
  font-weight: 700;
  color: $primary;
}
.brand-title-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
}
.brand-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #fff;
  letter-spacing: 2rpx;
}
.brand-slogan {
  display: block;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.82);
  margin-top: 8rpx;
  letter-spacing: 4rpx;
}

/* 搜索框 */
.search-box {
  margin-top: 36rpx;
  height: 88rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.96);
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0 32rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}
.search-icon {
  font-size: 30rpx;
  margin-right: 16rpx;
}
.search-placeholder {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- 通用区块 ---------- */
.section {
  padding: 0 32rpx;
  margin-top: 40rpx;
}
.section-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}
.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: $ink;
  position: relative;
  padding-left: 20rpx;
}
.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8rpx;
  height: 32rpx;
  border-radius: 4rpx;
  background: $primary;
}
.section-more {
  font-size: 24rpx;
  color: $ink-light;
}

/* ---------- 分类金刚区 ---------- */
.cat-scroll {
  width: 100%;
}
.cat-row {
  display: flex;
  flex-direction: row;
  padding-bottom: 8rpx;
  width: max-content;}
.cat-item {
  display: flex;
  width: 160rpx;
  align-items: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}
.cat-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  box-shadow: $shadow-card;
}
.cat-name {
  font-size: 24rpx;
  color: $ink;
  margin-top: 12rpx;
  font-weight: 600;
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
  padding-bottom: 8rpx;
  width: max-content;}
.feature-card {
  width: 300rpx;
  margin-right: 24rpx;
  padding: 0;
  overflow: hidden;
  flex-shrink: 0;
}
.feature-cover {
  height: 200rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.feature-cover-text {
  font-size: 64rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 6rpx;
  text-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.2);
}
.feature-level {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  font-size: 18rpx;
  color: #fff;
  background: rgba(0, 0, 0, 0.28);
  border-radius: 999rpx;
  padding: 4rpx 16rpx;
}
.feature-name {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
  padding: 20rpx 24rpx 0;
}
.feature-intro {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.5;
  padding: 8rpx 24rpx 24rpx;
  min-height: 96rpx;
}

/* ---------- 四大功能入口 ---------- */
.entry-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
}
.entry-card {
  padding: 28rpx 24rpx;
}
.entry-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-bottom: 16rpx;
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
  margin-top: 6rpx;
}

/* ---------- 小知识卡片 ---------- */
.knowledge {
  background: linear-gradient(135deg, #fdf9f0, #f6efe0);
  border: 1rpx solid $border;
}
.knowledge-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 16rpx;
}
.knowledge-badge {
  font-size: 22rpx;
  color: #fff;
  background: linear-gradient(135deg, $gold, #b78d4e);
  border-radius: 999rpx;
  padding: 6rpx 20rpx;
  font-weight: 600;
}
.knowledge-text {
  font-size: 26rpx;
  color: $ink;
  line-height: 1.7;
}
.knowledge-source {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  text-align: right;
  margin-top: 12rpx;
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
