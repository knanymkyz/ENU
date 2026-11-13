import json, math
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely import affinity
exec(open('zon3.py').read())
import pickle
rooms=[r for r in ROOMS]
c=AT.centroid; cx,cy=c.x,c.y
A_,u,n,Ln=edge('NW')            # n = inward normal
ax=n; px=(-n[1],n[0])          # axis dir (into building), perpendicular
E0=pt('NW',37.6,0)
def P(a,b): return (cx+ax[0]*a+px[0]*b, cy+ax[1]*a+px[1]*b)   # local frame at atrium centre: a along axis (+ inward / away from entrance), b across
def rot(points): return [P(a,b) for a,b in points]
def rect(a0,a1,b0,b1): return Polygon(rot([(a0,b0),(a1,b0),(a1,b1),(a0,b1)]))
# window in frame coords
GALP2=AT.buffer(GAL,join_style=2)
def toF(x,y):
    dx,dy=x-cx,y-cy; return (dx*ax[0]+dy*ax[1], dx*px[0]+dy*px[1])
W0,W1,H0,H1=-26,16,-17,17   # a range, b range
SC=1
def pth(geom):
    gs=[geom] if geom.geom_type=='Polygon' else list(geom.geoms); d=''
    for g in gs:
        if g.is_empty: continue
        for ring in [g.exterior]+list(g.interiors):
            d+='M'+' L'.join(f"{toF(x,y)[1]-H0:.2f},{toF(x,y)[0]-W0:.2f}" for x,y in ring.coords)+'Z '
    return d
# note: SVG x = b (across), y = a (along axis, entrance at top since a negative toward entrance)
VW,VH=H1-H0,W1-W0
o=[f'<svg class="plan" viewBox="0 0 {VW} {VH}" role="img" aria-label="Атриум 1 этажа: каталоги и СБО">',f'<rect class="ground" width="{VW}" height="{VH}"/>']
clipwin=Polygon(rot([(W0,H0),(W1,H0),(W1,H1),(W0,H1)]))
for r in ROOMS:
    if r['f']!=1 or r['g'] is None: continue
    g=r['g'].intersection(clipwin)
    if g.is_empty: continue
    cls={'cat':'z-cat','x':'z-x','avan':'z-avan','serv:sp':'z-sv','serv:bags':'z-sv','serv:lab':'z-sv','store:main':'z-st','abon':'z-abon','core':'z-core','serv:proc':'z-sv','serv:scat':'z-sv','store:oa':'z-oa'}.get(r['row'],'z-core')
    o.append(f'<path class="rm {cls}" d="{pth(g)}"/>')
o.append(f'<path class="atrE" d="{pth(AT)}"/>')
# furniture
F=[]
# SBO desk at a=-3
el=affinity.scale(Point(0,0).buffer(1,32),1.1,3.0); el2=affinity.scale(Point(0,0).buffer(1,32),0.5,2.3)
desk=Polygon(rot([(x-3.2,y) for x,y in el.exterior.coords])).difference(Polygon(rot([(x-3.2,y) for x,y in el2.exterior.coords])))
F.append(('desk',desk))
for b in [-6,-4.2,-2.4,2.4,4.2,6]:
    F.append(('term',rect(-6.9,-6.3,b-0.45,b+0.45).intersection(AT)))
# terraces with shelving risers + central stair
stair=rect(0.4,9.5,-1.5,1.5)
for i in range(4):
    a0=0.4+i*1.95
    band=rect(a0,a0+1.95,-30,30).intersection(AT).difference(stair)
    F.append(('terr%d'%i,band))
    F.append(('shelf',rect(a0,a0+0.45,-30,30).intersection(AT).difference(stair)))
    F.append(('tbl',rect(a0+0.5,a0+0.85,-30,30).intersection(AT).difference(stair).difference(rect(a0,a0+2,-30,-6.8)).difference(rect(a0,a0+2,6.8,30))))
F.append(('stair',stair.intersection(AT.buffer(0.01))))
for k in range(26):
    aa=0.4+k*0.3
    if aa<8.4: F.append(('tread',rect(aa,aa+0.04,-1.5,1.5).intersection(AT)))
for k,g in F: o.append(f'<path class="f-{k}" d="{pth(g)}"/>')
def T(a,b,s,cls='al',anchor='middle'): return f'<text class="{cls}" x="{b-H0:.2f}" y="{a-W0:.2f}" text-anchor="{anchor}">{s}</text>'
o.append(T(-4.7,0,'стойка СБО, 4 консультанта','al'))
o.append(T(-7.4,0,'электронный каталог, 12 терминалов','al'))
o.append(T(9.3,-5.2,'террасы-стеллажи, места за стойками','al2'));o.append(T(9.3,4.6,'↑ 2 этаж +6,000','al2'))

o.append(T(-9.6,0,'▲ пост контроля','alm'))
o.append(T(-21.5,0,'вестибюль ↑ главный вход','alm'))
o.append(T(-12.6,-11.5,'фойе (до контроля)','al2'))
o.append(T(-12.6,11.5,'галерея СБО (за контролем)','al2'))
o.append('</svg>')
PLAN=''.join(o)
# ---------- SECTION along axis
line=LineString([pt('NW',37.6,0.01),pt('NW',37.6,200)]).intersection(LP)
Ltot=line.length
def sample(f,s):
    q=line.interpolate(s)
    for r in ROOMS:
        if r['f']==f and r['g'] is not None and r['g'].buffer(0.01).contains(q): return r
    return None
segs={}
for f in (1,2,3):
    out=[];prev=None;st=0
    N=int(Ltot*4)
    for i in range(N+1):
        s=Ltot*i/N; r=sample(f,s); k=r['k'] if r else ('void' if AT.contains(line.interpolate(s)) else None)
        if k!=prev:
            if prev is not None: out.append((st,s,prev))
            prev=k;st=s
    out.append((st,Ltot,prev)); segs[f]=out
# atrium span on line
ia=line.intersection(AT); a0=line.project(Point(ia.coords[0])); a1=line.project(Point(ia.coords[-1]))
g0=line.project(Point(line.intersection(GALP2).coords[0]));g1=line.project(Point(line.intersection(GALP2).coords[-1]))
print('L',round(Ltot,1),'atr',round(a0,1),round(a1,1))
Z=[0,6.0,10.5,15.0]
SX=1.0
VW2=Ltot+12; VH2=25
def X(s): return s+6
def Y(z): return VH2-3-z
def person(x,h=1.75):
    return f'<g class="person"><circle cx="{x:.2f}" cy="{Y(h-0.12):.2f}" r="0.13"/><line x1="{x:.2f}" y1="{Y(h-0.25):.2f}" x2="{x:.2f}" y2="{Y(0.8):.2f}"/><line x1="{x:.2f}" y1="{Y(0.8):.2f}" x2="{x-0.2:.2f}" y2="{Y(0):.2f}"/><line x1="{x:.2f}" y1="{Y(0.8):.2f}" x2="{x+0.2:.2f}" y2="{Y(0):.2f}"/></g>'
o=[f'<svg class="plan" viewBox="0 0 {VW2:.1f} {VH2}" role="img" aria-label="Разрез по оси главного входа">',f'<rect class="ground" width="{VW2:.1f}" height="{VH2}"/>']
o.append(f'<rect class="earth" x="0" y="{Y(0):.2f}" width="{VW2:.1f}" height="3"/>')
names={r['k']:r for r in ROOMS}
CLS={'abon':'z-abon','avan':'z-avan','cat':'z-cat','readU':'z-ru','group':'z-gr','readS':'z-rs','av':'z-av','store:main':'z-st','store:comp':'z-st','store:oa':'z-oa','serv:mba':'z-sv','serv:proc':'z-sv','serv:scat':'z-sv','serv:lab':'z-sv','serv:sp':'z-sv','serv:bags':'z-sv','x':'z-x','core':'z-core','cor':'z-core'}
SHORT={'vest':'вестибюль','cat':'СБО','terr':' ','galE':'СБО','galW':'фойе','lab':'реставрация','g2':'групповые','g3':'групповые','av2g':'аванзал','av3g':'аванзал','oa2a':'откр. доступ','oa2b':'откр. доступ','oa2c':'откр. доступ','oa3a':'откр. доступ','oa3b':'откр. доступ','oa3c':'откр. доступ','comp2':'компактное','comp3':'компактное','u2b':'учебная зона','s2':'тихая зона','u2g':'места','oa2':'откр. доступ','st2':'хранение','st3':'хранение','lab':'лаборатории','cor3':'коридор','dir':'дирекция','buf':'буфет','u1':'учебный зал','exped':'экспедиция','st1':'хранение','scat':'сл. каталог'}
for f in (1,2,3):
    zb,zt=Z[f-1],Z[f]
    for s0,s1,k in segs[f]:
        if k in (None,'void'): continue
        r=names[k];cl=CLS[r['row']]
        o.append(f'<rect class="rm {cl}" x="{X(s0):.2f}" y="{Y(zt-0.35):.2f}" width="{s1-s0:.2f}" height="{zt-zb-0.35:.2f}"/>')
        if s1-s0>3.5:
            o.append(f'<text class="sl" x="{X((s0+s1)/2):.2f}" y="{Y(zb+ (zt-zb)/2)+0.4:.2f}" text-anchor="middle">{SHORT.get(k,r["n"].split(" ·")[0].lower())}</text>')
# slabs
for z in Z:
    if z==0: continue
    for s0,s1 in ([(0,g0+0.0),(g1,Ltot)] if z in (6.0,10.5) else [(0,a0),(a1,Ltot)]):
        pass
# slabs: void only at +6,000
o.append(f'<rect class="slab" x="{X(0):.2f}" y="{Y(6.0):.2f}" width="{a0:.2f}" height="0.35"/>')
o.append(f'<rect class="slab" x="{X(a1):.2f}" y="{Y(6.0):.2f}" width="{Ltot-a1:.2f}" height="0.35"/>')
for z in (10.5,15.0):
    o.append(f'<rect class="slab" x="{X(0):.2f}" y="{Y(z):.2f}" width="{Ltot:.2f}" height="0.35"/>')
o.append(f'<rect class="sandyk" x="{X(0)-3:.2f}" y="{Y(15.6):.2f}" width="3" height="{15.6-10.5:.2f}"/>')
o.append(f'<rect class="sandyk" x="{X(Ltot):.2f}" y="{Y(15.6):.2f}" width="1.2" height="{15.6-10.5:.2f}"/>')
# terraces
st=a1-7.8
d=f'M{X(st):.2f},{Y(0):.2f}'
for i in range(4):
    d+=f' L{X(st+i*1.95):.2f},{Y((i+1)*1.5):.2f} L{X(st+(i+1)*1.95):.2f},{Y((i+1)*1.5):.2f}'
d+=f' L{X(a1):.2f},{Y(0):.2f}Z'
o.append(f'<path class="terrs" d="{d}"/>')
for i in range(4):
    x0=X(st+i*1.95)
    o.append(f'<rect class="shelfs" x="{x0-0.5:.2f}" y="{Y((i+1)*1.5):.2f}" width="0.5" height="1.5"/>')
    for k in range(1,5):
        o.append(f'<line class="books" x1="{x0-0.5:.2f}" y1="{Y(i*1.5+k*0.3):.2f}" x2="{x0:.2f}" y2="{Y(i*1.5+k*0.3):.2f}"/>')
    o.append(f'<line class="ledl" x1="{x0-0.5:.2f}" y1="{Y((i+1)*1.5)+0.05:.2f}" x2="{x0:.2f}" y2="{Y((i+1)*1.5)+0.05:.2f}"/>')
o.append(f'<line class="stairl" x1="{X(st-0.5):.2f}" y1="{Y(0):.2f}" x2="{X(a1):.2f}" y2="{Y(6.0):.2f}"/>')
for i in (0,1,2,3):
    o.append(person(X(st+i*1.95+1.2),1.2).replace('class="person"',f'class="person" transform="translate(0,{-((i+1)*1.5):.2f})"'))
# ceiling lights (шаңырақ — светящийся потолок)
k=0
x=a0+0.8
while x<a1-0.5:
    o.append(f'<circle class="dl" cx="{X(x):.2f}" cy="{Y(10.15):.2f}" r="0.12"/>'); x+=1.2
o.append(f'<path class="lattice" d="M{X(a0):.2f},{Y(10.2):.2f} L{X(a1):.2f},{Y(10.2):.2f}"/>')
for sx in (a0,):
    o.append(f'<line class="curt" x1="{X(sx):.2f}" y1="{Y(10.15):.2f}" x2="{X(sx):.2f}" y2="{Y(6.35):.2f}"/>')
o.append(f'<rect class="slab" x="{X(0):.2f}" y="{Y(0):.2f}" width="{Ltot:.2f}" height="0.3"/>')
# facades
o.append(f'<line class="fac" x1="{X(0):.2f}" y1="{Y(0):.2f}" x2="{X(0):.2f}" y2="{Y(15.35):.2f}"/><line class="fac" x1="{X(Ltot):.2f}" y1="{Y(0):.2f}" x2="{X(Ltot):.2f}" y2="{Y(15.35):.2f}"/>')
# glass EI45 at atrium edge on F2/F3
for z0,z1 in ():
    for s in (a0,a1):
        o.append(f'<line class="glass" x1="{X(s):.2f}" y1="{Y(z0):.2f}" x2="{X(s):.2f}" y2="{Y(z1):.2f}"/>')
mid=(a0+a1)/2
# SBO desk & terminals & people on F1 atrium
dm=X(mid)
o.append(f'<rect class="f-desk" x="{X(a0+4.0):.2f}" y="{Y(1.05):.2f}" width="6.4" height="1.05"/>')
for b in (-6.2,-5.6):
    pass
tx_=X(a0+1.6)
o.append(f'<rect class="f-term" x="{tx_-0.3:.2f}" y="{Y(1.3):.2f}" width="0.6" height="1.3"/>')
for x in (X(4),X(9),tx_+0.7,X(a0+6.5),X(a1+2)):
    o.append(person(x))
for x in (X(g0-1.5),X(g1+1.2)):
    o.append(person(x).replace(f'cy="{Y(1.63):.2f}"',f'cy="{Y(1.63):.2f}"'))
# people on galleries F2/F3
for z in (6.35,10.85):
    for x in ((X(a0-1.6),X(a1+1.4)) if z<7 else (X(a0-6),)):
        o.append(person(x).replace('class="person"',f'class="person" transform="translate(0,{-z:.2f})"'))
# dims
for z,lab in ((0,'±0,000'),(6.0,'+6,000'),(10.5,'+10,500'),(15.0,'+15,000')):
    o.append(f'<text class="lv" x="{X(0)-0.6:.2f}" y="{Y(z)+0.5:.2f}" text-anchor="end">{lab}</text>')
o.append(f'<text class="sl2" x="{X(mid):.2f}" y="{Y(9.3):.2f}" text-anchor="middle">потолок-шаңырақ: решётка с точечным светом</text>')
o.append(f'<text class="sl2" x="{X(st+3.0):.2f}" y="{Y(4.6):.2f}" text-anchor="end">террасы-стеллажи, лестница по оси →</text>')
o.append(f'<text class="sl2" x="{X(a0)-0.4:.2f}" y="{Y(6.8):.2f}" text-anchor="end">штора EI 60</text>')
o.append(f'<text class="sl3" x="{X(Ltot*0.80):.2f}" y="{Y(16.4):.2f}" text-anchor="middle">«САНДЫҚ» — хранилище без окон</text>')
o.append(f'<text class="sl3" x="{X(Ltot*0.80):.2f}" y="{Y(-1.1):.2f}" text-anchor="middle">прозрачное основание 1–2 этажей</text>')
o.append(f'<text class="sl2" x="{X(0):.2f}" y="{Y(-2.2):.2f}" text-anchor="start">← главный вход, северо-запад</text>')
o.append(f'<text class="sl2" x="{X(Ltot):.2f}" y="{Y(-2.2):.2f}" text-anchor="end">юго-восток →</text>')
o.append('</svg>')
SEC=''.join(o)
json.dump(dict(APLAN=PLAN,SEC=SEC,SPAN=round(a1-a0,1)),open('atr3.json','w'),ensure_ascii=False)
