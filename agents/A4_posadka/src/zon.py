import json, math
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
exec(open('geo.py').read().split("LK={")[0].replace("print(","(lambda *a,**k:None)("))
LP=Polygon(LIB); AT=Polygon(ATR); C=(LP.centroid.x,LP.centroid.y)
RING=LP.exterior; PER=RING.length
OUTD=12; GAL=3
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
# ---------------- FLOOR 1
R(1,'vest','Вестибюль, высота 6 м','x','om',('NW',33),('NW',43))
R(1,'cloak','Гардероб читателей, 1 860 мест','x','om',('NW',43),('NW',51.1))
R(1,'cloak','Гардероб читателей, 1 860 мест','x','mid',('NW',51.1),('W',13.5))
R(1,'lect','Лекционный зал, 150 мест','x','out',('NW',51.1),('W',13.5))
R(1,'abon','Абонемент: выдача и место ожидания','abon','out',('W',13.5),('S',27.5),1.8)
R(1,'abonF','Фонд абонементов','abon','mid',('W',13.5),('S',27.5))
R(1,'exped','Экспедиция, приёмка, комплектование и обработка','serv:proc','out',('S',27.5),('SE',5))
R(1,'scat','Служебный каталог, МБА','serv:scat','out',('SE',5),('SE',22))
R(1,'lab','Копирование и реставрация','serv:lab','mid',('S',27.5),('SE',40.5))
R(1,'st1','Основное хранение · отсек 1','store:main','out',('SE',22),('NE',6))
R(1,'st1','Основное хранение · отсек 1','store:main','mid',('SE',40.5),('NE',6))
R(1,'st2','Основное хранение · отсек 2','store:main','om',('NE',6),('NE',40.5))
R(1,'staff','Служебные: персонал, приём пищи, душевые; сотрудники хранения','serv:sp','out',('NE',40.5),('NW',24.1))
R(1,'st3','Основное хранение · отсек 3','store:main','mid',('NE',40.5),('NW',24.1))
R(1,'dir','Дирекция, бюро записи','serv:sp','out',('NW',24.1),('NW',33))
R(1,'bags','Портфели, охрана, пожарный пост','serv:bags','mid',('NW',24.1),('NW',33))
R(1,'galW','Фойе у атриума и лекционного зала (до контроля)','x','gal',('NW',37.6),('S',27.5))
R(1,'galE','Аванзал, пост контроля','avan','gal',('S',27.5),('NW',37.6),1.5)
R(1,'cat','Зал каталогов и СБО под фонарём атриума','cat','atr',None,None)
# ---------------- FLOOR 2
R(2,'u2a','Читальный зал учебный · юго-запад','readU','out',('W',13.5),('S',27.5),2.4)
R(2,'u2b','Читальный зал учебный · юг','readU','out',('S',27.5),('SE',40.5),2.4)
R(2,'s2a','Читальный зал научный · восток','readS','out',('SE',40.5),('NE',40.5),3.0)
R(2,'link','Холл перехода в ректорат, пункт выдачи','avan','out',('NE',40.5),('NW',4))
R(2,'g2','Групповые комнаты','group','out',('NW',4),('NW',24.1),2.2)
R(2,'g2','Групповые комнаты','group','out',('NW',24.1),('NW',51.1),2.2)
R(2,'av2','Медиатека, зал АВ-обслуживания','av','out',('NW',51.1),('W',13.5),5.0)
R(2,'oa2a','Открытый доступ · запад','store:oa','mid',('NW',51.1),('S',27.5))
R(2,'comp2','Компактное хранение · у книгоподъёмника','store:comp','mid',('S',27.5),('SE',40.5))
R(2,'oa2b','Открытый доступ · восток','store:oa','mid',('SE',40.5),('NE',40.5))
R(2,'oa2c','Открытый доступ · север','store:oa','mid',('NE',40.5),('NW',51.1))
R(2,'av2g','Аванзал (галерея атриума)','avan','gal',None,None,1.5)
# ---------------- FLOOR 3
R(3,'u3a','Читальный зал учебный · юго-запад','readU','out',('W',13.5),('S',27.5),2.4)
R(3,'s3a','Читальный зал научный · юг','readS','out',('S',27.5),('SE',40.5),3.0)
R(3,'s3b','Читальный зал научный · восток','readS','out',('SE',40.5),('NE',40.5),3.0)
R(3,'rare','Зал редких книг','av','out',('NE',40.5),('NW',24.1),5.0)
R(3,'s3c','Читальный зал научный · северо-запад','readS','out',('NW',24.1),('NW',51.1),3.0)
R(3,'g3','Групповые комнаты','group','out',('NW',51.1),('W',13.5),2.2)
R(3,'oa3a','Открытый доступ · запад','store:oa','mid',('NW',51.1),('S',27.5))
R(3,'comp3','Компактное хранение · у книгоподъёмника','store:comp','mid',('S',27.5),('SE',40.5))
R(3,'oa3b','Открытый доступ · восток','store:oa','mid',('SE',40.5),('NE',24))
R(3,'rareSt','Хранилище редких книг, без окон','av','mid',('NE',24),('NW',24.1))
R(3,'oa3c','Открытый доступ · север','store:oa','mid',('NW',24.1),('NW',51.1))
R(3,'av3g','Аванзал (галерея атриума)','avan','gal',None,None,1.5)
K=0.88
for r in ROOMS: r['a']=r['g'].area
tot={f:sum(r['a'] for r in ROOMS if r['f']==f) for f in (1,2,3)}
print('floor sums',{f:round(v) for f,v in tot.items()})
import collections
agg=collections.defaultdict(float)
for r in ROOMS: agg[r['row']]+=r['a']
for k,v in sorted(agg.items()): print(k,round(v),'net',round(v*K))
for r in ROOMS:
    if r['row']!='core': print(r['f'],r['k'],round(r['a']))
import pickle; pickle.dump(ROOMS,open('rooms.pkl','wb'))
