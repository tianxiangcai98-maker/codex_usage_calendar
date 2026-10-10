const assert=require('node:assert/strict'),{createPreviewState}=require('./preview/preview-data'),{normalizeQuotaRow}=require('./quota-model'),{usageEstimates}=require('./usage-estimates'),{calendarMarkers}=require('./overview');
for(const date of [new Date(2026,9,10,16,20),new Date(2026,9,10,0,2),new Date(2026,10,2,0,10)]){
 const now=date.getTime()/1000;
 for(const plan of ['plus','prolite']){
  const state=createPreviewState(now,plan),rows=state.history.map(normalizeQuotaRow),latest=rows.at(-1);
  assert.equal(state.latest.at,now);assert.ok(rows.every(r=>r.at<=now&&r.source==='demo'&&!r.accountVerified));
  assert.equal(Boolean(latest.primary),plan==='plus');assert.equal(latest.secondary.windowDurationMins,10080);
  const pairs=rows.slice(1).map((b,i)=>[rows[i],b]);
  for(const [a,b] of pairs){assert.ok(b.at-a.at<=300);if(a.secondary.resetsAt===b.secondary.resetsAt)assert.ok(b.secondary.usedPercent>=a.secondary.usedPercent);if(plan==='plus'&&a.primary&&b.primary&&a.primary.resetsAt===b.primary.resetsAt&&a.secondary.resetsAt===b.secondary.resetsAt){const x=b.primary.usedPercent-a.primary.usedPercent,y=b.secondary.usedPercent-a.secondary.usedPercent;assert.ok(Math.abs(y-x*.105)<.02,'weekly quota follows consumed work');}}
  const marker=calendarMarkers(state.history);assert.equal(marker.some(m=>m.kind==='primary'),plan==='plus');
  const estimate=usageEstimates(rows,now);if(plan==='prolite'){assert.equal(estimate.equivalentWindows,null);assert.equal(estimate.rate,null)}else {assert.ok(Math.abs(estimate.weeklyCost-10.5)<.1)}
  assert.deepEqual(state,createPreviewState(now,plan),'stable snapshot');
 }
}
console.log('PASS: two API window layouts, proportional weekly usage, fixed cadence, midnight/DST, stable snapshot, no future data, no fake 5h estimate for Pro');
