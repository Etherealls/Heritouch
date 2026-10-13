<template>
  <view class="load-more">
    <text v-if="status === 'loading'">加载中…</text>
    <text v-else-if="status === 'nomore'">— 没有更多了 —</text>
    <text v-else-if="status === 'error'">加载失败，点击重试</text>
    <text v-else>上拉加载更多</text>
  </view>
</template>

<script setup>
defineProps({
  status: { type: String, default: 'more' } // more | loading | nomore | error
})
</script>

<style scoped>
.load-more {
  text-align: center;
  padding: 24rpx 0 48rpx;
  font-size: 24rpx;
  color: #9a8f7d;
}
</style>
