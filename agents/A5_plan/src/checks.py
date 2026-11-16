# Проверки: эвакуация (табл. 8, 9), тупики, путь до лифта, свет в коридорах (п. 4.3.3.1), лестницы, отсеки.
import heapq, math
import numpy as np
from shapely import contains_xy
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from plan import *

STEP = 0.5
X0, Y0 = -8.0, -1.0
NX, NY = int(90 / STEP), int(72 / STEP)
GXc = X0 + (np.arange(NX) + .5) * STEP
GYc = Y0 + (np.arange(NY) + .5) * STEP
MX, MY = np.meshgrid(GXc, GYc, indexing='ij')
NB = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
KN = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]  # ходы «конём» — точнее длина косых путей


def mask(g):
    return contains_xy(g.buffer(0.05), MX, MY)


def cell(p):
    return (int((p[0] - X0) / STEP), int((p[1] - Y0) / STEP))


def snap(m, p, rmax=2.5):
    i0, j0 = cell(p)
    best = None
    R = int(rmax / STEP)
    for di in range(-R, R + 1):
        for dj in range(-R, R + 1):
            i, j = i0 + di, j0 + dj
            if 0 <= i < NX and 0 <= j < NY and m[i, j]:
                d = (GXc[i] - p[0]) ** 2 + (GYc[j] - p[1]) ** 2
                if best is None or d < best[0]:
                    best = (d, i, j)
    return (best[1], best[2]) if best else None


def dijkstra(m, srcs, block=None):
    D = np.full((NX, NY), np.inf)
    P = {}
    h = []
    for s in srcs:
        if s is None:
            continue
        D[s] = 0
        heapq.heappush(h, (0, s))
    while h:
        d, (i, j) = heapq.heappop(h)
        if d > D[i, j]:
            continue
        for di, dj, w in NB:
            a, b = i + di, j + dj
            if 0 <= a < NX and 0 <= b < NY and m[a, b] and (block is None or not block[a, b]):
                if di and dj and not (m[i + di, j] and m[i, j + dj]):
                    continue
                nd = d + w * STEP
                if nd < D[a, b]:
                    D[a, b] = nd
                    P[(a, b)] = (i, j)
                    heapq.heappush(h, (nd, (a, b)))
        for di, dj in KN:
            a, b = i + di, j + dj
            if 0 <= a < NX and 0 <= b < NY and m[a, b] and (block is None or not block[a, b]):
                si, sj = (1 if di > 0 else -1), (1 if dj > 0 else -1)
                if abs(di) == 2:
                    mid = [(i + si, j), (i + si, j + sj)]
                else:
                    mid = [(i, j + sj), (i + si, j + sj)]
                if not all(m[x, y] and (block is None or not block[x, y]) for x, y in mid):
                    continue
                nd = d + 2.23607 * STEP
                if nd < D[a, b]:
                    D[a, b] = nd
                    P[(a, b)] = (i, j)
                    heapq.heappush(h, (nd, (a, b)))
    return D, P


def path(P, c):
    out = [c]
    while c in P:
        c = P[c]
        out.append(c)
    pts = [(GXc[i], GYc[j]) for i, j in out]
    return list(LineString(pts).simplify(0.6).coords) if len(pts) > 1 else pts


def rooms(f):
    return [r for r in ROOMS if r['f'] == f]


def door_candidates(r, walk):
    """дверь — в середине самого длинного участка стены, общего с коридором или залом"""
    from shapely.ops import linemerge
    b = r['g'].boundary.intersection(walk.buffer(0.3))
    if b.is_empty:
        return []
    if b.geom_type not in ('LineString',):
        parts = [q for q in getattr(b, 'geoms', []) if q.geom_type == 'LineString']
        if not parts:
            return []
        b = linemerge(parts)
    geoms = [b] if b.geom_type == 'LineString' else list(b.geoms)
    geoms.sort(key=lambda q: -q.length)
    out = []
    for q in geoms[:2]:
        if q.length > 1.2:
            p = q.interpolate(q.length / 2)
            out.append((p.x, p.y))
    return out


LK3S = (75.75, 30.0)   # вторая дверь ЛК-3 — в зал (2 и 3 этажи)
LK6S = pt('SW', 25.8, 4.5)  # дверь ЛК-6 в научный зал 3 этажа
MAIN = (37.62, 3.2)
SERV = (79.6, 23.7)
SKY = [(25.0, 28.5), (48.0, 28.5)]  # зенитные фонари над коридором хранилища

CFG = {
    1: dict(walk=['cor1', 'scor', 'vest', 'pkE', 'pkS', 'cafe', 'svest'],
            exits={**LKDOOR, 'Главный вход': MAIN, 'Служебный вход': SERV},
            lifts=LIFTDOOR, light_cor=['cor1', 'scor'],
            light=[('ЛК-1', LKDOOR['ЛК-1']), ('ЛК-2', LKDOOR['ЛК-2']), ('ЛК-3', LKDOOR['ЛК-3']), ('ЛК-4', LKDOOR['ЛК-4']),
                   ('ЛК-5', LKDOOR['ЛК-5']), ('ЛК-6', LKDOOR['ЛК-6'])], light_rooms=['vest', 'cafe', 'pkE', 'pkS', 'svest']),
    2: dict(walk=['zW', 'zNWl', 'zGal', 'zNWr', 'zSW', 'zS1', 'zS2', 'zSv', 'zSE1', 'zSE2', 'zE', 'zNE', 'oaW', 'oaE', 'hallbr', 'scor'],
            exits={**LKDOOR, 'ЛК-3 (из зала)': LK3S}, lifts=LIFTDOOR, light_cor=['scor'],
            light=[('ЛК-3', LKDOOR['ЛК-3'])], light_rooms=['hallbr']),
    3: dict(walk=['sS1', 'sS2', 'sSv', 'sSE1', 'sSE2', 'sE', 'sNE'],
            exits={'ЛК-4': LKDOOR['ЛК-4'], 'ЛК-5': LKDOOR['ЛК-5'], 'ЛК-6 (из зала)': LK6S, 'ЛК-3 (через дверь в коридор)': (69.75, 30.0)},
            lifts={'Б': LIFTDOOR['Б']}, light_cor=[], light=[], light_rooms=[]),
    '3s': dict(walk=['spine', 'corNWl', 'corSW', 'corNWr', 'corNE', 'rest0', 'rest1', 'rest2'],
               exits={'ЛК-1': LKDOOR['ЛК-1'], 'ЛК-2': LKDOOR['ЛК-2'], 'ЛК-3': LKDOOR['ЛК-3'], 'ЛК-6': LKDOOR['ЛК-6']},
               lifts={}, light_cor=['spine', 'corNWl', 'corSW', 'corNWr', 'corNE', 'rest0', 'rest1', 'rest2'],
               light=[('ЛК-1', LKDOOR['ЛК-1']), ('ЛК-2', LKDOOR['ЛК-2']), ('ЛК-3', LKDOOR['ЛК-3']), ('ЛК-6', LKDOOR['ЛК-6']), ('Копирование', (6.0, 9.4)), ('Реставрация', (69.7, 12.3)),
                      ('Фонарь 1', SKY[0]), ('Фонарь 2', SKY[1])] + [('', (x + dx, 28.5)) for x, _ in SKY for dx in (-2.0, 2.0)], light_rooms=[]),
}
SKIP = ('lk', 'core', 'wc', 'void')


def run(key):
    f = 3 if key == '3s' else key
    cfg = CFG[key]
    R = {r['k']: r for r in rooms(f)}
    walk = unary_union([R[k]['g'] for k in cfg['walk'] if k in R])
    m = mask(walk)
    ex = {n: snap(m, p) for n, p in cfg['exits'].items()}
    D, P = dijkstra(m, list(ex.values()))
    # какое из выходов ближайшее — по обратному пути
    def nearest(c):
        while c in P:
            c = P[c]
        for n, s in ex.items():
            if s == c:
                return n
    # поле «без ближайшего выхода»: для каждого выхода — поле от остальных с перекрытым проходом у него
    alt = {}
    for n, s in ex.items():
        if s is None:
            continue
        blk = (MX - GXc[s[0]]) ** 2 + (MY - GYc[s[1]]) ** 2 <= 2.6 ** 2
        alt[n] = dijkstra(m, [v for k, v in ex.items() if k != n and v], blk)[0]
    lf = None
    if cfg['lifts']:
        lf = dijkstra(m, [snap(m, p) for p in cfg['lifts'].values()])[0]
    res = []
    for r in rooms(f):
        if r['k'] in cfg['walk'] or r['c'] in SKIP or key == 3 or (key == '3s' and r['c'] == 'readS'):
            continue
        cand = [(c, snap(m, c, 1.2)) for c in door_candidates(r, walk)]
        cand = [(c, s) for c, s in cand if s is not None and np.isfinite(D[s])]
        if not cand:
            continue
        c, s = cand[0]
        if r['c'] in ('abon', 'av', 'store', 'readS', 'group') and len(cand) > 1 and D[cand[1][1]] < D[s]:
            pass
        n1 = nearest(s)
        d1 = float(D[s]) + 0.5
        d2 = float(alt[n1][s]) + 0.5 if n1 in alt else float('inf')
        res.append(dict(k=r['k'], n=r['n'], door=c, d1=d1, to=n1, dead=(not np.isfinite(d2)) and d1 > 3.6, d2=d2,
                        lift=(float(lf[s]) + 0.5) if lf is not None else None, path=path(P, s)))
    # залы без стен: самая далёкая точка
    hall = None
    if key in (2, 3):
        mm = m & np.isfinite(D)
        idx = np.unravel_index(np.argmax(np.where(mm, D, -1)), D.shape)
        hall = dict(d=float(D[idx]), p=(float(GXc[idx[0]]), float(GYc[idx[1]])), to=nearest(tuple(int(v) for v in idx)),
                    path=path(P, tuple(int(v) for v in idx)))
        if lf is not None:
            j = np.unravel_index(np.argmax(np.where(m & np.isfinite(lf), lf, -1)), lf.shape)
            hall['lift'] = float(lf[j]); hall['liftp'] = (float(GXc[j[0]]), float(GYc[j[1]]))
    # свет в коридорах
    light = None
    if cfg['light_cor']:
        cor = unary_union([R[k]['g'] for k in cfg['light_cor'] if k in R])
        cm = mask(cor)
        src = [snap(cm, p, 3.0) for _, p in cfg['light']]
        for k in cfg['light_rooms']:
            b = cor.boundary.intersection(R[k]['g'].buffer(0.3))
            for q in ([b] if b.geom_type == 'LineString' else getattr(b, 'geoms', [])):
                if q.geom_type != 'LineString':
                    continue
                for t in range(int(q.length / 0.5) + 1):
                    pp = q.interpolate(t * 0.5)
                    src.append(snap(cm, (pp.x, pp.y), 1.2))
        LD, LP_ = dijkstra(cm, [s for s in src if s])
        mm = cm & np.isfinite(LD)
        idx = np.unravel_index(np.argmax(np.where(mm, LD, -1)), LD.shape)
        light = dict(maxd=float(LD[idx]), p=(float(GXc[idx[0]]), float(GYc[idx[1]])), unlit=int((cm & ~np.isfinite(LD)).sum()),
                     over12=float((mm & (LD > 12)).sum() * STEP * STEP), field=LD, cm=cm)
    return dict(rooms=res, hall=hall, light=light, exits=cfg['exits'], D=D, m=m)


RES = {k: run(k) for k in (1, 2, 3, '3s')}

if __name__ == '__main__':
    for k, v in RES.items():
        print('=== этаж', k)
        for r in sorted(v['rooms'], key=lambda r: -r['d1'])[:8]:
            print(f"  {r['k']:8s} до {r['to']:14s} {r['d1']:5.1f} м  тупик={r['dead']}  2-й путь {r['d2']:5.1f}  до лифта {r['lift'] if r['lift'] is None else round(r['lift'],1)}")
        de = [r for r in v['rooms'] if r['dead']]
        print('  тупиковых:', [(r['k'], round(r['d1'], 1)) for r in de])
        if v['hall']:
            print('  зал: макс. путь', round(v['hall']['d'], 1), v['hall']['p'], v['hall']['to'], 'до лифта', round(v['hall'].get('lift', 0), 1), v['hall'].get('liftp'))
        if v['light']:
            print('  свет: макс. до источника', round(v['light']['maxd'], 1), v['light']['p'], 'без света клеток', v['light']['unlit'], 'площадь дальше 12 м', v['light']['over12'])
        ml = max([r['lift'] for r in v['rooms'] if r['lift'] is not None] or [0])
        print('  макс. до лифта от дверей', round(ml, 1))
