# mdpage.py OUT.html "Title" "Subtitle" id:Label:file.md [id:Label:file.md ...]
import sys, html, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md2html import convert
out, title, sub = sys.argv[1], sys.argv[2], sys.argv[3]
tabs = [a.split(':', 2) for a in sys.argv[4:]]
lk = os.environ.get('LINK', '')
linkhtml = (lambda u, t: f'<p class="go"><a href="{html.escape(u)}">{html.escape(t)} →</a></p>')(*lk.split('|', 1)) if lk else ''
def js(s):  # safe inside <script type=text/plain>
    return s.replace('</script', '<\\/script')
nav = ''.join(f'<a href="#{i}" data-id="{i}">{html.escape(l)}</a>' for i, l, _ in tabs)
srcs = ''.join(f'<section id="sec-{i}" hidden>{convert(open(f, encoding="utf8").read())}</section>\n' for i, l, f in tabs)
page = f'''<title>{html.escape(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: чертёжный лист — узкая колонка текста, закладки-вкладки сверху, таблицы в своей прокрутке */
:root{{--bg:#f6f7f8;--paper:#ffffff;--fg:#1c2329;--muted:#5d6974;--line:#d9dee3;--accent:#1f5f8b;--tint:#eaf1f6;
 --crit:#b3261e;--warn:#9a6a00;--ok:#2e7d4f;
 --f-body:"Golos Text",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--f-mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#12161a;--paper:#181d22;--fg:#e3e8ec;--muted:#98a4ae;--line:#2c343b;--accent:#7db4dc;--tint:#1d2a34;--crit:#ff8a80;--warn:#e6b84d;--ok:#7fd1a0;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#12161a;--paper:#181d22;--fg:#e3e8ec;--muted:#98a4ae;--line:#2c343b;--accent:#7db4dc;--tint:#1d2a34;--crit:#ff8a80;--warn:#e6b84d;--ok:#7fd1a0;color-scheme:dark}}
body{{background:var(--bg);color:var(--fg);font:15px/1.6 var(--f-body)}}
header{{background:var(--paper);border-bottom:1px solid var(--line);padding-block:22px 0;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.wrap{{max-width:880px;margin:0 auto}}
.eyebrow{{font:500 12px/1 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}
h1.t{{font-size:26px;line-height:1.2;margin:8px 0 4px;text-wrap:balance}}
.sub{{color:var(--muted);margin:0 0 16px}}
nav{{display:flex;flex-wrap:wrap;gap:4px}}
nav a{{padding:9px 14px;border:1px solid var(--line);border-bottom:none;border-radius:6px 6px 0 0;color:var(--muted);text-decoration:none;font-weight:500;background:var(--bg)}}
nav a.on{{background:var(--paper);color:var(--fg);border-color:var(--accent);box-shadow:inset 0 3px 0 var(--accent)}}
nav a:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
main{{padding-block:24px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
article{{max-width:880px;margin:0 auto;min-width:0}}
article h1{{font-size:23px;line-height:1.25;text-wrap:balance;margin:0 0 12px}}
article h2{{font-size:19px;margin:34px 0 10px;padding-top:14px;border-top:1px solid var(--line);text-wrap:balance}}
article h3{{font-size:16px;margin:24px 0 8px}}
article p,article li{{max-width:72ch}}
article ul,article ol{{padding-left:22px}} article li{{margin:3px 0}}
article code{{font:13px var(--f-mono);background:var(--tint);padding:1px 5px;border-radius:4px}}
article pre{{background:var(--tint);padding:12px;border-radius:6px;overflow-x:auto}}
article hr{{border:none;border-top:1px solid var(--line);margin:20px 0}}
article blockquote{{margin:12px 0;padding:8px 14px;border-left:3px solid var(--accent);background:var(--tint)}}
.tw{{overflow-x:auto;margin:12px 0;border:1px solid var(--line);border-radius:6px;background:var(--paper)}}
table{{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}}
th,td{{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
th{{background:var(--tint);font-weight:600}} tr:last-child td{{border-bottom:none}}
.meta{{color:var(--muted);font-size:13.5px;border:1px solid var(--line);background:var(--paper);border-radius:6px;padding:10px 14px;margin-bottom:18px}}
.meta p{{margin:2px 0}}
.sev-c{{color:var(--crit);font-weight:700}} .sev-w{{color:var(--warn);font-weight:700}} .sev-o{{color:var(--ok);font-weight:700}}
.err{{color:var(--crit)}}
.go{{margin:-6px 0 16px}} .go a{{display:inline-block;padding:8px 14px;border-radius:6px;background:var(--accent);color:var(--paper);text-decoration:none;font-weight:600}} .go a:focus-visible{{outline:2px solid var(--fg);outline-offset:2px}}
</style>
<header><div class="wrap"><div class="eyebrow">Проект 207 · библиотека ЕНУ</div><h1 class="t">{html.escape(title)}</h1><p class="sub">{html.escape(sub)}</p>{linkhtml}<nav>{nav}</nav></div></header>
<main><article id="doc">{srcs}</article></main>
<script>
const IDS={[t[0] for t in tabs]!r};
function hl(sec){{sec.querySelectorAll('li,td,p,h2,h3,strong').forEach(el=>{{for(const n of [...el.childNodes]){{if(n.nodeType!==3)continue;const t=n.nodeValue;const r=/(Критично|критично|Желательно|желательно|(?<![а-яё])(?:Важно|важно)(?![а-яё]))/;if(!r.test(t))continue;const sp=document.createElement('span');sp.innerHTML=t.replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c])).replace(new RegExp(r.source,'g'),m=>'<span class="sev-'+(/ритич/.test(m)?'c':/ажно/.test(m)?'w':'o')+'">'+m+'</span>');n.replaceWith(...sp.childNodes);}}}});
 const f=sec.firstElementChild;if(f&&f.tagName==='P'&&/Что это/.test(f.textContent)){{const d=document.createElement('div');d.className='meta';f.replaceWith(d);d.appendChild(f);}}}}
document.querySelectorAll('article section').forEach(hl);
function show(){{const id=IDS.includes(location.hash.slice(1))?location.hash.slice(1):IDS[0];
 document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.dataset.id===id));
 IDS.forEach(i=>document.getElementById('sec-'+i).hidden=(i!==id));window.scrollTo(0,0);}}
addEventListener('hashchange',show);show();
</script>
'''
open(out, 'w', encoding='utf8').write(page)
