<template>
  <view class="script-page">
    <!-- ===== 表单区 ===== -->
    <view class="form card">
      <!-- 主题输入 -->
      <text class="form-label">剧本主题</text>
      <input
        class="theme-input"
        type="text"
        v-model="theme"
        placeholder="如：扬州剪纸的一天 / 玉雕学徒的故事"
        placeholder-class="input-placeholder"
        :maxlength="30"
      />

      <!-- 时长选择 -->
      <text class="form-label">目标时长</text>
      <view class="chip-row">
        <view
          v-for="d in durations"
          :key="d"
          class="chip"
          :class="{ active: duration === d }"
          @click="duration = d"
        >
          <text>{{ d }} 秒</text>
        </view>
      </view>

      <!-- 角色数量 stepper -->
      <view class="stepper-row">
        <view class="flex-1">
          <text class="form-label inline">角色数量</text>
          <text class="stepper-tip">2 - 5 个角色</text>
        </view>
        <view class="stepper">
          <view class="stepper-btn" :class="{ disabled: roleCount <= 2 }" @click="changeRole(-1)">
            <text>－</text>
          </view>
          <text class="stepper-value">{{ roleCount }}</text>
          <view class="stepper-btn" :class="{ disabled: roleCount >= 5 }" @click="changeRole(1)">
            <text>＋</text>
          </view>
        </view>
      </view>

      <!-- 方言台词 switch -->
      <view class="switch-row">
        <view class="flex-1">
          <text class="form-label inline">方言台词</text>
          <text class="stepper-tip">开启后使用扬州方言词汇演绎</text>
        </view>
        <switch :checked="dialect" color="#b03a2e" @change="onDialectChange" />
      </view>

      <!-- 生成按钮 -->
      <view
        class="btn-primary generate-btn"
        :class="{ disabled: generating }"
        @click="onGenerate"
      >
        <text>{{ generating ? 'AI 正在编剧…' : '生成剧本' }}</text>
      </view>
    </view>

    <!-- ===== 生成中 loading ===== -->
    <view v-if="generating" class="loading card">
      <view class="loading-spinner"></view>
      <text class="loading-text">AI 正在编剧…</text>
      <text class="loading-sub">正在编排场景与角色台词</text>
    </view>

    <!-- ===== 结果区 ===== -->
    <view v-if="result" class="result card">
      <view class="result-header">
        <text class="form-label inline">《{{ result.theme }}》</text>
        <view class="ai-badge">
          <text>AI创作</text>
        </view>
      </view>
      <view class="result-info">
        <text class="result-meta-item">时长约 {{ result.duration }} 秒</text>
        <text class="result-meta-item">角色 {{ result.roles.length }} 个</text>
        <text class="result-meta-item" v-if="result.dialect">扬州方言</text>
      </view>

      <!-- 角色徽章 -->
      <view class="role-row">
        <view
          v-for="(r, i) in result.roles"
          :key="r"
          class="role-badge"
          :style="{ background: roleColors[i % roleColors.length] }"
        >
          <text>{{ r }}</text>
        </view>
      </view>

      <!-- 场景卡片 -->
      <view class="scene-card" v-for="s in result.scenes" :key="s.scene">
        <view class="scene-header">
          <view class="scene-index">
            <text>{{ s.scene }}</text>
          </view>
          <text class="scene-title">{{ s.title }}</text>
        </view>
        <text class="scene-content">{{ s.content }}</text>
      </view>

      <!-- 操作按钮 -->
      <view class="result-actions">
        <view class="action-btn outline" @click="onCopy">
          <text>复制全文</text>
        </view>
        <view class="action-btn primary" @click="onSaveWork">
          <text>保存作品</text>
        </view>
      </view>
    </view>

    <!-- 合规提示 -->
    <view class="compliance">
      <text class="compliance-text">🛡️ 生成内容将标注“AI 创作”标识，仅作学习交流使用</text>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { generateScript, saveWork } from '@/api/ai'

/* ---------- 表单数据 ---------- */
const theme = ref('')
const durations = [30, 60, 90]
const duration = ref(60)
const roleCount = ref(3)
const dialect = ref(false)

/* 角色徽章配色（循环取色） */
const roleColors = [
  'linear-gradient(135deg, #b03a2e, #d45a4a)',
  'linear-gradient(135deg, #3f6f6a, #5d8a85)',
  'linear-gradient(135deg, #c9a063, #ddc08f)',
  'linear-gradient(135deg, #9c6b9e, #b98cb9)',
  'linear-gradient(135deg, #3d3529, #5c5344)'
]

/* ---------- 生成状态 ---------- */
const generating = ref(false)
const result = ref(null)

/* ---------- 交互 ---------- */

/* 角色数量增减（限制 2-5） */
function changeRole(delta) {
  const next = roleCount.value + delta
  if (next < 2 || next > 5) return
  roleCount.value = next
}

/* 方言开关 */
function onDialectChange(e) {
  dialect.value = e.detail.value
  if (dialect.value) {
    uni.showToast({ title: '将使用扬州方言词汇', icon: 'none' })
  }
}

/* 生成剧本 */
async function onGenerate() {
  if (generating.value) return // 防重复提交
  if (!theme.value.trim()) {
    uni.showToast({ title: '请先输入剧本主题', icon: 'none' })
    return
  }
  generating.value = true
  try {
    result.value = await generateScript({
      theme: theme.value.trim(),
      duration: duration.value,
      dialect: dialect.value,
      roleCount: roleCount.value
    })
  } catch (e) {
    uni.showToast({ title: '生成失败，请重试', icon: 'none' })
  } finally {
    generating.value = false
  }
}

/* 拼接剧本全文 */
function fullText() {
  if (!result.value) return ''
  const lines = ['《' + result.value.theme + '》科普剧本', '时长：约 ' + result.value.duration + ' 秒', '']
  result.value.scenes.forEach((s) => {
    lines.push('【第 ' + s.scene + ' 幕 ' + s.title + '】')
    lines.push(s.content)
    lines.push('')
  })
  return lines.join('\n')
}

/* 复制全文 */
function onCopy() {
  const text = fullText()
  uni.setClipboardData({
    data: text,
    success: () => uni.showToast({ title: '全文已复制', icon: 'success' })
  })
}

/* 保存到我的作品 */
async function onSaveWork() {
  if (!result.value) return
  try {
    await saveWork({
      type: 'script',
      title: result.value.theme,
      theme: result.value.theme,
      content: fullText()
    })
    uni.showToast({ title: '已保存到我的作品', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
.script-page {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
}

/* ---------- 表单 ---------- */
.form {
  padding: 36rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.form-label {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
  margin: 28rpx 0 16rpx;
}
.form-label:first-child {
  margin-top: 0;
}
.form-label.inline {
  display: inline;
  margin: 0;
}
.chip-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.chip {
  display: inline-block;
  padding: 12rpx 28rpx;
  border-radius: $radius-pill;
  background: $paper;
  border: 1rpx solid $border;
  font-size: 24rpx;
  color: $ink-light;
  margin-right: 16rpx;
  line-height: 40rpx;
  min-height: 64rpx;
  text-align: center;
  transition: all 0.15s ease;
}
.chip.active {
  background: linear-gradient(135deg, $primary, $primary-light);
  border-color: transparent;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4rpx 12rpx rgba(176, 58, 46, 0.22);
}

/* 主题输入 */
.theme-input {
  width: 100%;
  height: 88rpx;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: $radius-md;
  padding: 0 24rpx;
  font-size: 26rpx;
  color: $ink;
  box-sizing: border-box;
}
.input-placeholder {
  font-size: 26rpx;
  color: $ink-faint;
}

/* stepper 行 */
.stepper-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 28rpx;
}
.stepper-tip {
  display: block;
  font-size: 20rpx;
  color: $ink-light;
  margin-top: 4rpx;
}
.stepper {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: 999rpx;
  padding: 6rpx;
}
.stepper-btn {
  display: flex;
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: $card;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(61, 53, 41, 0.08);
}
.stepper-btn.disabled {
  opacity: 0.4;
}
.stepper-btn text {
  font-size: 32rpx;
  color: $primary;
  font-weight: 600;
}
.stepper-value {
  min-width: 72rpx;
  text-align: center;
  font-size: 32rpx;
  font-weight: 700;
  color: $ink;
}

/* switch 行 */
.switch-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 32rpx;
  padding-top: 28rpx;
  border-top: 1rpx solid $border;
}

/* 生成按钮 */
.generate-btn {
  margin-top: 36rpx;
  min-height: 92rpx;
  line-height: 92rpx;
}
.generate-btn.disabled {
  opacity: 0.7;
}

/* ---------- loading ---------- */
.loading {
  display: flex;
  flex-direction: column;
  margin-top: 24rpx;
  align-items: center;
  padding: 56rpx 32rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.loading-spinner {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  border: 6rpx solid $primary-bg;
  border-top-color: $primary;
  animation: spin 1s linear infinite;
  margin-bottom: 20rpx;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.loading-text {
  font-size: 28rpx;
  font-weight: 600;
  color: $ink;
}
.loading-sub {
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 8rpx;
}

/* ---------- 结果区 ---------- */
.result {
  margin-top: 24rpx;
  padding: 36rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.result-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.ai-badge {
  background: $primary-bg;
  border-radius: 999rpx;
  padding: 6rpx 20rpx;
}
.ai-badge text {
  font-size: 20rpx;
  color: $primary;
  font-weight: 600;
}
.result-info {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 12rpx;
}
.result-meta-item {
  font-size: 20rpx;
  color: $ink-light;
  background: $paper;
  border-radius: 8rpx;
  padding: 4rpx 16rpx;
  margin-right: 12rpx;
}

/* 角色徽章 */
.role-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20rpx;
}
.role-badge {
  border-radius: 999rpx;
  padding: 8rpx 24rpx;
  margin: 0 12rpx 12rpx 0;
}
.role-badge text {
  font-size: 22rpx;
  color: #fff;
  font-weight: 600;
}

/* 场景卡片 */
.scene-card {
  background: $paper;
  border-radius: $radius-md;
  padding: 24rpx;
  margin-top: 20rpx;
  border: 1rpx solid $border;
}
.scene-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 12rpx;
}
.scene-index {
  display: flex;
  width: 44rpx;
  height: 44rpx;
  border-radius: 12rpx;
  background: linear-gradient(135deg, $primary, $primary-light);
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
}
.scene-index text {
  font-size: 22rpx;
  color: #fff;
  font-weight: 700;
}
.scene-title {
  font-size: 26rpx;
  font-weight: 700;
  color: $ink;
}
.scene-content {
  font-size: 24rpx;
  color: $ink;
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 操作按钮 */
.result-actions {
  display: flex;
  flex-direction: row;
  margin-top: 32rpx;
}
.action-btn {
  display: flex;
  flex: 1;
  min-height: 80rpx;
  border-radius: 999rpx;
  align-items: center;
  justify-content: center;
}
.action-btn + .action-btn {
  margin-left: 16rpx;
}
.action-btn.outline {
  border: 1rpx solid $primary;
  background: $primary-bg;
}
.action-btn.outline text {
  color: $primary;
  font-size: 26rpx;
}
.action-btn.primary {
  background: linear-gradient(135deg, $primary, $primary-light);
}
.action-btn.primary text {
  color: #fff;
  font-size: 26rpx;
  font-weight: 600;
}

/* ---------- 合规提示 ---------- */
.compliance {
  margin-top: 32rpx;
  padding: 0 8rpx;
}
.compliance-text {
  font-size: 20rpx;
  color: $ink-faint;
  line-height: 1.6;
}

.bottom-gap {
  height: 60rpx;
}
</style>
