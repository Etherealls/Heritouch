<template>
  <view class="edit-profile">
    <!-- ===== 头像区 ===== -->
    <view class="avatar-section" @click="chooseAvatar">
      <view class="avatar-box">
        <image v-if="avatar" class="avatar-img" :src="avatar" mode="aspectFill" />
        <block v-else>
          <text class="avatar-text">{{ avatarChar }}</text>
        </block>
      </view>
      <view class="avatar-right">
        <text class="avatar-title">头像</text>
        <text class="avatar-tip">点击更换头像</text>
      </view>
      <text class="menu-arrow">›</text>
    </view>

    <!-- ===== 基本信息 ===== -->
    <view class="group card">
      <text class="group-title">基本信息</text>

      <!-- 用户名（不可改） -->
      <view class="info-row">
        <text class="info-label">用户名</text>
        <text class="info-value">{{ username }}</text>
      </view>

      <!-- 昵称（可改） -->
      <view class="info-row">
        <text class="info-label">昵称</text>
        <input
          class="info-input"
          type="text"
          v-model="nickname"
          placeholder="请输入昵称"
          placeholder-class="input-placeholder"
          :maxlength="16"
        />
      </view>

      <!-- 注册时间（只读） -->
      <view class="info-row" v-if="createTime">
        <text class="info-label">注册时间</text>
        <text class="info-value">{{ createTime }}</text>
      </view>

      <!-- 保存按钮 -->
      <view class="btn-primary save-btn" :class="{ disabled: saving }" @click="onSaveProfile">
        <text>{{ saving ? '保存中…' : '保存资料' }}</text>
      </view>
    </view>

    <!-- ===== 修改密码 ===== -->
    <view class="group card">
      <text class="group-title">修改密码</text>
      <view class="info-row">
        <text class="info-label">旧密码</text>
        <input
          class="info-input"
          :password="true"
          type="text"
          v-model="oldPassword"
          placeholder="请输入旧密码"
          placeholder-class="input-placeholder"
          :maxlength="50"
        />
      </view>
      <view class="info-row">
        <text class="info-label">新密码</text>
        <input
          class="info-input"
          :password="true"
          type="text"
          v-model="newPassword"
          placeholder="至少 6 位"
          placeholder-class="input-placeholder"
          :maxlength="50"
        />
      </view>
      <view class="info-row">
        <text class="info-label">确认新密码</text>
        <input
          class="info-input"
          :password="true"
          type="text"
          v-model="confirmNewPassword"
          placeholder="请再次输入新密码"
          placeholder-class="input-placeholder"
          :maxlength="50"
        />
      </view>
      <view class="btn-ghost save-btn" :class="{ disabled: savingPwd }" @click="onChangePassword">
        <text>{{ savingPwd ? '提交中…' : '修改密码' }}</text>
      </view>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'
import { updateProfile, updatePassword } from '@/api/user'

/* ---------- 用户状态 ---------- */
const userStore = useUserStore()
const username = computed(() => userStore.username)
const avatar = ref(userStore.avatar)
const nickname = ref(userStore.userInfo.nickname || '')
const createTime = ref(userStore.userInfo.create_time || '')
const saving = ref(false)
const savingPwd = ref(false)

/* 修改密码字段 */
const oldPassword = ref('')
const newPassword = ref('')
const confirmNewPassword = ref('')

/* 头像占位字符（未设置头像时显示昵称首字） */
const avatarChar = computed(() => {
  const n = nickname.value || username.value || '我'
  return n.slice(0, 1)
})

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

/* 保存资料（昵称 + 头像） */
async function onSaveProfile() {
  if (saving.value) return
  saving.value = true
  try {
    const payload = {}
    if (nickname.value.trim()) payload.nickname = nickname.value.trim()
    if (avatar.value) payload.avatar = avatar.value
    await updateProfile(payload)
    uni.showToast({ title: '资料已保存', icon: 'success' })
    // 同步本地展示
    createTime.value = userStore.userInfo.create_time || ''
  } catch (e) {
    // 错误已在 request 层提示
  } finally {
    saving.value = false
  }
}

/* 修改密码 */
async function onChangePassword() {
  if (savingPwd.value) return
  if (!oldPassword.value) {
    uni.showToast({ title: '请输入旧密码', icon: 'none' })
    return
  }
  if (newPassword.value.length < 6) {
    uni.showToast({ title: '新密码至少 6 位', icon: 'none' })
    return
  }
  if (newPassword.value !== confirmNewPassword.value) {
    uni.showToast({ title: '两次输入的新密码不一致', icon: 'none' })
    return
  }
  savingPwd.value = true
  try {
    await updatePassword(oldPassword.value, newPassword.value)
    uni.showToast({ title: '密码已修改', icon: 'success' })
    oldPassword.value = ''
    newPassword.value = ''
    confirmNewPassword.value = ''
  } catch (e) {
    // 错误已在 request 层提示
  } finally {
    savingPwd.value = false
  }
}

/* ---------- 生命周期 ---------- */
onShow(() => {
  // 从其他页面返回时同步最新资料
  avatar.value = userStore.avatar
  nickname.value = userStore.userInfo.nickname || ''
  createTime.value = userStore.userInfo.create_time || ''
})
</script>

<style lang="scss" scoped>
.edit-profile {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
  padding-top: calc(40rpx + constant(safe-area-inset-top));
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

/* ---------- 头像区 ---------- */
.avatar-section {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: $card;
  border-radius: $radius-xl;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: $shadow-card;
}
.avatar-box {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary, $primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-right: 24rpx;
  flex-shrink: 0;
}
.avatar-img {
  width: 100%;
  height: 100%;
}
.avatar-text {
  font-size: 52rpx;
  font-weight: 700;
  color: #fff;
}
.avatar-right {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.avatar-title {
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
}
.avatar-tip {
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 8rpx;
}
.menu-arrow {
  font-size: 44rpx;
  color: $ink-faint;
}

/* ---------- 分组 ---------- */
.group {
  padding: 28rpx;
  margin-bottom: 24rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.group-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
  margin-bottom: 20rpx;
}

/* 信息行 */
.info-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  min-height: 88rpx;
  border-bottom: 1rpx solid $border-light;
}
.info-row:last-of-type {
  border-bottom: none;
}
.info-label {
  width: 160rpx;
  font-size: 28rpx;
  color: $ink-light;
  flex-shrink: 0;
}
.info-value {
  flex: 1;
  font-size: 28rpx;
  color: $ink;
}
.info-input {
  flex: 1;
  height: 76rpx;
  font-size: 28rpx;
  color: $ink;
}
.input-placeholder {
  font-size: 26rpx;
  color: $ink-faint;
}

/* 按钮 */
.save-btn {
  margin-top: 20rpx;
  min-height: 84rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-primary.disabled,
.btn-ghost.disabled {
  opacity: 0.7;
}

.bottom-gap {
  height: 60rpx;
}
</style>
