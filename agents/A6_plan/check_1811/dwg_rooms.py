import json, math, re, sys
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
def dec(s): return re.sub(r'\\U\+([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1),16)), s or '').replace('\\P',' ')
def ring(path):
    pts=[]
    if 'vertices' in path and path.get('vertices'):
        for v in path['vertices']: pts.append((v['x'],v['y']))
        return pts
    for e in path.get('edges',[]):
        if e['type']==1:
            pts.append((e['start']['x'],e['start']['y']))
        elif e['type']==2:
            c=e['center']; r=e['radius']; a0=e['startAngle']; a1=e['endAngle']; ccw=e.get('isCCW',1)
            if not ccw: a0,a1=-a0,-a1
            if a1<a0: a1+=2*math.pi
            for j in range(16):
                t=a0+(a1-a0)*j/16
                x,y=c['x']+r*math.cos(t), c['y']+r*math.sin(t)
                if not ccw: y=c['y']-r*math.sin(-t) if False else c['y']+r*math.sin(t)
                pts.append((x,y))
        else:
            pts.append((e.get('start',{}).get('x',0),e.get('start',{}).get('y',0)))
    return pts
def hpoly(h):
    rs=[Polygon(ring(p)).buffer(0) for p in h['boundaryPaths'] if len(ring(p))>=3]
    rs=[r for r in rs if not r.is_empty]
    if not rs: return None
    rs.sort(key=lambda g:-g.area)
    g=rs[0]
    for r in rs[1:]:
        g = g.difference(r) if g.contains(r.representative_point()) else g.union(r)
    return g
out={}
for f in (1,2,3):
    E=json.load(open(f'f{f}.json'))['ents']
    H=[(h,hpoly(h)) for h in E if h['type']=='HATCH' and h['layer']=='Помещения']
    H=[(h,g) for h,g in H if g is not None]
    LH=[(h,hpoly(h)) for h in E if h['type']=='HATCH' and h['layer']=='Легенды']
    LT=[(dec(e['text']),e['insertionPoint']) for e in E if e['type']=='MTEXT' and e['layer']=='Легенды']
    leg={}
    for h,g in LH:
        if g is None: continue
        c=g.centroid
        t=min(LT,key=lambda t:(abs(t[1]['y']-c.y)*3+abs(t[1]['x']-c.x)) if t[1]['x']>c.x else 1e12)
        leg[h['color']]=t[0]
    tags=[(dec(e['text']).strip(),e['insertionPoint']) for e in E if e['type']=='MTEXT' and e['layer']=='Марки помещений']
    rooms=[]
    for no,p in tags:
        pt=Point(p['x'],p['y'])
        hits=[(h,g) for h,g in H if g.buffer(300).contains(pt)]
        hits.sort(key=lambda t:t[1].area)
        if hits:
            h,g=hits[0]; rooms.append(dict(no=no,a=round(g.area/1e6,2),cat=leg.get(h['color'],'?'),x=p['x'],y=p['y']))
        else:
            rooms.append(dict(no=no,a=None,cat='—',x=p['x'],y=p['y']))
    out[f]=dict(rooms=rooms,legend=sorted(set(leg.values())),nhatch=len(H))
    print(f, 'tags',len(tags),'hatches',len(H),'legend',sorted(set(leg.values())))
json.dump(out,open('dwg_rooms.json','w'),ensure_ascii=False,indent=0)
