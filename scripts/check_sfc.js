/**
 * SFC 静态校验：用 @vue/compiler-sfc 逐一解析编译全部 .vue 文件。
 * 覆盖：<script setup> / Options API 脚本编译、模板编译、语法错误定位。
 * SCSS 样式块不在此编译（由 HBuilderX 内部 sass 处理），仅做存在性检查。
 */
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..', 'mobile-app')
const { parse, compileScript, compileTemplate } = require(
  path.resolve(ROOT, 'node_modules', '@vue', 'compiler-sfc')
)

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

const files = walk(ROOT)
const errors = []
let scriptSetupCount = 0

for (const file of files) {
  const rel = path.relative(ROOT, file)
  const source = fs.readFileSync(file, 'utf8')
  let descriptor
  try {
    const { errors: parseErrors } = parse(source, { filename: file })
    if (parseErrors.length) {
      errors.push(`${rel}: SFC 解析失败 - ${parseErrors[0].message}`)
      continue
    }
    descriptor = parse(source, { filename: file }).descriptor
  } catch (e) {
    errors.push(`${rel}: 解析异常 - ${e.message}`)
    continue
  }

  // 编译脚本（script setup / 普通 script）
  try {
    if (descriptor.script || descriptor.scriptSetup) {
      const compiled = compileScript(descriptor, {
        id: rel,
        isProd: false
      })
      if (descriptor.scriptSetup) scriptSetupCount++
    }
  } catch (e) {
    errors.push(`${rel}: <script> 编译失败 - ${e.message.split('\n')[0]}`)
    continue
  }

  // 编译模板
  if (descriptor.template) {
    try {
      const tpl = compileTemplate({
        source: descriptor.template.content,
        filename: file,
        id: rel,
        compilerOptions: { bindingMetadata: undefined }
      })
      if (tpl.errors && tpl.errors.length) {
        errors.push(`${rel}: <template> 编译失败 - ${tpl.errors[0].message || tpl.errors[0]}`)
      }
    } catch (e) {
      errors.push(`${rel}: <template> 编译异常 - ${e.message.split('\n')[0]}`)
    }
  }

  // 样式块存在性
  if (!descriptor.styles.length) {
    errors.push(`${rel}: 缺少 <style> 块`)
  }
}

console.log(`校验 ${files.length} 个 .vue 文件（其中 ${scriptSetupCount} 个使用 <script setup>）`)
if (errors.length) {
  console.log(`\n❌ 发现 ${errors.length} 处问题：`)
  errors.forEach((e) => console.log('  ' + e))
  process.exit(1)
}
console.log('✅ 全部 SFC 解析与编译通过')
