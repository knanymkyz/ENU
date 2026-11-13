import json, math
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
exec(open('geo.py').read().split("LK={")[0].replace("print(","(lambda *a,**k:None)("))
LP=Polygon(LIB); _c=LP.centroid; _k=(300/LP.area)**.5; ATR=[(_c.x+(x-_c.x)*_k,_c.y+(y-_c.y)*_k) for x,y in LIB]; AT=Polygon(ATR); C=(LP.centroid.x,LP.centroid.y)
RING=LP.exterior; PER=RING.length
OUTD=14; GAL=3
INNER=LP.buffer(-OUTD,join_style=2); GALP=AT.buffer(GAL,join_style=2)
BAND={'out':LP.difference(INNER),'mid':INNER.difference(GALP),'gal':GALP.difference(AT),'atr':AT,
      'om':LP.difference(GALP),'all':LP}
def T(e,s): return RING.project(Point(pt(e,s,0)))
def bpts(ta,tb):
    if tb<=ta: tb+=PER
    n=max(2,int((tb-ta)/1.0)); out=[]
    for i in range(n+1):
        t=ta+(tb-ta)*i/n; p=RING.interpolate(t%PER); out.append((p.x,p.y))
    return out
def sector(a,b):
    ta,tb=T(*a),T(*b); P=[C]+bpts(ta,tb); return Polygon(P).buffer(0)
LK={'ЛК-1':('W',18),'ЛК-2':('NW',55.6),'ЛК-3':('NW',19.6),'ЛК-4':('NE',36),'ЛК-5':('SE',36),'ЛК-6':('S',38)}
CORES={}
for k,(e,s) in LK.items(): CORES[k]=('st',Polygon(box(e,s-4.5,s+4.5,0,4.8)))
CORES['лифты']=('lift',Polygon(box('NW',45,51,12.5,18)))
CORES['гр. лифт, книгоподъёмник']=('lift',Polygon(box('S',27.5,33.5,0,5.5)))
CORES['книгоподъёмник В']=('lift',Polygon(box('NE',24,29,12,16)))
CORES['санузлы З']=('wc',Polygon(box('NW',53,62,12.5,19)))
CORES['санузлы В']=('wc',Polygon(box('SE',22,31,12.5,19)))
CORESET=unary_union([p for _,p in CORES.values()])
ROOMS=[]
def R(f,key,name,row,band,a,b,seats_norm=None,note=''):
    g=BAND[band].intersection(sector(a,b)) if a else BAND[band]
    g=g.difference(CORESET)
    ROOMS.append(dict(f=f,k=key,n=name,row=row,g=g,nrm=seats_norm,note=note))
for f in (1,2,3):
    for k,(t,p) in CORES.items():
        nm=k if t!='st' else k
        row={'st':'core','lift':'core','wc':'core'}[t]
        if f==1 and k=='книгоподъёмник В': pass
        ROOMS.append(dict(f=f,k=k,n=nm,row=row,g=p.intersection(LP),nrm=None,note=''))
