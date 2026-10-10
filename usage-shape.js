/* Width is remaining quota. Round the measured polyline within API rounding
   precision (0.5 percentage points), without changing any reported readings. */
function usageShape(samples, from, to, now) {
 const clamp=n=>Math.max(0,Math.min(100,n));
 const rows=[...new Map(samples.filter(s=>s.at<=now&&Number.isFinite(s.at)&&Number.isFinite(s.primary?.usedPercent)).map(s=>[s.at,s])).values()].sort((a,b)=>a.at-b.at);
 if(!rows.length||to<=from||rows[0].at>to)return null;
 const raw=rows.map(s=>[clamp(100-s.primary.usedPercent),s.at]),full=[];
 const lerp=(a,b,t)=>a.map((v,i)=>v+(b[i]-v)*t);
 const line=(a,b)=>{if(b[1]>a[1])full.push({from:a,c1:lerp(a,b,1/3),c2:lerp(a,b,2/3),to:b})};
 let cursor=raw[0];
 for(let i=1;i<raw.length-1;i++){
  const a=raw[i-1],b=raw[i],c=raw[i+1],h0=b[1]-a[1],h1=c[1]-b[1];
  const d0=(b[0]-a[0])/h0,d1=(c[0]-b[0])/h1;
  // Symmetric time handles preserve a linear time axis. Curvature is local,
  // not the same ease-in/ease-out repeated at every sampling interval.
  const radius=Math.min(h0/2,h1/2,Math.abs(d1-d0)>1e-12?2/Math.abs(d1-d0):Infinity);
  const left=[b[0]-d0*radius,b[1]-radius],right=[b[0]+d1*radius,b[1]+radius];
  line(cursor,left);
  full.push({from:left,c1:lerp(left,b,2/3),c2:lerp(right,b,2/3),to:right});
  cursor=right;
 }
 line(cursor,raw.at(-1));
 const split=(s,t)=>{const a=lerp(s.from,s.c1,t),b=lerp(s.c1,s.c2,t),c=lerp(s.c2,s.to,t),d=lerp(a,b,t),e=lerp(b,c,t),f=lerp(d,e,t);return [{from:s.from,c1:a,c2:d,to:f},{from:f,c1:e,c2:c,to:s.to}]};
 const map=p=>[p[0],clamp((p[1]-from)/(to-from)*100)];
 const segments=[];
 for(let s of full){if(s.to[1]<=from||s.from[1]>=to)continue;
  if(s.from[1]<from)s=split(s,(from-s.from[1])/(s.to[1]-s.from[1]))[1];
  if(s.to[1]>to)s=split(s,(to-s.from[1])/(s.to[1]-s.from[1]))[0];
  segments.push(Object.fromEntries(Object.entries(s).map(([k,p])=>[k,map(p)])));
 }
 const first=segments[0]?.from||map(raw.at(-1)),last=segments.at(-1)?.to||first;
 let edge=`M${first.join(' ')}`;
 for(const s of segments)edge+=` C${s.c1.join(' ')} ${s.c2.join(' ')} ${s.to.join(' ')}`;
 const knots=raw.filter(p=>p[1]>=from&&p[1]<=to).map(map),points=[first,...segments.map(s=>s.to)];
 const area=`M0 ${first[1]} L${first.join(' ')} ${edge.replace(/^M[^C]+/,'')} L0 ${last[1]} Z`;
 // No made-up 100% reading before the first observation: only a lighter fill.
 const leadIn=first[1]>0?`M0 0 H${first[0]} V${first[1]} H0 Z`:null;
 return {segments,leadIn,points,knots,edge,area,firstY:first[1],firstWidth:first[0],lastWidth:last[0],solidEnd:last[1],continuation:`M0 ${last[1]} H${last[0]} V100 H0 Z`};
}
// A quota's validity period is not an activity session. Only adjacent samples
// showing consumption form a block; plateaus and missing polling intervals
// remain empty. Never infer work across a reset or extend it into the future.
function usageSpans(samples, now=Date.now()/1000, maxGapSeconds=900) {
 const rows=[...new Map(samples.filter(s=>Number.isFinite(s.at)&&s.at<=now&&Number.isFinite(s.primary?.usedPercent)).map(s=>[s.at,s])).values()].sort((a,b)=>a.at-b.at);
 const spans=[];
 for(let i=1;i<rows.length;i++){
  const a=rows[i-1],b=rows[i],p=a.primary,q=b.primary;
  if(b.at-a.at>maxGapSeconds||p.resetsAt!==q.resetsAt||p.windowDurationMins!==q.windowDurationMins||q.usedPercent-p.usedPercent<=1e-6)continue;
  const previous=spans.at(-1);
  if(previous?.to===a.at){previous.to=b.at;previous.samples.push(b)}
  else spans.push({from:a.at,to:b.at,samples:[a,b]});
 }
 return spans;
}
if(typeof module!=='undefined')module.exports={usageShape,usageSpans};
