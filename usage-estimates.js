/* Heuristics from observed quota percentages, not tokens or billing. */
if(typeof module!=='undefined')var {normalizeQuotaRow,quotaWindows}=require('./quota-model');
function usageEstimates(history,now=Date.now()/1000,failed=false){
 const rows=history.filter(r=>r.source!=='local_log').map(normalizeQuotaRow).sort((a,b)=>a.at-b.at),latest=rows.at(-1);
 const result={reason:'insufficient',minutes:null,rate:null,spanMinutes:0,equivalentWindows:null,weeklyCost:null,pairs:0,windowsUntilReset:null};
 if(!latest)return result;
 const p=latest.primary,w=latest.secondary;
 if(p?.windowDurationMins>0&&w?.resetsAt>now)result.windowsUntilReset=(w.resetsAt-now)/(p.windowDurationMins*60);
 if(failed||now-latest.at>660){result.reason='stale';return result}
 if(!p||!p.resetsAt||p.resetsAt<=now){result.reason='reset';return result}
 let recent=[latest];
 for(let i=rows.length-2;i>=0;i--){let a=rows[i],b=recent[0];
  if(latest.at-a.at>1800||b.at-a.at>660||a.primary?.resetsAt!==p.resetsAt||a.primary?.windowDurationMins!==p.windowDurationMins||a.planType!==latest.planType||a.primary.usedPercent>b.primary.usedPercent)break;
  recent.unshift(a);
 }
 const span=latest.at-recent[0].at,delta=p.usedPercent-recent[0].primary.usedPercent;
 if(p.usedPercent>=100){result.reason='empty';result.minutes=0}
 else if(span>=120&&recent.length>=2){result.spanMinutes=span/60;result.rate=delta/(span/60);result.reason=delta>0?'estimate':'idle';if(delta>0)result.minutes=(100-p.usedPercent)/result.rate}
 let dp=0,dw=0;
 for(let i=1;i<rows.length;i++){
  const a=rows[i-1],b=rows[i];if(!a.primary||!b.primary||!a.secondary||!b.secondary)continue;
  if(!w?.resetsAt||a.secondary.resetsAt!==w.resetsAt||b.secondary.resetsAt!==w.resetsAt||a.primary.resetsAt!==b.primary.resetsAt||a.primary.windowDurationMins!==p.windowDurationMins||b.primary.windowDurationMins!==p.windowDurationMins||a.planType!==latest.planType||b.planType!==latest.planType||b.at-a.at<=0||b.at-a.at>660)continue;
  const x=b.primary.usedPercent-a.primary.usedPercent,y=b.secondary.usedPercent-a.secondary.usedPercent;
  if(x<0||y<0)continue;dp+=x;dw+=y;result.pairs++;
 }
 // Small rounded percentage changes are too noisy to extrapolate a full quota.
 if(dp>=10&&dw>=2&&result.pairs>=2&&w?.resetsAt>now){result.weeklyCost=dw/dp*100;result.equivalentWindows=Math.max(0,100-w.usedPercent)/result.weeklyCost}
 return result;
}
if(typeof module!=='undefined')module.exports={usageEstimates};

// Window presence and duration are authoritative; plan names are not quota rules.
function sidebarWindows(latest){
 return quotaWindows(latest);
}
if(typeof module!=='undefined')module.exports.sidebarWindows=sidebarWindows;
