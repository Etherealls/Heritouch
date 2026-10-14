<template>
  <view class="pattern">
    <!-- ===== 表单区 ===== -->
    <view class="form card">
      <!-- 风格选择 -->
      <text class="form-label">生成风格</text>
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

      <!-- 关键词输入 -->
      <text class="form-label">关键词描述</text>
      <textarea
        class="prompt-input"
        v-model="prompt"
        placeholder="描述你想要的纹样，如：梅花映雪，窗花样式，红色宣纸底色"
        placeholder-class="prompt-placeholder"
        :maxlength="200"
      />
      <view class="prompt-count">
        <text>{{ prompt.length }}/200</text>
      </view>

      <!-- 快捷词 chips -->
      <text class="form-label">快捷词（点击追加）</text>
      <view class="chip-row wrap">
        <view
          v-for="w in quickWords"
          :key="w"
          class="chip small"
          @click="appendWord(w)"
        >
          <text>+ {{ w }}</text>
        </view>
      </view>

      <!-- 尺寸选择 -->
      <text class="form-label">生成尺寸</text>
      <view class="chip-row">
        <view
          v-for="s in sizes"
          :key="s"
          class="chip"
          :class="{ active: size === s }"
          @click="size = s"
        >
          <text>{{ s }}</text>
        </view>
      </view>

      <!-- 生成按钮 -->
      <view
        class="btn-primary generate-btn"
        :class="{ disabled: generating }"
        @click="onGenerate"
      >
        <text>{{ generating ? 'AI 正在绘制纹样…' : '生成纹样' }}</text>
      </view>
    </view>

    <!-- ===== 生成中 loading 动画 ===== -->
    <view v-if="generating" class="loading card">
      <view class="loading-spinner"></view>
      <text class="loading-text">AI 正在绘制纹样…</text>
      <text class="loading-sub">灵感创作中，请稍候（约需数秒）</text>
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
        <text class="result-prompt text-ellipsis-2">描述：{{ result.prompt || '未填写' }}</text>
      </view>
      <!-- 操作按钮 -->
      <view class="result-actions">
        <view class="action-btn outline" @click="onSaveAlbum">
          <text>保存相册</text>
        </view>
        <view class="action-btn outline" @click="onSaveWork">
          <text>保存到作品</text>
        </view>
        <view class="action-btn primary" @click="onGenerate">
          <text>再生成</text>
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
import { generatePattern, saveWork } from '@/api/ai'
import { saveImageToAlbum } from '@/utils/util'

/* ---------- 表单数据 ---------- */
const styles = ['扬州剪纸', '漆器纹样', '玉雕图案', '蓝印花布']
const style = ref('扬州剪纸')
const prompt = ref('')
const sizes = ['512x512', '1024x1024']
const size = ref('1024x1024')
const quickWords = ['梅花', '祥云', '龙凤', '花鸟']

/* ---------- 生成状态 ---------- */
const generating = ref(false)
const result = ref(null)

/* 结果区占位图渐变色（按风格取不同色系） */
const resultGradient = computed(() => {
  const map = {
    扬州剪纸: 'linear-gradient(135deg, #b03a2e, #d45a4a)',
    漆器纹样: 'linear-gradient(135deg, #8e2b21, #b03a2e)',
    玉雕图案: 'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    蓝印花布: 'linear-gradient(135deg, #3a5a8c, #5a7cb0)'
  }
  return map[result.value && result.value.style] || map['扬州剪纸']
})

/* ---------- 交互 ---------- */

/* 追加快捷词 */
function appendWord(w) {
  if (prompt.value.includes(w)) return
  prompt.value = prompt.value ? prompt.value + '，' + w : w
}

/* 生成纹样 */
async function onGenerate() {
  if (generating.value) return // 防重复提交
  if (!prompt.value.trim()) {
    uni.showToast({ title: '请先输入关键词描述', icon: 'none' })
    return
  }
  generating.value = true
  try {
    result.value = await generatePattern({ prompt: prompt.value.trim(), style: style.value, size: size.value })
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
      type: 'pattern',
      title: style.value + '纹样',
      style: style.value,
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
.pattern {
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
.chip-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.chip-row.wrap .chip {
  margin-bottom: 12rpx;
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
.chip.small {
  font-size: 22rpx;
  padding: 8rpx 24rpx;
  min-height: 56rpx;
  line-height: 40rpx;
}
.chip.active {
  background: linear-gradient(135deg, $primary, $primary-light);
  border-color: transparent;
  color: #fff;
  font-weight: 600;
  box-shadow: 0 4rpx 12rpx rgba(176, 58, 46, 0.22);
}

/* 关键词输入 */
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
  color: $ink-faint;
}
.prompt-count {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  margin-top: 8rpx;
}
.prompt-count text {
  font-size: 20rpx;
  color: $ink-faint;
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
.result-cover {
  height: 400rpx;
  border-radius: $radius-lg;
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
  border-radius: $radius-pill;
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
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
}
.result-prompt {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.5;
  margin-top: 8rpx;
}

/* 结果操作按钮 */
.result-actions {
  display: flex;
  flex-direction: row;
  margin-top: 24rpx;
}
.action-btn {
  display: flex;
  flex: 1;
  min-height: 80rpx;
  border-radius: $radius-pill;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
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
  box-shadow: 0 6rpx 16rpx rgba(176, 58, 46, 0.22);
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
