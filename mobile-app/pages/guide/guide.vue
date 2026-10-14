<template>
  <view class="guide">
    <!-- 加载态 -->
    <view v-if="loading" class="loading-card card">
      <text class="loading-text">正在加载讲解资源…</text>
    </view>

    <template v-else>
      <!-- ===== 项目头部 ===== -->
      <view class="project-header card">
        <view class="project-cover" :style="{ background: heroGradient }">
          <text>{{ projectName.slice(0, 2) }}</text>
        </view>
        <view class="flex-1">
          <text class="project-name text-ellipsis">{{ projectName }}</text>
          <text class="project-sub">智能语音导览 · {{ langLabel }}</text>
        </view>
      </view>

      <!-- ===== 播放器 ===== -->
      <view class="player card">
        <!-- 播放/暂停按钮 -->
        <view class="play-btn" :class="{ playing: playing }" @click="togglePlay">
          <text>{{ playing ? '⏸' : '▶' }}</text>
        </view>

        <view class="flex-1 player-body">
          <view class="player-info">
            <text class="player-time">{{ formatTime(currentTime) }}</text>
            <text class="player-duration">/ {{ audioMode ? formatTime(totalDuration) : '字幕模式' }}</text>
          </view>
          <!-- 进度条 -->
          <view class="progress-bar">
            <view class="progress-inner" :style="{ width: progressPercent + '%' }"></view>
          </view>
        </view>

        <!-- 倍速切换 -->
        <view class="rate-btn" @click="cycleRate">
          <text>{{ rate }}x</text>
        </view>
      </view>

      <!-- 首次播放提示（H5 自动播放限制） -->
      <view v-if="audioMode && !hasStarted" class="autoplay-tip">
        <text class="autoplay-tip-text">👆 点击播放按钮开始收听讲解</text>
      </view>

      <!-- ===== 语言切换 ===== -->
      <view class="lang-switch">
        <view
          class="lang-item"
          :class="{ active: lang === 'mandarin' }"
          @click="switchLang('mandarin')"
        >
          <text>普通话</text>
        </view>
        <view
          class="lang-item"
          :class="{ active: lang === 'dialect' }"
          @click="switchLang('dialect')"
        >
          <text>扬州方言</text>
        </view>
      </view>

      <!-- ===== 字幕区 ===== -->
      <view class="subtitle card">
        <text class="subtitle-title">讲解字幕</text>
        <scroll-view scroll-y class="subtitle-scroll" :scroll-into-view="'sentence-' + activeIndex" scroll-with-animation>
          <view
            class="sentence"
            :class="{ active: i === activeIndex }"
            :id="'sentence-' + i"
            v-for="(s, i) in sentences"
            :key="i"
          >
            <text>{{ s }}</text>
          </view>
        </scroll-view>
      </view>

      <!-- ===== 功能入口 ===== -->
      <view class="guide-entries">
        <view class="guide-entry card" @click="goScan">
          <view class="guide-entry-icon" style="background: linear-gradient(135deg, #b03a2e, #d45a4a)">
            <text>📷</text>
          </view>
          <text class="flex-1 guide-entry-name">扫码导览</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="guide-entry card" @click="goQa">
          <view class="guide-entry-icon" style="background: linear-gradient(135deg, #3f6f6a, #5d8a85)">
            <text>💬</text>
          </view>
          <text class="flex-1 guide-entry-name">智能问答</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </template>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { getProjectDetail } from '@/api/heritage'
import { getGuideAudio as fetchGuideAudio } from '@/api/guide'

/* ---------- 数据 ---------- */
const projectId = ref(0)
const projectName = ref('')
const loading = ref(true)

/* 音频与播放状态 */
const audioUrl = ref('')       // 讲解音频地址（Mock 下可能为空）
const audioMode = ref(false)   // 是否有可用音频
const guideText = ref('')      // 讲解文本
const sentences = ref([])      // 拆分后的字幕句
const activeIndex = ref(0)     // 当前高亮句索引
const playing = ref(false)
const hasStarted = ref(false)  // 是否已开始播放（H5 需用户手势）
const currentTime = ref(0)
const totalDuration = ref(0)
const lang = ref('mandarin')

/* 倍速循环列表 */
const rates = [1.0, 1.25, 1.5, 2.0]
const rateIndex = ref(0)
const rate = computed(() => rates[rateIndex.value])

/* 音频上下文与定时器 */
let audioCtx = null
let textTimer = null

/* 语言标签 */
const langLabel = computed(() => (lang.value === 'dialect' ? '扬州方言版' : '普通话版'))

/* 封面渐变色 */
const heroGradient = computed(() => {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #8e2b21)',
    'linear-gradient(135deg, #3f6f6a, #2c5350)',
    'linear-gradient(135deg, #c9a063, #a87f45)',
    'linear-gradient(135deg, #3d3529, #28231b)'
  ]
  return palettes[projectId.value % palettes.length]
})

/* 播放进度百分比 */
const progressPercent = computed(() => {
  if (!totalDuration.value) return 0
  return Math.min(100, (currentTime.value / totalDuration.value) * 100)
})

/* ---------- 工具函数 ---------- */

/* 秒数格式化为 mm:ss */
function formatTime(sec) {
  const s = Math.floor(sec || 0)
  const m = Math.floor(s / 60)
  return String(m).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0')
}

/* 将讲解文本按句号拆分为字幕句 */
function splitSentences(text) {
  if (!text) return []
  return text
    .split('。')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => s + '。')
}

/* ---------- 音频初始化 ---------- */

/* 创建音频上下文并绑定事件 */
function createAudio() {
  if (audioCtx || !audioUrl.value) return
  audioCtx = uni.createInnerAudioContext()
  audioCtx.src = audioUrl.value
  audioCtx.playbackRate = rate.value
  audioCtx.onTimeUpdate(() => {
    currentTime.value = audioCtx.currentTime || 0
    // 按播放进度高亮字幕
    const idx = totalDuration.value
      ? Math.floor((currentTime.value / totalDuration.value) * sentences.value.length)
      : 0
    activeIndex.value = Math.min(Math.max(idx, 0), sentences.value.length - 1)
  })
  audioCtx.onPlay(() => {
    playing.value = true
    hasStarted.value = true
  })
  audioCtx.onPause(() => {
    playing.value = false
  })
  audioCtx.onEnded(() => {
    playing.value = false
    currentTime.value = 0
    activeIndex.value = 0
  })
  audioCtx.onError(() => {
    playing.value = false
    // 音频资源异常时降级为文案模式，不阻断体验
    uni.showToast({ title: '演示环境：音频资源未配置', icon: 'none' })
  })
}

/* ---------- 播放控制 ---------- */

/* 播放 / 暂停切换 */
function togglePlay() {
  if (!audioMode.value) {
    // 文案模式：用定时器模拟字幕推进
    toggleTextMode()
    return
  }
  createAudio()
  if (!audioCtx) return
  if (playing.value) {
    audioCtx.pause()
  } else {
    audioCtx.play()
    hasStarted.value = true
  }
}

/* 文案模式：定时器逐句推进字幕 */
function toggleTextMode() {
  if (textTimer) {
    clearInterval(textTimer)
    textTimer = null
    playing.value = false
    return
  }
  playing.value = true
  hasStarted.value = true
  // 每 2.4 秒推进一句，循环播放
  textTimer = setInterval(() => {
    if (activeIndex.value >= sentences.value.length - 1) {
      activeIndex.value = 0
    } else {
      activeIndex.value += 1
    }
  }, 2400)
}

/* 循环切换倍速 */
function cycleRate() {
  rateIndex.value = (rateIndex.value + 1) % rates.length
  if (audioCtx) audioCtx.playbackRate = rate.value
  uni.showToast({ title: '倍速 ' + rate.value + 'x', icon: 'none' })
}

/* ---------- 语言切换 ---------- */
async function switchLang(next) {
  if (lang.value === next) return
  lang.value = next
  // 停止当前播放
  stopPlay()
  await loadGuide(next)
}

/* 停止播放并重置状态 */
function stopPlay() {
  if (audioCtx) {
    audioCtx.stop()
    audioCtx.destroy()
    audioCtx = null
  }
  if (textTimer) {
    clearInterval(textTimer)
    textTimer = null
  }
  playing.value = false
  currentTime.value = 0
  activeIndex.value = 0
}

/* ---------- 数据加载 ---------- */

/* 加载讲解音频/文本 */
async function loadGuide(langValue) {
  try {
    const data = await fetchGuideAudio(projectId.value, langValue)
    audioUrl.value = (data && data.url) || ''
    guideText.value = (data && data.text) || ''
    totalDuration.value = (data && data.duration) || 60
    sentences.value = splitSentences(guideText.value)
    audioMode.value = !!audioUrl.value
    if (!audioMode.value) {
      // Mock 环境下音频资源未配置：降级为纯字幕文案模式
      uni.showToast({ title: '演示环境：音频资源未配置', icon: 'none' })
    }
  } catch (e) {
    audioMode.value = false
    uni.showToast({ title: '讲解加载失败', icon: 'none' })
  }
}

/* ---------- 跳转 ---------- */
function goScan() {
  uni.navigateTo({ url: '/pages/guide/scan' })
}
function goQa() {
  uni.navigateTo({ url: '/pages/guide/qa' })
}

/* ---------- 生命周期 ---------- */
onLoad(async (query) => {
  projectId.value = query && query.id ? Number(query.id) : 1
  // 先加载项目详情获取名称
  try {
    const detail = await getProjectDetail(projectId.value)
    projectName.value = (detail && detail.name) || '非遗项目'
  } catch (e) {
    projectName.value = '非遗项目'
  }
  // 再加载讲解资源
  await loadGuide('mandarin')
  loading.value = false
})

/* 卸载时销毁音频上下文与定时器，避免内存泄漏 */
onUnload(() => {
  stopPlay()
})
</script>

<style lang="scss" scoped>
.guide {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
  padding-top: calc(40rpx + constant(safe-area-inset-top));
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

/* ---------- 加载态 ---------- */
.loading-card {
  display: flex;
  padding: 120rpx 32rpx;
  align-items: center;
  margin-top: 100rpx;
  border-radius: $radius-xl;
}
.loading-text {
  font-size: 26rpx;
  color: $ink-light;
}

/* ---------- 项目头部 ---------- */
.project-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.project-cover {
  width: 120rpx;
  height: 120rpx;
  border-radius: 28rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 4rpx;
  margin-right: 24rpx;
  flex-shrink: 0;
}
.project-name {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $ink;
}
.project-sub {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 8rpx;
}

/* ---------- 播放器 ---------- */
.player {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 24rpx;
  padding: 28rpx 24rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.play-btn {
  width: 104rpx;
  height: 104rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary, $primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
  flex-shrink: 0;
  box-shadow: 0 8rpx 20rpx rgba(176, 58, 46, 0.3);
  transition: transform 0.1s ease;
  &:active { transform: scale(0.94); }
}
.play-btn text {
  font-size: 40rpx;
  color: #fff;
}
.play-btn.playing {
  background: linear-gradient(135deg, $teal, #4e857f);
  box-shadow: 0 8rpx 20rpx rgba(63, 111, 106, 0.3);
}
.player-body {
  min-width: 0;
}
.player-info {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-bottom: 12rpx;
}
.player-time {
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
}
.player-duration {
  font-size: 20rpx;
  color: $ink-light;
  margin-left: 8rpx;
}
.progress-bar {
  height: 12rpx;
  border-radius: $radius-pill;
  background: $border;
  overflow: hidden;
}
.progress-inner {
  height: 100%;
  border-radius: $radius-pill;
  background: linear-gradient(90deg, $primary, $primary-light);
  transition: width 0.2s linear;
}
.rate-btn {
  display: flex;
  min-width: 88rpx;
  height: 64rpx;
  border-radius: $radius-pill;
  background: $paper;
  border: 1rpx solid $border;
  align-items: center;
  justify-content: center;
  margin-left: 20rpx;
  flex-shrink: 0;
}
.rate-btn text {
  font-size: 24rpx;
  color: $primary;
  font-weight: 600;
}

/* ---------- 自动播放提示 ---------- */
.autoplay-tip {
  display: flex;
  margin-top: 16rpx;
  align-items: center;
}
.autoplay-tip-text {
  font-size: 22rpx;
  color: $warning;
  background: #fdf6e8;
  border-radius: $radius-pill;
  padding: 10rpx 28rpx;
}

/* ---------- 语言切换 ---------- */
.lang-switch {
  display: flex;
  flex-direction: row;
  margin-top: 24rpx;
  background: $card;
  border-radius: $radius-pill;
  padding: 6rpx;
  border: 1rpx solid $border;
  box-shadow: $shadow-xs;
}
.lang-item {
  display: flex;
  flex: 1;
  min-height: 72rpx;
  border-radius: $radius-pill;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}
.lang-item text {
  font-size: 26rpx;
  color: $ink-light;
}
.lang-item.active {
  background: linear-gradient(135deg, $primary, $primary-light);
  box-shadow: 0 4rpx 12rpx rgba(176, 58, 46, 0.22);
}
.lang-item.active text {
  color: #fff;
  font-weight: 600;
}

/* ---------- 字幕区 ---------- */
.subtitle {
  margin-top: 24rpx;
  padding: 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.subtitle-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
  margin-bottom: 16rpx;
}
.subtitle-scroll {
  height: 420rpx;
}
.sentence {
  padding: 14rpx 20rpx;
  border-radius: $radius-sm;
  margin-bottom: 8rpx;
}
.sentence text {
  font-size: 26rpx;
  color: $ink-light;
  line-height: 1.7;
  transition: all 0.2s;
}
.sentence.active {
  background: $primary-bg;
}
.sentence.active text {
  color: $primary;
  font-weight: 600;
}

/* ---------- 功能入口 ---------- */
.guide-entries {
  margin-top: 24rpx;
}
.guide-entry {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 20rpx;
  min-height: 112rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.guide-entry-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  margin-right: 20rpx;
  flex-shrink: 0;
}
.guide-entry-name {
  font-size: 30rpx;
  font-weight: 600;
  color: $ink;
}
.menu-arrow {
  font-size: 40rpx;
  color: $ink-faint;
}

.bottom-gap {
  height: 60rpx;
}
</style>
