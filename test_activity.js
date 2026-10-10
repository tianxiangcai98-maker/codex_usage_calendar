const assert=require('node:assert/strict');
const {usageSpans,usageShape}=require('./usage-shape');
const {createPreviewState}=require('./preview/preview-data');
const {normalizeQuotaRow}=require('./quota-model');
const row=(at,used,reset=20000)=>({at,primary:{usedPercent:used,resetsAt:reset,windowDurationMins:300}});
const samples=[row(0,0),row(300,10),row(600,20),row(900,20),row(1200,20),row(1500,30),row(1800,40),row(2100,40)];
const spans=usageSpans(samples,2400);
assert.deepEqual(spans.map(s=>[s.from,s.to]),[[0,600],[1200,1800]],'idle plateau leaves a real gap');
assert.equal(usageSpans([row(0,20),row(300,20)],600).length,0,'idle polling is not activity');
assert.equal(usageSpans([row(0,20)],600).length,0,'a lone reading cannot establish activity');
assert.equal(usageSpans([row(0,20),row(3600,40)],4000).length,0,'no connecting across an offline gap');
assert.equal(usageSpans([row(0,20),row(300,30,40000)],600).length,0,'no connecting across quota windows');
assert.equal(usageSpans([row(0,50),row(300,20)],600).length,0,'no consumption inferred from quota recovery');
assert.equal(usageSpans(samples,500).at(-1).to,300,'does not extend beyond the last observed consuming interval');
const duplicate=usageSpans([row(300,8),row(0,0),row(300,10),row(600,20)],600);
assert.deepEqual(duplicate[0].samples.map(s=>s.primary.usedPercent),[0,10,20]);
for(const s of spans){const shape=usageShape(s.samples,s.from,s.to,2400);assert.equal(shape.firstY,0);assert.equal(shape.solidEnd,100);assert.equal(shape.leadIn,null)}

for(const plan of ['plus','prolite']){
 const now=new Date(2026,9,10,16,20).getTime()/1000,state=createPreviewState(now,plan),groups=new Map();
 for(const r of state.history.map(normalizeQuotaRow)){
  const w=plan==='plus'?r.primary:r.secondary;if(!w)continue;
  const group=groups.get(w.resetsAt)||[];group.push({...r,primary:w});groups.set(w.resetsAt,group);
 }
 const blocks=[...groups.values()].flatMap(rows=>usageSpans(rows,now)).sort((a,b)=>a.from-b.from);
 assert.ok(blocks.length>20,'irregular usage produces separated activity blocks');
 assert.ok(blocks.some((b,i)=>i&&b.from-blocks[i-1].to>6*3600),'overnight remains empty');
 for(const rows of groups.values()){
  const intervals=usageSpans(rows,now);
  for(let i=1;i<rows.length;i++)if(rows[i].primary.usedPercent===rows[i-1].primary.usedPercent){
   const midpoint=(rows[i].at+rows[i-1].at)/2;
   assert.ok(!intervals.some(s=>midpoint>s.from&&midpoint<s.to),'no idle sample interval inside a rendered block');
  }
 }
 const seconds=blocks.reduce((sum,b)=>sum+b.to-b.from,0);
 assert.ok(seconds<state.history.at(-1).at-state.history[0].at,'calendar does not fill the entire quota period');
}
console.log('PASS: idle gaps, offline gaps, resets, future cutoff, lone readings, original quota widths, both preview plans');
