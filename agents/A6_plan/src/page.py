# Сборка страницы: планы трёх этажей (север вверху), экспликация, проверки, сверка с программой.
import json, math, collections, html
from shapely.ops import polylabel, unary_union
from checks import *
from furn import FURN, STAT

def fm(x, d=0):
    return f"{x:,.{d}f}".replace(',', ' ').replace('.', ',')

WX0, WX1, WY0, WY1 = 44.0, 166.0, 110.0, 211.0
W, H = WX1 - WX0, WY1 - WY0
def S(p):
    w = world(p)
    return (w[0] - WX0, WY1 - w[1])
def P(p):
    x, y = S(p); return f"{x:.2f},{y:.2f}"
def dpath(g):
    d = ''
    for q in polys(g):
        for ring in [q.exterior] + list(q.interiors):
            d += 'M' + ' L'.join(P(c) for c in ring.coords) + 'Z '
    return d
def line(a, b, cls, extra=''):
    (x1, y1), (x2, y2) = S(a), S(b)
    return f'<line class="{cls}" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {extra}/>'
def text(p, t, cls, anchor='middle', dy=0):
    x, y = S(p)
    return f'<text class="{cls}" x="{x:.2f}" y="{y+dy:.2f}" text-anchor="{anchor}">{t}</text>'

CAT = {'pub': ('Вестибюльная группа', 'x'), 'abon': ('Абонемент', 'abon'), 'cat': ('Каталоги, СБО', 'cat'), 'readU': ('Учебные зоны', 'ru'),
       'oa': ('Открытый фонд', 'oa'), 'readS': ('Научные зоны', 'rs'), 'group': ('Групповые', 'gr'), 'av': ('АВ-залы, редкие книги', 'av'),
       'store': ('Хранение', 'st'), 'scat': ('Служебные', 'sv'), 'proc': ('Служебные', 'sv'), 'sp': ('Служебные', 'sv'), 'lab': ('Служебные', 'sv'),
       'staff': ('Служебные', 'sv'), 'tech': ('Техника', 'core'), 'lk': ('Лестничная клетка', 'lk'), 'core': ('Лифты', 'core'), 'wc': ('Санузлы', 'core'),
       'cor': ('Коридоры и галереи', 'cor'), 'pocket': ('Световой карман', 'pk'), 'void': ('Проём в перекрытии', 'void'),
       'ter': ('Лестница-амфитеатр', 'ter'), 'lect': ('Лекционный зал', 'x')}

# нумерация помещений
for f in (1, 2, 3):
    n = 0
    for r in ROOMS:
        if r['f'] == f and r['c'] not in ('lk', 'core', 'wc', 'void'):
            n += 1; r['no'] = f"{f}.{n:02d}"
        elif r['f'] == f:
            r['no'] = ''
PERS = {}
import plan as PL

LPOS = {(1, 'vest'): (8.0, 28.0), (2, 'atr'): (35.2, 20.0), (3, 'atr'): (35.2, 24.0), (2, 'vv'): (6.5, 27.5), (1, 'terr'): (27.0, 20.0),
        (2, 'abon2'): (52.0, 20.5), (1, 'cloak'): (41.0, 23.7), (1, 'porch'): (-3.4, 24.0)}
SDOOR = {1: [((68.96, 16.65), (71.46, 16.65))], 2: [], 3: []}
def label(r):
    g = max(polys(r['g']), key=lambda q: q.area)
    if (r['f'], r['k']) in LPOS:
        return LPOS[(r['f'], r['k'])], g
    try:
        p = polylabel(g, 0.5)
    except Exception:
        p = g.representative_point()
    return (p.x, p.y), g

def plan(f):
    o = [f'<svg class="plan" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="План {f} этажа">', f'<rect class="ground" width="{W:.0f}" height="{H:.0f}"/>']
    rs = [r for r in ROOMS if r['f'] == f]
    for r in rs:
        cls = CAT[r['c']][1]
        zone = ' zone' if r['open'] else ''
        o.append(f'<path class="rm c-{cls}{zone}" data-k="{f}:{r["k"]}" tabindex="0" d="{dpath(r["g"])}"><title>{html.escape(r["n"])} — {fm(r["a"])} м²</title></path>')
    o.append(f'<path class="outline" d="{dpath(LP)}"/>')
    # мебель по расчёту (furn.py), один path на класс
    by = collections.defaultdict(list)
    for cls, pts in FURN[f]:
        if len(pts) == 2:
            by[cls].append('M' + P(pts[0]) + ' L' + P(pts[1]))
        else:
            by[cls].append('M' + ' L'.join(P(c) for c in pts[:-1]) + 'Z')
    o.append('<g class="fu">' + ''.join(f'<path class="fu-{c}" d="{" ".join(v)}"/>' for c, v in by.items()) + '</g>')
    # оси
    ax = ['<g class="ax">']
    for i, x in enumerate(GX):
        ax.append(line((x, -3.5), (x, 70.5), 'axl')); ax.append(text((x, -5.6), PL.GXN[i], 'axt', dy=.5))
    for j, y in enumerate(GY):
        ax.append(line((-9.5, y), (82.5, y), 'axl')); ax.append(text((-11.6, y), PL.GYN2[j], 'axt', dy=.5))
    ax.append('</g>'); o += ax
    # главная лестница-амфитеатр: террасы со стеллажами и марши по оси
    if f in (1, 2):
        x0, x1, y0, y1 = 21.2, 49.3, 16.9, 30.9
        xb = x1 if f == 2 else PL.CLX0
        n = 6
        for i in range(n):
            ta, tb = x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n
            if ta >= xb: break
            tb = min(tb, xb)
            o.append(f'<path class="tr tr{i%2}" d="M{P((ta,y0))} L{P((tb,y0))} L{P((tb,y1))} L{P((ta,y1))}Z"/>')
            for yy in ((y0 + .6, 22.3), (25.5, y1 - .6)):
                xs = ta + 1.3
                while xs < tb - .3:
                    o.append(line((xs, yy[0]), (xs, yy[1]), 'shelf')); xs += 1.5
            xs = ta + .3
            while xs < min(ta + 3.3, tb):
                o.append(line((xs, 22.9), (xs, 24.9), 'gtr')); xs += .33
        o.append(line((x0 + .6, 23.9), (min(xb, x1) - .8, 23.9), 'garr', 'marker-end="url(#mk)"'))
        if f == 1:
            o.append(line((4.6, 15.4), (4.6, 30.6), 'ctl'))
            o.append(text((6.2, 17.2), 'контроль', 'ctlt', anchor='start'))
            # гардероб: барьеры на двух длинных сторонах и 12 рядов консольных вешалок
            cx0, cx1, cy0, cy1 = PL.CLBOX
            for yb in (cy0 + 0.33, cy1 - 0.33):
                o.append(line((cx0, yb), (cx1, yb), 'bar'))
            ya, yb_ = cy0 + 1.65, cy1 - 1.65
            for i in range(12):
                xa = cx0 + 1.0 + i * 1.34
                o.append(f'<path class="hang" d="M{P((xa,ya))} L{P((xa+0.55,ya))} L{P((xa+0.55,yb_))} L{P((xa,yb_))}Z"/>')
    # подписи
    for r in rs:
        (px, py), g = label(r)
        c = r['c']
        if c == 'lk':
            o.append(text((px, py), r['k'][3:], 'lkl', dy=.6)); continue
        if c in ('core', 'wc'):
            t = {'liftA': 'Л-А', 'liftB': 'Л-Б', 'liftF': 'Гр', 'blift': '', 'wcA': 'WC', 'wcB': 'WC', 'wcS': 'WC', 'wcN': 'WC'}[r['k']]
            if t: o.append(text((px, py), t, 'cl', dy=.5))
            continue
        if c == 'void':
            o.append(text((px, py), {'atr': 'атриум', 'vv': 'второй свет', 'porch': 'ниша входа'}.get(r['k'], 'проём'), 'vl', dy=0)); continue
        if c == 'cor':
            continue
        big = r['a'] >= 110
        mid = r['a'] >= 60
        if big:
            o.append(text((px, py), r['no'], 'no', dy=-1.5))
            o.append(text((px, py), html.escape(r['s']), 'rl', dy=.4))
            o.append(text((px, py), fm(r['a']) + ' м²', 'ra', dy=2.2))
        elif mid:
            o.append(text((px, py), r['no'], 'no', dy=-.2))
            o.append(text((px, py), fm(r['a']), 'ra', dy=1.5))
        else:
            o.append(text((px, py), r['no'], 'no', dy=.5))
    for a_, b_ in SDOOR[f]:
        o.append(line(a_, b_, 'sdoor'))
    # входы
    def arrow(a, b, cls, t, ta='middle', off=(0, 0)):
        o.append(line(a, b, cls, f'marker-end="url(#m{cls})"'))
        o.append(text((a[0] + off[0], a[1] + off[1]), t, 'ml ' + cls + 't', anchor=ta))
    if f == 1:
        arrow((-13.0, 19.0), (-6.6, 19.0), 'am', 'главный вход', ta='end', off=(-.8, .6))
        arrow((88.0, 36.3), (81.4, 36.3), 'as', 'служебный вход, приёмка', ta='start', off=(.8, 1.4))
    if f == 2:
        o.append(f'<path class="bridge" d="M{P((76.2,-0.6))} L{P((82.2,-6.6))} L{P((86.8,-2.0))} L{P((80.8,4.0))}Z"/>')
        o.append(text((88.5, -6.0), 'переход в ректорат', 'ml amt', anchor='start'))
    # эвакуация
    ev = ['<g class="ov ov-evac">']
    keys = [f] + (['3s'] if f == 3 else [])
    seen = set()
    for key in keys:
        res = RES[key]
        worst = sorted(res['rooms'], key=lambda r: -r['d1'])[:3]
        for w_ in worst:
            pts = [w_['door']] + w_['path']
            ev.append('<polyline class="route" points="' + ' '.join(P(p) for p in pts) + '"/>')
            m = pts[len(pts) // 2]
            ev.append(text(m, f"{w_['d1']:.0f} м", 'rt', dy=-.6))
        if res['hall']:
            hl = res['hall']
            ev.append('<polyline class="route" points="' + ' '.join(P(p) for p in hl['path']) + '"/>')
            ev.append(f'<circle class="far" cx="{S(hl["p"])[0]:.2f}" cy="{S(hl["p"])[1]:.2f}" r=".9"/>')
            ev.append(text(hl['path'][len(hl['path']) // 2], f"{hl['d']:.0f} м", 'rt', dy=-.6))
        for n, p in res['exits'].items():
            if (round(p[0], 1), round(p[1], 1)) in seen: continue
            seen.add((round(p[0], 1), round(p[1], 1)))
            x, y = S(p); ev.append(f'<circle class="exit" cx="{x:.2f}" cy="{y:.2f}" r="1.1"><title>{n}</title></circle>')
    if f == 1:
        for n, p in LKOUT.items():
            e, s_ = None, None
            c = LKDOOR[n]; d = (p[0] - c[0], p[1] - c[1]); L = math.hypot(*d); u = (d[0] / L, d[1] / L)
            ev.append(line((p[0] - u[0] * 1.5, p[1] - u[1] * 1.5), (p[0] + u[0] * 4.0, p[1] + u[1] * 4.0), 'eo', 'marker-end="url(#meo)"'))
    ev.append('</g>'); o += ev
    # свет
    lt = ['<g class="ov ov-light">']
    for key in keys:
        cfg = CFG[key]
        R_ = {r['k']: r for r in rs}
        for k in cfg['light_cor']:
            if k in R_: lt.append(f'<path class="lcor" d="{dpath(R_[k]["g"])}"/>')
        for k in cfg['light_rooms']:
            if k in R_: lt.append(f'<path class="lroom" d="{dpath(R_[k]["g"])}"/>')
        for n, p in cfg['light']:
            if not n: continue
            x, y = S(p); lt.append(f'<path class="lsrc" d="M{x:.2f},{y-1.5:.2f} L{x+1.5:.2f},{y:.2f} L{x:.2f},{y+1.5:.2f} L{x-1.5:.2f},{y:.2f}Z"><title>{n}</title></path>')
    lt.append('</g>'); o += lt
    o.append(f'<g transform="translate({W-7:.0f},9)"><path class="na" d="M0,-5 L2,3 L0,1.6 L-2,3z"/><text class="ml" y="-6" text-anchor="middle">С</text></g>')
    o.append(f'<g transform="translate(6,{H-5:.0f})"><line class="sc" x1="0" y1="0" x2="20" y2="0"/><line class="sc" x1="0" y1="-.8" x2="0" y2=".8"/><line class="sc" x1="10" y1="-.8" x2="10" y2=".8"/><line class="sc" x1="20" y1="-.8" x2="20" y2=".8"/><text class="ml" x="10" y="-1.4" text-anchor="middle">0 — 10 — 20 м</text></g>')
    o.append('</svg>')
    return ''.join(o)

if __name__ == '__main__':
    import sys
    open('/tmp/a5dbg.html', 'w').write('<style>' + open('dbg.css').read() + '</style>' + ''.join(f'<div style="width:1400px">{plan(f)}</div>' for f in (1, 2, 3)))
