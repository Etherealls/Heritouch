/**
 * 全量命名导出校验：检查所有文件的 import 命名是否真实存在于目标模块。
 *
 * 背景：HBuilderX 编译报错 ""ref" is not exported by uni-app.es.js"——
 * 页面把 Vue 响应式 API 误从 @dcloudio/uni-app 导入。同类问题还有
 * "从 @/api/heritage 导入 getGuideAudio"（该函数实际在 @/api/guide）。
 * 本校验器在编译前拦截全部此类错误。
 *
 * 覆盖：
 * - 本地 .js / .vue 模块：正则提取真实导出（function/const/class/{a as b}/default）
 * - @dcloudio/uni-app：仅 18 个页面生命周期钩子
 * - vue / pinia：精选公开 API 白名单
 * - 默认导入：目标模块必须存在 default 导出
 *
 * 用法：node scripts/check_exports.js
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..', 'mobile-app')

// Vue 3 公开 API（精选）
const VUE_API = new Set([
  'ref', 'shallowRef', 'triggerRef', 'customRef', 'reactive', 'shallowReactive',
  'readonly', 'shallowReadonly', 'toRaw', 'markRaw', 'isRef', 'unref', 'toRef', 'toRefs',
  'computed', 'watch', 'watchEffect', 'watchPostEffect', 'watchSyncEffect', 'nextTick',
  'defineComponent', 'defineAsyncComponent', 'defineCustomElement',
  'h', 'provide', 'inject', 'getCurrentInstance', 'useAttrs', 'useSlots',
  'onMounted', 'onUnmounted', 'onBeforeMount', 'onBeforeUnmount',
  'onUpdated', 'onBeforeUpdate', 'onActivated', 'onDeactivated', 'onErrorCaptured',
  'onRenderTracked', 'onRenderTriggered', 'onServerPrefetch',
  'effectScope', 'EffectScope', 'isProxy', 'isReactive', 'isReadonly', 'isShallow',
  'createApp', 'createSSRApp', 'version', 'compile',
  'Transition', 'TransitionGroup', 'KeepAlive', 'Teleport', 'Suspense',
  'BaseTransition', 'Fragment', 'Text', 'Comment', 'Static',
  'vShow', 'vModel', 'vIf', 'vElse', 'vFor', 'vHtml', 'vText', 'vOnce', 'vPre', 'vCloak', 'vSlot',
  'withDirectives', 'withModifiers', 'resolveComponent', 'resolveDirective',
  'resolveDynamicComponent', 'mergeProps', 'useCssModule', 'useCssVars',
  'defineProps', 'defineEmits', 'defineExpose', 'defineOptions', 'defineModel', 'withDefaults',
  'nextTick'
])

// pinia 公开 API（来自 node_modules/pinia/dist/pinia.mjs 导出清单）
const PINIA_API = new Set([
  'MutationType', 'PiniaVuePlugin', 'acceptHMRUpdate', 'createPinia', 'defineStore',
  'disposePinia', 'getActivePinia', 'mapActions', 'mapGetters', 'mapState', 'mapStores',
  'mapWritableState', 'setActivePinia', 'setMapStoreSuffix', 'shouldHydrate',
  'skipHydrate', 'storeToRefs'
])

// @dcloudio/uni-app 合法导出（页面/应用生命周期钩子）
const UNI_HOOKS = new Set([
  'onLoad', 'onLaunch', 'onShow', 'onReady', 'onHide', 'onUnload', 'onPullDownRefresh',
  'onReachBottom', 'onPageScroll', 'onTabItemTap', 'onShareAppMessage',
  'onShareTimeline', 'onAddToFavorites', 'onSaveExitState',
  'onNavigationBarButtonTap', 'onBackPress', 'onError', 'onUnhandledRejection',
  'onThemeChange'
])

const EXTS = ['', '.js', '.vue', '.json', '.ts']
const IMPORT_RE =
  /import\s+(?:([\w$]+)\s*,\s*)?(?:\{([^}]*)\}\s*)?(?:\*\s+as\s+([\w$]+)\s+)?from\s*['"]([^'"]+)['"]/g

function walk(dir) {
  const out = []
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name)
    const st = fs.statSync(p)
    if (st.isDirectory()) {
      if (['node_modules', 'unpackage', 'dist'].includes(name)) continue
      out.push(...walk(p))
    } else if (/\.(vue|js)$/.test(name)) {
      out.push(p)
    }
  }
  return out
}

function resolveModule(spec, fromFile) {
  if (spec.startsWith('@/')) return path.join(ROOT, spec.slice(2))
  if (spec.startsWith('.')) return path.resolve(path.dirname(fromFile), spec)
  return null // 裸模块
}

function resolveFile(base) {
  for (const ext of EXTS) {
    if (fs.existsSync(base + ext) && fs.statSync(base + ext).isFile()) return base + ext
  }
  for (const ext of ['.js', '.vue']) {
    const idx = path.join(base, 'index' + ext)
    if (fs.existsSync(idx)) return idx
  }
  return null
}

/** 从 JS 源码提取导出名与 default 导出标记 */
function extractExports(src) {
  const names = new Set()
  let hasDefault = false
  const patterns = [
    /export\s+(?:async\s+)?function\s+([A-Za-z_$][\w$]*)/g,
    /export\s+(?:const|let|var)\s+([A-Za-z_$][\w$]*)/g,
    /export\s+class\s+([A-Za-z_$][\w$]*)/g
  ]
  for (const re of patterns) {
    let m
    while ((m = re.exec(src)) !== null) names.add(m[1])
  }
  const reBraces = /export\s*\{([^}]+)\}/g
  let mb
  while ((mb = reBraces.exec(src)) !== null) {
    for (const part of mb[1].split(',')) {
      const t = part.trim()
      if (!t) continue
      const asMatch = t.match(/^([\w$]+)\s+as\s+([\w$]+)$/)
      names.add(asMatch ? asMatch[2] : t)
    }
  }
  if (/export\s+default/.test(src)) hasDefault = true
  return { names, hasDefault }
}

/** .vue 文件：拼接全部 script 块后提取导出 */
function extractVueExports(src) {
  const scripts = [...src.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)]
    .map((m) => m[1])
    .join('\n')
  const hasScriptSetup = /<script[^>]*\bsetup\b/.test(src)
  const result = extractExports(scripts)
  // script setup 的绑定不自动成为命名导出，但其组件默认导出始终可用
  return { ...result, hasScriptSetup }
}

const files = walk(ROOT)
const errors = []
const warnings = []
let importCount = 0

for (const file of files) {
  const rel = path.relative(ROOT, file)
  const src = fs.readFileSync(file, 'utf8')
  let m
  IMPORT_RE.lastIndex = 0
  while ((m = IMPORT_RE.exec(src)) !== null) {
    const [, defaultName, namedRaw, nsName, spec] = m
    const named = namedRaw
      ? namedRaw
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean)
          .map((s) => {
            const as = s.match(/^([\w$]+)\s+as\s+([\w$]+)$/)
            return as ? as[1] : s // 校验被导入的原始名
          })
      : []
    if (!defaultName && named.length === 0 && !nsName) continue // 副作用导入
    importCount++

    // ---- 裸模块：vue / pinia / @dcloudio/uni-app ----
    if (spec === 'vue') {
      for (const n of named) {
        if (!VUE_API.has(n)) errors.push(`${rel}: "${n}" 不是 vue 的公开导出`)
      }
      continue
    }
    if (spec === 'pinia') {
      for (const n of named) {
        if (!PINIA_API.has(n)) errors.push(`${rel}: "${n}" 不是 pinia 的导出`)
      }
      continue
    }
    if (spec === '@dcloudio/uni-app') {
      for (const n of named) {
        if (!UNI_HOOKS.has(n)) {
          errors.push(`${rel}: "${n}" 不是 @dcloudio/uni-app 的导出（仅生命周期钩子；ref/computed 等响应式 API 应从 'vue' 导入）`)
        }
      }
      continue
    }

    // ---- 本地模块 ----
    const base = resolveModule(spec, file)
    if (!base) {
      errors.push(`${rel}: 无法识别的模块 "${spec}"`)
      continue
    }
    const target = resolveFile(base)
    if (!target) {
      errors.push(`${rel}: 模块 "${spec}" 不存在`)
      continue
    }
    const targetSrc = fs.readFileSync(target, 'utf8')
    const info = target.endsWith('.vue') ? extractVueExports(targetSrc) : extractExports(targetSrc)

    for (const n of named) {
      if (!info.names.has(n)) {
        errors.push(`${rel}: "${n}" 不是 ${path.relative(ROOT, target)} 的导出`)
      }
    }
    if (defaultName && !info.hasDefault && !info.hasScriptSetup) {
      errors.push(`${rel}: ${path.relative(ROOT, target)} 没有 default 导出，无法默认导入`)
    }
    if (target.endsWith('.vue') && named.length && info.hasScriptSetup && !info.names.size) {
      warnings.push(`${rel}: 从 script setup 组件 "${spec}" 命名导入 ${named.join(', ')}，需确认 defineExpose`)
    }
  }
}

console.log(`校验 ${files.length} 个文件，${importCount} 处 import`)
if (warnings.length) {
  console.log(`\n⚠️ ${warnings.length} 条提醒：`)
  warnings.forEach((w) => console.log('  ' + w))
}
if (errors.length) {
  console.log(`\n❌ ${errors.length} 处导出错误：`)
  errors.forEach((e) => console.log('  ' + e))
  process.exit(1)
}
console.log('✅ 全部命名导入均有效')
