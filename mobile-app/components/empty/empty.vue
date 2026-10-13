<template>
  <view class="empty">
    <text class="empty-icon">{{ icon || '📜' }}</text>
    <text class="empty-text">{{ text || '暂无内容' }}</text>
    <view class="empty-btn" v-if="btnText" @click="$emit('action')">
      <text>{{ btnText }}</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '' },
  text: { type: String, default: '' },
  btnText: { type: String, default: '' }
})
defineEmits(['action'])
</script>

<style scoped>
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}
.empty-icon {
  font-size: 80rpx;
  margin-bottom: 24rpx;
}
.empty-text {
  font-size: 26rpx;
  color: #9a8f7d;
}
.empty-btn {
  margin-top: 32rpx;
  padding: 14rpx 44rpx;
  border-radius: 999rpx;
  background: #faf3ee;
  color: #b03a2e;
  font-size: 26rpx;
}
</style>
