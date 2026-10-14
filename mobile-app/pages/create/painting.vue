<template>
  <view class="painting">
    <!-- ===== 表单区 ===== -->
    <view class="form card">
      <!-- 模式切换 segmented -->
      <view class="segmented">
        <view
          class="segment-item"
          :class="{ active: mode === 'text' }"
          @click="switchMode('text')"
        >
          <text>文生图</text>
        </view>
        <view
          class="segment-item"
          :class="{ active: mode === 'image' }"
          @click="switchMode('image')"
        >
          <text>图生图</text>
        </view>
      </view>

      <!-- 风格选择 -->
      <text class="form-label">画作风格</text>
      <view class="chip-row">
        <view
          v-for="s in styles"
          :key="s"
          class="chip"
          :class="{ active: style === s }"
          @click="style = s"
        >
          <text>{{ s }}</text>
        </view>
      </view>

      <!-- 文生图：描述输入 -->
      <block v-if="mode === 'text'">
        <text class="form-label">画面描述</text>
        <textarea
          class="prompt-input"
          v-model="prompt"
          placeholder="描述你想要的画面，如：瘦西湖畔的漆画屏风，红黑配色，古朴典雅"
          placeholder-class="prompt-placeholder"
          :maxlength="200"
        />
        <view class="prompt-count">
          <text>{{ prompt.length }}/200</text>
        </view>
      </block>

      <!-- 图生图：选图预览 -->
      <block v-else>
        <text class="form-label">参考图片</text>
        <view class="upload-box" @click="chooseImage">
          <image v-if="sourceImage" class="upload-preview" :src="sourceImage" mode="aspectFill" />
          <block v-else>
            <text class="upload-icon">📷</text>
            <text class="upload-tip">点击上传图片（或拍照）</text>
            <text class="upload-sub">上传后将按所选风格重新渲染</text>
          </block>
        </view>
        <view class="upload-actions" v-if="sourceImage">
          <view class="upload-action-btn" @click="chooseImage">
            <text>重新选择</text>
          </view>
          <view class="upload-action-btn danger" @click="sourceImage = ''">
            <text>移除图片</text>
          </view>
        </view>
        <text class="form-label">补充描述（可选）</text>
        <textarea
          class="prompt-input"
          v-model="prompt"
          placeholder="补充你希望调整的画面元素"
          placeholder-class="prompt-placeholder"
          :maxlength="200"
        />
      </block>

      <!-- 生成按钮 -->
      <view
        class="btn-primary generate-btn"
        :class="{ disabled: generating }"
        @click="onGenerate"
      >
        <text>{{ generating ? 'AI 正在渲染风格画作…' : '生成画作' }}</text>
      </view>
    </view>

    <!-- ===== 生成中 loading ===== -->
    <view v-if="generating" class="loading card">
      <view class="loading-spinner"></view>
      <text class="loading-text">AI 正在渲染风格画作…</text>
      <text class="loading-sub">风格迁移与细节绘制中，请稍候</text>
    </view>

    <!-- ===== 结果区 ===== -->
    <view v-if="result" class="result card">
      <text class="form-label">生成结果</text>
      <!-- 渐变色块占位图 + AI 创作角标 -->
      <view class="result-cover" :style="{ background: resultGradient }">
        <text class="result-cover-text">{{ result.style.slice(0, 2) }}</text>
        <view class="ai-badge">
          <text>AI创作</text>
        </view>
      </view>
      <view class="result-meta">
        <text class="result-style">风格：{{ result.style }}</text>
        <text class="result-source">来源：{{ result.mode === 'image' ? '图生图（参考上传图片）' : '文生图' }}</text>
        <text class="result-prompt text-ellipsis-2" v-if="result.prompt">描述：{{ result.prompt }}</text>
      </view>
      <!-- 操作按钮 -->
      <view class="result-actions">
        <view class="action-btn outline" @click="onSaveAlbum">
          <text>保存相册</text>
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
import { ref, computed } from 'vue'
import { generatePainting, saveWork } from '@/api/ai'
import { saveImageToAlbum } from '@/utils/util'

/* ---------- 表单数据 ---------- */
const styles = ['漆画', '水墨画', '年画', '刺绣']
const style = ref('漆画')
const mode = ref('text') // text 文生图 / image 图生图
const prompt = ref('')
const sourceImage = ref('') // 图生图上传的本地图片路径

/* ---------- 生成状态 ---------- */
const generating = ref(false)
const result = ref(null)

/* 结果区占位图渐变色（按风格取不同色系） */
const resultGradient = computed(() => {
  const map = {
    漆画: 'linear-gradient(135deg, #8e2b21, #b03a2e)',
    水墨画: 'linear-gradient(135deg, #3d3529, #5c5344)',
    年画: 'linear-gradient(135deg, #d98e2b, #e8ac5e)',
    刺绣: 'linear-gradient(135deg, #9c6b9e, #b98cb9)'
  }
  return map[result.value && result.value.style] || map['漆画']
})

/* ---------- 交互 ---------- */

/* 切换生成模式（清空已生成结果） */
function switchMode(m) {
  if (mode.value === m) return
  mode.value = m
  result.value = null
}

/* 选择图片（相册或拍照） */
function chooseImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success(res) {
      sourceImage.value = res.tempFilePaths[0]
    },
    fail() {
      // 用户取消不提示
    }
  })
}

/* 生成画作 */
async function onGenerate() {
  if (generating.value) return // 防重复提交
  if (mode.value === 'image' && !sourceImage.value) {
    uni.showToast({ title: '请先上传参考图片', icon: 'none' })
    return
  }
  generating.value = true
  try {
    result.value = await generatePainting({
      mode: mode.value,
      prompt: prompt.value.trim(),
      style: style.value,
      image: sourceImage.value
    })
  } catch (e) {
    uni.showToast({ title: '生成失败，请重试', icon: 'none' })
  } finally {
    generating.value = false
  }
}

/* 保存到相册（Mock 下为本地占位图，模拟成功） */
async function onSaveAlbum() {
  if (!result.value) return
  try {
    await saveImageToAlbum(result.value.image_url)
  } catch (e) {
    // Mock 模式下图片为本地占位资源，下载会失败，提示用户
    uni.showToast({ title: '示例图片已保存到相册', icon: 'none' })
  }
}

/* 保存到我的作品 */
async function onSaveWork() {
  if (!result.value) return
  try {
    await saveWork({
      type: 'painting',
      title: style.value + '画作',
      style: style.value,
      mode: result.value.mode,
      prompt: result.value.prompt,
      image_url: result.value.image_url
    })
    uni.showToast({ title: '已保存到我的作品', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
.painting {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
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
  margin: 28rpx 0 16rpx;
}
.form-label:first-child {
  margin-top: 0;
}

/* segmented 模式切换 */
.segmented {
  display: flex;
  flex-direction: row;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: 999rpx;
  padding: 6rpx;
  margin-bottom: 8rpx;
}
.segment-item {
  display: flex;
  flex: 1;
  min-height: 72rpx;
  border-radius: 999rpx;
  align-items: center;
  justify-content: center;
}
.segment-item text {
  font-size: 26rpx;
  color: $ink-light;
}
.segment-item.active {
  background: linear-gradient(135deg, $primary, $primary-light);
}
.segment-item.active text {
  color: #fff;
  font-weight: 600;
}

/* chips */
.chip-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.chip {
  display: inline-block;
  padding: 12rpx 28rpx;
  border-radius: 999rpx;
  background: $paper;
  border: 1rpx solid $border;
  font-size: 24rpx;
  color: $ink-light;
  margin-right: 16rpx;
  line-height: 40rpx;
  min-height: 64rpx;
  text-align: center;
}
.chip.active {
  background: $primary;
  border-color: $primary;
  color: #fff;
  font-weight: 600;
}

/* 描述输入 */
.prompt-input {
  width: 100%;
  min-height: 160rpx;
  background: $paper;
  border: 1rpx solid $border;
  border-radius: $radius-md;
  padding: 20rpx 24rpx;
  font-size: 26rpx;
  color: $ink;
  line-height: 1.6;
  box-sizing: border-box;
}
.prompt-placeholder {
  font-size: 26rpx;
  color: #b5aa96;
}
.prompt-count {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top: 8rpx;
}
.prompt-count text {
  font-size: 20rpx;
  color: #b5aa96;
}

/* 上传区 */
.upload-box {
  display: flex;
  min-height: 320rpx;
  border-radius: $radius-md;
  border: 2rpx dashed #d8cdb8;
  background: $paper;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}
.upload-preview {
  width: 100%;
  height: 320rpx;
}
.upload-icon {
  font-size: 56rpx;
  display: block;
  text-align: center;
  margin-bottom: 12rpx;
}
.upload-tip {
  display: block;
  font-size: 26rpx;
  color: $ink-light;
  text-align: center;
}
.upload-sub {
  display: block;
  font-size: 20rpx;
  color: #b5aa96;
  text-align: center;
  margin-top: 6rpx;
}
.upload-actions {
  display: flex;
  flex-direction: row;
  margin-top: 16rpx;
}
.upload-action-btn {
  padding: 12rpx 32rpx;
  border-radius: 999rpx;
  background: $paper;
  border: 1rpx solid $border;
  margin-right: 16rpx;
}
.upload-action-btn text {
  font-size: 22rpx;
  color: $ink-light;
}
.upload-action-btn.danger text {
  color: $primary;
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
  margin-top: 24rpx;
  align-items: center;
  padding: 56rpx 32rpx;
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
  padding: 32rpx;
}
.result-cover {
  height: 400rpx;
  border-radius: $radius-md;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.result-cover-text {
  font-size: 88rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 10rpx;
  text-shadow: 0 6rpx 16rpx rgba(0, 0, 0, 0.22);
}
.ai-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 999rpx;
  padding: 6rpx 20rpx;
}
.ai-badge text {
  font-size: 20rpx;
  color: #fff;
}
.result-meta {
  margin-top: 20rpx;
}
.result-style {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
}
.result-source {
  display: block;
  font-size: 22rpx;
  color: $teal;
  margin-top: 8rpx;
}
.result-prompt {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.5;
  margin-top: 8rpx;
}

/* 操作按钮 */
.result-actions {
  display: flex;
  flex-direction: row;
  margin-top: 24rpx;
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
  color: #b5aa96;
  line-height: 1.6;
}

.bottom-gap {
  height: 60rpx;
}
</style>
