import pickle, json, math, collections
from shapely.geometry import Polygon, MultiPolygon
exec(open('zon4.py').read())
K=0.88
for r in ROOMS: r['a']=r['g'].area
# merge same (f,k)
M=collections.OrderedDict()
for r in ROOMS:
    key=(r['f'],r['k'])
    if key in M: M[key]['g']=M[key]['g'].union(r['g']); M[key]['a']+=r['a']
    else: M[key]=dict(r)
ROOMS=list(M.values())
RECT=[('R','rS','Научный читальный зал','readS',600,3.0),('R','rG','Групповые комнаты','group',150,2.2),('R','rV','Пункт выдачи по заказам','avan',50,None),('R','rW','Санузлы читателей','core',40,None),('R','rC','Аванзал, коридоры','cor',160,None)]
for f,k,n,row,a,nrm in []: ROOMS.append(dict(f=f,k=k,n=n,row=row,g=None,a=a,nrm=nrm))
def seats(r): return int(r['a']*K/r['nrm']+1e-6) if r['nrm'] and r['row'] not in('avan',) else 0
for r in ROOMS: r['m']=seats(r)
# rare storage & avfund no seats
for r in ROOMS:
    if r['k']=='rareSt': r['m']=0
ROWS=[('Абонемент (читатели 648 + сотрудники 30)',['abon'],678,678),('Аванзал (с пунктами выдачи)',['avan'],450,None),('Каталоги, сотрудники каталогов, СБО',['cat'],503,503),
('Учебные залы + открытый доступ (open space)',['readU','store:oa'],3528,3228),('Помещения групповых занятий',['group'],792,792),('Читальные залы научного отделения',['readS'],2700,2700),
('АВ-залы, крупноформатные, редкие книги',['av'],900,900),('Основное и компактное хранение (мобильные стеллажи)',['store:main','store:comp'],3150,1625),
('Сотрудники хранения, фонд АВ',['store:staff'],52,52),('МБА',['serv:mba'],78,78),('Комплектование и обработка',['serv:proc'],78,78),('Служебный каталог',['serv:scat'],112.5,112.5),
('Лаборатории копирования и реставрации',['serv:lab'],360,360),('Служебно-производственные (с дирекцией, персоналом)',['serv:sp'],540,540),('Портфели (в гардеробе)',['serv:bags'],90,None)]
P=collections.defaultdict(float)
for r in ROOMS: P[r['row']]+=r['a']*K
# scat row in plan contains МБА: split proportionally 112.5:78
sc=P['serv:scat']; P['serv:scat']=sc*112.5/190.5; P['serv:mba']=sc*78/190.5
def fm(x,d=0):
    s=f"{x:,.{d}f}".replace(',',' ').replace('.',','); return s
rows_html=[];TN=TP=TC=TRN=TRC=0
for nm,keys,norm,rn in ROWS:
    net=sum(P[k] for k in keys); c=min(net,norm); TN+=norm;TP+=net;TC+=c
    if rn: TRN+=rn; rc=min(net,rn); TRC+=rc; rp=round(100*net/rn); cl='ok' if rp>=95 else ('mid' if rp>=70 else 'low'); rps=f"{rp} %"
    else: cl='';rps='не обяз.'
    rows_html.append(f"<tr><td>{nm}</td><td class='n'>{fm(norm)}</td><td class='n'>{fm(rn) if rn else '—'}</td><td class='n'>{fm(net)}</td><td class='n {cl}'>{rps}</td></tr>")
rows_html.append(f"<tr class='tot'><td>Итого</td><td class='n'>{fm(TN)}</td><td class='n'>{fm(TRN)}</td><td class='n'>{fm(TP)}</td><td class='n'>{round(100*TRC/TRN)} %</td></tr>")
STOR=sum(P[k] for k in ('store:main','store:comp'))
seat=collections.defaultdict(int)
for r in ROOMS: seat[r['row']]+=r['m']
SEATS=dict(U=seat['readU'],S=seat['readS'],A=seat['av'],G=seat['group'],AB=seat['abon'])
print(SEATS, round(TC/TN*100), round(TRC/TRN*100))
# ---------- render
CLS={'abon':'z-abon','avan':'z-avan','cat':'z-cat','readU':'z-ru','group':'z-gr','readS':'z-rs','av':'z-av','store:main':'z-st','store:comp':'z-st','store:oa':'z-oa',
 'serv:mba':'z-sv','serv:proc':'z-sv','serv:scat':'z-sv','serv:lab':'z-sv','serv:sp':'z-sv','serv:bags':'z-sv','x':'z-x','core':'z-core','cor':'z-core','store:staff':'z-sv'}
SHORT={'vest':'Вестибюль','cloak':'Гардероб','lect':'Лекц. зал 150','abon':'Абонемент','abonF':'Фонд абон.','exped':'Экспедиция, обработка','scat':'Сл. каталог, МБА','staffS':'Персонал',
 'u1':'Научный зал','terr':'Террасы','lounge':'Гостиная','dir':'Дирекция, кабинеты','buf':'Буфет','galW':'Фойе','galE':'СБО','cat':'Каталоги и СБО',
 'u2a':'Учебная зона','u2b':'Научная зона','s2':'Научная зона','link':'Холл перехода','g2':'Групповые','u2c':'Учебная зона','oa2':'Открытый доступ','u2g':'Места у атриума',
 'st1':'Хранение 1','st5':'Хранение 5','lab':'Копир., оцифр., реставр.','st2':'Хранение 2','st3':'Хранение 3','st4':'Хранение 4','stf':'Сотр. хранения, фонд АВ','rareSt':'Хран. редких','rare':'Зал редких','av3':'Медиатека','st0':'Хранение 6','cor3':'Сл. коридор','st7':'Хранение 7'}
X0,X1,Y0,Y1=48,162,113,210
W=X1-X0;H=Y1-Y0
def pts(geom):
    gs=[geom] if geom.geom_type=='Polygon' else list(geom.geoms)
    d=''
    for g in gs:
        if g.is_empty or g.area<0.5: continue
        for ring in [g.exterior]+list(g.interiors):
            d+='M'+' L'.join(f"{x-X0:.2f},{Y1-y:.2f}" for x,y in ring.coords)+'Z '
    return d
def plan(f):
    o=[f'<svg class="plan" viewBox="0 0 {W} {H}" role="img" aria-label="План {f} этажа">',f'<rect class="ground" width="{W}" height="{H}"/>']
    if f in (2,3): o.append(f'<path class="void" d="{pts(AT)}"/>')
    if f==2: o.append(f'<path class="oa-dash" d="{pts(BAND["mid"])}"/>')
    for r in ROOMS:
        if r['f']!=f or r['g'] is None or r['g'].is_empty: continue
        c=CLS[r['row']]
        if r['row']=='core':
            c='z-st2' if r['k'].startswith('ЛК') else 'z-core'
        o.append(f'<path class="rm {c}" d="{pts(r["g"])}"><title>{r["n"]} — {fm(r["a"])} м²</title></path>')
    o.append(f'<path class="outline" d="{pts(LP)}"/>')
    if f in (2,3): o.append(f'<text class="vl" x="{AT.centroid.x-X0:.2f}" y="{Y1-AT.centroid.y:.2f}" text-anchor="middle">атриум</text>')
    for r in ROOMS:
        if r['f']!=f or r['g'] is None or r['g'].is_empty: continue
        if r['row']=='core':
            if r['k'].startswith('ЛК'):
                p=r['g'].centroid;o.append(f'<text class="lkl" x="{p.x-X0:.2f}" y="{Y1-p.y+0.6:.2f}" text-anchor="middle">{r["k"][3:]}</text>')
            continue
        g=r['g'];g=max(g.geoms,key=lambda q:q.area) if g.geom_type!='Polygon' else g
        p=g.representative_point() if r['k'] not in('galW','galE','u2g','cor3','cat','terr','lounge') else None
        if p is None:
            continue
        lab=SHORT.get(r['k'],r['k']);o.append(f'<text class="rl" x="{p.x-X0:.2f}" y="{Y1-p.y:.2f}" text-anchor="middle">{lab}<tspan class="ra" x="{p.x-X0:.2f}" dy="2.1">{fm(r["a"])} м²</tspan></text>')
    # markers
    def tri(e,s,cls,txt,d0=-1.2,d1=-6):
        a=pt(e,s,d1);b=pt(e,s,d0);o.append(f'<line class="{cls}" x1="{a[0]-X0:.2f}" y1="{Y1-a[1]:.2f}" x2="{b[0]-X0:.2f}" y2="{Y1-b[1]:.2f}" marker-end="url(#m{cls})"/>')
        t=pt(e,s,d1-2.2);o.append(f'<text class="ml {cls}t" x="{t[0]-X0:.2f}" y="{Y1-t[1]:.2f}" text-anchor="middle">{txt}</text>')
    if f==1:
        tri('NW',37.6,'am','главный вход');tri('SE',8,'as','служебный')
        p=pt('NW',37.6,24);o.append(f'<text class="ctl" x="{p[0]-X0:.2f}" y="{Y1-p[1]:.2f}" text-anchor="middle">▲ пост контроля</text>')
    if f==2:
        a=(126,205);b=(136,213);o.append(f'<line class="am" x1="{b[0]-X0:.2f}" y1="{Y1-b[1]:.2f}" x2="{a[0]-X0:.2f}" y2="{Y1-a[1]:.2f}" marker-end="url(#mam)"/>')
        o.append(f'<text class="ml amt" x="{137-X0:.2f}" y="{Y1-208.5:.2f}" text-anchor="start">в ректорат</text>')
    o.append(f'<g transform="translate({W-5},{6})"><path class="na" d="M0,-4 L1.6,2.4 L0,1.3 L-1.6,2.4z"/><text class="ml" y="-4.8" text-anchor="middle">С</text></g>')
    o.append('</svg>')
    return ''.join(o)
DEFS='<svg width="0" height="0" style="position:absolute"><defs><marker id="mam" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0L10,5L0,10z" class="mkm"/></marker><marker id="mas" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0L10,5L0,10z" class="mks"/></marker></defs></svg>'
# room lists
def lst(f):
    rs=[r for r in ROOMS if r['f']==f and r['row'] not in('core',)]
    h=''.join(f"<tr><td>{r['n']}</td><td class='n'>{fm(r['a'])}</td><td class='n'>{r['m'] or ''}</td></tr>" for r in rs)
    cs=sum(r['a'] for r in ROOMS if r['f']==f and r['row'] in('core',))
    tot=sum(r['a'] for r in ROOMS if r['f']==f)
    h+=f"<tr><td>ЛК, лифты, книгоподъёмники, санузлы</td><td class='n'>{fm(cs)}</td><td></td></tr>"
    h+=f"<tr class='tot'><td>Итого по этажу</td><td class='n'>{fm(tot)}</td><td class='n'>{sum(r['m'] for r in rs)}</td></tr>"
    return h
json.dump(dict(P1=plan(1),P2=plan(2),P3=plan(3),DEFS=DEFS,T26=''.join(rows_html),L1=lst(1),L2=lst(2),L3=lst(3),LR=lst('R'),SEATS=SEATS,
  TC=round(100*TC/TN),TRC=round(100*TRC/TRN),TRN=fm(TRN),TP=fm(TP),TN=fm(TN),STOR=round(STOR),CAP=round(STOR/1625*1.5,2)),open('zsv4.json','w'),ensure_ascii=False)
