import json
L=75.24; PAD=8; H=15.6; VW=L+2*PAD; VH=24
def X(s): return PAD+(L-s)          # вид с площади: слева запад (s=75), справа север (s=0)
def Y(z): return VH-3-z
o=[f'<svg class="plan" viewBox="0 0 {VW:.1f} {VH}" role="img" aria-label="Северо-западный фасад: концепция">',
'<defs><pattern id="oyu" width="2.4" height="2.4" patternUnits="userSpaceOnUse">'
'<rect width="2.4" height="2.4" class="sd-bg"/>'
'<path class="sd-orn" d="M1.2,0.25 L2.15,1.2 L1.2,2.15 L0.25,1.2Z M1.2,0.75 C1.55,0.75 1.65,1.05 1.45,1.2 M1.2,1.65 C0.85,1.65 0.75,1.35 0.95,1.2 M0.75,1.2 C0.75,0.85 1.05,0.75 1.2,0.95 M1.65,1.2 C1.65,1.55 1.35,1.65 1.2,1.45"/>'
'<circle class="sd-dot" cx="0" cy="0" r="0.12"/><circle class="sd-dot" cx="2.4" cy="0" r="0.12"/><circle class="sd-dot" cx="0" cy="2.4" r="0.12"/><circle class="sd-dot" cx="2.4" cy="2.4" r="0.12"/>'
'</pattern></defs>',
f'<rect class="ground" width="{VW:.1f}" height="{VH}"/>',
f'<rect class="earth" x="0" y="{Y(0):.2f}" width="{VW:.1f}" height="3"/>']
# glass base
o.append(f'<rect class="gl" x="{X(L):.2f}" y="{Y(10.5):.2f}" width="{L:.2f}" height="10.5"/>')
o.append(f'<rect class="slabe" x="{X(L):.2f}" y="{Y(6.0):.2f}" width="{L:.2f}" height="0.35"/>')
s=0.0
while s<=L+0.01:
    o.append(f'<line class="mul" x1="{X(s):.2f}" y1="{Y(0):.2f}" x2="{X(s):.2f}" y2="{Y(10.5):.2f}"/>'); s+=1.5
s=0.0
while s<=L+0.01:
    o.append(f'<rect class="fin" x="{X(s)-0.15:.2f}" y="{Y(10.5):.2f}" width="0.3" height="10.5"/>'); s+=3.0
# entrance portal (centre) — recess with tall glazing
e0,e1=31.6,43.6
o.append(f'<rect class="portal" x="{X(e1):.2f}" y="{Y(10.5):.2f}" width="{e1-e0:.2f}" height="10.5"/>')
for k in range(1,8):
    xx=X(e1)+k*(e1-e0)/8; o.append(f'<line class="mul2" x1="{xx:.2f}" y1="{Y(0):.2f}" x2="{xx:.2f}" y2="{Y(10.5):.2f}"/>')
o.append(f'<rect class="door" x="{X(39.6):.2f}" y="{Y(3.2):.2f}" width="4" height="3.2"/>')
# сандық (3 этаж) with cantilever shadow
o.append(f'<rect class="shadow" x="{X(L)-1.5:.2f}" y="{Y(10.5):.2f}" width="{L+3:.2f}" height="0.45"/>')
o.append(f'<rect class="orn" x="{X(L)-1.5:.2f}" y="{Y(H):.2f}" width="{L+3:.2f}" height="{H-10.5:.2f}" fill="url(#oyu)"/>')
o.append(f'<rect class="sd-frame" x="{X(L)-1.5:.2f}" y="{Y(H):.2f}" width="{L+3:.2f}" height="{H-10.5:.2f}"/>')
# stair towers flanking entrance
for sc in (19.6,55.6):
    o.append(f'<rect class="tower" x="{X(sc+4.5):.2f}" y="{Y(H+1.2):.2f}" width="9" height="{H+1.2:.2f}"/>')
    o.append(f'<rect class="tower-sl" x="{X(sc+0.6):.2f}" y="{Y(H-1):.2f}" width="1.2" height="{H-3:.2f}"/>')
# people
def person(x):
    return f'<g class="person"><circle cx="{x:.2f}" cy="{Y(1.63):.2f}" r="0.13"/><line x1="{x:.2f}" y1="{Y(1.5):.2f}" x2="{x:.2f}" y2="{Y(0.8):.2f}"/><line x1="{x:.2f}" y1="{Y(0.8):.2f}" x2="{x-0.2:.2f}" y2="{Y(0):.2f}"/><line x1="{x:.2f}" y1="{Y(0.8):.2f}" x2="{x+0.2:.2f}" y2="{Y(0):.2f}"/></g>'
for s_ in (36,38.5,41,47,29,12,63):
    o.append(person(X(s_)))
# labels
def T(x,y,t,c='el',a='middle'): o.append(f'<text class="{c}" x="{x:.2f}" y="{y:.2f}" text-anchor="{a}">{t}</text>')
T(X(L)-1.5,Y(H+2.9),'«сандық»: хранилище без окон, металл с орнаментом ою-өрнек','el','start')
T(X(37.6),Y(-1.6),'главный вход: портал на всю высоту основания, 10,5 м')
T(X(70),Y(-1.6),'запад','el2'); T(X(4),Y(-1.6),'север','el2')
T(X(19.6),Y(H+1.8),'ЛК-3','el2'); T(X(55.6),Y(H+1.8),'ЛК-2','el2')
for z,lab in ((0,'±0,000'),(6.0,'+6,000'),(10.5,'+10,500'),(15.6,'+15,600')):
    T(X(L)-2.2,Y(z)+0.4,lab,'lv','end')
o.append('</svg>')
json.dump(dict(ELEV=''.join(o)),open('elev3.json','w'),ensure_ascii=False)
