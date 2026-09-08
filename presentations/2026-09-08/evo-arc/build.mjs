process.on('uncaughtException', e=>{console.error(e.stack?.split('\n').filter(x=>x.length<2000).join('\n'));process.exit(1);});
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {FileBlob, PresentationFile} from '@oai/artifact-tool';
const dir=path.dirname(fileURLToPath(import.meta.url));
const source=process.env.TEMPLATE_PPTX;
if(!source) throw new Error('Set TEMPLATE_PPTX to the selected Simple Light Mode reference.pptx.');
const data=JSON.parse(await fs.readFile(path.join(dir,'source-data.json'),'utf8'));
const p=await PresentationFile.importPptx(await FileBlob.load(source));
const originals=Array.from({length:26},(_,i)=>p.slides.getItem(i));
const selected=[0,4,13,13,13,14].map(i=>originals[i].duplicate());
for(const s of originals)s.delete();
selected.forEach((s,i)=>s.moveTo(i));
const base={typeface:'Helvetica Neue',fontSize:21.33,color:'#000000',alignment:'left',verticalAlignment:'top',autoFit:'none',wrap:'square',insets:{top:0,right:0,bottom:0,left:0}};
async function elements(s){return JSON.parse(await (await s.export({format:'layout'})).text()).elements;}
function text(a,value,size=21.33){const sh=p.resolve(a);sh.text=value;sh.text.style={...base,fontSize:size};return sh;}
function paragraphs(a,rows){const sh=p.resolve(a);sh.text.style=base;sh.text.set(rows.map((v,i)=>({bulletCharacter:'',marginLeft:0,indent:0,spaceBefore:0,spaceAfter:1200,runs:[{run:v,textStyle:{typeface:'Helvetica Neue',fontSize:i===0?'32px':'21.33px'}}]})));return sh;}
for(let i=0;i<6;i++){
 const s=selected[i], es=await elements(s), d=data.slides[i];
 const title=es.find(e=>e.name==='Title 3'||e.name==='Google Shape;533;p58');
 text(title.aid,d.title,i===0?72:38.67);
 const number=es.find(e=>e.name==='Google Shape;532;p58');if(number)text(number.aid,String(i+1),13.33);
 const foot=es.find(e=>e.name.startsWith('Footer Placeholder'));if(foot)text(foot.aid,'8 September 2026  |  hardware-benchmarks',13.33);
 if(i===0){
   const st=es.filter(e=>e.name==='Subtitle 4').sort((a,b)=>a.bbox[1]-b.bbox[1]);
   text(st[0].aid,d.kicker,21.33);text(st[1].aid,d.subtitle,26.67);
 }else if(i===1){
   paragraphs(es.find(e=>e.name==='Google Shape;534;p58').aid,d.left);
   paragraphs(es.find(e=>e.name==='Content Placeholder 3').aid,d.right);
 }else if(i>=2&&i<=4){
   text(es.find(e=>e.name==='Content Placeholder 15').aid,d.intro,21.33);
   const t=p.resolve(es.find(e=>e.kind==='table').aid);
   t.setValues(d.table);
   t.columnWidths=d.widths;
   for(let r=0;r<d.table.length;r++){
    t.rows[r].height=412.87/d.table.length;
    for(let c=0;c<d.table[r].length;c++){
      const cell=t.getCell(r,c);cell.fill='#FFFFFF';cell.text.style={...base,fontSize:18.67,bold:r===0};
    }
   }
 }else{
   paragraphs(es.find(e=>e.name==='Google Shape;534;p58').aid,d.left);
   const rows=es.filter(e=>e.bbox[0]>450&&e.bbox[1]>200&&e.bbox[1]<650).sort((a,b)=>a.bbox[1]-b.bbox[1]||a.bbox[0]-b.bbox[0]);
   for(let r=0;r<4;r++){text(rows[r*2].aid,d.rows[r][0],21.33).text.style={...base,typeface:'Helvetica Neue Medium'};text(rows[r*2+1].aid,d.rows[r][1],21.33);}
 }
 s.speakerNotes.textFrame.setText(d.notes+'\n\nSources:\n'+d.sources.join('\n'));
}
await fs.writeFile(path.join(dir,'authored-inspect.ndjson'),(await p.inspect({kind:'slide,textbox,table',maxChars:150000})).ndjson);
await(await PresentationFile.exportPptx(p)).save(path.join(dir,'candidate.pptx'));
for(let i=0;i<6;i++){
 await fs.writeFile(path.join(dir,`slide-${i+1}.png`),new Uint8Array(await(await selected[i].export({format:'png',scale:1})).arrayBuffer()));
 await fs.writeFile(path.join(dir,`slide-${i+1}.layout.json`),await(await selected[i].export({format:'layout'})).text());
}
await fs.writeFile(path.join(dir,'build-provenance.json'),JSON.stringify({templateSha256:crypto.createHash('sha256').update(await fs.readFile(source)).digest('hex'),templateSlides:[1,5,14,14,14,15],slideCount:6,sourceCommit:data.sourceCommit},null,2));
console.log('Built and rendered six editable slides.');
