/**
 * 修复脚本（第二轮）：修复 fix_uni_imports.js 首轮遗漏 onLoad 导致的导入丢失。
 *
 * 背景：首轮修复脚本的 UNI_HOOKS 集合漏了 onLoad，导致 9 个文件的 onLoad
 * 导入被误删（其余钩子保留）。本脚本按原始导入清单恢复。
 * 同时清理 guide.vue 中从 @/api/heritage 误导入的 getGuideAudio（该函数
 * 实际导出自 @/api/guide，页面中并未使用 heritage 的那个导入）。
 *
 * 用法：node scripts/repair_imports.js（幂等）
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..', 'mobile-app')

// 每个文件需要恢复的 @dcloudio/uni-app 钩子导入（据首轮修复前的原始导入清单）
const RESTORE = {
  'pages/game/levels.vue': ['onLoad'],
  'pages/game/play.vue': ['onLoad', 'onUnload'],
  'pages/game/rank.vue': ['onLoad'],
  'pages/game/result.vue': ['onLoad'],
  'pages/game/wrong.vue': ['onLoad', 'onShow'],
  'pages/guide/guide.vue': ['onLoad', 'onUnload'],
  'pages/heritage/detail.vue': ['onLoad'],
  'pages/profile/favorites.vue': ['onLoad', 'onShow'],
  'pages/profile/works.vue': ['onLoad', 'onShow']
}

for (const [rel, hooks] of Object.entries(RESTORE)) {
  const file = path.join(ROOT, rel)
  let src = fs.readFileSync(file, 'utf8')
  const importLine = `import { ${hooks.join(', ')} } from '@dcloudio/uni-app'`

  if (src.includes(importLine)) {
    console.log(`⏭️ ${rel} 已正确，跳过`)
    continue
  }

  // 情况 1：存在 uni-app 导入行但钩子不全 → 合并
  const existing = src.match(/import\s*\{([^}]+)\}\s*from\s*'@dcloudio\/uni-app'/)
  if (existing) {
    const names = existing[1].split(',').map((s) => s.trim()).filter(Boolean)
    const merged = [...new Set([...hooks, ...names])].sort()
    src = src.replace(existing[0], `import { ${merged.join(', ')} } from '@dcloudio/uni-app'`)
    console.log(`🔧 ${rel} 合并钩子导入 → ${merged.join(', ')}`)
  } else {
    // 情况 2：完全没有 uni-app 导入行 → 在最后一个 vue 导入行后插入
    const vueRe = /import\s*\{[^}]+\}\s*from\s*'vue'/
    const m = src.match(vueRe)
    if (!m) {
      console.error(`❌ ${rel} 未找到 vue 导入行，无法定位插入点，请人工处理`)
      continue
    }
    src = src.replace(m[0], `${m[0]}\n${importLine}`)
    console.log(`🔧 ${rel} 补回导入 → ${importLine}`)
  }
  fs.writeFileSync(file, src, 'utf8')
}

// guide.vue：移除从 @/api/heritage 误导入的 getGuideAudio（实际来自 @/api/guide，且未使用）
const guideFile = path.join(ROOT, 'pages/guide/guide.vue')
let guideSrc = fs.readFileSync(guideFile, 'utf8')
if (guideSrc.includes("import { getProjectDetail, getGuideAudio } from '@/api/heritage'")) {
  guideSrc = guideSrc.replace(
    "import { getProjectDetail, getGuideAudio } from '@/api/heritage'",
    "import { getProjectDetail } from '@/api/heritage'"
  )
  fs.writeFileSync(guideFile, guideSrc, 'utf8')
  console.log('🔧 pages/guide/guide.vue 移除误导入 getGuideAudio（@/api/heritage）')
}

console.log('\n修复完成')
