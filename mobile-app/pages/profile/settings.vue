<template>
  <view class="settings">
    <!-- ===== 服务器地址 ===== -->
    <view class="group card">
      <text class="group-title">服务器地址</text>
      <view class="server-row">
        <input
          class="server-input"
          type="text"
          v-model="baseUrlInput"
          placeholder="http://192.168.1.100:8000/api/v1"
          placeholder-class="server-placeholder"
          @blur="onBaseUrlBlur"
        />
        <view class="save-btn" @click="saveBaseUrl">
          <text>保存</text>
        </view>
      </view>
      <view class="server-actions">
        <view class="test-btn" :class="{ disabled: testing }" @click="onTestConnection">
          <text>{{ testing ? '测试中…' : '测试连接' }}</text>
        </view>
        <view class="reset-btn" @click="onResetBaseUrl">
          <text>恢复默认</text>
        </view>
      </view>
      <text class="server-tip">
        真机调试时填写电脑的局域网 IP（如 http://192.168.x.x:8000/api/v1），
        手机与电脑需连接同一 WiFi。换网络后在此更新 IP 即可，无需重新打包。
      </text>
      <text v-if="testResult" class="server-test-result" :class="testOk ? 'ok' : 'fail'">{{ testResult }}</text>
    </view>

    <!-- ===== 清除本地缓存 ===== -->
    <view class="group card">
      <text class="group-title">存储管理</text>
      <view class="setting-row clickable" @click="onClearCache">
        <view class="flex-1">
          <text class="setting-name">清除本地缓存</text>
          <text class="setting-desc">清除作品、收藏、错题、游戏进度等本地数据</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- ===== 关于 ===== -->
    <view class="group card about">
      <text class="group-title">关于</text>
      <view class="about-logo">
        <view class="about-logo-badge">
          <image class="about-logo-img" src="/static/logo.png" mode="aspectFit" />
        </view>
        <text class="about-name">指尖非遗</text>
        <text class="about-version">版本 1.0.0</text>
      </view>
      <text class="about-desc">
        地方非遗文化 AI 解码与传承平台，致力于扬州非遗的数字化保护与传播。
      </text>
      <view class="tech-row">
        <text class="tech-tag">UniApp</text>
        <text class="tech-tag">Vue3</text>
        <text class="tech-tag">FastAPI</text>
        <text class="tech-tag">Neo4j</text>
      </view>
      <text class="about-copyright">技术栈：UniApp + FastAPI + Neo4j</text>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'

/* ---------- 数据 ---------- */
const appStore = useAppStore()
const baseUrlInput = ref(appStore.baseUrl)
const testing = ref(false)
const testResult = ref('')
const testOk = ref(false)

/* ---------- 交互 ---------- */

/* 服务器地址输入框失焦自动保存 */
function onBaseUrlBlur() {
  if (baseUrlInput.value.trim() && baseUrlInput.value.trim() !== appStore.baseUrl) {
    appStore.setBaseUrl(baseUrlInput.value.trim())
    uni.showToast({ title: '服务器地址已保存', icon: 'none' })
  }
}

/* 手动保存服务器地址 */
function saveBaseUrl() {
  const url = baseUrlInput.value.trim()
  if (!url) {
    uni.showToast({ title: '请输入服务器地址', icon: 'none' })
    return
  }
  appStore.setBaseUrl(url)
  testResult.value = ''
  uni.showToast({ title: '服务器地址已保存', icon: 'success' })
}

/* 测试连接：向服务器发一个轻量请求验证地址是否可达 */
function onTestConnection() {
  const url = baseUrlInput.value.trim()
  if (!url) {
    uni.showToast({ title: '请先填写服务器地址', icon: 'none' })
    return
  }
  // 保存后测试（确保测试的是当前输入框里的地址）
  appStore.setBaseUrl(url)
  testing.value = true
  testResult.value = ''
  // 请求一个无需登录的轻量接口：非遗分类列表
  uni.request({
    url: url + '/heritage/categories',
    method: 'GET',
    timeout: 10000,
    success(res) {
      if (res.statusCode >= 200 && res.statusCode < 300) {
        testOk.value = true
        testResult.value = '✅ 连接成功，服务器可达'
      } else {
        testOk.value = false
        testResult.value = '❌ 连接失败（HTTP ' + res.statusCode + '），请检查地址与后端是否启动'
      }
    },
    fail() {
      testOk.value = false
      testResult.value = '❌ 无法连接，请确认：1) 后端已用 --host 0.0.0.0 启动 2) 手机与电脑同一 WiFi 3) 防火墙已放行端口'
    },
    complete() {
      testing.value = false
    }
  })
}

/* 恢复默认地址 */
function onResetBaseUrl() {
  baseUrlInput.value = 'http://localhost:8000/api/v1'
  appStore.setBaseUrl(baseUrlInput.value)
  testResult.value = ''
  uni.showToast({ title: '已恢复默认地址', icon: 'none' })
}

/* 清除本地缓存 */
function onClearCache() {
  uni.showModal({
    title: '清除本地缓存',
    content: '将清除作品、收藏、错题本、游戏进度与离线包等本地数据，登录状态也会被清除，确定继续吗？',
    confirmColor: '#b03a2e',
    success(res) {
      if (!res.confirm) return
      try {
        // 逐项清除本地存储（与 config.storageKeys 对应）
        uni.removeStorageSync('heritouch_token')
        uni.removeStorageSync('heritouch_user_info')
        uni.removeStorageSync('heritouch_favorites')
        uni.removeStorageSync('heritouch_works')
        uni.removeStorageSync('heritouch_wrong_book')
        uni.removeStorageSync('heritouch_game_progress')
        uni.removeStorageSync('heritouch_offline_cache')
        uni.showToast({ title: '本地缓存已清除', icon: 'success' })
      } catch (e) {
        uni.showToast({ title: '清除失败', icon: 'none' })
      }
    }
  })
}

/* ---------- 生命周期 ---------- */

/* onShow：从其他设置项返回时同步最新配置 */
onShow(() => {
  baseUrlInput.value = appStore.baseUrl
})
</script>

<style lang="scss" scoped>
.settings {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
  padding-top: calc(40rpx + constant(safe-area-inset-top));
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

/* ---------- 设置分组 ---------- */
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

/* 设置行 */
.setting-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  min-height: 88rpx;
}
.setting-row.clickable {
  padding: 8rpx 0;
}
.setting-name {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: $ink;
}
.setting-desc {
  display: block;
  font-size: 20rpx;
  color: $ink-light;
  margin-top: 6rpx;
  line-height: 1.5;
}
.menu-arrow {
  font-size: 40rpx;
  color: $ink-light;
}

/* ---------- 服务器地址 ---------- */
.server-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.server-input {
  flex: 1;
  height: 80rpx;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: $radius-md;
  padding: 0 24rpx;
  font-size: 26rpx;
  color: $ink;
}
.server-placeholder {
  font-size: 26rpx;
  color: $ink-faint;
}
.save-btn {
  display: flex;
  min-width: 120rpx;
  height: 80rpx;
  border-radius: $radius-md;
  background: linear-gradient(135deg, $primary, $primary-light);
  align-items: center;
  justify-content: center;
  margin-left: 16rpx;
}
.save-btn text {
  font-size: 26rpx;
  color: #fff;
  font-weight: 600;
}
.server-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 16rpx;
}
.test-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64rpx;
  padding: 0 28rpx;
  border-radius: $radius-md;
  background: #edf3f2;
  margin-right: 16rpx;
}
.test-btn text {
  font-size: 24rpx;
  color: $teal;
  font-weight: 600;
}
.test-btn.disabled {
  opacity: 0.5;
}
.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64rpx;
  padding: 0 28rpx;
  border-radius: $radius-md;
  background: $paper;
  border: 1rpx solid $border;
}
.reset-btn text {
  font-size: 24rpx;
  color: $ink-light;
}
.server-tip {
  display: block;
  font-size: 20rpx;
  color: $ink-light;
  margin-top: 12rpx;
  line-height: 1.6;
}
.server-test-result {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  margin-top: 12rpx;
}
.server-test-result.ok {
  color: #1a7f37;
}
.server-test-result.fail {
  color: $danger;
}

/* ---------- 关于 ---------- */
.about {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 44rpx 28rpx;
}
.about-logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20rpx;
}
.about-logo-badge {
  width: 112rpx;
  height: 112rpx;
  border-radius: 24rpx;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(176, 58, 46, 0.28);
  overflow: hidden;
}
.about-logo-img {
  width: 100%;
  height: 100%;
  border-radius: 24rpx;
}
.about-name {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $ink;
  margin-top: 16rpx;
}
.about-version {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 6rpx;
}
.about-desc {
  font-size: 24rpx;
  color: $ink-light;
  line-height: 1.7;
  text-align: center;
  max-width: 480rpx;
}
.tech-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 20rpx;
}
.tech-tag {
  font-size: 20rpx;
  color: $teal;
  background: #edf3f2;
  border-radius: 8rpx;
  padding: 6rpx 20rpx;
  margin: 0 10rpx 10rpx 0;
}
.about-copyright {
  display: block;
  font-size: 20rpx;
  color: $ink-faint;
  margin-top: 16rpx;
  text-align: center;
}

.bottom-gap {
  height: 60rpx;
}
</style>
