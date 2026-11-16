# Чтение векторного PDF коллеги: перевод точек листа (1:200, А0) в оси здания.
import pymupdf, glob, math, collections, json
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from geom import *
F = glob.glob('/root/.claude/uploads/bb2fce9f-64bd-51be-9b3b-d67c281d68e1/*.pdf')[0]
DOC = pymupdf.open(F)
K = 25.4 / 72 * 200 / 1000  # м на пункт
def segs(page, color=None, wmin=0, wmax=9):
    out = []
    for g in page.get_drawings():
        c = g.get('color'); w = g.get('width') or 0
        if c is None or not (wmin <= w <= wmax): continue
        if color is not None and tuple(round(v, 1) for v in c) != color: continue
        for it in g['items']:
            if it[0] == 'l':
                out.append(((it[1].x, it[1].y), (it[2].x, it[2].y)))
    return out
def fills(page):
    out = []
    for g in page.get_drawings():
        f = g.get('fill')
        if f is None or g.get('color') is not None: continue
        col = tuple(round(v, 2) for v in f)
        if col in ((1.0, 1.0, 1.0), (0.0, 0.0, 0.0), (0.37, 0.37, 0.37), (1.0, 0.0, 0.0), (0.62, 0.62, 0.62)): continue
        pts = []
        for it in g['items']:
            if it[0] == 'l': pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
            elif it[0] == 're': r = it[1]; pts += [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
            elif it[0] == 'qu': q = it[1]; pts += [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]
            elif it[0] == 'c': pts += [(it[1].x, it[1].y), (it[4].x, it[4].y)]
        if len(pts) >= 3:
            out.append((col, pts))
    return out
if __name__ == '__main__':
    p = DOC[1]
    S = segs(p, (0.0, 0.0, 0.0), 1.0, 1.2)
    S.sort(key=lambda s: -math.dist(*s))
    for a, b in S[:14]:
        print('len m', round(math.dist(a, b) * K, 2), [round(v, 1) for v in a], [round(v, 1) for v in b])

ORG = {1: (769.4, 1269.1), 0: (870.7, 1115.5)}
EPX = (0.82072, -0.57133)
def to_uv(pi, p):
    ox, oy = ORG[pi]
    dx, dy = p[0] - ox, p[1] - oy
    return ((dx * EPX[0] + dy * EPX[1]) * K, (-dx * EPX[1] + dy * EPX[0]) * K)
