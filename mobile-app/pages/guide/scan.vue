<template>
  <view class="scan">
    <!-- ===== 说明卡 ===== -->
    <view class="intro card">
      <view class="intro-icon">
        <text>📷</text>
      </view>
      <text class="intro-title">扫码导览</text>
      <text class="intro-sub">扫描展品二维码，直达项目讲解</text>
    </view>

    <!-- ===== 扫码按钮 ===== -->
    <view class="scan-btn card" @click="onScan">
      <view class="scan-btn-icon" style="background: linear-gradient(135deg, #b03a2e, #d45a4a)">
        <text>🔍</text>
      </view>
      <text class="flex-1 scan-btn-text">开始扫码</text>
      <text class="menu-arrow">›</text>
    </view>

    <!-- ===== 解析中 ===== -->
    <view v-if="resolving" class="resolving card">
      <view class="loading-spinner"></view>
      <text class="resolving-text">正在解析二维码…</text>
    </view>

    <!-- ===== H5 端降级：手动输入项目 ID ===== -->
    <!-- #ifdef H5 -->
    <view class="manual card">
      <text class="manual-title">H5 端请使用 APP 或小程序扫码</text>
      <text class="manual-sub">也可以手动输入项目 ID 进行跳转（1-14）</text>
      <view class="manual-input-row">
        <input
          class="manual-input"
          type="number"
          v-model="manualId"
          placeholder="输入项目 ID"
          placeholder-class="manual-placeholder"
        />
        <view class="manual-btn" @click="onManualResolve">
          <text>跳转</text>
        </view>
      </view>
    </view>
    <!-- #endif -->

    <!-- ===== 演示说明 ===== -->
    <view class="demo-tip card">
      <text class="demo-tip-title">演示提示</text>
      <text class="demo-tip-text">
        演示环境可输入符合 heritouch://project?id=1 格式的二维码内容，
        或直接使用上方手动输入功能体验完整流程。
      </text>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { scanResolve } from '@/api/guide'

/* ---------- 数据 ---------- */
const resolving = ref(false)
const manualId = ref('')

/* ---------- 扫码 ---------- */

/* 调起扫码（仅允许相机） */
function onScan() {
  // #ifdef H5
  // H5 端不支持相机扫码，降级提示
  uni.showToast({ title: 'H5 端请使用 APP 或小程序扫码', icon: 'none' })
  return
  // #endif

  // #ifndef H5
  uni.scanCode({
    onlyFromCamera: true,
    scanType: ['qrCode'],
    success(res) {
      resolveCode(res.result)
    },
    fail() {
      // 用户取消扫码，不提示
    }
  })
  // #endif
}

/* ---------- 解析二维码内容 ---------- */
async function resolveCode(code) {
  if (!code) return
  resolving.value = true
  try {
    const data = await scanResolve(code)
    resolving.value = false
    uni.showToast({ title: '已跳转到 ' + data.name + ' 讲解', icon: 'none' })
    // 解析成功后跳转项目详情（redirectTo 替换当前页）
    setTimeout(() => {
      uni.redirectTo({ url: '/pages/heritage/detail?id=' + data.projectId })
    }, 600)
  } catch (e) {
    resolving.value = false
    uni.showToast({ title: (e && e.message) || '无效的非遗二维码', icon: 'none' })
  }
}

/* ---------- H5 手动输入兜底 ---------- */
function onManualResolve() {
  const id = manualId.value.trim()
  if (!id) {
    uni.showToast({ title: '请输入项目 ID', icon: 'none' })
    return
  }
  // 拼接标准二维码格式内容进行解析
  resolveCode('heritouch://project?id=' + id)
}
</script>

<style lang="scss" scoped>
.scan {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 说明卡 ---------- */
.intro {
  display: flex;
  align-items: center;
  padding: 56rpx 32rpx;
  margin-top: 24rpx;
}
.intro-icon {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: $primary-bg;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64rpx;
  margin-bottom: 20rpx;
}
.intro-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: $ink;
}
.intro-sub {
  display: block;
  font-size: 24rpx;
  color: $ink-light;
  margin-top: 10rpx;
}

/* ---------- 扫码按钮 ---------- */
.scan-btn {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 32rpx;
  min-height: 128rpx;
  padding: 24rpx 28rpx;
}
.scan-btn-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
}
.scan-btn-text {
  font-size: 30rpx;
  font-weight: 600;
  color: $ink;
}
.menu-arrow {
  font-size: 40rpx;
  color: $ink-light;
}

/* ---------- 解析中 ---------- */
.resolving {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-top: 32rpx;
  padding: 40rpx;
}
.loading-spinner {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  border: 5rpx solid $primary-bg;
  border-top-color: $primary;
  animation: spin 1s linear infinite;
  margin-right: 16rpx;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.resolving-text {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- H5 手动输入 ---------- */
.manual {
  margin-top: 32rpx;
  padding: 28rpx;
}
.manual-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $primary;
}
.manual-sub {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 8rpx;
}
.manual-input-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 20rpx;
}
.manual-input {
  flex: 1;
  height: 80rpx;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: $radius-md;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: $ink;
}
.manual-placeholder {
  font-size: 26rpx;
  color: #b5aa96;
}
.manual-btn {
  display: flex;
  min-width: 128rpx;
  height: 80rpx;
  border-radius: $radius-md;
  background: linear-gradient(135deg, $primary, $primary-light);
  align-items: center;
  justify-content: center;
  margin-left: 16rpx;
}
.manual-btn text {
  font-size: 26rpx;
  color: #fff;
  font-weight: 600;
}

/* ---------- 演示说明 ---------- */
.demo-tip {
  margin-top: 32rpx;
  padding: 28rpx;
  background: #fdf6e8;
  border: 1rpx solid #f0e2c4;
}
.demo-tip-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: #9a7b3a;
}
.demo-tip-text {
  display: block;
  font-size: 22rpx;
  color: #9a7b3a;
  line-height: 1.6;
  margin-top: 10rpx;
}

.bottom-gap {
  height: 60rpx;
}
</style>
