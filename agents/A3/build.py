# Запуск из папки tools:  python3 build.py zoning_V1.js ../ADM_LIB_Zoning.html ["Заголовок страницы"]
import sys
src, out = sys.argv[1], sys.argv[2]
title = sys.argv[3] if len(sys.argv) > 3 else None
t = open('template.html', encoding='utf8').read()
z = open(src, encoding='utf8').read()
a = t.index('// Примеры (раскомментировать по образцу, не как решение):')
b = t.index('// ════════════ РАЗДЕЛ 4.')
html = t[:a] + z.rstrip() + '\n\n' + t[b:]
if title:
    html = html.replace('<title>Ректорат и библиотека — зонирование</title>', '<title>' + title + '</title>', 1)
open(out, 'w', encoding='utf8').write(html)
