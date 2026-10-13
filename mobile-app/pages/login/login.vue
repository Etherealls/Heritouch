<template>
  <view class="login">
    <!-- ===== 品牌头 ===== -->
    <view class="brand">
      <view class="brand-logo">
        <text>遗</text>
      </view>
      <text class="brand-title">Heritouch 非遗</text>
      <text class="brand-slogan">可查询 · 可互动 · 可创作 · 可游玩</text>
    </view>

    <!-- ===== 头像选择 ===== -->
    <view class="avatar-area">
      <view class="avatar-picker" @click="chooseAvatar">
        <image v-if="avatar" class="avatar-img" :src="avatar" mode="aspectFill" />
        <block v-else>
          <text class="avatar-placeholder">👤</text>
          <text class="avatar-tip">选择头像</text>
        </block>
      </view>
      <text class="avatar-note">头像可选，不选则使用默认头像</text>
    </view>

    <!-- ===== 昵称输入 ===== -->
    <view class="form card">
      <text class="form-label">昵称</text>
      <input
        class="nickname-input"
        type="text"
        v-model="nickname"
        placeholder="默认“非遗体验官”"
        placeholder-class="input-placeholder"
        :maxlength="16"
      />

      <!-- 登录按钮 -->
      <view class="btn-primary login-btn" :class="{ disabled: submitting }" @click="onWechatLogin">
        <text>{{ submitting ? '登录中…' : '微信一键登录' }}</text>
      </view>
      <view class="btn-primary guest-btn" :class="{ disabled: submitting }" @click="onGuestLogin">
        <text>游客体验</text>
      </view>
    </view>

    <!-- 协议提示 -->
    <view class="agreement">
      <text class="agreement-text">登录即代表同意《用户协议》与《隐私政策》</text>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { login } from '@/api/user'

/* ---------- 数据 ---------- */
const nickname = ref('非遗体验官')
const avatar = ref('')
const submitting = ref(false)

/* ---------- 交互 ---------- */

/* 选择头像（相册或拍照） */
function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success(res) {
      avatar.value = res.tempFilePaths[0]
    },
    fail() {
      // 用户取消不提示
    }
  })
}

/* 执行登录（成功后回到个人中心） */
async function doLogin(payload) {
  if (submitting.value) return // 防重复提交
  submitting.value = true
  try {
    await login({
      nickname: nickname.value.trim() || '非遗体验官',
      avatar: avatar.value
    })
    uni.showToast({ title: '登录成功', icon: 'success' })
    // 延迟跳转，让 toast 展示完成
    setTimeout(() => {
      uni.switchTab({ url: '/pages/profile/profile' })
    }, 500)
  } catch (e) {
    uni.showToast({ title: '登录失败，请重试', icon: 'none' })
  } finally {
    submitting.value = false
  }
}

/* 微信一键登录 */
function onWechatLogin() {
  // #ifdef MP-WEIXIN
  // 小程序端：尝试获取微信用户信息
  uni.getUserProfile({
    desc: '用于完善个人资料',
    success(res) {
      const info = res.userInfo || {}
      if (info.nickName) nickname.value = info.nickName
      if (info.avatarUrl) avatar.value = info.avatarUrl
      doLogin({})
    },
    fail() {
      // 用户拒绝授权：使用输入的昵称登录
      doLogin({})
    }
  })
  // #endif
  // #ifndef MP-WEIXIN
  // 其他平台：直接使用输入的昵称与头像登录
  doLogin({})
  // #endif
}

/* 游客体验 */
function onGuestLogin() {
  doLogin({})
}

/* ---------- 生命周期 ---------- */

/* 已登录用户进入登录页时直接跳回个人中心 */
onLoad(() => {
  const token = uni.getStorageSync('heritouch_token')
  if (token) {
    uni.switchTab({ url: '/pages/profile/profile' })
  }
})
</script>

<style lang="scss" scoped>
.login {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 品牌头 ---------- */
.brand {
  flex-direction: column;
  align-items: center;
  padding: 64rpx 0 48rpx;
}
.brand-logo {
  width: 128rpx;
  height: 128rpx;
  border-radius: 28rpx;
  background: linear-gradient(135deg, $primary, $primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 68rpx;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 12rpx 32rpx rgba(176, 58, 46, 0.3);
}
.brand-title {
  display: block;
  font-size: 42rpx;
  font-weight: 700;
  color: $ink;
  margin-top: 24rpx;
  letter-spacing: 2rpx;
}
.brand-slogan {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 12rpx;
  letter-spacing: 4rpx;
}

/* ---------- 头像选择 ---------- */
.avatar-area {
  align-items: center;
  margin-bottom: 40rpx;
}
.avatar-picker {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: $card;
  border: 2rpx dashed #d8cdb8;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.avatar-img {
  width: 100%;
  height: 100%;
}
.avatar-placeholder {
  font-size: 56rpx;
  display: block;
  text-align: center;
}
.avatar-tip {
  display: block;
  font-size: 20rpx;
  color: $ink-light;
  text-align: center;
  margin-top: 4rpx;
}
.avatar-note {
  display: block;
  font-size: 20rpx;
  color: #b5aa96;
  margin-top: 12rpx;
}

/* ---------- 表单 ---------- */
.form {
  padding: 32rpx;
}
.form-label {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
  margin-bottom: 16rpx;
}
.nickname-input {
  width: 100%;
  height: 88rpx;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: $radius-md;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: $ink;
  box-sizing: border-box;
}
.input-placeholder {
  font-size: 28rpx;
  color: #b5aa96;
}

/* 登录按钮 */
.login-btn {
  margin-top: 36rpx;
  min-height: 92rpx;
  line-height: 92rpx;
}
.guest-btn {
  margin-top: 20rpx;
  min-height: 92rpx;
  line-height: 92rpx;
  background: $card;
  border: 2rpx solid $primary;
  color: $primary;
}
.guest-btn::after {
  border: none;
}
.guest-btn text {
  color: $primary;
}
.btn-primary.disabled {
  opacity: 0.7;
}

/* ---------- 协议提示 ---------- */
.agreement {
  align-items: center;
  margin-top: 40rpx;
}
.agreement-text {
  font-size: 20rpx;
  color: #b5aa96;
}

.bottom-gap {
  height: 60rpx;
}
</style>
