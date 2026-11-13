import json, math
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
exec(open('zon4.py').read())
c=AT.centroid; cx,cy=c.x,c.y
ax=_n; px=(-_n[1],_n[0])
def P(a,b): return (cx+ax[0]*a+px[0]*b, cy+ax[1]*a+px[1]*b)
def rot(pts): return [P(a,b) for a,b in pts]
def rect(a0,a1,b0,b1): return Polygon(rot([(a0,b0),(a1,b0),(a1,b1),(a0,b1)]))
def toF(x,y): dx,dy=x-cx,y-cy; return (dx*ax[0]+dy*ax[1], dx*px[0]+dy*px[1])
GALP2=AT.buffer(GAL,join_style=2)
CLS={'abon':'z-abon','avan':'z-avan','cat':'z-cat','readU':'z-ru','group':'z-gr','readS':'z-rs','av':'z-av','store:main':'z-st','store:comp':'z-st','store:oa':'z-oa','serv:mba':'z-sv','serv:proc':'z-sv','serv:scat':'z-sv','serv:lab':'z-sv','serv:sp':'z-sv','serv:bags':'z-sv','x':'z-x','core':'z-core','cor':'z-core','store:staff':'z-sv'}
# ================= PLAN of atrium F1
W0,W1,H0,H1=-24,16,-19,19
def pth(geom):
    gs=[geom] if geom.geom_type=='Polygon' else [g for g in getattr(geom,'geoms',[]) if g.geom_type=='Polygon']; d=''
    for g in gs:
        if g.is_empty: continue
        for ring in [g.exterior]+list(g.interiors):
            d+='M'+' L'.join(f"{toF(x,y)[1]-H0:.2f},{toF(x,y)[0]-W0:.2f}" for x,y in ring.coords)+'Z '
    return d
VW,VH=H1-H0,W1-W0
o=[f'<svg class="plan" viewBox="0 0 {VW} {VH}" role="img" aria-label="Атриум 1 этажа">',f'<rect class="ground" width="{VW}" height="{VH}"/>']
clip=rect(W0,W1,H0,H1)
for r in ROOMS:
    if r['f']!=1: continue
    g=r['g'].intersection(clip)
    if not g.is_empty: o.append(f'<path class="rm {CLS[r["row"]]}" d="{pth(g)}"/>')
o.append(f'<path class="atrE" d="{pth(AT)}"/>')
F=[]
el=affinity.scale(Point(0,0).buffer(1,32),1.0,2.8); el2=affinity.scale(Point(0,0).buffer(1,32),0.45,2.2)
F.append(('desk',Polygon(rot([(x-4.6,y) for x,y in el.exterior.coords])).difference(Polygon(rot([(x-4.6,y) for x,y in el2.exterior.coords])))))
for b in [-7.5,-5.7,-3.9,3.9,5.7,7.5]:
    F.append(('term',rect(-7.0,-6.4,b-0.45,b+0.45).intersection(AT)))
# stair (b -1.4..1.6) + terraces (b < -1.4)
ST=rect(-2.6,9.6,-1.4,1.6).intersection(AT)
for i in range(4):
    a0=-2.6+i*3.0
    band=rect(a0,a0+3.0,-30,-1.4).intersection(AT)
    F.append((f'terr{i}',band))
    F.append(('shelf',rect(a0,a0+0.45,-30,-1.4).intersection(AT)))
    F.append(('tbl',rect(a0+0.5,a0+0.85,-30,-1.6).intersection(AT.buffer(-0.6))))
F.append(('stair',ST))
for k in range(40):
    aa=-2.6+k*0.3
    F.append(('tread',rect(aa,aa+0.04,-1.4,1.6).intersection(AT)))
# lounge pit
L=BAND['atrL']
F.append(('pit0',L))
F.append(('pit1',L.buffer(-0.45,join_style=2)))
pit=L.buffer(-0.9,join_style=2); F.append(('pit2',pit))
cush=pit.difference(pit.buffer(-0.95,join_style=2)).difference(rect(-3.0,-1.0,-30,30))
F.append(('cush',cush))
lc=pit.centroid; la,lb=toF(lc.x,lc.y)
F.append(('wood',rect(la-2.6,la+2.6,lb-1.2,lb+1.2).intersection(pit.buffer(-1.6))))
outer=GALP2.difference(GALP2.buffer(-0.5,join_style=2)).intersection(L)
F.append(('bshelf',outer))
for g in F: o.append(f'<path class="f-{g[0]}" d="{pth(g[1])}"/>')
for (a,b) in [(la-3.4,lb+1.6),(la+3.0,lb-1.0),(-2.0,7.5)]:
    if L.contains(Point(P(a,b))): o.append(f'<circle class="plant" cx="{b-H0:.2f}" cy="{a-W0:.2f}" r="0.75"/>')
def T(a,b,s,cls='al',anc='middle'): o.append(f'<text class="{cls}" x="{b-H0:.2f}" y="{a-W0:.2f}" text-anchor="{anc}">{s}</text>')
T(-10.2,0,'▲ пост контроля','alm'); T(-20.5,0,'вестибюль ↑ главный вход','alm')
T(-7.8,0,'электронный каталог, 12 терминалов'); T(-2.6,0,'стойка СБО')
T(10.4,-8.5,'террасы-стеллажи','al2')
T(la+0.2,lb,'стол','al2'); T(la+5.6,lb+0.8,'читальная гостиная −0,45','al')
o.append('</svg>')
APLAN=''.join(o)
# ================= SECTIONS
Z=[0,6.0,10.5,15.0]
def cut(line):
    L_=line.length
    def samp(f,s):
        q=line.interpolate(s)
        for r in ROOMS:
            if r['f']==f and r['g'].buffer(0.01).contains(q): return r
        return None
    segs={}
    for f in (1,2,3):
        out=[];prev=None;st=0;N=int(L_*4)
        for i in range(N+1):
            s=L_*i/N; r=samp(f,s); k=r['k'] if r else ('void' if AT.contains(line.interpolate(s)) else None)
            if k!=prev:
                if prev is not None: out.append((st,s,prev))
                prev=k;st=s
        out.append((st,L_,prev)); segs[f]=out
    return segs
names={r['k']:r for r in ROOMS}
SH={'vest':'вестибюль','cat':'СБО','galE':'СБО','galW':'фойе','u2g':'места','oa2':'откр. доступ','cor3':'коридор','u1':'научный зал','s2':'научная зона','u2b':'научная зона','dir':'дирекция','staffS':'персонал','lect':'лекц. зал','cloak':'гардероб','abonF':'фонд абон.','abon':'абонемент','lab':'лаборатории','g2':'групповые','u2a':'учебная зона','u2c':'учебная зона','rare':'зал редких','av3':'медиатека','stf':'сотр. хранения','rareSt':'хран. редких','buf':'буфет','exped':'экспедиция','scat':'сл. каталог','link':'холл перехода'}
def person(X,Y,x,z=0,h=1.75):
    return f'<g class="person"><circle cx="{x:.2f}" cy="{Y(z+h-0.12):.2f}" r="0.13"/><line x1="{x:.2f}" y1="{Y(z+h-0.25):.2f}" x2="{x:.2f}" y2="{Y(z+0.8):.2f}"/><line x1="{x:.2f}" y1="{Y(z+0.8):.2f}" x2="{x-0.2:.2f}" y2="{Y(z):.2f}"/><line x1="{x:.2f}" y1="{Y(z+0.8):.2f}" x2="{x+0.2:.2f}" y2="{Y(z):.2f}"/></g>'
def section(line,title,skip=(),clipw=None):
    segs=cut(line); L_=line.length
    ia=line.intersection(AT); s0=line.project(Point(ia.coords[0])); s1=line.project(Point(ia.coords[-1]))
    lo,hi=(0,L_) if clipw is None else clipw
    VW_=hi-lo+12; VH_=25
    X=lambda s: s-lo+6; Y=lambda z: VH_-3-z
    o=[f'<svg class="plan" viewBox="0 0 {VW_:.1f} {VH_}" role="img" aria-label="{title}">',f'<rect class="ground" width="{VW_:.1f}" height="{VH_}"/>',
       f'<rect class="earth" x="0" y="{Y(0):.2f}" width="{VW_:.1f}" height="3"/>']
    for f in (1,2,3):
        zb,zt=Z[f-1],Z[f]
        for a_,b_,k in segs[f]:
            if k in (None,'void') or k in skip: continue
            a_,b_=max(a_,lo),min(b_,hi)
            if b_<=a_: continue
            r=names[k]
            o.append(f'<rect class="rm {CLS[r["row"]]}" x="{X(a_):.2f}" y="{Y(zt-0.35):.2f}" width="{b_-a_:.2f}" height="{zt-zb-0.35:.2f}"/>')
            if b_-a_>4: o.append(f'<text class="sl" x="{X((a_+b_)/2):.2f}" y="{Y(zb+(zt-zb)/2)+0.4:.2f}" text-anchor="middle">{SH.get(k,r["n"].split(" ·")[0].split(":")[0].lower()[:16])}</text>')
    for z in (6.0,10.5,15.0):
        o.append(f'<rect class="slab" x="{X(lo):.2f}" y="{Y(z):.2f}" width="{s0-lo:.2f}" height="0.35"/>')
        o.append(f'<rect class="slab" x="{X(s1):.2f}" y="{Y(z):.2f}" width="{hi-s1:.2f}" height="0.35"/>')
    o.append(f'<rect class="slab" x="{X(lo):.2f}" y="{Y(0):.2f}" width="{hi-lo:.2f}" height="0.3"/>')
    for sx in (s0-0.3,s1):
        o.append(f'<rect class="shaftw" x="{X(sx):.2f}" y="{Y(15.0):.2f}" width="0.3" height="{15.0-10.85:.2f}"/>')
    o.append(f'<path class="sky" d="M{X(s0):.2f},{Y(15.35):.2f} L{X(s0+1):.2f},{Y(17.2):.2f} L{X(s1-1):.2f},{Y(17.2):.2f} L{X(s1):.2f},{Y(15.35):.2f}"/>')
    for t in (0.2,0.4,0.6,0.8):
        xs=X(s0+(s1-s0)*t);o.append(f'<line class="ray" x1="{xs:.2f}" y1="{Y(16.8):.2f}" x2="{xs+(t-0.5)*3:.2f}" y2="{Y(1.0):.2f}"/>')
    if lo==0: o.append(f'<line class="fac" x1="{X(0):.2f}" y1="{Y(0):.2f}" x2="{X(0):.2f}" y2="{Y(15.35):.2f}"/>')
    if hi==L_: o.append(f'<line class="fac" x1="{X(L_):.2f}" y1="{Y(0):.2f}" x2="{X(L_):.2f}" y2="{Y(15.35):.2f}"/>')
    for z,lab in ((0,'±0,000'),(6.0,'+6,000'),(10.5,'+10,500'),(15.0,'+15,000')):
        o.append(f'<text class="lv" x="{X(lo)-0.6:.2f}" y="{Y(z)+0.5:.2f}" text-anchor="end">{lab}</text>')
    o.append(f'<text class="sl2" x="{X((s0+s1)/2):.2f}" y="{Y(17.6):.2f}" text-anchor="middle">фонарь-шаңырақ</text>')
    o.append(f'<text class="sl2" x="{X((s0+s1)/2):.2f}" y="{Y(12.8):.2f}" text-anchor="middle">атриум на 3 этажа</text>')
    return o,X,Y,s0,s1,line,VW_,VH_
# ---- longitudinal (axis, through stair)
lineA=LineString([pt('NW',37.6,0.01),pt('NW',37.6,200)]).intersection(LP)
o,X,Y,s0,s1,ln,VWa,VHa=section(lineA,'Разрез по оси главного входа',skip=('cat','terr','lounge'))
sc=ln.project(Point(cx,cy))
# floor 1 in atrium: SBO desk + stair; terraces beyond
o.append(f'<rect class="z-cat rm" x="{X(s0):.2f}" y="{Y(5.65):.2f}" width="{sc-3.0-s0:.2f}" height="5.65"/>')
d=f'M{X(sc-2.6):.2f},{Y(0):.2f}'
for i in range(4): d+=f' L{X(sc-2.6+i*3):.2f},{Y((i+1)*1.5):.2f} L{X(sc-2.6+(i+1)*3):.2f},{Y((i+1)*1.5):.2f}'
d+=f' L{X(sc+9.4):.2f},{Y(0):.2f}Z'
o.append(f'<path class="terrs" d="{d}"/>')
for i in range(4):
    x0=X(sc-2.6+i*3)
    o.append(f'<rect class="shelfs" x="{x0:.2f}" y="{Y((i+1)*1.5):.2f}" width="0.45" height="1.5"/>')
    for k in range(1,5): o.append(f'<line class="books" x1="{x0:.2f}" y1="{Y(i*1.5+k*0.3):.2f}" x2="{x0+0.45:.2f}" y2="{Y(i*1.5+k*0.3):.2f}"/>')
    o.append(f'<line class="ledl" x1="{x0:.2f}" y1="{Y((i+1)*1.5)+0.05:.2f}" x2="{x0+0.45:.2f}" y2="{Y((i+1)*1.5)+0.05:.2f}"/>')
    o.append(person(X,Y,X(sc-2.6+i*3+1.8),(i+1)*1.5,1.2))
o.append(f'<line class="stairl" x1="{X(sc-2.6):.2f}" y1="{Y(0):.2f}" x2="{X(sc+9.4):.2f}" y2="{Y(6.0):.2f}"/>')
o.append(f'<rect class="f-desk" x="{X(sc-5.6):.2f}" y="{Y(1.05):.2f}" width="2" height="1.05"/>')
o.append(f'<rect class="f-term" x="{X(sc-7.0):.2f}" y="{Y(1.3):.2f}" width="0.6" height="1.3"/>')
for x in (X(4),X(10),X(sc-6.3),X(sc-4)): o.append(person(X,Y,x))
o.append(f'<text class="sl2" x="{X(sc+3.4):.2f}" y="{Y(7.0):.2f}" text-anchor="middle">лестница и террасы-стеллажи</text>')
o.append(f'<text class="sl2" x="{X(sc-6):.2f}" y="{Y(3.6):.2f}" text-anchor="middle">СБО</text>')
o.append(f'<text class="sl3" x="{X(ln.length*0.80):.2f}" y="{Y(16.4):.2f}" text-anchor="middle">«САНДЫҚ» — хранилище без окон</text>')
o.append(f'<text class="sl2" x="{X(0):.2f}" y="{Y(-2.2):.2f}" text-anchor="start">← главный вход, северо-запад</text>')
o.append(f'<text class="sl2" x="{X(ln.length):.2f}" y="{Y(-2.2):.2f}" text-anchor="end">юго-восток →</text>')
o.append('</svg>'); SECA=''.join(o)
# ---- cross section through lounge (a = la)
lineB=LineString([P(la,-200),P(la,200)]).intersection(LP)
sB=lineB.project(Point(P(la,0)))
o,X,Y,s0,s1,ln,VWb,VHb=section(lineB,'Поперечный разрез через гостиную и террасы',skip=('cat','terr','lounge'),clipw=(sB-26,sB+26))
def Xb(b): return X(sB+b)
# lounge: b from 1.6 to its outer edge (under gallery)
Lb=[toF(*q)[1] for q in BAND['atrL'].exterior.coords if abs(toF(*q)[0]-la)<40]
lb0,lb1=1.6,max(toF(*pp)[1] for pp in lineB.intersection(BAND['atrL']).coords)
o.append(f'<rect class="z-ru rm" x="{Xb(lb0):.2f}" y="{Y(5.65):.2f}" width="{lb1-lb0:.2f}" height="5.65"/>')
o.append(f'<path class="pitS" d="M{Xb(lb0):.2f},{Y(0):.2f} L{Xb(lb0+0.45):.2f},{Y(0):.2f} L{Xb(lb0+0.45):.2f},{Y(-0.22):.2f} L{Xb(lb0+0.9):.2f},{Y(-0.22):.2f} L{Xb(lb0+0.9):.2f},{Y(-0.45):.2f} L{Xb(lb1-0.9):.2f},{Y(-0.45):.2f} L{Xb(lb1-0.9):.2f},{Y(-0.22):.2f} L{Xb(lb1-0.45):.2f},{Y(-0.22):.2f} L{Xb(lb1-0.45):.2f},{Y(0):.2f} L{Xb(lb1):.2f},{Y(0):.2f} L{Xb(lb1):.2f},{Y(0.3):.2f} L{Xb(lb0):.2f},{Y(0.3):.2f}Z"/>')
for bb in (lb0+0.95,lb1-1.9):
    o.append(f'<rect class="cushS" x="{Xb(bb):.2f}" y="{Y(0.25):.2f}" width="0.95" height="0.7" rx="0.25"/>')
    o.append(f'<rect class="cushS" x="{Xb(bb+(0.0 if bb<lb1-2 else 0.65)):.2f}" y="{Y(0.95):.2f}" width="0.3" height="0.7" rx="0.12"/>')
mt=(lb0+lb1)/2
o.append(f'<rect class="woodS" x="{Xb(mt-1.2):.2f}" y="{Y(-0.05):.2f}" width="2.4" height="0.4"/>')
o.append(f'<rect class="potS" x="{Xb(mt+1.5):.2f}" y="{Y(0.15):.2f}" width="0.6" height="0.6"/><circle class="plantS" cx="{Xb(mt+1.8):.2f}" cy="{Y(1.9):.2f}" r="1.1"/>')
# shelving on the back wall of the lounge (under gallery) and on F2 gallery wall
o.append(f'<rect class="bshelfS" x="{Xb(lb1)-0.45:.2f}" y="{Y(5.4):.2f}" width="0.45" height="5.4"/>')
for k in range(1,14): o.append(f'<line class="books" x1="{Xb(lb1)-0.45:.2f}" y1="{Y(k*0.4):.2f}" x2="{Xb(lb1):.2f}" y2="{Y(k*0.4):.2f}"/>')
gB=max(toF(*pp)[1] for pp in lineB.intersection(GALP2).coords)
for side in (1,):
    o.append(f'<rect class="bshelfS" x="{Xb(gB)-0.45:.2f}" y="{Y(9.9):.2f}" width="0.45" height="3.6"/>')
    for k in range(1,9): o.append(f'<line class="books" x1="{Xb(gB)-0.45:.2f}" y1="{Y(6.35+k*0.4):.2f}" x2="{Xb(gB):.2f}" y2="{Y(6.35+k*0.4):.2f}"/>')
# glass railings at gallery edges F2
for bb in (toF(*lineB.intersection(AT).coords[0])[1],toF(*lineB.intersection(AT).coords[-1])[1]):
    o.append(f'<line class="rail" x1="{Xb(bb):.2f}" y1="{Y(6.35):.2f}" x2="{Xb(bb):.2f}" y2="{Y(7.45):.2f}"/>')
# stair & terrace at this a
zst=(la+2.6)/12*6
o.append(f'<rect class="f-stair" x="{Xb(-1.4):.2f}" y="{Y(zst):.2f}" width="3.0" height="{zst:.2f}"/>')
ti=min(3,int((la+2.6)//3)); zt=(ti+1)*1.5
bA=toF(*lineB.intersection(AT).coords[0])[1]; bA=min(bA,toF(*lineB.intersection(AT).coords[-1])[1])
o.append(f'<rect class="terrs" x="{Xb(bA):.2f}" y="{Y(zt):.2f}" width="{-1.4-bA:.2f}" height="{zt:.2f}"/>')
o.append(f'<rect class="shelfs" x="{Xb(bA):.2f}" y="{Y(zt+1.5):.2f}" width="{-1.4-bA:.2f}" height="1.5" opacity=".55"/>')
for x in (Xb(lb0+1.4),Xb(lb1-1.4)): o.append(person(X,Y,x,0.25,1.0))
o.append(person(X,Y,Xb(0.1),zst)); o.append(person(X,Y,Xb((bA-1.4)/2),zt,1.2))
o.append(f'<text class="sl2" x="{Xb(mt):.2f}" y="{Y(3.4):.2f}" text-anchor="middle">читальная гостиная −0,45</text>')
o.append(f'<text class="sl2" x="{Xb((bA-1.4)/2):.2f}" y="{Y(zt+2.6):.2f}" text-anchor="middle">террасы</text>')
o.append(f'<text class="sl2" x="{Xb(0.1):.2f}" y="{Y(zst+2.4):.2f}" text-anchor="middle">лестница</text>')
o.append(f'<text class="sl2" x="{Xb(gB)-3.6:.2f}" y="{Y(9.6):.2f}" text-anchor="end">стеллажи на галерее →</text>')
o.append('</svg>'); SECB=''.join(o)
json.dump(dict(APLAN=APLAN,SEC=SECA,SECB=SECB,LOUNGE=round(BAND['atrL'].area)),open('atr4.json','w'),ensure_ascii=False)
print('ok',round(la,1),round(lb,1),round(BAND['atrL'].area))
