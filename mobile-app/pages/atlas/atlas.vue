<template>
  <view class="atlas">
    <!-- 顶部类别筛选 chips -->
    <scroll-view scroll-x class="filter-scroll" :show-scrollbar="false">
      <view class="filter-row">
        <view
          class="filter-chip"
          :class="{ active: activeCategory === '' }"
          @click="switchCategory('')"
        >
          <text>全部</text>
        </view>
        <view
          v-for="c in categoryNames"
          :key="c"
          class="filter-chip"
          :class="{ active: activeCategory === c }"
          @click="switchCategory(c)"
        >
          <text>{{ c }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- 图谱容器（固定高度，内部 canvas 自适应） -->
    <view class="graph-wrap card">
      <!-- 加载态 -->
      <view v-if="loading" class="graph-loading">
        <text class="graph-loading-text">图谱加载中…</text>
      </view>
      <!-- 力导向图组件 -->
      <force-graph
        v-else-if="nodes.length"
        :nodes="nodes"
        :edges="edges"
        @node-click="onNodeClick"
      />
      <!-- 空态 -->
      <view v-else class="graph-loading">
        <text class="graph-loading-text">暂无图谱数据</text>
      </view>
    </view>

    <!-- 底部操作提示 -->
    <view class="tips-bar safe-bottom">
      <text class="tips-text">🔍 双指缩放 · 单指拖拽 · 点击节点查看详情</text>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getKnowledgeGraph, getCategories } from '@/api/heritage'

/* ---------- 数据 ---------- */
const categoryNames = ref([])
const activeCategory = ref('')
const nodes = ref([])
const edges = ref([])
const loading = ref(false)

/* ---------- 图谱加载 ---------- */

/* 加载分类名（chips 数据源） */
async function loadCategories() {
  try {
    const list = await getCategories()
    categoryNames.value = (list || []).map((c) => c.name)
  } catch (e) {
    // 分类加载失败时使用内置默认列表兜底
    categoryNames.value = ['传统技艺', '传统美术', '传统戏剧', '传统音乐', '曲艺', '民俗', '传统医药']
  }
}

/* 加载知识图谱：category 为空字符串表示全图 */
async function loadGraph() {
  loading.value = true
  try {
    const data = await getKnowledgeGraph({ category: activeCategory.value })
    nodes.value = (data && data.nodes) || []
    edges.value = (data && data.edges) || []
  } catch (e) {
    nodes.value = []
    edges.value = []
    uni.showToast({ title: '图谱加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/* 切换类别筛选 */
function switchCategory(name) {
  if (activeCategory.value === name) return
  activeCategory.value = name
  loadGraph()
}

/* ---------- 节点点击 ---------- */
function onNodeClick(node) {
  if (!node) return
  if (node.type === 'heritage') {
    // 非遗项目节点 → 跳转详情页
    uni.navigateTo({ url: '/pages/heritage/detail?id=' + node.refId })
  } else if (node.type === 'inheritor') {
    // 传承人节点 → toast 展示姓名（详情复用项目详情页）
    uni.showToast({ title: '传承人：' + node.name, icon: 'none' })
  } else {
    // 其他类型（类别/朝代/材料/民俗）→ toast 展示名称
    uni.showToast({ title: node.name, icon: 'none' })
  }
}

/* ---------- 生命周期 ---------- */
onLoad(() => {
  loadCategories()
  loadGraph()
})
</script>

<style lang="scss" scoped>
.atlas {
  min-height: 100vh;
  background: $paper;
  display: flex;
  flex-direction: column;
}

/* ---------- 筛选 chips ---------- */
.filter-scroll {
  width: 100%;
  background: $paper;
  white-space: nowrap;
}
.filter-row {
  flex-direction: row;
  padding: 20rpx 32rpx;
}
.filter-chip {
  display: inline-block;
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: $card;
  border: 1rpx solid $border;
  font-size: 24rpx;
  color: $ink-light;
  margin-right: 16rpx;
  min-height: 56rpx;
  line-height: 56rpx;
  text-align: center;
}
.filter-chip.active {
  background: $primary;
  border-color: $primary;
  color: #fff;
  font-weight: 600;
}

/* ---------- 图谱容器 ---------- */
.graph-wrap {
  flex: 1;
  margin: 0 32rpx 24rpx;
  padding: 0;
  overflow: hidden;
  position: relative;
  min-height: 900rpx;
}
.graph-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.graph-loading-text {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- 底部提示 ---------- */
.tips-bar {
  padding: 20rpx 32rpx 32rpx;
  align-items: center;
}
.tips-text {
  font-size: 22rpx;
  color: $ink-light;
  background: $card;
  border-radius: 999rpx;
  padding: 12rpx 32rpx;
  border: 1rpx solid $border;
}
</style>
