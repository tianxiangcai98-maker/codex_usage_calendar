const assert=require('node:assert/strict'),{usageShape}=require('./usage-shape');
const row=(at,used)=>({at,primary:{usedPercent:used}});
const samples=[row(0,0),row(100,20),row(200,60)];
const s=usageShape(samples,0,1000,250);
assert.deepEqual(s.knots,[[100,0],[80,10],[40,20]]);
assert.equal(s.lastWidth,40);assert.equal(s.solidEnd,20);
assert.equal(usageShape([row(200,47)],0,1000,250).firstY,20);
assert.equal(usageShape([row(0,100)],0,1000,100).lastWidth,0);
assert.equal(usageShape([],0,1000,10),null);
assert.ok(Math.abs(usageShape(samples,150,1000,250).firstWidth-60)<1e-9);
assert.ok(Math.abs(usageShape(samples,0,150,250).lastWidth-60)<1e-9);
const evaluate=(seg,t)=>{const u=1-t;return u**3*seg.from[0]+3*u*u*t*seg.c1[0]+3*u*t*t*seg.c2[0]+t**3*seg.to[0]};
const straight=usageShape([row(0,0),row(100,10),row(300,30),row(500,50)],0,1000,500);
for(const seg of straight.segments)for(const [x,y] of [seg.c1,seg.c2])assert.ok(Math.abs(x-(100-y))<1e-9);
const measured=[row(0,0),row(30,2),row(100,40),row(200,40),row(300,95),row(400,100)];
const curve=usageShape(measured,0,1000,400);
for(const seg of curve.segments){let previous=seg.from[0];for(let j=0;j<=100;j++){
 const t=j/100,x=evaluate(seg,t),at=(seg.from[1]+(seg.to[1]-seg.from[1])*t)*10;
 assert.ok(x<=previous+1e-8&&x>=seg.to[0]-1e-8);previous=x;
 const k=Math.max(0,measured.findIndex(r=>r.at>=at)-1),a=measured[k],b=measured[k+1];
 const observed=100-a.primary.usedPercent-(b.primary.usedPercent-a.primary.usedPercent)*(at-a.at)/(b.at-a.at);
 assert.ok(Math.abs(x-observed)<=.500001,'bounded smoothing error');
}}
for(let i=1;i<curve.segments.length;i++){const a=curve.segments[i-1],b=curve.segments[i];assert.ok(Math.abs((a.to[0]-a.c2[0])/(a.to[1]-a.c2[1])-(b.c1[0]-b.from[0])/(b.c1[1]-b.from[1]))<1e-8,'continuous tangent')}
const clipped=usageShape(measured,77,233,400);
for(const seg of clipped.segments)for(let i=0;i<=10;i++){
 const t=i/10,at=77+(seg.from[1]+(seg.to[1]-seg.from[1])*t)*1.56;
 const whole=curve.segments.find(s=>s.from[1]*10<=at+1e-6&&s.to[1]*10>=at-1e-6);
 assert.ok(Math.abs(evaluate(seg,t)-evaluate(whole,(at/10-whole.from[1])/(whole.to[1]-whole.from[1])))<1e-7,'clipping does not reshape the curve');
}
assert.ok(!usageShape([row(0,0),row(0,2),row(10,8)],0,100,10).edge.includes('NaN'));
console.log('PASS: original readings, bounded 0.5pp rounding, monotonic curve, straight rates, shared tangents, exact clipping, missing/duplicate/exhausted samples');
