const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+process.argv[2]);
console.log(await p.evaluate(()=>{const o=[];const zs={};for(const b of blocks("V1")){const a=geom(b).area;zs[b.f+" "+b.z]=(zs[b.f+" "+b.z]||0)+a;o.push(`${b.f} | ${b.z} | ${b.n} | ${Math.round(a)}`);}
 return o.join("\n")+"\n\n"+Object.entries(zs).map(([k,v])=>k+": "+Math.round(v)).join("\n");}));await b.close();})();
