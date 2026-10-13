<template>
  <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px', background: bgColor }">
    <view class="nav-bar-inner" :style="{ height: navHeight + 'px' }">
      <view class="nav-back" v-if="showBack" @click="goBack">
        <text class="nav-back-icon">‹</text>
      </view>
      <view class="nav-title-wrap">
        <text class="nav-title" :style="{ color: textColor }">{{ title }}</text>
        <text class="nav-subtitle" v-if="subtitle">{{ subtitle }}</text>
      </view>
      <view class="nav-right">
        <slot name="right" />
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  showBack: { type: Boolean, default: false },
  bgColor: { type: String, default: '#f8f5ef' },
  textColor: { type: String, default: '#3d3529' }
})

const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 20)
const navHeight = ref(44)

function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/index/index' })
}
</script>

<style scoped>
.nav-bar {
  width: 100%;
}
.nav-bar-inner {
  display: flex;
  align-items: center;
  padding: 0 24rpx;
}
.nav-back {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-back-icon {
  font-size: 48rpx;
  color: #3d3529;
  font-weight: 300;
}
.nav-title-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.nav-title {
  font-size: 32rpx;
  font-weight: 700;
}
.nav-subtitle {
  font-size: 20rpx;
  color: #8a7f6a;
  margin-top: 2rpx;
}
.nav-right {
  min-width: 56rpx;
  display: flex;
  justify-content: flex-end;
}
</style>
