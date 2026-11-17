# Расстановка мебели по расчёту: места по нормам площади на место, стеллажи по вместимости.
# Мебель ставится сеткой модулей в системе координат помещения: ось u — вдоль фасада, v — от окна вглубь
# (столы торцом к окну). Модуль = габарит мебели со стульями + проход. Перебираются сдвиги сетки, берётся
# вариант с наибольшим числом модулей; лишние снимаются с дальнего от окна края.
import math
from shapely.geometry import Polygon, Point, LineString, box
from shapely.prepared import prep
from shapely.ops import unary_union
from plan import *
from checks import LIFTDOOR, LKDOOR1

R = lambda x0, y0, x1, y1: (x0, y0, x1, y1)

# ---------------------------------------------------------------- модули (u — вдоль фасада, v — вглубь), метры
# fw, fd — габарит; mw, md — шаг сетки (габарит + проход); items — (класс, прямоугольник); seats — число стульев
MOD = {
    # стол на 4 места 0,9 × 1,6 торцом к окну; проходы 1,2 м между рядами и 0,9 м между торцами
    'read4': dict(fw=1.9, fd=1.6, mw=3.1, md=2.5, items=[('tb', R(.5, 0, 1.4, 1.6)), ('ch', R(0, .2, .45, .65)), ('ch', R(0, .95, .45, 1.4)),
                                                        ('ch', R(1.45, .2, 1.9, .65)), ('ch', R(1.45, .95, 1.9, 1.4))]),
    # стол на 6 мест 0,9 × 2,4 — для узких полос у окон
    'read6': dict(fw=1.9, fd=2.4, mw=3.1, md=3.3, items=[('tb', R(.5, 0, 1.4, 2.4)), ('ch', R(0, .15, .45, .6)), ('ch', R(0, .975, .45, 1.425)), ('ch', R(0, 1.8, .45, 2.25)),
                                                        ('ch', R(1.45, .15, 1.9, .6)), ('ch', R(1.45, .975, 1.9, 1.425)), ('ch', R(1.45, 1.8, 1.9, 2.25))]),
    # научный блок на 6 мест: стол 1,0 × 3,6 с экранами
    'sci6': dict(fw=2.0, fd=3.6, mw=3.1, md=4.2, items=[('tb', R(.5, 0, 1.5, 3.6)), ('sc', R(.98, 0, 1.02, 3.6)), ('sc', R(.5, 1.18, 1.5, 1.22)), ('sc', R(.5, 2.38, 1.5, 2.42)),
                                                       ('ch', R(0, .375, .45, .825)), ('ch', R(0, 1.575, .45, 2.025)), ('ch', R(0, 2.775, .45, 3.225)),
                                                       ('ch', R(1.55, .375, 2.0, .825)), ('ch', R(1.55, 1.575, 2.0, 2.025)), ('ch', R(1.55, 2.775, 2.0, 3.225))]),
    # научный блок на 4 места: стол 1,0 × 2,4 с экранами крестом
    'sci4': dict(fw=2.0, fd=2.4, mw=3.1, md=3.0, items=[('tb', R(.5, 0, 1.5, 2.4)), ('sc', R(.98, 0, 1.02, 2.4)), ('sc', R(.5, 1.18, 1.5, 1.22)),
                                                       ('ch', R(0, .375, .45, .825)), ('ch', R(0, 1.575, .45, 2.025)),
                                                       ('ch', R(1.55, .375, 2.0, .825)), ('ch', R(1.55, 1.575, 2.0, 2.025))]),
    # рабочее место с компьютером (АВ-залы)
    'pc1': dict(fw=1.2, fd=1.3, mw=1.6, md=2.2, items=[('tb', R(0, 0, 1.2, .7)), ('pc', R(.35, .05, .85, .2)), ('ch', R(.375, .8, .825, 1.25))]),
    # столик буфета на 4 места
    'cafe4': dict(fw=1.9, fd=1.9, mw=2.4, md=2.4, items=[('tb', R(.55, .55, 1.35, 1.35)), ('ch', R(.725, 0, 1.175, .45)), ('ch', R(.725, 1.45, 1.175, 1.9)),
                                                        ('ch', R(0, .725, .45, 1.175)), ('ch', R(1.45, .725, 1.9, 1.175))]),
    # стол сотрудника
    'desk': dict(fw=1.4, fd=1.3, mw=1.9, md=2.3, items=[('tb', R(0, 0, 1.4, .7)), ('ch', R(.475, .8, .925, 1.25))]),
    # лабораторный стол на 2 места
    'bench': dict(fw=1.4, fd=2.0, mw=2.4, md=2.9, items=[('tb', R(.5, 0, 1.4, 2.0)), ('ch', R(0, .3, .45, .75)), ('ch', R(0, 1.25, .45, 1.7))]),
    # терминал поиска: стойка и табурет, 4 м² на место (Пособие, п. 3.50)
    'term': dict(fw=.8, fd=1.0, mw=2.0, md=2.0, items=[('tm', R(0, 0, .8, .5)), ('ch', R(.175, .55, .625, 1.0))]),
    # стойка выдачи 6 м с тремя местами персонала за ней
    'desk6': dict(fw=6.0, fd=1.6, mw=7.0, md=3.0, items=[('cn', R(0, 0, 6.0, .8)), ('ch', R(.8, 1.0, 1.25, 1.45)), ('ch', R(2.775, 1.0, 3.225, 1.45)), ('ch', R(4.75, 1.0, 5.2, 1.45))]),
    # двусторонний стеллаж открытого фонда 0,6 × 4,5 м, шаг рядов 1,5 м, поперечный проход 1,5 м
    'oa': dict(cols=True, fw=.6, mw=1.5, L=6.3, gap=1.5, Lmin=1.8, cls='sh', mid=True),
    # витрина новых поступлений в абонементе
    'disp': dict(fw=.6, fd=3.0, mw=2.4, md=4.2, items=[('sh', R(0, 0, .6, 3.0)), ('sl', R(.3, 0, .3, 3.0))], run=3.0),
    # блок мобильных стеллажей: 10 двусторонних тележек 0,6 × 6 м и один подвижный проход 1,0 м; главный проход 1,2 м
    'mob': dict(cols=True, fw=.6, mw=.6, blk=10, blkgap=1.0, L=7.2, gap=1.2, Lmin=1.8, cls='st', mid=False),
    # стационарный двусторонний стеллаж 0,5 × 6 м, проход 0,75 м
    'fix': dict(cols=True, fw=.5, mw=1.25, L=7.2, gap=1.2, Lmin=1.8, cls='st', mid=False),
    # шкаф / стеллаж у стены в служебных
    'rack': dict(fw=.6, fd=2.7, mw=1.6, md=3.6, items=[('sh', R(0, 0, .6, 2.7))], run=2.7),
}
# вместимость (допущения): открытый фонд — 7 полок по 30 книг на 1 м с каждой стороны; закрытое хранение — 8 полок по 35
BOOKS = {'oa': 2 * 7 * 30, 'disp': 2 * 6 * 30, 'mob': 2 * 8 * 35, 'fix': 2 * 8 * 35, 'rack': 0}

# ---------------------------------------------------------------- что ставить в каждое помещение
# список заказов: (модуль, сколько модулей или мест, порядок: 'near' — от окна, 'far' — у дальней стены), поле — что считаем
PLANS = {
    'readU': lambda r: [('read4|read6', r['seats'], 'near')],
    'group': lambda r: [('read4|read6', r['seats'], 'near')],
    'readS': lambda r: [('sci4|sci6', r['seats'], 'near')],
    'av': lambda r: [('sci4', r['seats'], 'near')] if r['k'] == 'rare' else [('pc1', r['seats'], 'near')],
    'oa': lambda r: [('oa', None, 'near')],
    'store': lambda r: [('fix' if r['f'] == 1 else 'mob', None, 'near')],
}
ROOMPLAN = {
    (1, 'info'): [('desk6', 1, 'far'), ('term', 8, 'near'), ('rack', 6, 'far')],
    (1, 'abon'): [('desk6', 2, 'near'), ('disp', 8, 'near'), ('read4', 40, 'far')],   # отсчёт от стены хранилища, см. FRAME_OVR
    (2, 'abon2'): [('desk6', 1, 'far'), ('read4', 12, 'near')],
    (1, 'cafe'): [('desk6', 1, 'far'), ('cafe4', 44, 'near')],
    (1, 'staff1'): [('cafe4', 16, 'near'), ('rack', 4, 'far')],
    (1, 'dir'): [('desk', 12, 'near')],
    (1, 'proc'): [('desk', 12, 'near'), ('rack', 4, 'far')],
    (1, 'stf'): [('desk', 6, 'near'), ('rack', 4, 'far')],
    (1, 'restor'): [('bench', 8, 'near'), ('rack', 4, 'far')],
    (1, 'copy'): [('desk', 6, 'near'), ('bench', 2, 'far')],
    (1, 'hyg'): [('bench', 4, 'near'), ('rack', 4, 'far')],
    (1, 'exped'): [('bench', 4, 'near'), ('rack', 6, 'far')],
    (1, 'post'): [('desk', 2, 'near')],
    (1, 'lectA'): [('desk', 2, 'near')],
}
# абонемент: стойки — вдоль северной стены (за ней хранилище), места для просмотра — у окон
FRAME_OVR = {(1, 'abon'): ((55.2, 47.75), (-1.0, 0.0), (0.0, 1.0), True)}
TERM_OA = {(2, 'oaS'): 8, (2, 'oaN'): 4, (3, 'oa3'): 5}   # терминалы поиска в открытом фонде (сверх 8 на 1 этаже): 17 из 25

# ---------------------------------------------------------------- система координат помещения
FAC = list(LP.exterior.coords)


def frame(g):
    """ось u — вдоль самого длинного участка фасада, на который выходит помещение; иначе — вдоль длинной стороны"""
    gb = g.buffer(0.35)
    best = None
    for a, b in zip(FAC[:-1], FAC[1:]):
        ov = LineString([a, b]).intersection(gb).length
        if ov > 1.0 and (best is None or ov > best[0]):
            best = (ov, a, b)
    win = best is not None
    if win:
        a, b = best[1], best[2]
    else:
        c = list(g.minimum_rotated_rectangle.exterior.coords)
        a, b = max(zip(c[:-1], c[1:]), key=lambda t: math.dist(*t))
    L = math.dist(a, b)
    eu = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    ev = (-eu[1], eu[0])
    cx, cy = g.centroid.x, g.centroid.y
    if (cx - a[0]) * ev[0] + (cy - a[1]) * ev[1] < 0:
        ev = (-ev[0], -ev[1])
    return a, eu, ev, win


def to_loc(p, F):
    O, eu, ev, _ = F
    d = (p[0] - O[0], p[1] - O[1])
    return (d[0] * eu[0] + d[1] * eu[1], d[0] * ev[0] + d[1] * ev[1])


def to_w(p, F):
    O, eu, ev, _ = F
    return (O[0] + p[0] * eu[0] + p[1] * ev[0], O[1] + p[0] * eu[1] + p[1] * ev[1])


def gloc(g, F):
    out = []
    for q in polys(g):
        out.append(Polygon([to_loc(c, F) for c in q.exterior.coords], [[to_loc(c, F) for c in h.coords] for h in q.interiors]))
    return unary_union(out)


def P_(g):
    if g.is_empty: return []
    if g.geom_type == 'Polygon': return [g] if g.area > 1e-4 else []
    return [q for q in getattr(g, 'geoms', []) if q.geom_type == 'Polygon' and q.area > 1e-4]


def free_iv(field, rect, along):
    """отрезки внутри полосы rect, где полоса целиком лежит в поле (along=0 — вдоль u, 1 — вдоль v)"""
    inside = rect.intersection(field)
    if inside.is_empty:
        return []
    ivs = []
    for q in P_(inside):
        b = q.bounds
        ivs.append((b[0], b[2]) if along == 0 else (b[1], b[3]))
    blk = []
    for q in P_(rect.difference(field).buffer(-2e-3, join_style=2)):
        b = q.bounds
        blk.append((b[0] - 2e-3, b[2] + 2e-3) if along == 0 else (b[1] - 2e-3, b[3] + 2e-3))
    out = []
    for a, b in ivs:
        cur = [(a, b)]
        for c, d in blk:
            nxt = []
            for p, q in cur:
                if d <= p + 1e-6 or c >= q - 1e-6:
                    nxt.append((p, q))
                else:
                    if c > p: nxt.append((p, c))
                    if d < q: nxt.append((d, q))
            cur = nxt
        out += cur
    return out


def grid(field, m, order):
    """модули рядами: полосы глубиной fd с шагом md, в каждой — подряд с шагом mw; лучший из 6 сдвигов"""
    if field.is_empty:
        return []
    x0, y0, x1, y1 = field.bounds
    best = []
    for sy in range(6):
        got = []
        y = y0 + sy * m['md'] / 6
        while y < y1:
            for a, b in free_iv(field, box(x0 - 1, y, x1 + 1, y + m['fd']), 0):
                n = int((b - a - m['fw']) / m['mw'] + 1e-6) + 1 if b - a >= m['fw'] else 0
                pad = (b - a - (n - 1) * m['mw'] - m['fw']) / 2 if n else 0
                got += [(a + pad + i * m['mw'], y) for i in range(n)]
            y += m['md']
        if len(got) > len(best):
            best = got
    best.sort(key=lambda t: (t[1], t[0]) if order == 'near' else (-t[1], t[0]))
    return best


def cols(field, m):
    """стеллажи колоннами вдоль v: длина по месту, поперечные проходы выровнены по всему залу"""
    if field.is_empty:
        return []
    x0, y0, x1, y1 = field.bounds
    per = m['L'] + m['gap']
    best = (0, [])
    for sx in range(5):
        got = []; tot = 0; xs = []
        x = x0 + sx * m['mw'] / 5; i = 0
        while x < x1:
            xs.append(x); i += 1
            x += m['mw'] + (m['blkgap'] if m.get('blk') and i % m['blk'] == 0 else 0)
        for x in xs:
            for a, b in free_iv(field, box(x, y0 - 1, x + m['fw'], y1 + 1), 1):
                for k in range(math.floor((a - y0) / per), int((b - y0) / per) + 1):
                    p, q = max(a, y0 + k * per), min(b, y0 + k * per + m['L'])
                    if q - p >= m['Lmin']:
                        got.append((x, p, q - p)); tot += q - p
        if tot > best[0]:
            best = (tot, got)
    return best[1]


def keepouts(f):
    pts = list(LIFTDOOR.values()) + list((LKDOOR1 if f == 1 else LKDOOR).values())
    return unary_union([Point(p).buffer(2.4) for p in pts])


FURN = {1: [], 2: [], 3: []}      # (класс, точки в осях здания)
STAT = {}                          # по помещению: места, стеллажи, вместимость
SEATLIKE = ('read4', 'read6', 'sci4', 'sci6', 'pc1', 'cafe4', 'term')


def nch(m):
    return sum(1 for c, _ in m['items'] if c == 'ch')


def place(r, orders, rot=False):
    F = FRAME_OVR.get((r['f'], r['k'])) or frame(r['g'])
    if rot:                 # запасной вариант: столы вдоль фасада
        F = (F[0], F[2], F[1], F[3])
    OUT = []
    field = gloc(r['g'].buffer(-0.6, join_style=2).difference(keepouts(r['f'])), F)
    st = dict(seats=0, run=0.0, books=0, mods=collections.Counter(), win=F[3], need=0, term=0, staff=0)
    for name, n, order in orders:
        if '|' in name:      # вариант стола, при котором встаёт расчётное число мест; при равенстве — первый
            alts = name.split('|')
            cnt = lambda a: min(n, len(grid(field, MOD[a], order)) * nch(MOD[a]))
            name = max(alts, key=lambda a: (cnt(a), -alts.index(a)))
        m = MOD[name]
        if m.get('cols'):
            cc = cols(field, m)
            nt = TERM_OA.get((r['f'], r['k']), 0) if name == 'oa' else 0
            long_ = [i for i, c in enumerate(cc) if c[2] >= 4.0]
            npk = math.ceil(nt / 2)
            pick = set(long_[int((j + .5) * len(long_) / npk)] for j in range(npk)) if nt and long_ else set()
            for i, (x, y, L) in enumerate(cc):
                if i in pick:      # торец стеллажа 1,5 м отдан под два терминала спиной друг к другу
                    L -= 1.5
                    OUT.append(('tm', [to_w(p, F) for p in box(x - .1, y + L + .3, x + m['fw'] + .1, y + L + 1.5).exterior.coords]))
                    OUT.append(('sl', [to_w((x + m['fw'] / 2, y + L + .3), F), to_w((x + m['fw'] / 2, y + L + 1.5), F)]))
                    st['term'] += min(2, nt - st['term'])
                OUT.append((m['cls'], [to_w(p, F) for p in box(x, y, x + m['fw'], y + L).exterior.coords]))
                if m['mid']:
                    OUT.append(('sl', [to_w((x + m['fw'] / 2, y), F), to_w((x + m['fw'] / 2, y + L), F)]))
                st['run'] += L; st['books'] += L * BOOKS[name]; st['mods'][name] += 1
            continue
        cells = grid(field, m, order)
        seatlike = name in SEATLIKE
        if n is not None:
            if seatlike and name != 'term':
                st['need'] += n
            cells = cells[:math.ceil(n / nch(m))] if seatlike else cells[:n]
        left = n if (n is not None and seatlike) else None
        used = []
        for (x, y) in cells:
            for cls, (a, b, c, d) in m['items']:
                if cls == 'ch' and seatlike:
                    if left is not None and left <= 0:
                        continue
                    if left is not None:
                        left -= 1
                    st['term' if name == 'term' else 'seats'] += 1
                elif cls == 'ch':
                    st['staff'] += 1
                if c > a and d > b:
                    pts = box(x + a, y + b, x + c, y + d).exterior.coords
                else:
                    pts = [(x + a, y + b), (x + c, y + d)]
                OUT.append(('sl' if cls == 'sl' else cls, [to_w(p, F) for p in pts]))
            st['mods'][name] += 1
            if 'run' in m:
                st['run'] += m['run']; st['books'] += m['run'] * BOOKS.get(name, 0)
            hw, hd = (m['mw'] - m['fw']) / 2, (m['md'] - m['fd']) / 2
            used.append(box(x - hw, y - hd, x + m['fw'] + hw, y + m['fd'] + hd))
        if used:
            field = field.difference(unary_union(used))
    st['rot'] = rot
    return st, OUT


def lecture(r):
    """150 мест: 8 рядов по 19 кресел, 2 места в последнем ряду — для МГН; шаг рядов 0,9 м, проходы по 1,0 м, сцена у восточной стены"""
    x0, y0, x1, y1 = r['g'].bounds
    st = dict(seats=0, run=0, books=0, mods=collections.Counter(), win=False, need=r['seats'], term=0, staff=0)
    ya = (y0 + y1) / 2 - 19 * .55 / 2
    xs = x1 - 3.0 - 1.5                                   # сцена 3 м + площадка 1,5 м
    FURN[1].append(('cn', [(x1 - 3.0, y0 + 2.0), (x1 - .4, y0 + 2.0), (x1 - .4, y1 - 2.0), (x1 - 3.0, y1 - 2.0), (x1 - 3.0, y0 + 2.0)]))
    for i in range(8):
        x = xs - i * .9
        for j in range(19):
            if st['seats'] >= r['seats'] - 2 or (i == 7 and j in (0, 18)):
                continue
            y = ya + j * .55
            FURN[1].append(('ch', [(x - .45, y + .03), (x, y + .03), (x, y + .52), (x - .45, y + .52), (x - .45, y + .03)]))
            st['seats'] += 1
    xm = xs - 7 * .9
    for j in (0, 18):                                     # места МГН в торцах последнего ряда
        y = ya + j * .55 - .2
        FURN[1].append(('mgn', [(xm - .9, y), (xm + .1, y), (xm + .1, y + .9), (xm - .9, y + .9), (xm - .9, y)]))
    st['seats'] += 2
    STAT[(1, r['k'])] = st


import collections
for r in ROOMS:
    if r['f'] == 1 and r['k'] == 'lect':
        lecture(r)
        continue
    o = ROOMPLAN.get((r['f'], r['k'])) or (PLANS[r['c']](r) if r['c'] in PLANS else None)
    if o:
        st, out = place(r, o)
        if st['need'] > st['seats']:
            st2, out2 = place(r, o, rot=True)
            if st2['seats'] > st['seats']:
                st, out = st2, out2
        STAT[(r['f'], r['k'])] = st
        FURN[r['f']] += out

if __name__ == '__main__':
    for (f, k), st in STAT.items():
        print(f, k, 'мест', st['seats'], 'нужно', st['need'], 'терм', st.get('term', 0), 'перс', st.get('staff', 0), 'пог.м', round(st['run']), 'книг', st['books'], dict(st['mods']))
    print({f: len(v) for f, v in FURN.items()})
