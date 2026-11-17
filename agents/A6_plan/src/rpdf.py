# План 1 этажа архитектора (Revit, PDF 17.11): помещения и подписи → оси здания.
import pymupdf, glob, math, collections
import numpy as np
F = glob.glob('/root/.claude/uploads/bb2fce9f-64bd-51be-9b3b-d67c281d68e1/65648d57-*.pdf')[0]
DOC = pymupdf.open(F); P = DOC[0]
K = 25.4 / 72 * 200 / 1000           # м на пункт при 1:200
EX = np.array([0.82072, -0.57133]); EY = np.array([0.57133, 0.82072])
def red_lines():
    out = []
    for g in P.get_drawings():
        c = g.get('color')
        if c and tuple(round(v, 1) for v in c) == (1.0, 0.0, 0.0):
            for it in g['items']:
                if it[0] == 'l':
                    out.append(((it[1].x, it[1].y), (it[2].x, it[2].y)))
    return out
def calib():
    L = red_lines()
    xs, ys = [], []
    for a, b in L:
        d = np.array(b) - np.array(a); n = np.linalg.norm(d)
        if n < 50: continue
        d /= n
        m = (np.array(a) + np.array(b)) / 2
        if abs(d @ EY) > 0.99: xs.append(m @ EX)      # линия вдоль EY → постоянный X
        elif abs(d @ EX) > 0.99: ys.append(m @ EY)
    def cl(v):
        v = sorted(v); g = [[v[0]]]
        for t in v[1:]:
            (g[-1].append(t) if t - g[-1][-1] < 3 else g.append([t]))
        return [np.mean(x) for x in g if len(x) >= 2]
    return cl(xs), cl(ys)
if __name__ == '__main__':
    cx, cy = calib()
    print('X-линии', [round(v, 1) for v in cx]); print('шаг', [round(b - a, 1) for a, b in zip(cx, cx[1:])])
    print('Y-линии', [round(v, 1) for v in cy]); print('шаг', [round(b - a, 1) for a, b in zip(cy, cy[1:])])
    print('8,4 м =', round(8.4 / K, 1), 'pt')

def to_uv(x, y):
    p = np.array([x, y])
    return ((p @ EX + 148.3) * K - 3.9, (p @ EY - 1482.6) * K + 0.1)
def labels():
    out = []
    for b in P.get_text('blocks'):
        x0, y0, x1, y1, t = b[:5]
        t = ' '.join(t.split())
        u = to_uv((x0 + x1) / 2, (y0 + y1) / 2)
        if -10 < u[0] < 90 and -5 < u[1] < 75:
            out.append((t, u))
    return out
def fills():
    from shapely.geometry import Polygon
    out = []
    for g in P.get_drawings():
        f = g.get('fill')
        if f is None: continue
        col = tuple(round(v, 2) for v in f)
        if col in ((1.0, 1.0, 1.0), (0.0, 0.0, 0.0)): continue
        pts = []
        for it in g['items']:
            if it[0] == 'l': pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == 're': r = it[1]; pts += [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
            elif it[0] == 'qu': q = it[1]; pts += [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]
            elif it[0] == 'c': pts += [(it[1].x, it[1].y), (it[4].x, it[4].y)]
        if len(pts) < 3: continue
        try:
            pg = Polygon([to_uv(*p) for p in pts]).buffer(0)
        except Exception:
            continue
        if pg.area > 2: out.append((col, pg))
    return out
