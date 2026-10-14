<template>
  <view class="force-graph">
    <canvas
      class="fg-canvas"
      :type="canvasType"
      :canvas-id="canvasId"
      :id="canvasId"
      :disable-scroll="true"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    ></canvas>
    <!-- 图例 -->
    <view class="fg-legend">
      <view class="fg-legend-item" v-for="item in legend" :key="item.type">
        <view class="fg-legend-dot" :style="{ background: item.color }"></view>
        <text>{{ item.label }}</text>
      </view>
    </view>
    <!-- 缩放控制 -->
    <view class="fg-zoom">
      <view class="fg-zoom-btn" @click="zoomBy(1.25)">＋</view>
      <view class="fg-zoom-btn" @click="zoomBy(0.8)">－</view>
      <view class="fg-zoom-btn" @click="resetView">⟳</view>
    </view>
    <!-- 节点详情卡片（点击节点弹出，不跳转新页面） -->
    <view class="fg-card" v-if="activeNode" @click="onCardClick">
      <view class="fg-card-header">
        <view class="fg-card-badge" :style="{ background: nodeColor(activeNode.type) }">{{ typeLabel(activeNode.type) }}</view>
        <text class="fg-card-title">{{ activeNode.name }}</text>
        <text class="fg-card-close" @click.stop="activeNode = null">✕</text>
      </view>
      <view class="fg-card-body">
        <text class="fg-card-desc">{{ activeNode.desc || '点击查看更多详情' }}</text>
        <view class="fg-card-rel" v-if="neighbors.length">
          <text class="fg-card-rel-title">关联（{{ neighbors.length }}）：</text>
          <text class="fg-card-rel-item" v-for="n in neighbors.slice(0, 6)" :key="n.id">{{ n.name }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, getCurrentInstance } from 'vue'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  edges: { type: Array, default: () => [] },
  // 选中节点后是否允许跳转（emit node-click）
  centerNodeId: { type: String, default: '' }
})

const emit = defineEmits(['node-click'])

const canvasId = 'fg_' + Math.random().toString(36).slice(2, 8)
const activeNode = ref(null)
const neighbors = ref([])

// H5 走旧版 createCanvasContext；小程序/App 走新版 type="2d"
let canvasType = ''
// #ifndef H5
canvasType = '2d'
// #endif

const NODE_COLORS = {
  heritage: '#b03a2e',
  inheritor: '#c9a063',
  category: '#3f6f6a',
  dynasty: '#7a6a53',
  material: '#8c9a5b',
  work: '#9c6b9e',
  folk_custom: '#d98e2b'
}
const TYPE_LABELS = {
  heritage: '非遗项目',
  inheritor: '传承人',
  category: '类别',
  dynasty: '朝代',
  material: '材料',
  work: '作品',
  folk_custom: '民俗'
}
const legend = [
  { type: 'heritage', label: '非遗项目', color: NODE_COLORS.heritage },
  { type: 'inheritor', label: '传承人', color: NODE_COLORS.inheritor },
  { type: 'category', label: '类别', color: NODE_COLORS.category },
  { type: 'dynasty', label: '朝代', color: NODE_COLORS.dynasty },
  { type: 'folk_custom', label: '民俗', color: NODE_COLORS.folk_custom }
]

function nodeColor(type) { return NODE_COLORS[type] || '#9a8f7d' }
function typeLabel(type) { return TYPE_LABELS[type] || type }

/* ---------- 物理仿真状态 ---------- */
const sim = reactive({
  nodes: [],   // { id, name, type, x, y, vx, vy, r }
  edges: [],
  running: true
})

const view = reactive({ scale: 1, offsetX: 0, offsetY: 0 })
const ctx = ref(null)
const canvasW = ref(0)
const canvasH = ref(0)

const REPULSION = 2600      // 斥力
const SPRING = 0.045        // 弹簧（边）拉力
const CENTER = 0.012        // 向心力
const DAMPING = 0.86        // 阻尼
const NODE_R = { heritage: 15, inheritor: 12, category: 13, dynasty: 11, material: 11, work: 10, folk_custom: 11 }

/* ---------- 初始化与仿真 ---------- */
function initSim() {
  const w = canvasW.value || 375
  const h = canvasH.value || 600
  sim.nodes = props.nodes.map((n, i) => {
    const angle = (i / Math.max(props.nodes.length, 1)) * Math.PI * 2
    const radius = Math.min(w, h) * 0.32
    return {
      ...n,
      x: w / 2 + Math.cos(angle) * radius,
      y: h / 2 + Math.sin(angle) * radius,
      vx: 0, vy: 0,
      r: NODE_R[n.type] || 10
    }
  })
  sim.edges = props.edges.map((e) => ({ source: e.source, target: e.target, label: e.label }))
}

function tick() {
  if (!sim.running) return
  const nodes = sim.nodes
  const cx = canvasW.value / 2
  const cy = canvasH.value / 2
  // 斥力
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i]
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j]
      let dx = a.x - b.x
      let dy = a.y - b.y
      let dist2 = dx * dx + dy * dy
      if (dist2 < 1) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; dist2 = 1 }
      const dist = Math.sqrt(dist2)
      const force = Math.min(REPULSION / dist2, 12)
      const fx = (dx / dist) * force
      const fy = (dy / dist) * force
      a.vx += fx; a.vy += fy
      b.vx -= fx; b.vy -= fy
    }
  }
  // 弹簧
  const index = {}
  nodes.forEach((n) => { index[n.id] = n })
  for (const e of sim.edges) {
    const a = index[e.source]
    const b = index[e.target]
    if (!a || !b) continue
    const dx = b.x - a.x
    const dy = b.y - a.y
    const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
    const f = (dist - 110) * SPRING
    const fx = (dx / dist) * f
    const fy = (dy / dist) * f
    a.vx += fx; a.vy += fy
    b.vx -= fx; b.vy -= fy
  }
  // 向心 + 阻尼
  for (const n of nodes) {
    n.vx += (cx - n.x) * CENTER
    n.vy += (cy - n.y) * CENTER
    n.vx *= DAMPING
    n.vy *= DAMPING
    n.x += n.vx
    n.y += n.vy
  }
  draw()
  if (sim.running) {
    // #ifdef MP-WEIXIN || APP-PLUS
    setTimeout(() => tick(), 16)
    // #endif
    // #ifdef H5
    requestAnimationFrame(tick)
    // #endif
  }
}

/* ---------- 渲染 ---------- */
function draw() {
  const c = ctx.value
  if (!c) return
  const w = canvasW.value
  const h = canvasH.value
  c.clearRect(0, 0, w, h)
  c.save()
  c.translate(view.offsetX, view.offsetY)
  c.scale(view.scale, view.scale)

  const index = {}
  sim.nodes.forEach((n) => { index[n.id] = n })

  // 边
  c.strokeStyle = 'rgba(138,127,106,0.45)'
  c.lineWidth = 1.2
  for (const e of sim.edges) {
    const a = index[e.source]
    const b = index[e.target]
    if (!a || !b) continue
    const isActive = activeNode.value && (a.id === activeNode.value.id || b.id === activeNode.value.id)
    c.strokeStyle = isActive ? 'rgba(176,58,46,0.8)' : 'rgba(138,127,106,0.35)'
    c.beginPath()
    c.moveTo(a.x, a.y)
    c.lineTo(b.x, b.y)
    c.stroke()
  }

  // 节点
  for (const n of sim.nodes) {
    const isActive = activeNode.value && n.id === activeNode.value.id
    const isNeighbor = neighbors.value.some((nb) => nb.id === n.id)
    c.beginPath()
    c.arc(n.x, n.y, n.r * (isActive ? 1.35 : 1), 0, Math.PI * 2)
    c.fillStyle = nodeColor(n.type)
    c.globalAlpha = activeNode.value && !isActive && !isNeighbor ? 0.35 : 1
    c.fill()
    c.globalAlpha = 1
    if (isActive) {
      c.strokeStyle = '#3d3529'
      c.lineWidth = 2.5
      c.stroke()
    }
    // 名称（节点放大到一定尺寸才显示，避免拥挤）
    if (view.scale > 0.65 || n.type === 'heritage') {
      c.fillStyle = '#3d3529'
      c.font = `${Math.max(9, 11 / view.scale)}px sans-serif`
      c.textAlign = 'center'
      c.fillText(n.name.length > 6 ? n.name.slice(0, 6) + '…' : n.name, n.x, n.y + n.r + 12 / view.scale)
    }
  }
  c.restore()
  // H5 端 createCanvasContext 是命令缓存式，需显式 draw() 提交到画布
  // #ifdef H5
  if (typeof c.draw === 'function') c.draw()
  // #endif
}

/* ---------- 触控交互：单指拖拽 / 双指缩放 / 点击 ---------- */
let lastTouch = null
let pinchStart = null
let moved = false

function getPos(e) {
  const t = e.touches[0] || {}
  // MP 端 canvas 触摸事件用 x/y，H5/APP 端用 clientX/clientY
  return { x: t.x !== undefined ? t.x : t.clientX || 0, y: t.y !== undefined ? t.y : t.clientY || 0 }
}

function onTouchStart(e) {
  moved = false
  if (e.touches.length === 1) {
    lastTouch = getPos(e)
  } else if (e.touches.length === 2) {
    const p0 = { x: e.touches[0].x !== undefined ? e.touches[0].x : e.touches[0].clientX || 0, y: e.touches[0].y !== undefined ? e.touches[0].y : e.touches[0].clientY || 0 }
    const p1 = { x: e.touches[1].x !== undefined ? e.touches[1].x : e.touches[1].clientX || 0, y: e.touches[1].y !== undefined ? e.touches[1].y : e.touches[1].clientY || 0 }
    const dx = p0.x - p1.x
    const dy = p0.y - p1.y
    pinchStart = { dist: Math.sqrt(dx * dx + dy * dy), scale: view.scale }
  }
}

function onTouchMove(e) {
  const tp = (t) => ({ x: t.x !== undefined ? t.x : t.clientX || 0, y: t.y !== undefined ? t.y : t.clientY || 0 })
  if (e.touches.length === 1 && lastTouch) {
    const p = tp(e.touches[0])
    const dx = p.x - lastTouch.x
    const dy = p.y - lastTouch.y
    if (Math.abs(dx) + Math.abs(dy) > 3) moved = true
    view.offsetX += dx
    view.offsetY += dy
    lastTouch = p
    draw()
  } else if (e.touches.length === 2 && pinchStart) {
    moved = true
    const p0 = tp(e.touches[0])
    const p1 = tp(e.touches[1])
    const dx = p0.x - p1.x
    const dy = p0.y - p1.y
    const dist = Math.sqrt(dx * dx + dy * dy)
    view.scale = Math.max(0.3, Math.min(3, (pinchStart.scale * dist) / pinchStart.dist))
    draw()
  }
}

function onTouchEnd(e) {
  // 点击命中检测（未拖动时视为点击）
  if (!moved && (!e.changedTouches || e.changedTouches.length === 1)) {
    const t = (e.changedTouches && e.changedTouches[0]) || null
    if (t) {
      const x = t.x !== undefined ? t.x : t.clientX || 0
      const y = t.y !== undefined ? t.y : t.clientY || 0
      hitTest(x, y)
    }
  }
  lastTouch = null
  pinchStart = null
}

function hitTest(x, y) {
  const sx = (x - view.offsetX) / view.scale
  const sy = (y - view.offsetY) / view.scale
  let hit = null
  for (const n of sim.nodes) {
    const dx = sx - n.x
    const dy = sy - n.y
    if (dx * dx + dy * dy <= (n.r + 8) * (n.r + 8)) { hit = n; break }
  }
  if (hit) {
    activeNode.value = hit
    neighbors.value = sim.edges
      .filter((e) => e.source === hit.id || e.target === hit.id)
      .map((e) => sim.nodes.find((n) => n.id === (e.source === hit.id ? e.target : e.source)))
      .filter(Boolean)
    emit('node-click', hit)
  } else {
    activeNode.value = null
    neighbors.value = []
  }
  draw()
}

function onCardClick() {
  if (activeNode.value) emit('node-click', activeNode.value)
}

function zoomBy(factor) {
  view.scale = Math.max(0.3, Math.min(3, view.scale * factor))
  draw()
}

function resetView() {
  view.scale = 1
  view.offsetX = 0
  view.offsetY = 0
  draw()
}

/* ---------- 画布尺寸 ---------- */
async function measure() {
  await nextTick()
  // 必须用 .in(instance) 限定组件作用域，否则 H5 端查不到节点
  const instance = getCurrentInstance()
  const query = uni.createSelectorQuery().in(instance)
  query.select('.fg-canvas').fields({ node: true, size: true }).exec((res) => {
    let w = (res && res[0] && res[0].width) || 0
    let h = (res && res[0] && res[0].height) || 0
    // 尺寸兜底：拿不到时用窗口尺寸估算（宽度满宽，高度按容器 900rpx 折算）
    if (!w || !h) {
      const sys = uni.getSystemInfoSync()
      w = w || sys.windowWidth - 40 || 335
      h = h || Math.round((sys.windowWidth - 40) * 1.34) || 450
    }
    canvasW.value = w
    canvasH.value = h
    const node = res && res[0] && res[0].node
    // #ifdef MP-WEIXIN || APP-PLUS
    if (node && node.getContext) {
      const c2d = node.getContext('2d')
      const dpr = (uni.getSystemInfoSync().pixelRatio) || 2
      node.width = Math.round(w * dpr)
      node.height = Math.round(h * dpr)
      c2d.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.value = c2d
    } else {
      ctx.value = uni.createCanvasContext(canvasId, instance)
    }
    // #endif
    // #ifdef H5
    // H5 端用 createCanvasContext 获取上下文（需传组件实例定位 canvas）
    ctx.value = uni.createCanvasContext(canvasId, instance)
    // #endif
    initSim()
    // 预热若干帧让布局快速收敛
    for (let i = 0; i < 60; i++) simulateStep()
    draw()
    tick()
  })
}

/* H5/App：canvas 元素 context 需通过 node 获取；此处兼容处理 */
function simulateStep() {
  const nodes = sim.nodes
  const cx = canvasW.value / 2
  const cy = canvasH.value / 2
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i]
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j]
      let dx = a.x - b.x; let dy = a.y - b.y
      let dist2 = dx * dx + dy * dy
      if (dist2 < 1) { dx = 1; dy = 1; dist2 = 2 }
      const dist = Math.sqrt(dist2)
      const force = Math.min(REPULSION / dist2, 12)
      const fx = (dx / dist) * force; const fy = (dy / dist) * force
      a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy
    }
  }
  const index = {}
  nodes.forEach((n) => { index[n.id] = n })
  for (const e of sim.edges) {
    const a = index[e.source]; const b = index[e.target]
    if (!a || !b) continue
    const dx = b.x - a.x; const dy = b.y - a.y
    const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
    const f = (dist - 110) * SPRING
    const fx = (dx / dist) * f; const fy = (dy / dist) * f
    a.vx += fx; a.vy += fy; b.vx -= fx; b.vy -= fy
  }
  for (const n of nodes) {
    n.vx += (cx - n.x) * CENTER
    n.vy += (cy - n.y) * CENTER
    n.vx *= DAMPING; n.vy *= DAMPING
    n.x += n.vx; n.y += n.vy
  }
}

watch(() => [props.nodes, props.edges], () => {
  if (ctx.value) {
    initSim()
    for (let i = 0; i < 60; i++) simulateStep()
    draw()
  }
}, { deep: true })

onMounted(() => {
  measure()
})
</script>

<style scoped>
.force-graph {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 600rpx;
}
.fg-canvas {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
}
.fg-legend {
  position: absolute;
  left: 16rpx;
  top: 16rpx;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 16rpx;
  padding: 12rpx 18rpx;
  display: flex;
  flex-wrap: wrap;
  max-width: 340rpx;
  box-shadow: 0 4rpx 12rpx rgba(61, 53, 41, 0.08);
}
.fg-legend-item {
  display: flex;
  align-items: center;
  font-size: 18rpx;
  color: #8a7f6a;
  margin: 4rpx 10rpx 4rpx 0;
}
.fg-legend-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  margin-right: 6rpx;
}
.fg-zoom {
  position: absolute;
  right: 16rpx;
  bottom: 200rpx;
  display: flex;
  flex-direction: column;
}
.fg-zoom-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 4rpx 12rpx rgba(61, 53, 41, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30rpx;
  color: #b03a2e;
  margin-top: 16rpx;
}
.fg-card {
  position: absolute;
  left: 24rpx;
  right: 24rpx;
  bottom: 24rpx;
  background: #ffffff;
  border-radius: 24rpx;
  box-shadow: 0 12rpx 32rpx rgba(61, 53, 41, 0.16);
  padding: 24rpx;
}
.fg-card-header {
  display: flex;
  align-items: center;
}
.fg-card-badge {
  font-size: 18rpx;
  color: #fff;
  border-radius: 999rpx;
  padding: 4rpx 14rpx;
  margin-right: 12rpx;
}
.fg-card-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #3d3529;
  flex: 1;
}
.fg-card-close {
  color: #9a8f7d;
  font-size: 28rpx;
  padding: 8rpx;
}
.fg-card-body {
  margin-top: 12rpx;
}
.fg-card-desc {
  font-size: 24rpx;
  color: #8a7f6a;
  line-height: 1.6;
}
.fg-card-rel {
  margin-top: 12rpx;
}
.fg-card-rel-title {
  font-size: 22rpx;
  color: #b03a2e;
  font-weight: 600;
}
.fg-card-rel-item {
  font-size: 22rpx;
  color: #8a7f6a;
  margin-left: 12rpx;
}
</style>
