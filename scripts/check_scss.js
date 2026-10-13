/**
 * SCSS 校验：抽取每个 .vue 的 <style lang="scss"> 块，拼接 uni.scss
 * 全局变量后用 sass 编译，提前拦截样式语法错误（HBuilderX 编译时
 * SCSS 错误同样会导致构建失败）。
 *
 * 用法：node scripts/check_scss.js（需先 npm install，依赖 mobile-app/node_modules/sass）
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..', 'mobile-app')
const sass = require(path.join(ROOT, 'node_modules', 'sass'))

function walk(dir) {
  const out = []
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name)
    const st = fs.statSync(p)
    if (st.isDirectory()) {
      if (['node_modules', 'unpackage', 'dist'].includes(name)) continue
      out.push(...walk(p))
    } else if (name.endsWith('.vue')) {
      out.push(p)
    }
  }
  return out
}

// uni.scss 全局变量与工具类（注入到每个样式块之前）
const globalScss = fs.readFileSync(path.join(ROOT, 'uni.scss'), 'utf8')

const files = walk(ROOT)
const errors = []
let styleCount = 0

for (const file of files) {
  const rel = path.relative(ROOT, file)
  const src = fs.readFileSync(file, 'utf8')
  // 匹配 <style ... lang="scss" ...> ... </style>（含 scoped）
  const re = /<style([^>]*lang\s*=\s*["']scss["'][^>]*)>([\s\S]*?)<\/style>/gi
  let m
  let idx = 0
  while ((m = re.exec(src)) !== null) {
    idx++
    styleCount++
    const body = m[2]
    try {
      sass.compileString(`${globalScss}\n${body}`, {
        syntax: 'scss',
        quietDeps: false,
        logger: {
          warn: (msg) => {
            // deprecation 等警告不阻断，仅记录
            if (/deprecat/i.test(msg)) return
            errors.push(`${rel} <style #${idx}>: ${msg}`)
          }
        }
      })
    } catch (e) {
      const line = e.span ? e.span.start.line - globalScss.split('\n').length : '?'
      errors.push(`${rel} <style #${idx}> 第 ${line} 行: ${e.message.split('\n')[0]}`)
    }
  }
}

console.log(`校验 ${files.length} 个 .vue 中的 ${styleCount} 个 SCSS 样式块`)
if (errors.length) {
  console.log(`\n❌ ${errors.length} 处 SCSS 错误：`)
  errors.forEach((e) => console.log('  ' + e))
  process.exit(1)
}
console.log('✅ 全部 SCSS 编译通过')
