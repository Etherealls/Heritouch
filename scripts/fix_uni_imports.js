/**
 * 修复脚本：将误从 @dcloudio/uni-app 导入的 Vue 核心 API 拆回 'vue'。
 * @dcloudio/uni-app 仅导出页面生命周期钩子（onLoad/onShow/...），
 * ref/reactive/computed/watch 等响应式 API 必须从 'vue' 导入，否则
 * Rollup 报 "xxx is not exported by uni-app.es.js" 导致编译失败。
 *
 * 用法：node scripts/fix_uni_imports.js（幂等，可重复执行）
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..', 'mobile-app')

// Vue 3 核心 API（允许从 vue 导入的集合）
const VUE_CORE = new Set([
  'ref', 'shallowRef', 'reactive', 'shallowReactive', 'readonly', 'shallowReadonly',
  'computed', 'watch', 'watchEffect', 'watchPostEffect', 'watchSyncEffect',
  'nextTick', 'toRef', 'toRefs', 'isRef', 'unref', 'customRef', 'triggerRef',
  'defineComponent', 'defineAsyncComponent', 'h', 'provide', 'inject',
  'onMounted', 'onUnmounted', 'onBeforeMount', 'onBeforeUnmount',
  'onUpdated', 'onBeforeUpdate', 'onActivated', 'onDeactivated', 'onErrorCaptured',
  'getCurrentInstance', 'useAttrs', 'useSlots', 'markRaw', 'toRaw',
  'isProxy', 'isReactive', 'isReadonly', 'effectScope', 'version'
])

// @dcloudio/uni-app 合法导出（页面/应用生命周期钩子）
const UNI_HOOKS = new Set([
  'onLoad', 'onLaunch', 'onShow', 'onReady', 'onHide', 'onUnload', 'onPullDownRefresh',
  'onReachBottom', 'onPageScroll', 'onTabItemTap', 'onShareAppMessage',
  'onShareTimeline', 'onAddToFavorites', 'onSaveExitState',
  'onNavigationBarButtonTap', 'onBackPress', 'onError', 'onUnhandledRejection',
  'onThemeChange'
])

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

const RE = /import\s*\{([^}]+)\}\s*from\s*'@dcloudio\/uni-app'/g
let fixedCount = 0

for (const file of walk(ROOT)) {
  const src = fs.readFileSync(file, 'utf8')
  let changed = false

  const next = src.replace(RE, (match, names) => {
    const list = names.split(',').map((s) => s.trim()).filter(Boolean)
    const vueApis = list.filter((n) => VUE_CORE.has(n))
    const hooks = list.filter((n) => UNI_HOOKS.has(n))
    const unknown = list.filter((n) => !VUE_CORE.has(n) && !UNI_HOOKS.has(n))

    if (unknown.length) {
      console.warn(`⚠️ ${path.relative(ROOT, file)}: 未知命名导入 ${unknown.join(', ')}，请人工确认`)
    }
    if (vueApis.length === 0) return match // 无需修复

    changed = true
    const parts = []
    if (vueApis.length) parts.push(`import { ${vueApis.join(', ')} } from 'vue'`)
    if (hooks.length) parts.push(`import { ${hooks.join(', ')} } from '@dcloudio/uni-app'`)
    return parts.join('\n')
  })

  if (changed) {
    fs.writeFileSync(file, next, 'utf8')
    fixedCount++
    console.log(`✅ 已修复 ${path.relative(ROOT, file)}`)
  }
}

console.log(`\n共修复 ${fixedCount} 个文件`)
