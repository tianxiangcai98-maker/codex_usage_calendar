if(typeof module!=='undefined')var {quotaWindows}=require('./quota-model');
function overviewMonths(anchor,mode){
 const n=mode==='year'?12:mode==='quarter'?3:1;
 const first=mode==='year'?0:mode==='quarter'?Math.floor(anchor.getMonth()/3)*3:anchor.getMonth();
 return Array.from({length:n},(_,i)=>new Date(anchor.getFullYear(),first+i,1));
}
function dailyUsage(history,cloudDays=[]){
 const days=new Map;
 for(const r of cloudDays){const [y,m,d]=r.date.split('-').map(Number);days.set(`${y}-${m-1}-${d}`,{windows:new Set,peak:null,samples:0,cloud:true,active:r.active===true?true:r.active===false?false:null})}
 for(const s of history){const {primary,weekly}=quotaWindows(s),w=primary||weekly;if(!w)continue;const d=new Date(s.at*1000),key=`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
 if(!days.has(key))days.set(key,{windows:new Set,peak:0,samples:0});const item=days.get(key);if(primary)item.windows.add(primary.resetsAt);item.peak=Math.max(item.peak||0,w.usedPercent);item.samples++}
 return days;
}
// Sampling proves coverage, not activity: an idle weekly quota can be sampled.
function dayStatus(date,days,now=new Date()){
 const key=`${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`,item=days.get(key);
 const today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
 if(date>today)return {kind:'future',label:'尚未到来',item};
 if(item?.samples)return {kind:'sampled',label:'有额度采样',item};
 if(item?.active===true)return {kind:'activity',label:'有使用 · 缺曲线',item};
 if(item?.active===false)return {kind:'idle',label:date.getTime()===today.getTime()?'暂无使用':'未使用',item};
 return {kind:'unknown',label:'记录未知',item};
}
if(typeof module!=='undefined')module.exports={overviewMonths,dailyUsage,dayStatus};
function calendarMarkers(history){
 const result=new Map();
 for(const s of history){
  const {primary:p,weekly:w}=quotaWindows(s);
  if(p?.usedPercent>=100&&p.resetsAt)result.set('recovery:'+p.resetsAt,{kind:'recovery',at:p.resetsAt,inferred:false});
  if(p?.resetsAt&&p.windowDurationMins>0){const at=p.resetsAt-p.windowDurationMins*60;result.set('primary:'+at,{kind:'primary',at,hours:p.windowDurationMins/60,inferred:true})}
  if(w?.resetsAt){result.set('weekly:'+w.resetsAt,{kind:'weekly',at:w.resetsAt,inferred:false});if(w.windowDurationMins>0){const at=w.resetsAt-w.windowDurationMins*60;const key='weekly:'+at;if(!result.has(key))result.set(key,{kind:'weekly',at,inferred:true})}}
 }
 return [...result.values()].sort((a,b)=>a.at-b.at);
}
if(typeof module!=='undefined')module.exports.calendarMarkers=calendarMarkers;
