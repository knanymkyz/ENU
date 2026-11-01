# Сборка HTML: вставляет раздел 3 (зонирование) в шаблон.
# Запуск из папки tools:  python3 build.py zoning_V1.js ../ADM_LIB_Zoning.html
import sys
src = sys.argv[1] if len(sys.argv) > 2 else 'zoning_V1.js'
out = sys.argv[-1]
t = open('template.html', encoding='utf8').read()
z = open(src, encoding='utf8').read()
a = t.index('// Примеры (раскомментировать по образцу, не как решение):')
b = t.index('// ════════════ РАЗДЕЛ 4.')
open(out, 'w', encoding='utf8').write(t[:a] + z.rstrip() + '\n\n' + t[b:])
