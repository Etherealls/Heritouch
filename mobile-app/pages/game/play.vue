<template>
  <view class="play">
    <!-- 加载态 -->
    <view v-if="loading" class="loading-card card">
      <text class="loading-text">正在加载题目…</text>
    </view>

    <template v-else-if="questions.length">
      <!-- ===== 顶部进度区 ===== -->
      <view class="progress-header card">
        <view class="progress-info">
          <text class="progress-step">第 {{ currentIndex + 1 }}/{{ questions.length }} 题</text>
          <text class="progress-score">当前得分 {{ score }}</text>
        </view>
        <view class="progress-bar">
          <view
            class="progress-inner"
            :style="{ width: ((currentIndex) / questions.length) * 100 + '%' }"
          ></view>
        </view>
      </view>

      <!-- ===== 题干卡 ===== -->
      <view class="question card">
        <view class="question-type-row">
          <view class="question-type" :class="'type-' + current.question_type">
            <text>{{ typeLabel(current.question_type) }}</text>
          </view>
          <text class="question-difficulty">{{ '★'.repeat(current.difficulty || 1) }}</text>
        </view>
        <text class="question-text">{{ current.question_text }}</text>
        <!-- 识图题：渐变色块占位图 -->
        <view v-if="current.question_type === 'image'" class="question-image" :style="{ background: imageGradient }">
          <text class="question-image-text">🖼️ 识图题</text>
          <text class="question-image-sub">请根据图示选择对应非遗</text>
        </view>
      </view>

      <!-- ===== 选项列表 ===== -->
      <view class="options">
        <!-- 单选 / 识图：A/B/C/D 大行按钮 -->
        <template v-if="current.question_type !== 'judge'">
          <view
            v-for="opt in current.options"
            :key="opt.key"
            class="option-row"
            :class="optionClass(opt.key)"
            @click="submit(opt.key)"
          >
            <view class="option-letter">{{ opt.key }}</view>
            <text class="flex-1 option-text">{{ opt.text }}</text>
            <text v-if="feedback && opt.key === feedback.answer" class="option-mark">✓ 正确答案</text>
            <text v-else-if="feedback && opt.key === selected && !feedback.correct" class="option-mark">✗ 你的选择</text>
          </view>
        </template>
        <!-- 判断：正确/错误 两个大按钮 -->
        <template v-else>
          <view class="judge-row">
            <view
              v-for="opt in current.options"
              :key="opt.key"
              class="judge-btn"
              :class="optionClass(opt.key)"
              @click="submit(opt.key)"
            >
              <text class="judge-icon">{{ opt.key === 'A' ? '✔' : '✘' }}</text>
              <text class="judge-text">{{ opt.text }}</text>
              <text v-if="feedback && opt.key === feedback.answer" class="option-mark">✓</text>
              <text v-else-if="feedback && opt.key === selected && !feedback.correct" class="option-mark">✗</text>
            </view>
          </view>
        </template>
      </view>

      <!-- ===== 反馈解析卡 ===== -->
      <view v-if="feedback" class="feedback card" :class="feedback.correct ? 'feedback-correct' : 'feedback-wrong'">
        <view class="feedback-header">
          <text class="feedback-title">{{ feedback.correct ? '🎉 回答正确 +' + feedback.score + ' 分' : '😅 回答错误' }}</text>
        </view>
        <text class="feedback-analysis">{{ feedback.analysis }}</text>
        <view class="feedback-answer">
          <text>正确答案：{{ feedback.answer }}</text>
        </view>
      </view>
    </template>

    <!-- 空态 -->
    <view v-else class="loading-card card">
      <text class="loading-text">本题库暂未开放</text>
      <view class="back-btn" @click="backToLevels"><text>返回关卡</text></view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { getQuestions, submitAnswer, recordLevelResult } from '@/api/game'

/* ---------- 数据 ---------- */
const loading = ref(true)
const levelId = ref(1)
const levelName = ref('')
const questions = ref([])
const currentIndex = ref(0)
const score = ref(0)
const correctCount = ref(0)
const selected = ref('')     // 当前题已选答案
const feedback = ref(null)   // 提交后的判分结果
let nextTimer = null         // 下一题定时器

/* 当前题目（附带组装好的选项列表） */
const current = computed(() => questions.value[currentIndex.value] || {})

/* 识图题占位图渐变色（按题目 id 轮换色系） */
const imageGradient = computed(() => {
  const palettes = [
    'linear-gradient(135deg, #b03a2e, #d45a4a)',
    'linear-gradient(135deg, #3f6f6a, #5d8a85)',
    'linear-gradient(135deg, #c9a063, #ddc08f)',
    'linear-gradient(135deg, #3d3529, #5c5344)'
  ]
  return palettes[(current.value.id || 0) % palettes.length]
})

/* ---------- 工具函数 ---------- */

/* 题型标签 */
function typeLabel(type) {
  const map = { single: '单选题', judge: '判断题', image: '识图题' }
  return map[type] || '单选题'
}

/* 选项样式（答题反馈高亮） */
function optionClass(key) {
  if (!feedback.value) return ''
  if (key === feedback.value.answer) return 'option-correct'
  if (key === selected.value && !feedback.value.correct) return 'option-wrong'
  return 'option-dim'
}

/* ---------- 答题流程 ---------- */

/* 提交答案 */
async function submit(key) {
  if (selected.value || !current.value.id) return // 已作答或数据异常，防重复
  selected.value = key
  try {
    const res = await submitAnswer({ questionId: current.value.id, answer: key, levelId: levelId.value })
    feedback.value = res
    if (res.correct) {
      score.value += res.score || 0
      correctCount.value += 1
    }
    // 2 秒后进入下一题或查看结果
    nextTimer = setTimeout(nextStep, 2000)
  } catch (e) {
    uni.showToast({ title: '提交失败', icon: 'none' })
    selected.value = ''
  }
}

/* 下一题 / 查看结果 */
function nextStep() {
  if (currentIndex.value >= questions.value.length - 1) {
    finish()
  } else {
    currentIndex.value += 1
    selected.value = ''
    feedback.value = null
  }
}

/* 结算并跳转结果页 */
function finish() {
  // 记录本关成绩
  recordLevelResult(levelId.value, score.value, questions.value.length)
  uni.redirectTo({
    url: '/pages/game/result?levelId=' + levelId.value +
      '&score=' + score.value +
      '&correct=' + correctCount.value +
      '&total=' + questions.value.length
  })
}

/* 返回关卡（空态兜底） */
function backToLevels() {
  uni.redirectTo({ url: '/pages/game/levels' })
}

/* ---------- 生命周期 ---------- */
onLoad(async (query) => {
  levelId.value = query && query.levelId ? Number(query.levelId) : 1
  levelName.value = query && query.levelName ? decodeURIComponent(query.levelName) : ''
  try {
    const list = await getQuestions(levelId.value, 10)
    // 组装选项列表：单选/识图取 A-D，判断题仅取 A/B（正确/错误）
    questions.value = (list || []).map((q) => {
      const options = [
        { key: 'A', text: q.option_a || '' },
        { key: 'B', text: q.option_b || '' }
      ]
      if (q.question_type !== 'judge') {
        options.push({ key: 'C', text: q.option_c || '' }, { key: 'D', text: q.option_d || '' })
      }
      return { ...q, options }
    })
  } catch (e) {
    questions.value = []
    uni.showToast({ title: '题目加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
})

/* 页面卸载时清理定时器 */
onUnload(() => {
  if (nextTimer) clearTimeout(nextTimer)
})
</script>

<style lang="scss" scoped>
.play {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
  padding-bottom: 140rpx;
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
.back-btn {
  margin-top: 32rpx;
  padding: 16rpx 48rpx;
  border-radius: 999rpx;
  background: $primary;
}
.back-btn text {
  font-size: 26rpx;
  color: #fff;
}

/* ---------- 顶部进度 ---------- */
.progress-header {
  padding: 24rpx 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.progress-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}
.progress-step {
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
}
.progress-score {
  font-size: 26rpx;
  font-weight: 600;
  color: $primary;
}
.progress-bar {
  height: 12rpx;
  border-radius: 999rpx;
  background: $border;
  overflow: hidden;
}
.progress-inner {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, $primary, $primary-light);
  transition: width 0.3s;
}

/* ---------- 题干卡 ---------- */
.question {
  margin-top: 24rpx;
  padding: 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.question-type-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}
.question-type {
  border-radius: 8rpx;
  padding: 4rpx 16rpx;
}
.question-type text {
  font-size: 20rpx;
  font-weight: 600;
}
.question-type.type-single {
  background: $primary-bg;
}
.question-type.type-single text {
  color: $primary;
}
.question-type.type-judge {
  background: #e8f0fa;
}
.question-type.type-judge text {
  color: #3a5a8c;
}
.question-type.type-image {
  background: #f0eaf8;
}
.question-type.type-image text {
  color: #7a5a9e;
}
.question-difficulty {
  font-size: 22rpx;
  color: $gold;
  letter-spacing: 2rpx;
}
.question-text {
  font-size: 30rpx;
  font-weight: 600;
  color: $ink;
  line-height: 1.7;
}
.question-image {
  display: flex;
  height: 320rpx;
  border-radius: $radius-md;
  margin-top: 20rpx;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.question-image-text {
  font-size: 44rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.92);
  letter-spacing: 4rpx;
}
.question-image-sub {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.75);
  margin-top: 12rpx;
}

/* ---------- 选项 ---------- */
.options {
  margin-top: 24rpx;
}
.option-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: $card;
  border-radius: $radius-lg;
  padding: 24rpx 28rpx;
  margin-bottom: 16rpx;
  border: 2rpx solid transparent;
  min-height: 100rpx;
  box-shadow: $shadow-card;
  transition: all 0.15s ease;
  &:active { transform: scale(0.99); }
}
.option-letter {
  display: flex;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: $paper;
  border: 1rpx solid $border;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
  color: $ink-light;
  margin-right: 20rpx;
  flex-shrink: 0;
}
.option-text {
  font-size: 28rpx;
  color: $ink;
  line-height: 1.5;
}
.option-mark {
  font-size: 20rpx;
  margin-left: 12rpx;
  flex-shrink: 0;
}
.option-row.option-correct {
  border-color: $success;
  background: #eaf4ec;
}
.option-row.option-correct .option-letter {
  background: $success;
  border-color: $success;
  color: #fff;
}
.option-row.option-correct .option-mark {
  color: $success;
  font-weight: 600;
}
.option-row.option-wrong {
  border-color: $primary;
  background: #fdeeea;
}
.option-row.option-wrong .option-letter {
  background: $primary;
  border-color: $primary;
  color: #fff;
}
.option-row.option-wrong .option-mark {
  color: $primary;
  font-weight: 600;
}
.option-row.option-dim {
  opacity: 0.55;
}

/* 判断题两个大按钮 */
.judge-row {
  display: flex;
  flex-direction: row;
}
.judge-btn {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: $card;
  border-radius: $radius-lg;
  padding: 40rpx 0;
  border: 2rpx solid transparent;
  min-height: 200rpx;
  box-shadow: $shadow-card;
  transition: all 0.15s ease;
  &:active { transform: scale(0.99); }
}
.judge-btn + .judge-btn {
  margin-left: 20rpx;
}
.judge-icon {
  font-size: 56rpx;
}
.judge-text {
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
  margin-top: 12rpx;
}
.option-mark {
  font-size: 20rpx;
  margin-top: 8rpx;
}
.judge-btn.option-correct {
  border-color: $success;
  background: #eaf4ec;
}
.judge-btn.option-correct .judge-icon,
.judge-btn.option-correct .judge-text {
  color: $success;
}
.judge-btn.option-correct .option-mark {
  color: $success;
}
.judge-btn.option-wrong {
  border-color: $primary;
  background: #fdeeea;
}
.judge-btn.option-wrong .judge-icon,
.judge-btn.option-wrong .judge-text {
  color: $primary;
}
.judge-btn.option-wrong .option-mark {
  color: $primary;
}
.judge-btn.option-dim {
  opacity: 0.55;
}

/* ---------- 反馈解析卡 ---------- */
.feedback {
  margin-top: 24rpx;
  padding: 24rpx 28rpx;
  border-radius: $radius-xl;
}
.feedback-correct {
  background: #eaf4ec;
  border: 1rpx solid #cbe4d2;
}
.feedback-wrong {
  background: #fdeeea;
  border: 1rpx solid #f5d5cc;
}
.feedback-title {
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
}
.feedback-analysis {
  display: block;
  font-size: 24rpx;
  color: $ink;
  line-height: 1.7;
  margin-top: 12rpx;
}
.feedback-answer {
  margin-top: 12rpx;
}
.feedback-answer text {
  font-size: 22rpx;
  color: $ink-light;
}
</style>
