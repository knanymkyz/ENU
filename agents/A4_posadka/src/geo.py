import json, math
OX,OY=679500,5668400
V=[(73.51,128.00,0),(117.07,118.68,.277),(121.94,120.34,0),(152.42,156.40,.340),(152.71,162.49,0),(125.82,201.12,.414),(118.86,202.36,0),(57.10,159.38,.400),(55.72,152.62,0),(69.57,130.50,.248)]
def arcpts(a,b,bu,N=8):
    th=4*math.atan(bu);dx,dy=b[0]-a[0],b[1]-a[1];c=math.hypot(dx,dy);nx,ny=-dy/c,dx/c;k=(c/2)*(1-bu*bu)/(2*bu)
    cx,cy=(a[0]+b[0])/2+nx*k,(a[1]+b[1])/2+ny*k;R=math.hypot(a[0]-cx,a[1]-cy);a0=math.atan2(a[1]-cy,a[0]-cx)
    return [(cx+R*math.cos(a0+th*j/N),cy+R*math.sin(a0+th*j/N)) for j in range(1,N)]
LIB=[]
for i,(x,y,bu) in enumerate(V):
    LIB.append((x,y)); n=V[(i+1)%10]
    if bu: LIB+=arcpts((x,y),(n[0],n[1]),bu)
def area(P): return abs(sum(P[i][0]*P[(i+1)%len(P)][1]-P[(i+1)%len(P)][0]*P[i][1] for i in range(len(P)))/2)
print('area',round(area(LIB),1))
E={'S':(0,1),'SE':(2,3),'NE':(4,5),'NW':(6,7),'W':(8,9)}
def edge(nm):
    a,b=E[nm];A=V[a][:2];B=V[b][:2];L=math.hypot(B[0]-A[0],B[1]-A[1]);u=((B[0]-A[0])/L,(B[1]-A[1])/L);n=(-u[1],u[0]);return A,u,n,L
def pt(nm,s,d=0):
    A,u,n,L=edge(nm);return (A[0]+u[0]*s+n[0]*d,A[1]+u[1]*s+n[1]*d)
def box(nm,s0,s1,d0,d1):
    return [pt(nm,s0,d0),pt(nm,s1,d0),pt(nm,s1,d1),pt(nm,s0,d1)]
for k in E: print(k,round(edge(k)[3],2))
# centroid
cx=sum(p[0] for p in LIB)/len(LIB);cy=sum(p[1] for p in LIB)/len(LIB)
A=0;Cx=0;Cy=0
for i in range(len(LIB)):
    x0,y0=LIB[i];x1,y1=LIB[(i+1)%len(LIB)];c=x0*y1-x1*y0;A+=c;Cx+=(x0+x1)*c;Cy+=(y0+y1)*c
Cx/=3*A;Cy/=3*A;print('centroid',round(Cx,1),round(Cy,1))
ATR=[(Cx+(x-Cx)*0.3,Cy+(y-Cy)*0.3) for x,y in LIB];print('atrium',round(area(ATR)))
LK={ 'ЛК-1':('S',7), 'ЛК-2':('NW',37), 'ЛК-3':('NE',40), 'ЛК-4':('SE',40), 'ЛК-5':('SE',7)}
LKB={k:box(e,s-4.5,s+4.5,0.3,4.8) for k,(e,s) in LK.items()}
DOOR={k:pt(e,s,4.8) for k,(e,s) in LK.items()}
OUT={k:pt(e,s,0) for k,(e,s) in LK.items()}
names=list(LK)
for i in range(5):
    a,b=names[i],names[(i+1)%5];print(a,b,round(math.dist(DOOR[a],DOOR[b]),1))
def inside(P,x,y):
    c=False;n=len(P)
    for i in range(n):
        x0,y0=P[i];x1,y1=P[(i+1)%n]
        if (y0>y)!=(y1>y) and x<(x1-x0)*(y-y0)/(y1-y0)+x0: c=not c
    return c
mx=0;arg=None
for gx in range(50,160):
    for gy in range(115,207):
        x,y=gx+.5,gy+.5
        if inside(LIB,x,y) and not inside(ATR,x,y):
            d=min(math.dist((x,y),DOOR[k]) for k in names)
            if d>mx: mx=d;arg=(x,y,min(names,key=lambda k:math.dist((x,y),DOOR[k])))
print('max to nearest LK door',round(mx,1),arg)
json.dump(dict(LIB=LIB,ATR=ATR,LKB=LKB,DOOR=DOOR,OUT=OUT,FAR=arg,FARD=mx,C=(Cx,Cy)),open('geo.json','w'))
