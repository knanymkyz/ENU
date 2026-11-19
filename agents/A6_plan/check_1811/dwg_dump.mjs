import { Dwg_File_Type, LibreDwg } from '@mlightcad/libredwg-web';
import fs from 'fs';
const lib = await LibreDwg.create(new URL('./node_modules/@mlightcad/libredwg-web/wasm/', import.meta.url).pathname);
const buf = fs.readFileSync(process.argv[2]);
const dwg = lib.dwg_read_data(buf, Dwg_File_Type.DWG);
const db = lib.convert(dwg);
const ents = db.entities || [];
const cnt = {};
for (const e of ents) { const k = e.type + '|' + e.layer; cnt[k] = (cnt[k] || 0) + 1; }
console.log('entities', ents.length);
console.log(Object.entries(cnt).sort((a,b)=>b[1]-a[1]).slice(0,40));
const blocks = db.tables?.BLOCK_RECORD?.entries || [];
console.log('blocks', blocks.length, blocks.slice(0,15).map(b=>b.name+':'+(b.entities||[]).length));
fs.writeFileSync(process.argv[3], JSON.stringify({ents, blocks: blocks.map(b=>({name:b.name, basePoint:b.basePoint, entities:b.entities}))}, (k,v)=> typeof v==="bigint"? Number(v): v));
