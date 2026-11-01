const {chromium}=require('playwright');
(async()=>{const f=process.argv[2],out=process.argv[3]||'.';
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1700,height:1150}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 for(const fl of (process.argv[4]||'1,2,3,4').split(',')){
  await p.goto('file://'+f+'#v=V1&f='+fl+'&legend=0&cols=0');await p.waitForTimeout(400);
  await p.evaluate((FLR)=>{S.f=FLR;const bb=bbox(SP.LIB);const r=stage.getBoundingClientRect();const pad=9;let w=bb[2]-bb[0]+2*pad,h=bb[3]-bb[1]+2*pad;const k=Math.max(w/r.width,h/r.height);VB={x:bb[0]-pad-(r.width*k-w)/2,y:bb[1]-pad-(r.height*k-h)/2,w:r.width*k,h:r.height*k};render();},fl);await p.waitForTimeout(200);
  await p.screenshot({path:`${out}/f${fl}.png`});}
 const r=await p.evaluate(()=>{const r=selfCheck("V1");const all=blocks("V1").filter(b=>!b.bad),pg={},zs={};
   for(const b of all){const a=geom(b).area;if(b.p)pg[b.p]=(pg[b.p]||0)+a;const k=(b.in||b.c)+b.f;}
   const fl={};for(const b of all){const k=(b.in||b.c)+' '+b.f;fl[k]=(fl[k]||0)+geom(b).area;}
   return {e:r.errors.map(x=>x.t),w:r.warnings.map(x=>x.t),cov:r.coverage.map(c=>c.c+c.f+':'+c.pct.toFixed(1)),pg:Object.fromEntries(Object.entries(pg).map(([k,v])=>[k,Math.round(v)+' net≈'+Math.round(v*.88)+' / '+PROG[k].a[0]]))};});
 console.log(JSON.stringify(r,null,1));console.log('JSERR',errs);await b.close();})();
