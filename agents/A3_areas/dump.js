const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://'+process.argv[2]);await p.waitForTimeout(300);
const r=await p.evaluate(()=>blocks("V1").filter(b=>!b.bad&&b.c==="LIB").map(b=>({f:b.f,z:b.z,k:b.k.join("+"),n:b.n,s:b.s,p:b.p||"",a:+geom(b).area.toFixed(2),nl:!!b.nl})));
require('fs').writeFileSync(process.argv[3],JSON.stringify(r));console.log(r.length);await b.close();})();
