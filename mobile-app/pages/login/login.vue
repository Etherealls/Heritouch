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

    <!-- ===== 登录/注册切换 ===== -->
    <view class="tab-switch">
      <view class="tab-item" :class="{ active: mode === 'login' }" @click="switchMode('login')">
        <text>登录</text>
      </view>
      <view class="tab-item" :class="{ active: mode === 'register' }" @click="switchMode('register')">
        <text>注册</text>
      </view>
    </view>

    <!-- ===== 表单 ===== -->
    <view class="form card">
      <!-- 用户名 -->
      <view class="field">
        <text class="field-label">用户名</text>
        <input
          class="field-input"
          type="text"
          v-model="username"
          placeholder="请输入用户名"
          placeholder-class="input-placeholder"
          :maxlength="30"
        />
      </view>

      <!-- 密码 -->
      <view class="field">
        <text class="field-label">密码</text>
        <input
          class="field-input"
          :password="!showPassword"
          type="text"
          v-model="password"
          placeholder="请输入密码（至少 6 位）"
          placeholder-class="input-placeholder"
          :maxlength="50"
        />
      </view>

      <!-- 注册模式额外字段 -->
      <template v-if="mode === 'register'">
        <!-- 确认密码 -->
        <view class="field">
          <text class="field-label">确认密码</text>
          <input
            class="field-input"
            :password="!showPassword"
            type="text"
            v-model="confirmPassword"
            placeholder="请再次输入密码"
            placeholder-class="input-placeholder"
            :maxlength="50"
          />
        </view>

        <!-- 昵称（可选） -->
        <view class="field">
          <text class="field-label">昵称（可选）</text>
          <input
            class="field-input"
            type="text"
            v-model="nickname"
            placeholder="默认使用用户名"
            placeholder-class="input-placeholder"
            :maxlength="16"
          />
        </view>
      </template>

      <!-- 提交按钮 -->
      <view class="btn-primary submit-btn" :class="{ disabled: submitting }" @click="onSubmit">
        <text>{{ submitting ? '提交中…' : (mode === 'login' ? '登录' : '注册') }}</text>
      </view>
    </view>

    <!-- 提示 -->
    <view class="agreement">
      <text class="agreement-text">登录即代表同意《用户协议》与《隐私政策》</text>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { login, register } from '@/api/user'

/* ---------- 数据 ---------- */
const mode = ref('login') // 'login' | 'register'
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const nickname = ref('')
const showPassword = ref(false)
const submitting = ref(false)

/* ---------- 交互 ---------- */

/* 切换登录/注册模式 */
function switchMode(m) {
  if (mode.value === m) return
  mode.value = m
  // 切换时清空密码相关字段，避免混淆
  password.value = ''
  confirmPassword.value = ''
}

/* 提交（登录或注册） */
async function onSubmit() {
  if (submitting.value) return

  // 基础校验
  const name = username.value.trim()
  if (!name) {
    uni.showToast({ title: '请输入用户名', icon: 'none' })
    return
  }
  if (!password.value) {
    uni.showToast({ title: '请输入密码', icon: 'none' })
    return
  }

  // 注册额外校验
  if (mode.value === 'register') {
    if (password.value.length < 6) {
      uni.showToast({ title: '密码至少 6 位', icon: 'none' })
      return
    }
    if (password.value !== confirmPassword.value) {
      uni.showToast({ title: '两次输入的密码不一致', icon: 'none' })
      return
    }
  }

  submitting.value = true
  try {
    if (mode.value === 'login') {
      await login({ username: name, password: password.value })
      uni.showToast({ title: '登录成功', icon: 'success' })
    } else {
      await register({
        username: name,
        password: password.value,
        nickname: nickname.value.trim()
      })
      uni.showToast({ title: '注册成功', icon: 'success' })
    }
    // 延迟跳转，让 toast 展示完成
    setTimeout(() => {
      uni.switchTab({ url: '/pages/profile/profile' })
    }, 600)
  } catch (e) {
    // 错误信息已在 request 层 toast 提示，这里不再重复
  } finally {
    submitting.value = false
  }
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
  padding: 40rpx;
  padding-top: calc(40rpx + constant(safe-area-inset-top));
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

/* ---------- 品牌头 ---------- */
.brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 0 40rpx;
}
.brand-logo {
  width: 128rpx;
  height: 128rpx;
  border-radius: 30rpx;
  background: linear-gradient(135deg, $primary, $primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 68rpx;
  font-weight: 700;
  color: #fff;
  box-shadow: 0 16rpx 40rpx rgba(176, 58, 46, 0.3);
}
.brand-title {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
  color: $ink;
  margin-top: 24rpx;
  letter-spacing: 2rpx;
}
.brand-slogan {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 10rpx;
  letter-spacing: 4rpx;
}

/* ---------- 登录/注册切换 ---------- */
.tab-switch {
  display: flex;
  flex-direction: row;
  margin-bottom: 28rpx;
  background: $card;
  border-radius: $radius-pill;
  padding: 6rpx;
  box-shadow: $shadow-xs;
}
.tab-item {
  flex: 1;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: $radius-pill;
}
.tab-item text {
  font-size: 28rpx;
  color: $ink-light;
  font-weight: 500;
}
.tab-item.active {
  background: linear-gradient(135deg, $primary, $primary-light);
}
.tab-item.active text {
  color: #fff;
  font-weight: 600;
}

/* ---------- 表单 ---------- */
.form {
  padding: 36rpx 32rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.field {
  margin-bottom: 28rpx;
}
.field-label {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
  margin-bottom: 14rpx;
}
.field-input {
  width: 100%;
  height: 88rpx;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: $radius-md;
  padding: 0 28rpx;
  font-size: 28rpx;
  color: $ink;
  box-sizing: border-box;
}
.input-placeholder {
  font-size: 26rpx;
  color: $ink-faint;
}

/* 提交按钮 */
.submit-btn {
  margin-top: 12rpx;
  min-height: 92rpx;
  line-height: 92rpx;
}
.btn-primary.disabled {
  opacity: 0.7;
}

/* ---------- 协议提示 ---------- */
.agreement {
  display: flex;
  justify-content: center;
  margin-top: 40rpx;
}
.agreement-text {
  font-size: 20rpx;
  color: $ink-faint;
}

.bottom-gap {
  height: 60rpx;
}
</style>
