# Геометрия контура библиотеки (DWG «Посадка», 5 012 м²) в осях здания.
# X — вдоль северо-западного фасада от западного угла к северному, Y — вглубь здания, метры.
import math
from shapely.geometry import Polygon, Point, LineString, MultiPolygon, GeometryCollection
from shapely.ops import unary_union

# вершины контура в координатах чертежа (минус 679500, 5668400); третье число — выпуклость дуги до следующей вершины
V = [(73.51, 128.00, 0), (117.07, 118.68, .277), (121.94, 120.34, 0), (152.42, 156.40, .340), (152.71, 162.49, 0),
     (125.82, 201.12, .414), (118.86, 202.36, 0), (57.10, 159.38, .400), (55.72, 152.62, 0), (69.57, 130.50, .248)]


def _arc(a, b, bu, N=8):
    th = 4 * math.atan(bu)
    dx, dy = b[0] - a[0], b[1] - a[1]
    c = math.hypot(dx, dy)
    nx, ny = -dy / c, dx / c
    k = (c / 2) * (1 - bu * bu) / (2 * bu)
    cx, cy = (a[0] + b[0]) / 2 + nx * k, (a[1] + b[1]) / 2 + ny * k
    R = math.hypot(a[0] - cx, a[1] - cy)
    a0 = math.atan2(a[1] - cy, a[0] - cx)
    return [(cx + R * math.cos(a0 + th * j / N), cy + R * math.sin(a0 + th * j / N)) for j in range(1, N)]


_W = []
for i, (x, y, bu) in enumerate(V):
    _W.append((x, y))
    n = V[(i + 1) % 10]
    if bu:
        _W += _arc((x, y), (n[0], n[1]), bu)

OX, OY = V[7][0], V[7][1]
_L = math.hypot(V[6][0] - OX, V[6][1] - OY)
EU = ((V[6][0] - OX) / _L, (V[6][1] - OY) / _L)
EV = (EU[1], -EU[0])


def uv(p):
    dx, dy = p[0] - OX, p[1] - OY
    return (dx * EU[0] + dy * EU[1], dx * EV[0] + dy * EV[1])


def world(p):
    return (OX + p[0] * EU[0] + p[1] * EV[0], OY + p[0] * EU[1] + p[1] * EV[1])


LP = Polygon([uv(p) for p in _W]).buffer(0)
CEN = (LP.centroid.x, LP.centroid.y)
VU = [uv(p[:2]) for p in V]
EDGES = {'S': (0, 1), 'SE': (2, 3), 'NE': (4, 5), 'NW': (6, 7), 'SW': (8, 9)}
EDGE_RU = {'S': 'южный', 'SE': 'юго-восточный', 'NE': 'северо-восточный', 'NW': 'северо-западный', 'SW': 'юго-западный'}

# сетка осей 8,4 × 8,4; крайние пролёты по X — половина модуля; главный вход в пролёте 6–7
GX = [-4.38, -0.18, 8.22, 16.62, 25.02, 33.42, 41.82, 50.22, 58.62, 67.02, 75.42, 79.62]
GY = [0.6, 9.0, 17.4, 25.8, 34.2, 42.6, 51.0, 59.4, 67.8]
GYN = 'АБВГДЕЖИК'


def edge(nm):
    a, b = EDGES[nm]
    A, B = VU[a], VU[b]
    L = math.hypot(B[0] - A[0], B[1] - A[1])
    u = ((B[0] - A[0]) / L, (B[1] - A[1]) / L)
    n = (-u[1], u[0])
    m = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    if (CEN[0] - m[0]) * n[0] + (CEN[1] - m[1]) * n[1] < 0:
        n = (-n[0], -n[1])
    return A, u, n, L


def pt(nm, s, d=0.0):
    A, u, n, L = edge(nm)
    return (A[0] + u[0] * s + n[0] * d, A[1] + u[1] * s + n[1] * d)


def fb(nm, s0, s1, d0, d1):
    """прямоугольник вдоль фасада: s — вдоль фасада от его начала, d — вглубь"""
    return Polygon([pt(nm, s0, d0), pt(nm, s1, d0), pt(nm, s1, d1), pt(nm, s0, d1)]).buffer(0)


def rect(x0, x1, y0, y1):
    return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def off(d):
    return LP.buffer(-d, join_style=2) if d > 0 else LP


def band(d0, d1):
    return off(d0).difference(off(d1))


def strip(nm, s0, s1, d0=0.0, d1=9.0):
    """комната в фасадной полосе: между двумя сечениями, перпендикулярными фасаду"""
    return fb(nm, s0, s1, -3, d1 + 0.01).intersection(band(d0, d1))


def corner(a, sa, b, sb, d0=0.0, d1=9.0):
    """угловой кусок полосы: за сечением sa фасада a и до сечения sb фасада b"""
    A, ua, na, La = edge(a)
    g = band(d0, d1).intersection(fb(a, sa, sa + 300, -300, 300)).intersection(fb(b, sb - 300, sb, -300, 300))
    v = pt(a, La)
    if g.geom_type != 'Polygon':
        parts = [q for q in getattr(g, 'geoms', []) if q.geom_type == 'Polygon']
        g = min(parts, key=lambda q: q.distance(Point(v))) if parts else Polygon()
    return g


def polys(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [q for q in g.geoms if q.geom_type == 'Polygon' and q.area > 0.05]


def clean(g, eps=0.25):
    """убрать щепки"""
    g = g.buffer(-eps, join_style=2).buffer(eps, join_style=2)
    return unary_union(polys(g)) if not g.is_empty else g


if __name__ == '__main__':
    print('area', round(LP.area, 1), 'bounds', [round(v, 2) for v in LP.bounds])
    for k in EDGES:
        A, u, n, L = edge(k)
        print(k, round(L, 2), [round(v, 2) for v in A], 'u', [round(v, 3) for v in u], 'n', [round(v, 3) for v in n])
    for d in (9, 12):
        print('off', d, round(off(d).area), [tuple(round(c, 1) for c in p) for p in off(d).simplify(0.3).exterior.coords])
