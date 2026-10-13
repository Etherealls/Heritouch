<template>
  <view class="list-page">
    <!-- ===== 筛选区 ===== -->
    <view class="filter-area">
      <!-- 搜索框 -->
      <view class="search-box">
        <text class="search-icon">🔍</text>
        <input
          class="search-input"
          type="text"
          placeholder="搜索项目名称 / 关键词"
          placeholder-class="search-placeholder"
          :value="keywordInput"
          confirm-type="search"
          @input="onKeywordInput"
          @confirm="onSearch"
        />
        <view v-if="keywordInput" class="search-clear" @click="clearKeyword">
          <text>✕</text>
        </view>
      </view>

      <!-- 类别 chips -->
      <scroll-view scroll-x class="chip-scroll" :show-scrollbar="false">
        <view class="chip-row">
          <view
            class="chip"
            :class="{ active: filterCategory === '' }"
            @click="selectCategory('')"
          >
            <text>全部类别</text>
          </view>
          <view
            v-for="c in categoryOptions"
            :key="c"
            class="chip"
            :class="{ active: filterCategory === c }"
            @click="selectCategory(c)"
          >
            <text>{{ c }}</text>
          </view>
        </view>
      </scroll-view>

      <!-- 级别 chips -->
      <view class="level-row">
        <view
          class="chip small"
          :class="{ active: filterLevel === '' }"
          @click="selectLevel('')"
        >
          <text>全部级别</text>
        </view>
        <view
          class="chip small"
          :class="{ active: filterLevel === '国家级' }"
          @click="selectLevel('国家级')"
        >
          <text>国家级</text>
        </view>
        <view
          class="chip small"
          :class="{ active: filterLevel === '省级' }"
          @click="selectLevel('省级')"
        >
          <text>省级</text>
        </view>
      </view>
    </view>

    <!-- ===== 列表区 ===== -->
    <view class="list-body">
      <!-- 首次加载骨架 -->
      <view v-if="loading && list.length === 0" class="card loading-card">
        <text class="loading-text">正在加载非遗名录…</text>
      </view>

      <!-- 项目卡片列表 -->
      <view
        v-for="p in list"
        :key="p.id"
        class="project-card card"
        @click="goDetail(p.id)"
      >
        <!-- 渐变色块封面 -->
        <view class="project-cover" :style="{ background: coverGradient(p.id) }">
          <text class="project-cover-text">{{ p.name.slice(0, 2) }}</text>
          <view class="project-level">{{ p.level }}</view>
        </view>
        <view class="flex-1 project-info">
          <text class="project-name text-ellipsis">{{ p.name }}</text>
          <view class="project-meta">
            <text class="tag">{{ p.category }}</text>
            <text class="project-region">{{ p.region }}</text>
          </view>
          <text class="project-intro text-ellipsis-2">{{ p.intro }}</text>
        </view>
      </view>

      <!-- 空态 -->
      <empty
        v-if="!loading && list.length === 0"
        icon="🔍"
        text="没有找到相关非遗项目"
        btn-text="重置筛选条件"
        @action="resetFilter"
      />

      <!-- 加载更多 -->
      <load-more v-if="list.length > 0" :status="loadStatus" />
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { getProjectList } from '@/api/heritage'

/* ---------- 筛选与列表状态 ---------- */
const categoryOptions = ['传统技艺', '传统美术', '传统戏剧', '传统音乐', '曲艺', '民俗', '传统医药']
const filterCategory = ref('')
const filterLevel = ref('')
const keywordInput = ref('')   // 搜索框输入值
const keyword = ref('')        // 已触发的搜索关键词
const list = ref([])
const page = ref(1)
const total = ref(0)
const loading = ref(false)
const loadStatus = ref('more') // more | loading | nomore

/* ---------- 工具函数 ---------- */

/* 按 id 生成渐变色系（朱砂红/黛青/泥金/墨色轮换） */
function coverGradient(id) {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)',
    'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    'linear-gradient(135deg, #c9a063, #ddc08f)',
    'linear-gradient(135deg, #3d3529, #5c5344)'
  ]
  return palettes[(Number(id) || 0) % palettes.length]
}

/* ---------- 数据加载 ---------- */

/* 加载第一页（筛选条件变化时调用） */
async function loadFirstPage() {
  loading.value = true
  page.value = 1
  try {
    const data = await getProjectList({
      category: filterCategory.value,
      level: filterLevel.value,
      keyword: keyword.value,
      page: 1,
      size: 10
    })
    list.value = (data && data.list) || []
    total.value = (data && data.total) || 0
    loadStatus.value = list.value.length >= total.value ? 'nomore' : 'more'
  } catch (e) {
    list.value = []
    uni.showToast({ title: '加载失败，请重试', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/* 加载下一页 */
async function loadNextPage() {
  if (loadStatus.value !== 'more') return
  loadStatus.value = 'loading'
  try {
    const data = await getProjectList({
      category: filterCategory.value,
      level: filterLevel.value,
      keyword: keyword.value,
      page: page.value + 1,
      size: 10
    })
    const items = (data && data.list) || []
    list.value = list.value.concat(items)
    page.value += 1
    loadStatus.value = list.value.length >= total.value ? 'nomore' : 'more'
  } catch (e) {
    loadStatus.value = 'more'
    uni.showToast({ title: '加载失败，请重试', icon: 'none' })
  }
}

/* ---------- 筛选交互 ---------- */
function selectCategory(name) {
  if (filterCategory.value === name) return
  filterCategory.value = name
  loadFirstPage()
}
function selectLevel(name) {
  if (filterLevel.value === name) return
  filterLevel.value = name
  loadFirstPage()
}

/* 搜索框输入（防抖：输入即触发，简单节流） */
let searchTimer = null
function onKeywordInput(e) {
  keywordInput.value = e.detail.value
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    keyword.value = keywordInput.value.trim()
    loadFirstPage()
  }, 400)
}

/* 回车搜索 */
function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  keyword.value = keywordInput.value.trim()
  loadFirstPage()
}

/* 清空搜索 */
function clearKeyword() {
  keywordInput.value = ''
  keyword.value = ''
  loadFirstPage()
}

/* 重置全部筛选 */
function resetFilter() {
  filterCategory.value = ''
  filterLevel.value = ''
  keywordInput.value = ''
  keyword.value = ''
  loadFirstPage()
}

/* ---------- 跳转 ---------- */
function goDetail(id) {
  uni.navigateTo({ url: '/pages/heritage/detail?id=' + id })
}

/* ---------- 生命周期 ---------- */

/* onLoad 接收路由参数：category / level / keyword */
onLoad((query) => {
  if (query && query.category) filterCategory.value = decodeURIComponent(query.category)
  if (query && query.level) filterLevel.value = decodeURIComponent(query.level)
  if (query && query.keyword) {
    keyword.value = decodeURIComponent(query.keyword)
    keywordInput.value = keyword.value
  }
  loadFirstPage()
})

/* 下拉刷新 */
onPullDownRefresh(async () => {
  await loadFirstPage()
  uni.stopPullDownRefresh()
})

/* 上拉加载更多 */
onReachBottom(() => {
  loadNextPage()
})
</script>

<style lang="scss" scoped>
.list-page {
  min-height: 100vh;
  background: $paper;
}

/* ---------- 筛选区 ---------- */
.filter-area {
  background: $card;
  padding: 24rpx 32rpx 20rpx;
  border-bottom: 1rpx solid $border;
  position: sticky;
  top: 0;
  z-index: 10;
}

/* 搜索框 */
.search-box {
  flex-direction: row;
  align-items: center;
  height: 80rpx;
  border-radius: 999rpx;
  background: $paper;
  padding: 0 28rpx;
  border: 1rpx solid $border;
}
.search-icon {
  font-size: 26rpx;
  margin-right: 12rpx;
}
.search-input {
  flex: 1;
  font-size: 26rpx;
  color: $ink;
  height: 100%;
}
.search-placeholder {
  font-size: 26rpx;
  color: #b5aa96;
}
.search-clear {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #e5ddd0;
  align-items: center;
  justify-content: center;
}
.search-clear text {
  font-size: 20rpx;
  color: $ink-light;
}

/* 类别 chips（横滑） */
.chip-scroll {
  width: 100%;
  margin-top: 20rpx;
  white-space: nowrap;
}
.chip-row {
  flex-direction: row;
  padding-bottom: 4rpx;
}
.chip {
  display: inline-block;
  padding: 10rpx 26rpx;
  border-radius: 999rpx;
  background: $paper;
  border: 1rpx solid $border;
  font-size: 22rpx;
  color: $ink-light;
  margin-right: 16rpx;
  line-height: 40rpx;
  min-height: 60rpx;
  text-align: center;
}
.chip.small {
  font-size: 22rpx;
  padding: 8rpx 24rpx;
}
.chip.active {
  background: $primary;
  border-color: $primary;
  color: #fff;
  font-weight: 600;
}

/* 级别 chips */
.level-row {
  flex-direction: row;
  margin-top: 16rpx;
}

/* ---------- 列表区 ---------- */
.list-body {
  padding: 24rpx 32rpx;
}

/* 项目卡片 */
.project-card {
  flex-direction: row;
  align-items: stretch;
  padding: 0;
  overflow: hidden;
  margin-bottom: 24rpx;
}
.project-cover {
  width: 200rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.project-cover-text {
  font-size: 48rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 4rpx;
  text-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.2);
}
.project-level {
  position: absolute;
  top: 12rpx;
  left: 12rpx;
  font-size: 16rpx;
  color: #fff;
  background: rgba(0, 0, 0, 0.28);
  border-radius: 999rpx;
  padding: 2rpx 12rpx;
}
.project-info {
  padding: 24rpx 24rpx 20rpx;
  min-height: 180rpx;
}
.project-name {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
}
.project-meta {
  flex-direction: row;
  align-items: center;
  margin-top: 10rpx;
}
.project-meta .tag {
  margin-bottom: 0;
  margin-right: 12rpx;
}
.project-region {
  font-size: 20rpx;
  color: $ink-light;
}
.project-intro {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.6;
  margin-top: 12rpx;
}

/* 加载态卡片 */
.loading-card {
  padding: 80rpx;
  align-items: center;
}
.loading-text {
  font-size: 26rpx;
  color: $ink-light;
}
</style>
