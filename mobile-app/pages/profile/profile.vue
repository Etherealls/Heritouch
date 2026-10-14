<template>
  <view class="profile">
    <!-- ===== 未登录：登录卡片 ===== -->
    <view v-if="!isLogin" class="login-card card" @click="goLogin">
      <view class="login-avatar">
        <text>👤</text>
      </view>
      <view class="flex-1">
        <text class="login-title">点击登录</text>
        <text class="login-sub">登录后可收藏项目、管理作品与同步积分</text>
      </view>
      <text class="login-arrow">›</text>
    </view>

    <!-- ===== 已登录：头像昵称积分卡 ===== -->
    <view v-else class="user-card">
      <view class="user-card-bg"></view>
      <view class="user-card-body">
        <!-- 头像占位（无图片资源，用首字色块） -->
        <view class="user-avatar" :style="{ background: 'linear-gradient(135deg, #b03a2e, #d45a4a)' }">
          <text>{{ (userInfo.nickname || '我').slice(0, 1) }}</text>
        </view>
        <view class="flex-1">
          <text class="user-name text-ellipsis">{{ userInfo.nickname || '非遗体验官' }}</text>
          <view class="user-score-row">
            <text class="user-score-label">累计积分</text>
            <text class="user-score-value">{{ totalScore }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- ===== 功能列表 ===== -->
    <view class="menu-list card">
      <view class="menu-item" @click="goWorks">
        <view class="menu-icon" style="background: linear-gradient(135deg, #b03a2e, #d45a4a)">
          <text>🗂️</text>
        </view>
        <text class="flex-1 menu-name">我的作品</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="goFavorites">
        <view class="menu-icon" style="background: linear-gradient(135deg, #c9a063, #ddc08f)">
          <text>❤️</text>
        </view>
        <text class="flex-1 menu-name">我的收藏</text>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="onOfflineCache">
        <view class="menu-icon" style="background: linear-gradient(135deg, #3f6f6a, #5d8a85)">
          <text>📦</text>
        </view>
        <view class="flex-1 menu-name">离线缓存</view>
        <text class="menu-arrow">›</text>
      </view>
      <view class="menu-item" @click="goSettings">
        <view class="menu-icon" style="background: linear-gradient(135deg, #3d3529, #5c5344)">
          <text>⚙️</text>
        </view>
        <text class="flex-1 menu-name">设置</text>
        <text class="menu-arrow">›</text>
      </view>
      <!-- 退出登录（仅登录态展示） -->
      <view class="menu-item" v-if="isLogin" @click="onLogout">
        <view class="menu-icon" style="background: linear-gradient(135deg, #9a8f7d, #b5aa96)">
          <text>🚪</text>
        </view>
        <text class="flex-1 menu-name logout-text">退出登录</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 底部版本信息 -->
    <view class="version-tip">
      <text>Heritouch 非遗 v1.0.0</text>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { downloadOfflinePack, getOfflinePack } from '@/api/guide'

/* ---------- 用户状态 ---------- */
const userStore = useUserStore()
const isLogin = computed(() => userStore.isLogin)
const userInfo = computed(() => userStore.userInfo)
const totalScore = computed(() => userStore.totalScore)

/* ---------- 页面跳转 ---------- */
function goLogin() {
  uni.navigateTo({ url: '/pages/login/login' })
}
function goWorks() {
  uni.navigateTo({ url: '/pages/profile/works' })
}
function goFavorites() {
  uni.navigateTo({ url: '/pages/profile/favorites' })
}
function goSettings() {
  uni.navigateTo({ url: '/pages/profile/settings' })
}

/* ---------- 离线缓存 ---------- */
function onOfflineCache() {
  const pack = getOfflinePack()
  // 已下载离线包时展示大小，否则引导下载
  const sizeText = pack ? '已缓存：' + pack.size + '（' + pack.projects.length + ' 个项目）' : '尚未下载离线包'
  uni.showActionSheet({
    title: sizeText,
    itemList: ['下载离线包（约 12.6MB）', '查看已缓存大小'],
    success(res) {
      if (res.tapIndex === 0) {
        downloadPack()
      } else {
        showCachedSize()
      }
    }
  })
}

/* 下载离线包 */
async function downloadPack() {
  uni.showLoading({ title: '正在下载…', mask: true })
  try {
    const pack = await downloadOfflinePack()
    uni.hideLoading()
    uni.showToast({ title: '离线包下载完成 ' + pack.size, icon: 'none' })
  } catch (e) {
    uni.hideLoading()
    uni.showToast({ title: '下载失败，请重试', icon: 'none' })
  }
}

/* 查看已缓存大小 */
function showCachedSize() {
  const pack = getOfflinePack()
  uni.showToast({
    title: pack ? '已缓存 ' + pack.size + '，可离线浏览' : '暂无离线缓存',
    icon: 'none'
  })
}

/* ---------- 退出登录 ---------- */
function onLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确定要退出当前账号吗？',
    confirmColor: '#b03a2e',
    success(res) {
      if (res.confirm) {
        userStore.logout()
        uni.showToast({ title: '已退出登录', icon: 'none' })
      }
    }
  })
}

/* ---------- 生命周期 ---------- */
// onShow：每次 tab 显示时刷新登录态与积分
onShow(() => {})
</script>

<style lang="scss" scoped>
.profile {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 未登录卡片 ---------- */
.login-card {
  display: flex;
  flex-direction: row;
  align-items: center;
  min-height: 160rpx;
}
.login-avatar {
  width: 104rpx;
  height: 104rpx;
  border-radius: 50%;
  background: $primary-bg;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 52rpx;
  margin-right: 24rpx;
}
.login-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $ink;
}
.login-sub {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 8rpx;
}
.login-arrow {
  font-size: 44rpx;
  color: $ink-light;
}

/* ---------- 已登录用户卡 ---------- */
.user-card {
  position: relative;
  border-radius: $radius-lg;
  overflow: hidden;
  padding: 44rpx 36rpx;
  box-shadow: 0 12rpx 32rpx rgba(176, 58, 46, 0.22);
}
.user-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #b03a2e 0%, #8e2b21 100%);
}
.user-card-body {
  display: flex;
  position: relative;
  flex-direction: row;
  align-items: center;
}
.user-avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 56rpx;
  font-weight: 700;
  color: #fff;
  margin-right: 28rpx;
  flex-shrink: 0;
}
.user-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #fff;
  max-width: 420rpx;
}
.user-score-row {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-top: 12rpx;
  background: rgba(255, 255, 255, 0.16);
  border-radius: 999rpx;
  padding: 8rpx 24rpx;
  align-self: flex-start;
}
.user-score-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.85);
}
.user-score-value {
  font-size: 32rpx;
  font-weight: 700;
  color: #fff;
  margin-left: 12rpx;
}

/* ---------- 功能列表 ---------- */
.menu-list {
  margin-top: 32rpx;
  padding: 8rpx 0;
}
.menu-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  min-height: 112rpx;
  padding: 0 28rpx;
}
.menu-item + .menu-item {
  border-top: 1rpx solid $border;
}
.menu-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
}
.menu-name {
  font-size: 30rpx;
  color: $ink;
  font-weight: 500;
}
.logout-text {
  color: $primary;
}
.menu-arrow {
  font-size: 40rpx;
  color: $ink-light;
}

/* ---------- 版本信息 ---------- */
.version-tip {
  display: flex;
  align-items: center;
  margin-top: 48rpx;
}
.version-tip text {
  font-size: 20rpx;
  color: #b5aa96;
}

.bottom-gap {
  height: 40rpx;
}
</style>
