<template>
  <view class="qa">
    <!-- ===== 页面说明 ===== -->
    <view class="qa-intro card">
      <text class="qa-intro-title">💬 智能问答</text>
      <text class="qa-intro-sub">关于扬州非遗，有什么想了解的？按住下方按钮说出问题，或直接输入文字</text>
    </view>

    <!-- ===== 按住说话按钮 ===== -->
    <view class="voice-area">
      <view
        class="voice-btn"
        :class="{ recording: recording }"
        @touchstart="onTouchStart"
        @touchend="onTouchEnd"
        @touchcancel="onTouchCancel"
      >
        <text class="voice-btn-icon">🎤</text>
        <text class="voice-btn-text">{{ recording ? '松开结束录音…' : '按住说话' }}</text>
      </view>
      <text class="voice-tip">录音将自动识别为文字问题（演示环境）</text>
    </view>

    <!-- ===== 文字输入兜底（H5 等无录音场景） ===== -->
    <view class="text-input-area card">
      <input
        class="text-input"
        type="text"
        v-model="textQuestion"
        placeholder="或直接输入问题，如：扬州剪纸有多少年历史"
        placeholder-class="input-placeholder"
        confirm-type="send"
        @confirm="onTextAsk"
      />
      <view class="send-btn" @click="onTextAsk">
        <text>提问</text>
      </view>
    </view>

    <!-- ===== 当前回答区 ===== -->
    <view v-if="current" class="answer card">
      <view class="answer-question">
        <text class="answer-question-label">我的提问</text>
        <text class="answer-question-text">{{ current.question }}</text>
      </view>
      <view class="answer-body">
        <view class="answer-header">
          <text class="answer-label">AI 回答</text>
          <view class="answer-play" v-if="current.audio" @click="playAnswerAudio">
            <text>🔊 播放语音</text>
          </view>
        </view>
        <text class="answer-text" v-if="!answering">{{ current.answer }}</text>
        <view v-else class="answer-loading">
          <view class="loading-spinner"></view>
          <text>正在思考…</text>
        </view>
      </view>
    </view>

    <!-- ===== 推荐问题 ===== -->
    <view class="recommend card">
      <text class="recommend-title">推荐问题</text>
      <view class="chip-row">
        <view
          v-for="q in recommendQuestions"
          :key="q"
          class="chip"
          @click="ask(q)"
        >
          <text>{{ q }}</text>
        </view>
      </view>
    </view>

    <!-- ===== 历史问答 ===== -->
    <view class="history" v-if="history.length">
      <text class="history-title">历史问答</text>
      <view class="history-item card" v-for="(h, i) in history" :key="i" @click="ask(h.question)">
        <text class="history-question text-ellipsis">Q：{{ h.question }}</text>
        <text class="history-answer text-ellipsis-2">A：{{ h.answer }}</text>
      </view>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onUnload } from '@dcloudio/uni-app'
import { askQuestion } from '@/api/guide'

/* ---------- 数据 ---------- */
const recording = ref(false)
const answering = ref(false)
const textQuestion = ref('')
const current = ref(null)          // 当前问答 {question, answer, audio}
const history = ref([])            // 历史问答列表（本地数组）

/* 推荐问题列表 */
const recommendQuestions = [
  '扬州剪纸有多少年历史',
  '漆器制作要多久',
  '扬州玉雕的山子雕是什么',
  '扬州早茶有什么讲究'
]

/* ---------- 录音管理（小程序 / APP 端可用） ---------- */
let recorderManager = null
// #ifdef MP-WEIXIN || APP-PLUS
recorderManager = uni.getRecorderManager()
recorderManager.onStop(() => {
  // 录音结束：提示已收到语音，并模拟识别为一个推荐问题
  recording.value = false
  uni.showToast({ title: '已收到语音', icon: 'none' })
  const guess = recommendQuestions[Math.floor(Math.random() * recommendQuestions.length)]
  ask(guess)
})
// #endif

/* 回答音频上下文 */
let answerAudio = null

/* ---------- 按住说话交互 ---------- */
let recordStart = 0

function onTouchStart() {
  recording.value = true
  recordStart = Date.now()
  // #ifdef MP-WEIXIN || APP-PLUS
  recorderManager && recorderManager.start({ format: 'mp3', duration: 60000 })
  // #endif
}

function onTouchEnd() {
  if (!recording.value) return
  const duration = Date.now() - recordStart
  recording.value = false
  if (duration < 800) {
    // 按压时间过短，取消
    // #ifdef MP-WEIXIN || APP-PLUS
    recorderManager && recorderManager.stop()
    // #endif
    uni.showToast({ title: '说话时间太短', icon: 'none' })
    return
  }
  // #ifdef MP-WEIXIN || APP-PLUS
  recorderManager && recorderManager.stop()
  // #endif
  // #ifdef H5
  // H5 端无录音能力，提示使用文字输入
  uni.showToast({ title: 'H5 端请使用下方文字输入', icon: 'none' })
  // #endif
}

function onTouchCancel() {
  recording.value = false
}

/* ---------- 提问 ---------- */

/* 文字提问 */
function onTextAsk() {
  const q = textQuestion.value.trim()
  if (!q) {
    uni.showToast({ title: '请先输入问题', icon: 'none' })
    return
  }
  textQuestion.value = ''
  ask(q)
}

/* 发起问答 */
async function ask(question) {
  if (answering.value) return // 防重复提交
  answering.value = true
  current.value = { question, answer: '', audio: '' }
  try {
    const res = await askQuestion(question)
    current.value = {
      question,
      answer: res.answer || '暂无回答',
      audio: res.audio || ''
    }
    // 记录历史（最新的在最前）
    history.value.unshift({
      question,
      answer: current.value.answer,
      time: Date.now()
    })
  } catch (e) {
    uni.showToast({ title: '提问失败，请重试', icon: 'none' })
    current.value = null
  } finally {
    answering.value = false
  }
}

/* ---------- 播放回答语音 ---------- */
function playAnswerAudio() {
  if (!current.value || !current.value.audio) return
  if (answerAudio) {
    answerAudio.destroy()
    answerAudio = null
  }
  answerAudio = uni.createInnerAudioContext()
  answerAudio.src = current.value.audio
  answerAudio.onError(() => {
    // 音频资源缺失时降级提示，不报错
    uni.showToast({ title: '演示环境：语音播报未配置', icon: 'none' })
  })
  answerAudio.play()
}

/* ---------- 生命周期 ---------- */

/* 卸载时销毁音频上下文 */
onUnload(() => {
  if (answerAudio) {
    answerAudio.destroy()
    answerAudio = null
  }
})
</script>

<style lang="scss" scoped>
.qa {
  min-height: 100vh;
  background: $paper;
  padding: 40rpx;
}

/* ---------- 页面说明 ---------- */
.qa-intro {
  padding: 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.qa-intro-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $ink;
}
.qa-intro-sub {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.6;
  margin-top: 10rpx;
}

/* ---------- 按住说话 ---------- */
.voice-area {
  display: flex;
  align-items: center;
  margin-top: 40rpx;
}
.voice-btn {
  display: flex;
  width: 220rpx;
  height: 220rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, $primary, $primary-light);
  align-items: center;
  justify-content: center;
  box-shadow: 0 16rpx 40rpx rgba(176, 58, 46, 0.32);
  transition: all 0.15s;
}
.voice-btn.recording {
  background: linear-gradient(135deg, #8e2b21, #6d1f17);
  transform: scale(1.05);
  box-shadow: 0 16rpx 40rpx rgba(142, 43, 33, 0.45);
}
.voice-btn-icon {
  font-size: 64rpx;
  display: block;
  text-align: center;
}
.voice-btn-text {
  display: block;
  font-size: 24rpx;
  color: #fff;
  margin-top: 12rpx;
  font-weight: 600;
}
.voice-tip {
  font-size: 20rpx;
  color: $ink-light;
  margin-top: 20rpx;
}

/* ---------- 文字输入 ---------- */
.text-input-area {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-top: 32rpx;
  padding: 12rpx 12rpx 12rpx 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.text-input {
  flex: 1;
  height: 72rpx;
  font-size: 26rpx;
  color: $ink;
}
.input-placeholder {
  font-size: 26rpx;
  color: $ink-faint;
}
.send-btn {
  display: flex;
  min-width: 128rpx;
  height: 72rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, $primary, $primary-light);
  align-items: center;
  justify-content: center;
  margin-left: 16rpx;
}
.send-btn text {
  font-size: 26rpx;
  color: #fff;
  font-weight: 600;
}

/* ---------- 回答区 ---------- */
.answer {
  margin-top: 32rpx;
  padding: 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.answer-question {
  background: $paper;
  border-radius: $radius-sm;
  padding: 20rpx 24rpx;
  margin-bottom: 20rpx;
}
.answer-question-label {
  font-size: 20rpx;
  color: $primary;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}
.answer-question-text {
  font-size: 26rpx;
  color: $ink;
  line-height: 1.6;
}
.answer-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}
.answer-label {
  font-size: 26rpx;
  font-weight: 700;
  color: $ink;
}
.answer-play {
  background: $primary-bg;
  border-radius: 999rpx;
  padding: 8rpx 24rpx;
}
.answer-play text {
  font-size: 22rpx;
  color: $primary;
  font-weight: 600;
}
.answer-text {
  font-size: 26rpx;
  color: $ink;
  line-height: 1.8;
}
.answer-loading {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 24rpx;
  color: $ink-light;
}
.loading-spinner {
  width: 40rpx;
  height: 40rpx;
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

/* ---------- 推荐问题 ---------- */
.recommend {
  margin-top: 32rpx;
  padding: 28rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.recommend-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
  margin-bottom: 20rpx;
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
  font-size: 22rpx;
  color: $ink-light;
  margin: 0 16rpx 16rpx 0;
  line-height: 40rpx;
  min-height: 64rpx;
  text-align: center;
}

/* ---------- 历史问答 ---------- */
.history {
  margin-top: 32rpx;
}
.history-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
  margin-bottom: 20rpx;
}
.history-item {
  padding: 24rpx 28rpx;
  margin-bottom: 16rpx;
  border-radius: $radius-xl;
  box-shadow: $shadow-card;
}
.history-question {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  color: $ink;
}
.history-answer {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  line-height: 1.6;
  margin-top: 8rpx;
}

.bottom-gap {
  height: 60rpx;
}
</style>
