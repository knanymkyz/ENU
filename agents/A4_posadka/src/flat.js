const B=require("./blocks.json");const fs=require("fs");
const map={};for(const b of B)map[b.name]=b;
const out=[];
function bulgePts(v,closed){const r=[];const n=v.length;for(let i=0;i<n;i++){const a=v[i];r.push([a.x,a.y]);if(!closed&&i==n-1)break;const b=v[(i+1)%n];const bu=a.bulge||0;if(Math.abs(bu)>1e-6){const th=4*Math.atan(bu);const dx=b.x-a.x,dy=b.y-a.y,c=Math.hypot(dx,dy);const nx=-dy/c,ny=dx/c;const k=(c/2)*(1-bu*bu)/(2*bu);const cx=(a.x+b.x)/2+nx*k,cy=(a.y+b.y)/2+ny*k;const R=Math.hypot(a.x-cx,a.y-cy);const a0=Math.atan2(a.y-cy,a.x-cx);const N=10;for(let j=1;j<N;j++){const t=a0+th*j/N;r.push([cx+R*Math.cos(t),cy+R*Math.sin(t)])}}}return r}
function T(m,p){return [m[0]*p[0]+m[1]*p[1]+m[2], m[3]*p[0]+m[4]*p[1]+m[5]]}
function mul(A,Bm){return [A[0]*Bm[0]+A[1]*Bm[3],A[0]*Bm[1]+A[1]*Bm[4],A[0]*Bm[2]+A[1]*Bm[5]+A[2],A[3]*Bm[0]+A[4]*Bm[3],A[3]*Bm[1]+A[4]*Bm[4],A[3]*Bm[2]+A[4]*Bm[5]+A[5]]}
function walk(name,m,path,depth){const b=map[name];if(!b||depth>6)return;const bp=b.basePoint||{x:0,y:0};
 for(const e of b.entities||[]){
  if(e.type=="INSERT"){const r=e.rotation||0,sx=e.xScale||1,sy=e.yScale||sx,p=e.insertionPoint;const sub=map[e.name];const bb=(sub&&sub.basePoint)||{x:0,y:0};
    const M=[Math.cos(r)*sx,-Math.sin(r)*sy,p.x,Math.sin(r)*sx,Math.cos(r)*sy,p.y];const M2=mul(M,[1,0,-bb.x,0,1,-bb.y]);walk(e.name,mul(m,M2),path+"/"+e.name,depth+1);continue}
  let polys=[];
  if(e.type=="LWPOLYLINE")polys.push({c:!!(e.flag&513),p:bulgePts(e.vertices,!!(e.flag&513))});
  if(e.type=="LINE")polys.push({c:false,p:[[e.startPoint.x,e.startPoint.y],[e.endPoint.x,e.endPoint.y]]});
  if(e.type=="HATCH")for(const bp of e.boundaryPaths||[])if(bp.vertices)polys.push({c:true,h:1,p:bulgePts(bp.vertices,true)});
  for(const q of polys)out.push({b:path,l:e.layer,t:e.type,c:q.c,h:q.h,p:q.p.map(pt=>T(m,pt))});
  if((e.type=="TEXT"||e.type=="MTEXT")&&e.insertionPoint)out.push({b:path,l:e.layer,t:"TX",txt:(e.text||"").replace(/\{[^;]*;|\}|\\[A-Za-z][^;]*;/g,""),p:[T(m,[e.insertionPoint.x,e.insertionPoint.y])]});
 }}
walk("*Model_Space",[1,0,0,0,1,0],"MS",0);
const cx=+process.argv[2],cy=+process.argv[3],R=+process.argv[4];
const sel=out.filter(o=>o.p.some(q=>Math.abs(q[0]-cx)<R&&Math.abs(q[1]-cy)<R));
fs.writeFileSync("near.json",JSON.stringify(sel));console.log(out.length,sel.length);
const c={};for(const o of sel){const k=o.b+"|"+o.l+"|"+o.t;c[k]=(c[k]||0)+1}console.log(c);
