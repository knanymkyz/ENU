import json, math
exec(open('geo.py').read().split("LK={")[0].replace("print(","(lambda *a,**k:None)("))
S=json.load(open('near.json'))
def loc(p): return [(x-OX,y-OY) for x,y in p]
def bb(p): xs=[a for a,b in p];ys=[b for a,b in p];return min(xs),max(xs),min(ys),max(ys)
feat={'road':[], 'bike':[], 'plaza':[], 'walk':[], 'bld':[], 'link':None,'blue':None}
for q in S:
    if q['t']=='TX': continue
    p=loc(q['p']);x0,x1,y0,y1=bb(p)
    if q['l']=='ZAL_ROAD': feat['road'].append((p,True))
    elif q['l']=='0_вело': feat['bike'].append((p,False))
    elif q['l']=='CONTOUR':
        if x0<-90 and x1>200 and y1>390: feat['plaza'].append((p,q['c']))
        else: feat['walk'].append((p,q['c']))
    elif 'extieuvbn' in q['b'] and q['l']=='0':
        if abs(x0-55)<2 and abs(y1-203)<2: continue
        if abs(x0-119)<2 and abs(y1-217)<2: feat['link']=p; continue
        if abs(x0-133)<2 and abs(y1-274)<2: feat['blue']=p
        feat['bld'].append((p,q['c']))
def ptsY(p,Y): return " ".join(f"{x:.2f},{Y-y:.2f}" for x,y in p)
def poly(p,cls,Y,closed=True): return f'<{"polygon" if closed else "polyline"} class="{cls}" points="{ptsY(p,Y)}"/>'
def inside(P,x,y):
    c=False;n=len(P)
    for i in range(n):
        x0,y0=P[i];x1,y1=P[(i+1)%n]
        if (y0>y)!=(y1>y) and x<(x1-x0)*(y-y0)/(y1-y0)+x0: c=not c
    return c
# ---------- LK config
LK={'ЛК-1':('W',18),'ЛК-2':('NW',55.6),'ЛК-3':('NW',19.6),'ЛК-4':('NE',36),'ЛК-5':('SE',36),'ЛК-6':('S',38)}
LKB={k:box(e,s-4.5,s+4.5,0.3,4.8) for k,(e,s) in LK.items()}
DOOR={k:pt(e,s,4.8) for k,(e,s) in LK.items()}
names=list(LK)
SP=[(names[i],names[(i+1)%6],math.dist(DOOR[names[i]],DOOR[names[(i+1)%6]])) for i in range(6)]
mx=0;far=None
for gx in range(50,160):
    for gy in range(115,207):
        x,y=gx+.5,gy+.5
        if inside(LIB,x,y) and not inside(ATR,x,y):
            k=min(names,key=lambda k:math.dist((x,y),DOOR[k]));d=math.dist((x,y),DOOR[k])
            if d>mx: mx=d;far=(x,y,k)
print('spacing',[(a,b,round(d,1)) for a,b,d in SP],'max',round(mx,1),far)
# ---------- SITUATION svg  window
X0,X1,Y0,Y1=-115,300,10,330
W=X1-X0;H=Y1-Y0
def T(p): return [(x-X0,y) for x,y in p]
Ysvg=Y1
o=[f'<svg class="plan" viewBox="0 0 {W} {H}" role="img" aria-label="Ситуационная схема"><defs><clipPath id="cs"><rect width="{W}" height="{H}"/></clipPath>'
   '<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" class="mk"/></marker>'
   '<marker id="ahs" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" class="mks"/></marker>'
   '<marker id="ahp" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" class="mkp"/></marker></defs><g clip-path="url(#cs)">']
o.append(f'<rect class="ground" width="{W}" height="{H}"/>')
for p,c in feat['road']: o.append(poly(T(p),'road',Ysvg))
for p,c in feat['plaza']: o.append(poly(T(p),'plaza',Ysvg,c))
for p,c in feat['walk']: o.append(poly(T(p),'walk',Ysvg,c))
for p,c in feat['bike']: o.append(poly(T(p),'bike',Ysvg,False))
for p,c in feat['bld']: o.append(poly(T(p),'bld',Ysvg,c))
o.append(poly(T(feat['link']),'bld',Ysvg))
o.append(poly(T(LIB),'lib',Ysvg))
def tx(x,y,s,cls='lbl',anchor='middle',rot=0):
    r=f' transform="rotate({rot} {x-X0:.1f} {Ysvg-y:.1f})"' if rot else ''
    return f'<text class="{cls}" x="{x-X0:.1f}" y="{Ysvg-y:.1f}" text-anchor="{anchor}"{r}>{s}</text>'
def arrow(p,cls,mk):
    return f'<polyline class="{cls}" points="{ptsY(T(p),Ysvg)}" marker-end="url(#{mk})"/>'
o.append(tx(-40,62,'ул. А123','road-l',rot=12))
o.append(tx(60,300,'центральная площадь','core-l'))
o.append(tx(60,290,'(ядро кампуса)','small'))
o.append(tx(105,160,'БИБЛИОТЕКА','lib-l'))
o.append(tx(105,151,'3 эт. · 5 012 м²','small'))

o.append(tx(-20,195,'корпус 2 эт.','small'))
# arrows
mainE=pt('NW',37.6,0)
o.append(arrow([(62,262),(70,215),(mainE[0]-4,mainE[1]+5)],'a-main','ah'))
o.append(arrow([(20,95),(36,135),(48,166),(mainE[0]-6,mainE[1]+2)],'a-main','ah'))
o.append(tx(10,88,'от остановки / дороги','small','start'))
o.append(arrow([(131,86),(131,104),(128,112)],'a-serv','ahs'))
o.append(tx(137,95,'съезд с дороги → служебный двор','small','start'))
o.append(tx(141,205,'переход на 2 эт.','small','start'));o.append(tx(160,262,'ректорат: 1 000 м² библиотеке','small'))
# north arrow
o.append(f'<g transform="translate({W-22},{24})"><path class="na" d="M0,-12 L5,8 L0,4 L-5,8z"/><text class="lbl" y="-15" text-anchor="middle">С</text></g>')
o.append(f'<g transform="translate({W-90},{H-12})"><rect class="sb" width="25" height="2.5"/><rect class="sb2" x="25" width="25" height="2.5"/><text class="small" x="0" y="-3">0</text><text class="small" x="50" y="-3" text-anchor="middle">50 м</text></g>')
o.append('</g></svg>')
SIT="".join(o)
# ---------- BUILDING svg
X0,X1,Y0,Y1=36,178,96,228
W=X1-X0;H=Y1-Y0;Ysvg=Y1
def T(p): return [(x-X0,y) for x,y in p]
o=[f'<svg class="plan" viewBox="0 0 {W} {H}" role="img" aria-label="Схема входов и эвакуационных лестниц"><defs><clipPath id="cb"><rect width="{W}" height="{H}"/></clipPath>'
   '<marker id="bh" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" class="mk"/></marker>'
   '<marker id="bhs" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" class="mks"/></marker>'
   '<marker id="bhl" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" class="mkl"/></marker></defs><g clip-path="url(#cb)">']
o.append(f'<rect class="ground" width="{W}" height="{H}"/>')
for p,c in feat['walk']+feat['plaza']: o.append(poly(T(p),'walk',Ysvg,c))
for p,c in feat['bld']: o.append(poly(T(p),'bld',Ysvg,c))
o.append(poly(T(feat['link']),'bld',Ysvg))
# forecourt + service yard
fc=[pt('NW',24,0),pt('NW',51.2,0),pt('NW',51.2,-15),pt('NW',24,-15)]
o.append(poly(T(fc),'fore',Ysvg))
yd=[pt('S',28,0),V[1][:2],V[2][:2],pt('SE',16,0),pt('SE',16,-14),pt('S',28,-16)]
o.append(poly(T(yd),'yard',Ysvg))
o.append(poly(T(LIB),'lib2',Ysvg))
o.append(poly(T(ATR),'atr',Ysvg))
def tx(x,y,s,cls='lbl',anchor='middle',rot=0):
    r=f' transform="rotate({rot:.1f} {x-X0:.2f} {Ysvg-y:.2f})"' if rot else ''
    return f'<text class="{cls}" x="{x-X0:.2f}" y="{Ysvg-y:.2f}" text-anchor="{anchor}"{r}>{s}</text>'
def line(a,b,cls,mk=None):
    m=f' marker-end="url(#{mk})"' if mk else ''
    return f'<line class="{cls}" x1="{a[0]-X0:.2f}" y1="{Ysvg-a[1]:.2f}" x2="{b[0]-X0:.2f}" y2="{Ysvg-b[1]:.2f}"{m}/>'
C=(sum(p[0] for p in ATR)/len(ATR),sum(p[1] for p in ATR)/len(ATR))
o.append(tx(C[0],C[1]+1,'АТРИУМ','atr-l'));o.append(tx(C[0],C[1]-2.6,'≈450 м²','tiny'))
# distances between LK doors
for a,b,d in SP:
    A,B=DOOR[a],DOOR[b];o.append(line(A,B,'dist'))
    m=((A[0]+B[0])/2,(A[1]+B[1])/2);ang=-math.degrees(math.atan2(B[1]-A[1],B[0]-A[0]))
    if ang>90: ang-=180
    if ang<-90: ang+=180
    o.append(tx(m[0],m[1]+0.9,f'{d:.0f} м','dist-l',rot=ang))
# LK boxes
for k,(e,s) in LK.items():
    o.append(poly(T(LKB[k]),'lk',Ysvg))
    c=pt(e,s,2.55);A,u,n,L=edge(e);ang=-math.degrees(math.atan2(u[1],u[0]))
    if ang>90: ang-=180
    if ang<-90: ang+=180
    o.append(tx(c[0],c[1]-0.8,k,'lk-l',rot=ang))
    o.append(line(pt(e,s,0.3),pt(e,s,-4.5),'exit','bhl'))
# lifts
lb=box('NW',45,50,11,17);o.append(poly(T(lb),'lift',Ysvg));c=pt('NW',47.5,14);o.append(tx(c[0],c[1]-0.8,'лифты','tiny'))
c=pt('NW',37.6,12);o.append(tx(c[0],c[1],'вестибюль 6 м','tiny'));c=pt('NW',37.6,9.6);o.append(tx(c[0],c[1],'ось → атриум','tiny'))
sb=box('S',28,33,0.3,4.8);o.append(poly(T(sb),'lift',Ysvg));c=pt('S',30.5,2.5);o.append(tx(c[0],c[1]-0.8,'гр.','tiny'))
# entrances
me=pt('NW',37.6,0);o.append(poly(T(box('NW',31.6,43.6,0.3,5)),'tamb',Ysvg))
o.append(line(pt('NW',37.6,-12),pt('NW',37.6,-0.8),'a-main','bh'))
c=pt('NW',37.6,-16.5);o.append(tx(c[0],c[1],'ГЛАВНЫЙ ВХОД','main-l'))

c=pt('NW',37.6,2.7);o.append(tx(c[0],c[1]-0.8,'тамбур','tiny',rot=-math.degrees(math.atan2(edge('NW')[1][1],edge('NW')[1][0]))-180))
# link entrance
lm=(129.5,206.5);o.append(line((136,213),(124.2,204.0),'a-main2','bh'))
o.append(tx(140,216,'переход в ректорат, 2 эт.','main-l2','start'))
o.append(tx(140,212.6,'+6,000 · под ним проезд ≥ 4,5 м','tiny','start'))
# service
o.append(line(pt('SE',8,-13),pt('SE',8,-0.8),'a-serv','bhs'))
o.append(poly(T(box('SE',3,13,0.3,6)),'dock',Ysvg))
c=pt('SE',8,3.1);ang=-math.degrees(math.atan2(edge('SE')[1][1],edge('SE')[1][0]))
o.append(tx(c[0],c[1]-0.8,'приёмка','tiny',rot=ang))
c=pt('SE',8,-17);o.append(tx(c[0]+1,c[1],'СЛУЖЕБНЫЙ ВХОД','serv-l'))
c=pt('SE',8,-20);o.append(tx(c[0]+1,c[1],'разгрузка книг, персонал','tiny'))
o.append(line((131,98),(126,112),'a-serv','bhs'));o.append(tx(131,99.5-2,'от дороги','tiny','start'))
# facade lengths
for nm,lab,off in [('S','44,6',-3.2),('SE','47,2',-3.2),('NE','47,1',-3.2),('NW','75,2',-3.2),('W','26,1',-3.4)]:
    A,u,n,L=edge(nm);c=pt(nm,L/2 if nm!='NW' else 8,off);ang=-math.degrees(math.atan2(u[1],u[0]))
    if ang>90: ang-=180
    if ang<-90: ang+=180
    o.append(tx(c[0],c[1]-0.7,lab+' м','dim',rot=ang))
# far point
fx,fy,fk=far;o.append(f'<circle class="far" cx="{fx-X0:.2f}" cy="{Ysvg-fy:.2f}" r="0.9"/>');o.append(line((fx,fy),DOOR[fk],'farl'))
o.append(tx(fx+1.5,fy-3,f'самая дальняя точка: {mx:.0f} м до {fk}','tiny','start'))
o.append(f'<g transform="translate({W-8},{9})"><path class="na" d="M0,-5 L2,3 L0,1.6 L-2,3z"/><text class="tiny" y="-6.2" text-anchor="middle">С</text></g>')
o.append(f'<g transform="translate({4},{H-5})"><rect class="sb" width="10" height="1"/><rect class="sb2" x="10" width="10" height="1"/><text class="tiny" x="0" y="-1.4">0</text><text class="tiny" x="20" y="-1.4" text-anchor="middle">20 м</text></g>')
o.append('</g></svg>')
BLD="".join(o)
json.dump(dict(SIT=SIT,BLD=BLD,SP=[(a,b,round(d,1)) for a,b,d in SP],MAX=round(mx,1),FARK=far[2]),open('svgs.json','w'),ensure_ascii=False)
