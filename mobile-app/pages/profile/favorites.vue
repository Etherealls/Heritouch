<template>
  <view class="favorites">
    <!-- 加载态 -->
    <view v-if="loading" class="loading-card card">
      <text class="loading-text">正在加载收藏…</text>
    </view>

    <!-- 收藏列表 -->
    <view v-else-if="list.length">
      <view v-for="f in list" :key="f.type + '-' + f.id" class="fav-card card">
        <!-- 类型标识块 -->
        <view class="fav-cover" :style="{ background: favGradient(f) }">
          <text>{{ (f.name || '藏').slice(0, 2) }}</text>
        </view>

        <view class="flex-1 fav-info" @click="onCardClick(f)">
          <text class="fav-name text-ellipsis">{{ f.name }}</text>
          <view class="fav-meta">
            <text class="tag">{{ f.type === 'project' ? '非遗项目' : '传承人' }}</text>
            <text class="fav-time">{{ fromNow(f.fav_time) }}收藏</text>
          </view>
        </view>

        <!-- 取消收藏按钮 -->
        <view class="fav-cancel" @click="onCancel(f)">
          <text>{{ f.type === 'project' ? '❤️' : '💛' }}</text>
        </view>
      </view>
    </view>

    <!-- 空态 -->
    <empty
      v-else
      icon="❤️"
      text="还没有收藏，去非遗名录发现心仪的项目吧"
      btn-text="去逛逛"
      @action="goList"
    />
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { getFavorites, toggleFavorite } from '@/api/user'
import { fromNow } from '@/utils/util'

/* ---------- 数据 ---------- */
const loading = ref(true)
const list = ref([])

/* ---------- 工具函数 ---------- */

/* 收藏项占位块渐变色（按类型取不同色系） */
function favGradient(f) {
  return f.type === 'project'
    ? 'linear-gradient(135deg, #b03a2e, #d45a4a)'
    : 'linear-gradient(135deg, #c9a063, #ddc08f)'
}

/* ---------- 交互 ---------- */

/* 点击卡片：项目跳详情，传承人 toast 提示 */
function onCardClick(f) {
  if (f.type === 'project') {
    uni.navigateTo({ url: '/pages/heritage/detail?id=' + f.id })
  } else {
    uni.showToast({ title: '传承人：' + f.name, icon: 'none' })
  }
}

/* 取消收藏 */
async function onCancel(f) {
  uni.showModal({
    title: '取消收藏',
    content: '确定要取消收藏「' + f.name + '」吗？',
    confirmColor: '#b03a2e',
    success: async (res) => {
      if (!res.confirm) return
      try {
        // toggleFavorite 传入 favorited:true 表示当前已收藏，执行移除
        await toggleFavorite({ type: f.type, id: f.id, name: f.name, favorited: true })
        list.value = list.value.filter((item) => !(item.type === f.type && item.id === f.id))
        uni.showToast({ title: '已取消收藏', icon: 'none' })
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    }
  })
}

/* 去名录页逛逛 */
function goList() {
  uni.navigateTo({ url: '/pages/heritage/list' })
}

/* ---------- 数据加载 ---------- */
async function loadFavorites() {
  loading.value = true
  try {
    list.value = await getFavorites() || []
  } catch (e) {
    list.value = []
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

/* ---------- 生命周期 ---------- */
onLoad(loadFavorites)

/* onShow：从详情页取消收藏返回时刷新 */
onShow(() => {
  if (!loading.value) loadFavorites()
})
</script>

<style lang="scss" scoped>
.favorites {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 加载态 ---------- */
.loading-card {
  padding: 120rpx 32rpx;
  align-items: center;
  margin-top: 40rpx;
}
.loading-text {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- 收藏卡 ---------- */
.fav-card {
  flex-direction: row;
  align-items: center;
  margin-bottom: 20rpx;
  padding: 20rpx 24rpx;
  min-height: 144rpx;
}
.fav-cover {
  width: 104rpx;
  height: 104rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 4rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
}
.fav-info {
  min-width: 0;
}
.fav-name {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
}
.fav-meta {
  flex-direction: row;
  align-items: center;
  margin-top: 10rpx;
}
.fav-meta .tag {
  margin-bottom: 0;
  margin-right: 12rpx;
}
.fav-time {
  font-size: 20rpx;
  color: $ink-light;
}
.fav-cancel {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: $primary-bg;
  align-items: center;
  justify-content: center;
  margin-left: 16rpx;
  flex-shrink: 0;
}
.fav-cancel text {
  font-size: 32rpx;
}
</style>
