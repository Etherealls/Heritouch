/**
 * 静态检查脚本：验证 mobile-app 下所有 .vue/.js 的 import 能否解析到真实文件。
 * 覆盖：相对路径、@/ 别名（指向 mobile-app 根目录）、常见扩展名省略。
 * 外部依赖（vue / @dcloudio/uni-app / pinia）跳过不校验。
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..', 'mobile-app')
const EXTS = ['', '.js', '.vue', '.json', '.ts']
const EXTERNAL = ['vue', 'pinia', '@dcloudio', 'uni:', 'uview', 'lodash']

function walk(dir) {
  const out = []
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name)
    const st = fs.statSync(p)
    if (st.isDirectory()) {
      if (name === 'node_modules' || name === 'unpackage') continue
      out.push(...walk(p))
    } else if (/\.(vue|js)$/.test(name)) {
      out.push(p)
    }
  }
  return out
}

function resolve(spec, fromFile) {
  let base
  if (spec.startsWith('@/')) {
    base = path.join(ROOT, spec.slice(2))
  } else if (spec.startsWith('.')) {
    base = path.resolve(path.dirname(fromFile), spec)
  } else {
    return 'external'
  }
  for (const ext of EXTS) {
    if (fs.existsSync(base + ext) && fs.statSync(base + ext).isFile()) return 'ok'
  }
  // 目录形式：xxx/index.js
  for (const ext of ['.js', '.vue']) {
    const idx = path.join(base, 'index' + ext)
    if (fs.existsSync(idx)) return 'ok'
  }
  return 'missing'
}

const files = walk(ROOT)
const errors = []
let importCount = 0

for (const file of files) {
  const src = fs.readFileSync(file, 'utf8')
  const re = /(?:import\s+(?:[\w*\s{},]*?\s+from\s+)?|export\s+[\w*\s{},]*?\s+from\s+)['"]([^'"]+)['"]/g
  let m
  while ((m = re.exec(src)) !== null) {
    const spec = m[1]
    if (EXTERNAL.some((e) => spec === e || spec.startsWith(e))) continue
    importCount++
    const r = resolve(spec, file)
    if (r === 'missing') {
      const line = src.slice(0, m.index).split('\n').length
      errors.push(`${path.relative(ROOT, file)}:${line} -> ${spec}`)
    }
  }
}

console.log(`检查文件 ${files.length} 个，内部 import ${importCount} 处`)
if (errors.length) {
  console.log(`\n❌ 无法解析 ${errors.length} 处：`)
  errors.forEach((e) => console.log('  ' + e))
  process.exit(1)
} else {
  console.log('✅ 全部 import 均可解析')
}
