const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.argv[2]);
const r=await p.evaluate(()=>blocks("V1").filter(b=>(b.in||b.c)==="LIB").map(b=>({f:b.f,z:b.z,k:b.k[0],n:b.n,p:b.p||"",a:geom(b).area,u:b.u,v:b.v})));
console.log(JSON.stringify(r));await b.close();})();
