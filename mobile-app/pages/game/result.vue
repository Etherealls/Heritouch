<template>
  <view class="result">
    <!-- ===== 大分数展示 ===== -->
    <view class="score-hero">
      <view class="score-hero-bg"></view>
      <view class="score-hero-body">
        <text class="result-title">{{ levelName || '闯关结算' }}</text>
        <view class="score-circle">
          <text class="score-number">{{ score }}</text>
          <text class="score-unit">分</text>
        </view>
        <text class="result-evaluation">{{ evaluation }}</text>
        <view class="result-stats">
          <view class="stat-item">
            <text class="stat-value">{{ correct }}/{{ total }}</text>
            <text class="stat-label">答对题数</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-value">{{ accuracy }}%</text>
            <text class="stat-label">正确率</text>
          </view>
        </view>
      </view>
    </view>

    <!-- ===== 解锁提示 ===== -->
    <view v-if="unlockTip" class="unlock-tip card">
      <text class="unlock-icon">🔓</text>
      <view class="flex-1">
        <text class="unlock-title">恭喜过关！</text>
        <text class="unlock-sub">{{ unlockTip }}</text>
      </view>
    </view>
    <view v-else-if="!passed" class="unlock-tip card fail">
      <text class="unlock-icon">💪</text>
      <view class="flex-1">
        <text class="unlock-title">再接再厉</text>
        <text class="unlock-sub">达到 60 分即可通关，再试一次吧</text>
      </view>
    </view>

    <!-- ===== 操作按钮 ===== -->
    <view class="actions">
      <view class="action-btn primary" @click="retry">
        <text>再来一次</text>
      </view>
      <view class="action-row">
        <view class="action-btn outline" @click="backToLevels">
          <text>返回关卡</text>
        </view>
        <view class="action-btn outline" @click="goWrong">
          <text>查看错题</text>
        </view>
      </view>
      <view class="action-btn share" @click="onShare">
        <text>📤 分享成绩</text>
      </view>
    </view>

    <view class="bottom-gap safe-bottom"></view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getLevels } from '@/api/game'
import { shareText } from '@/utils/util'

/* ---------- 数据 ---------- */
const levelId = ref(1)
const levelName = ref('')
const score = ref(0)
const correct = ref(0)
const total = ref(10)
const levels = ref([])

/* 正确率 */
const accuracy = computed(() => (total.value ? Math.round((correct.value / total.value) * 100) : 0))

/* 是否通关（60 分及格线） */
const passed = computed(() => score.value >= 60)

/* 评价语 */
const evaluation = computed(() => {
  if (score.value >= 90) return '🏆 非遗大师'
  if (score.value >= 60) return '⚔️ 过关斩将'
  return '🌱 再接再厉'
})

/* 解锁提示：过关且存在下一关 */
const unlockTip = computed(() => {
  if (!passed.value) return ''
  const sorted = levels.value.slice().sort((a, b) => a.id - b.id)
  const next = sorted.find((lv) => lv.id > levelId.value)
  return next ? '已解锁新关卡：' + next.name : '已通关全部关卡，你就是非遗大师！'
})

/* ---------- 操作 ---------- */

/* 再来一次 */
function retry() {
  uni.redirectTo({ url: '/pages/game/play?levelId=' + levelId.value + '&levelName=' + encodeURIComponent(levelName.value) })
}

/* 返回关卡 */
function backToLevels() {
  uni.redirectTo({ url: '/pages/game/levels' })
}

/* 查看错题 */
function goWrong() {
  uni.navigateTo({ url: '/pages/game/wrong' })
}

/* 分享成绩 */
function onShare() {
  shareText(
    '我在 Heritouch 非遗闯关中获得 ' + score.value + ' 分！',
    '等级：' + evaluation.value.replace(/[^\u4e00-\u9fa5]/g, '') + '，答对 ' + correct.value + '/' + total.value + ' 题'
  )
}

/* ---------- 生命周期 ---------- */
onLoad(async (query) => {
  levelId.value = query && query.levelId ? Number(query.levelId) : 1
  levelName.value = query && query.levelName ? decodeURIComponent(query.levelName) : ''
  score.value = query && query.score ? Number(query.score) : 0
  correct.value = query && query.correct ? Number(query.correct) : 0
  total.value = query && query.total ? Number(query.total) : 10
  // 加载关卡列表用于推导解锁提示
  try {
    levels.value = await getLevels() || []
  } catch (e) {
    levels.value = []
  }
})
</script>

<style lang="scss" scoped>
.result {
  min-height: 100vh;
  background: $paper;
  padding: 32rpx;
}

/* ---------- 分数展示 ---------- */
.score-hero {
  position: relative;
  border-radius: $radius-lg;
  overflow: hidden;
  padding: 56rpx 36rpx;
  box-shadow: 0 12rpx 32rpx rgba(176, 58, 46, 0.22);
}
.score-hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(160deg, #b03a2e 0%, #8e2b21 100%);
}
.score-hero-body {
  position: relative;
  align-items: center;
}
.result-title {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}
.score-circle {
  flex-direction: row;
  align-items: baseline;
  margin-top: 24rpx;
}
.score-number {
  font-size: 120rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1.1;
}
.score-unit {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-left: 8rpx;
}
.result-evaluation {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #ffd9a0;
  margin-top: 12rpx;
}
.result-stats {
  flex-direction: row;
  align-items: center;
  margin-top: 36rpx;
  background: rgba(255, 255, 255, 0.14);
  border-radius: $radius-md;
  padding: 24rpx 0;
}
.stat-item {
  flex: 1;
  align-items: center;
}
.stat-value {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #fff;
  text-align: center;
}
.stat-label {
  display: block;
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
  margin-top: 6rpx;
}
.stat-divider {
  width: 1rpx;
  height: 56rpx;
  background: rgba(255, 255, 255, 0.3);
}

/* ---------- 解锁提示 ---------- */
.unlock-tip {
  flex-direction: row;
  align-items: center;
  margin-top: 32rpx;
  padding: 28rpx;
  background: linear-gradient(135deg, #fdf6e8, #f9edd6);
  border: 1rpx solid #f0e2c4;
}
.unlock-tip.fail {
  background: $card;
  border: 1rpx solid $border;
}
.unlock-icon {
  font-size: 48rpx;
  margin-right: 20rpx;
}
.unlock-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $ink;
}
.unlock-sub {
  display: block;
  font-size: 22rpx;
  color: $ink-light;
  margin-top: 6rpx;
  line-height: 1.5;
}

/* ---------- 操作按钮 ---------- */
.actions {
  margin-top: 40rpx;
}
.action-btn {
  min-height: 92rpx;
  border-radius: 999rpx;
  align-items: center;
  justify-content: center;
}
.action-btn text {
  font-size: 30rpx;
  font-weight: 600;
}
.action-btn.primary {
  background: linear-gradient(135deg, $primary, $primary-light);
}
.action-btn.primary text {
  color: #fff;
}
.action-row {
  flex-direction: row;
  margin-top: 20rpx;
}
.action-btn.outline {
  flex: 1;
  border: 2rpx solid $primary;
  background: $card;
}
.action-btn.outline text {
  color: $primary;
}
.action-btn.outline + .action-btn.outline {
  margin-left: 20rpx;
}
.action-btn.share {
  margin-top: 20rpx;
  background: $card;
  border: 1rpx solid $border;
}
.action-btn.share text {
  color: $ink;
  font-weight: 500;
}

.bottom-gap {
  height: 60rpx;
}
</style>
