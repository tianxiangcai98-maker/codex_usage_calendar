/* Synthetic scenarios only. One frozen clock keeps dates, quota and forecasts
   consistent; no signed-in account values are embedded in the public build. */
function createPreviewState(now=Date.now()/1000,plan='prolite') {
 const date=new Date(now*1000),atDay=(ago,h=0,m=0)=>new Date(date.getFullYear(),date.getMonth(),date.getDate()-ago,h,m).getTime()/1000;
 const short=plan==='plus',currentStart=now-47*60,weekEnd=atDay(-4,17),history=[];
 const sessions=[
 [13,10,17,47,182],[13,20,43,82,245],[12,8,52,23,71],[12,15,26,96,271],
 [10,13,8,64,211],[10,22,34,31,93],[9,11,41,100,142],[9,18,19,48,202],
 [8,9,23,12,34],[7,7,46,71,253],[7,14,12,39,147],[7,22,51,91,224],
 [6,16,38,26,82],[5,10,9,58,193],[5,19,47,100,119],
 [4,8,37,34,103],[4,16,14,79,249],[4,23,42,45,154],
 [3,11,26,92,262],[3,20,8,19,51],[2,9,53,100,173],[2,15,41,62,217],
 [1,13,17,29,98],[1,21,36,84,269]
 ].map(([ago,h,m,total,duration],i)=>({start:atDay(ago,h,m),total,duration,pause:i%3===0})).filter(s=>s.start+18000<=currentStart);
 sessions.push({start:currentStart,total:76,duration:83,pause:false});
 const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
 function usage(s,at){const t=(at-s.start)/60;
  return s.pause?s.total*(.42*smooth(t/(s.duration*.36))+.58*smooth((t-s.duration*.53)/(s.duration*.47))):s.total*smooth(t/s.duration);
 }
 let previousEnd=null;
 const weeklyLedger=new Map(),activeDays=new Set();
 const key=at=>{const d=new Date(at*1000);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`};
 // Persisted quota samples every five minutes, including quiet time. Weekly
 // consumption changes only when the same underlying work consumes quota.
 const start=sessions[0].start;
 for(let at=start;at<=now;at=Math.min(at+300,now)){
  const session=sessions.find(s=>at>=s.start&&at<s.start+18000);
  const reset=weekEnd-Math.floor((weekEnd-at-1)/604800)*604800;
  let delta=0;
  for(const s of sessions){const a=Math.max(previousEnd??start,s.start,reset-604800),b=Math.min(at,s.start+18000);if(b>a)delta+=Math.max(0,usage(s,b)-usage(s,a))}
  const weekly=(weeklyLedger.get(reset)||0)+delta*.105;weeklyLedger.set(reset,weekly);
  if(delta>.00001)activeDays.add(key(at));
  const w={usedPercent:Math.round(Math.min(100,weekly)*100)/100,windowDurationMins:10080,resetsAt:reset};
  const p=session?{usedPercent:Math.round(usage(session,at)*100)/100,windowDurationMins:300,resetsAt:session.start+18000}:null;
  history.push({at,source:'demo',accountVerified:false,planType:plan,primary:short?p:w,secondary:short?w:null,resetCredits:{availableCount:2,expiresAt:[atDay(-12,14)]}});
  previousEnd=at;if(at===now)break;
 }
 return {demo:true,asOf:now,signedIn:true,history,latest:history.at(-1),cloudDays:[...activeDays].sort().map(date=>({date,active:true})),cloudSyncedAt:now,interval:300,nextPoll:null,error:null,refreshing:false};
}
let previewState=createPreviewState();
if(typeof module!=='undefined')module.exports={createPreviewState};
