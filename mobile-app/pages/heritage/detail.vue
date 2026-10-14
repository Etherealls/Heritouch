<template>
  <view class="detail" v-if="project">
    <!-- ===== 头部渐变封面区 ===== -->
    <view class="hero" :style="{ background: heroGradient }">
      <!-- 收藏按钮 -->
      <view class="hero-fav" @click="onToggleFavorite">
        <text>{{ favorited ? '❤️' : '🤍' }}</text>
      </view>
      <text class="hero-name">{{ project.name }}</text>
      <view class="hero-tags">
        <view class="hero-level">{{ project.level }}</view>
        <view class="hero-batch">{{ project.batch }} 年入选</view>
      </view>
    </view>

    <!-- ===== 信息行 ===== -->
    <view class="info-bar card">
      <view class="info-item">
        <text class="info-label">类别</text>
        <text class="info-value">{{ project.category }}</text>
      </view>
      <view class="info-divider"></view>
      <view class="info-item">
        <text class="info-label">地区</text>
        <text class="info-value">{{ project.region }}</text>
      </view>
      <view class="info-divider"></view>
      <view class="info-item">
        <text class="info-label">批次</text>
        <text class="info-value">{{ project.batch }}</text>
      </view>
    </view>

    <!-- ===== 简介 / 历史 / 工艺 ===== -->
    <view class="section card">
      <text class="section-title">项目简介</text>
      <text class="section-text">{{ project.intro }}</text>
    </view>

    <view class="section card">
      <text class="section-title">历史渊源</text>
      <text class="section-text">{{ project.history }}</text>
    </view>

    <view class="section card">
      <text class="section-title">工艺流程</text>
      <view class="craft-step" v-for="(step, i) in craftSteps" :key="i">
        <view class="craft-index">{{ i + 1 }}</view>
        <text class="craft-text">{{ step }}</text>
      </view>
    </view>

    <!-- ===== 传承人横滑 ===== -->
    <view class="section" v-if="inheritors.length">
      <view class="section-header">
        <text class="section-title plain">代表性传承人</text>
      </view>
      <scroll-view scroll-x class="people-scroll" :show-scrollbar="false">
        <view class="people-row">
          <view class="person-card card" v-for="p in inheritors" :key="p.id">
            <!-- 圆形头像占位 -->
            <view class="person-avatar" :style="{ background: avatarGradient(p.id) }">
              <text>{{ p.name.slice(0, 1) }}</text>
            </view>
            <text class="person-name text-ellipsis">{{ p.name }}</text>
            <text class="person-title text-ellipsis">{{ p.title }}</text>
            <text class="person-bio text-ellipsis-2">{{ p.biography }}</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- ===== 代表作品 / 关联民俗 ===== -->
    <view class="section card" v-if="works.length">
      <text class="section-title">代表作品</text>
      <view class="tag-group">
        <text class="tag" v-for="(w, i) in works" :key="i">{{ w }}</text>
      </view>
    </view>

    <view class="section card" v-if="folkCustoms.length">
      <text class="section-title">关联民俗</text>
      <view class="tag-group">
        <text class="tag" v-for="(f, i) in folkCustoms" :key="i">{{ f }}</text>
      </view>
    </view>

    <!-- ===== 智能推荐 ===== -->
    <view class="section" v-if="recommendLoading || hasRecommend">
      <view class="section-header">
        <text class="section-title plain">智能推荐</text>
      </view>

      <!-- 相似推荐 -->
      <block v-if="recommend.similar && recommend.similar.length">
        <text class="rec-group-title">技艺相似</text>
        <scroll-view scroll-x class="rec-scroll" :show-scrollbar="false">
          <view class="rec-row">
            <view
              class="rec-card card"
              v-for="p in recommend.similar"
              :key="p.id"
              @click="goDetail(p.id)"
            >
              <view class="rec-cover" :style="{ background: coverGradient(p.id) }">
                <text>{{ p.name.slice(0, 2) }}</text>
              </view>
              <text class="rec-name text-ellipsis">{{ p.name }}</text>
            </view>
          </view>
        </scroll-view>
      </block>

      <!-- 同类推荐 -->
      <block v-if="recommend.sameCategory && recommend.sameCategory.length">
        <text class="rec-group-title">同属{{ project.category }}</text>
        <scroll-view scroll-x class="rec-scroll" :show-scrollbar="false">
          <view class="rec-row">
            <view
              class="rec-card card"
              v-for="p in recommend.sameCategory"
              :key="p.id"
              @click="goDetail(p.id)"
            >
              <view class="rec-cover" :style="{ background: coverGradient(p.id) }">
                <text>{{ p.name.slice(0, 2) }}</text>
              </view>
              <text class="rec-name text-ellipsis">{{ p.name }}</text>
            </view>
          </view>
        </scroll-view>
      </block>

      <!-- 同地区推荐 -->
      <block v-if="recommend.sameRegion && recommend.sameRegion.length">
        <text class="rec-group-title">同地区（{{ project.region }}）</text>
        <scroll-view scroll-x class="rec-scroll" :show-scrollbar="false">
          <view class="rec-row">
            <view
              class="rec-card card"
              v-for="p in recommend.sameRegion"
              :key="p.id"
              @click="goDetail(p.id)"
            >
              <view class="rec-cover" :style="{ background: coverGradient(p.id) }">
                <text>{{ p.name.slice(0, 2) }}</text>
              </view>
              <text class="rec-name text-ellipsis">{{ p.name }}</text>
            </view>
          </view>
        </scroll-view>
      </block>
    </view>

    <!-- 底部留白（避开固定操作栏） -->
    <view class="bottom-gap"></view>

    <!-- ===== 底部操作栏 ===== -->
    <view class="action-bar safe-bottom">
      <view class="action-btn" @click="goGuide">
        <text class="action-icon">🎧</text>
        <text class="action-text">语音讲解</text>
      </view>
      <view class="action-btn" @click="goScan">
        <text class="action-icon">📷</text>
        <text class="action-text">扫码导览</text>
      </view>
      <view class="action-btn primary" @click="onShare">
        <text class="action-icon">📤</text>
        <text class="action-text">分享</text>
      </view>
    </view>
  </view>

  <!-- 加载态 -->
  <view v-else-if="!loadError" class="detail-loading">
    <text class="detail-loading-text">正在加载项目详情…</text>
  </view>

  <!-- 加载失败 -->
  <view v-else class="detail-loading">
    <text class="detail-loading-text">项目加载失败</text>
    <view class="retry-btn" @click="loadDetail"><text>重新加载</text></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getProjectDetail, getRecommendations } from '@/api/heritage'
import { toggleFavorite } from '@/api/user'
import { useUserStore } from '@/store/user'
import { shareText } from '@/utils/util'

/* ---------- 数据 ---------- */
const userStore = useUserStore()
const project = ref(null)
const inheritors = ref([])
const works = ref([])
const folkCustoms = ref([])
const craftSteps = ref([])
const recommend = ref({})
const recommendLoading = ref(true)
const loadError = ref(false)
const favorited = ref(false)
const projectId = ref(0)

/* 封面渐变色（按 id 轮换色系） */
const heroGradient = computed(() => {
  const palettes = [
    'linear-gradient(160deg, #b03a2e, #8e2b21)',
    'linear-gradient(160deg, #3f6f6a, #2c5350)',
    'linear-gradient(160deg, #c9a063, #a87f45)',
    'linear-gradient(160deg, #3d3529, #28231b)'
  ]
  return palettes[((project.value && project.value.id) || 0) % palettes.length]
})

/* 是否存在推荐内容 */
const hasRecommend = computed(() => {
  const r = recommend.value
  return (r.similar && r.similar.length) || (r.sameCategory && r.sameCategory.length) || (r.sameRegion && r.sameRegion.length)
})

/* ---------- 工具函数 ---------- */

/* 按 id 生成渐变色系 */
function coverGradient(id) {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)',
    'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    'linear-gradient(135deg, #c9a063, #ddc08f)',
    'linear-gradient(135deg, #3d3529, #5c5344)'
  ]
  return palettes[(Number(id) || 0) % palettes.length]
}

/* 传承人头像占位渐变色（按 id 轮换） */
function avatarGradient(id) {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)',
    'linear-gradient(135deg, #c9a063, #ddc08f)',
    'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    'linear-gradient(135deg, #9c6b9e, #b98cb9)'
  ]
  return palettes[(Number(id) || 0) % palettes.length]
}

/* ---------- 数据加载 ---------- */
async function loadDetail() {
  loadError.value = false
  try {
    const data = await getProjectDetail(projectId.value)
    project.value = data
    inheritors.value = (data && data.inheritor_list) || []
    works.value = (data && data.works) || []
    folkCustoms.value = (data && data.folk_customs) || []
    // 工艺流程：按 → 拆分为有序步骤
    craftSteps.value = data && data.craft ? data.craft.split('→').filter(Boolean) : []
    // 判断是否已收藏
    favorited.value = userStore.favorites.some((f) => f.type === 'project' && f.id === data.id)
  } catch (e) {
    loadError.value = true
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

/* 加载推荐数据 */
async function loadRecommend() {
  recommendLoading.value = true
  try {
    recommend.value = await getRecommendations(projectId.value) || {}
  } catch (e) {
    recommend.value = {}
  } finally {
    recommendLoading.value = false
  }
}

/* ---------- 交互 ---------- */

/* 收藏 / 取消收藏 */
async function onToggleFavorite() {
  if (!project.value) return
  try {
    const res = await toggleFavorite({
      type: 'project',
      id: project.value.id,
      name: project.value.name,
      cover: project.value.cover_image || ''
    })
    favorited.value = res.favorited
    uni.showToast({ title: res.favorited ? '已收藏' : '已取消收藏', icon: 'none' })
  } catch (e) {
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

/* 跳转语音讲解 */
function goGuide() {
  uni.navigateTo({ url: '/pages/guide/guide?id=' + project.value.id })
}

/* 跳转扫码导览 */
function goScan() {
  uni.navigateTo({ url: '/pages/guide/scan' })
}

/* 分享 */
function onShare() {
  shareText(project.value.name, project.value.intro)
}

/* 跳转其他项目详情（推荐） */
function goDetail(id) {
  uni.navigateTo({ url: '/pages/heritage/detail?id=' + id })
}

/* ---------- 生命周期 ---------- */
onLoad((query) => {
  projectId.value = query && query.id ? Number(query.id) : 0
  loadDetail()
  loadRecommend()
})
</script>

<style lang="scss" scoped>
.detail {
  min-height: 100vh;
  background: $paper;
  padding-bottom: 40rpx;
}

/* ---------- 头部封面区 ---------- */
.hero {
  padding: 56rpx 32rpx 40rpx;
  position: relative;
}
.hero-fav {
  position: absolute;
  top: 32rpx;
  right: 32rpx;
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
}
.hero-name {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
  max-width: 560rpx;
}
.hero-tags {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 16rpx;
}
.hero-level {
  font-size: 20rpx;
  color: #fff;
  background: rgba(0, 0, 0, 0.28);
  border-radius: 999rpx;
  padding: 6rpx 20rpx;
  margin-right: 16rpx;
}
.hero-batch {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.85);
}

/* ---------- 信息行 ---------- */
.info-bar {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin: 24rpx 32rpx 0;
  padding: 24rpx 0;
}
.info-item {
  display: flex;
  flex: 1;
  align-items: center;
}
.info-label {
  display: block;
  font-size: 20rpx;
  color: $ink-light;
  text-align: center;
}
.info-value {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
  text-align: center;
  margin-top: 6rpx;
}
.info-divider {
  width: 1rpx;
  height: 48rpx;
  background: $border;
}

/* ---------- 内容区块 ---------- */
.section {
  margin: 24rpx 32rpx 0;
}
.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
  margin-bottom: 16rpx;
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
  height: 30rpx;
  border-radius: 4rpx;
  background: $primary;
}
.section-title.plain {
  margin-bottom: 0;
}
.section-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}
.section-text {
  font-size: 26rpx;
  color: $ink;
  line-height: 1.8;
}

/* 工艺流程步骤 */
.craft-step {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  margin-bottom: 16rpx;
}
.craft-step:last-child {
  margin-bottom: 0;
}
.craft-index {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary, $primary-light);
  color: #fff;
  font-size: 20rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
  margin-top: 4rpx;
  flex-shrink: 0;
}
.craft-text {
  flex: 1;
  font-size: 26rpx;
  color: $ink;
  line-height: 1.7;
}

/* ---------- 传承人横滑 ---------- */
.section .people-scroll {
  width: 100%;
}
.people-row {
  display: flex;
  flex-direction: row;
  padding-bottom: 8rpx;
}
.person-card {
  display: flex;
  width: 260rpx;
  margin-right: 20rpx;
  padding: 28rpx 20rpx;
  align-items: center;
}
.person-avatar {
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  font-weight: 700;
  color: #fff;
  margin-bottom: 16rpx;
}
.person-name {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
  max-width: 220rpx;
  text-align: center;
}
.person-title {
  display: block;
  font-size: 20rpx;
  color: $primary;
  max-width: 220rpx;
  text-align: center;
  margin-top: 6rpx;
}
.person-bio {
  display: block;
  font-size: 20rpx;
  color: $ink-light;
  line-height: 1.5;
  margin-top: 10rpx;
}

/* ---------- 标签组 ---------- */
.tag-group {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}

/* ---------- 推荐 ---------- */
.rec-group-title {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: $ink-light;
  margin: 20rpx 0 16rpx;
}
.rec-scroll {
  width: 100%;
}
.rec-row {
  display: flex;
  flex-direction: row;
  padding-bottom: 8rpx;
}
.rec-card {
  width: 180rpx;
  margin-right: 20rpx;
  padding: 0;
  overflow: hidden;
}
.rec-cover {
  height: 120rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 4rpx;
}
.rec-name {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  color: $ink;
  padding: 16rpx 16rpx 20rpx;
  max-width: 180rpx;
}

/* ---------- 加载态 ---------- */
.detail-loading {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: $paper;
}
.detail-loading-text {
  font-size: 26rpx;
  color: $ink-light;
}
.retry-btn {
  margin-top: 32rpx;
  padding: 16rpx 48rpx;
  border-radius: 999rpx;
  background: $primary;
}
.retry-btn text {
  font-size: 26rpx;
  color: #fff;
}

/* ---------- 底部操作栏 ---------- */
.action-bar {
  display: flex;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  flex-direction: row;
  align-items: center;
  background: $card;
  border-top: 1rpx solid $border;
  padding: 16rpx 32rpx 16rpx;
  box-shadow: 0 -4rpx 24rpx rgba(61, 53, 41, 0.06);
}
.action-btn {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 88rpx;
  border-radius: $radius-md;
}
.action-btn + .action-btn {
  margin-left: 16rpx;
}
.action-btn.primary {
  background: linear-gradient(135deg, $primary, $primary-light);
}
.action-icon {
  font-size: 32rpx;
}
.action-text {
  display: block;
  font-size: 20rpx;
  color: $ink;
  margin-top: 2rpx;
}
.action-btn.primary .action-text {
  color: #fff;
}
.bottom-gap {
  height: 160rpx;
}
</style>
