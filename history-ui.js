/* A date's cloud activity and its quota-sampling coverage are separate facts. */
function historyLegendMarkup(){
 return '<span><i class="history-key sampled"></i>额度采样</span><span><i class="history-key activity"></i>使用 · 缺曲线</span><span><i class="history-key idle"></i>未使用</span><span><i class="history-key unknown"></i>未知</span><button class="info" aria-label="历史状态说明" data-tip="实色表示有额度采样，不等于当天一定有消耗。斜纹表示云端确认使用，但缺少额度采样。只有云端明确返回零，才标为未使用；没有返回记录则标为未知。云端使用日期按接口原样显示。"><img src="/assets/info.circle.svg" alt=""></button>';
}
function renderDayStrip(days){
 const strip=$('#activity-strip');strip.replaceChildren();strip.hidden=!state?.signedIn;
 const label=document.createElement('span');label.className='activity-axis';label.textContent='记录';strip.append(label);
 for(let i=0;i<count;i++){
  const day=shift(anchor,i),info=dayStatus(day,days,today()),cell=document.createElement('div'),b=document.createElement('button');
  cell.className='activity-cell';b.className='activity-badge '+info.kind;b.textContent=info.kind==='future'?'—':info.label;
  b.setAttribute('aria-label',day.toLocaleDateString(calendarI18n.locale)+'，'+info.label);b.title=b.getAttribute('aria-label');
  b.onclick=()=>{selected=null;selectedDay=day;details()};cell.append(b);strip.append(cell);
 }
 $('#history-legend').innerHTML=historyLegendMarkup();$('#history-legend').hidden=!state?.signedIn;
}
function showHistoryDetail(date){
 const info=dayStatus(date,dailyUsage(state?.history||[],state?.cloudDays||[]),today()),item=info.item,panel=$('#detail');
 const activity=item?.active===true?'已使用':item?.active===false?'云端记录为零':info.kind==='future'?'尚未到来':'未知';
 panel.hidden=false;panel.replaceChildren();
 const heading=document.createElement('div');heading.className='detail-heading';
 const title=document.createElement('strong');title.textContent=date.toLocaleDateString(calendarI18n.locale,{month:'long',day:'numeric'})+' · 历史记录';heading.append(title);
 const help=document.createElement('button');help.className='info';help.setAttribute('aria-label','关于这一天的历史');help.dataset.tip='云端按日记录不包含具体开始时间、每个时刻的剩余额度或过去的重置时间，不能直接换算成额度曲线。额度查询采样独立保存；没有记录的日期保持未知。';help.innerHTML='<img src="/assets/info.circle.svg" alt="">';heading.append(help);panel.append(heading);
 const rows=[['使用状态',activity],['额度曲线',item?.samples?item.samples+' 次采样':info.kind==='future'?'尚未到来':'缺少采样'],['数据来源',item?.cloud&&item?.samples?'云端汇总 + 额度查询':item?.cloud?'云端按日汇总':item?.samples?'账户额度查询':'尚无记录']];
 for(const [name,value] of rows){const row=document.createElement('div');row.className='detail-row';for(const text of [name,value]){const span=document.createElement('span');span.textContent=text;row.append(span)}panel.append(row)}
 revealDetail(panel,'day:'+dateKey(date));
}
function openHistoryDay(date){
 anchor=date;selected=null;selectedDay=date;viewMode='1';count=1;$('#days').value='1';render();
 const rows=(state?.history||[]).filter(s=>dateKey(new Date(s.at*1000))===dateKey(date));
 $('.scroll').scrollTop=rows.length?Math.max(0,(new Date(rows[0].at*1000).getHours()-startHour-1)*pxPerHour):0;
}
function renderCalendarOverview(){
 $('.calendar').classList.add('overview-mode');$('#overview')?.remove();const container=document.createElement('div');container.id='overview';container.className=viewMode;
 const dates=overviewMonths(anchor,viewMode),usage=dailyUsage(state?.history||[],state?.cloudDays||[]);
 $('#month').textContent=viewMode==='year'?anchor.getFullYear()+'年':viewMode==='quarter'?anchor.getFullYear()+'年 · 第 '+(Math.floor(anchor.getMonth()/3)+1)+' 季度':anchor.toLocaleDateString(calendarI18n.locale,{year:'numeric',month:'long'});
 for(const month of dates){
  const section=document.createElement('section');section.className='month-section';section.innerHTML=`<h3>${month.toLocaleDateString(calendarI18n.locale,{month:'long'})}</h3><div class="month-grid">${Array.from({length:7},(_,i)=>new Date(2024,0,calendarI18n.weekStart+i).toLocaleDateString(calendarI18n.locale,{weekday:'narrow'})).map(d=>'<span class="weekday-label">'+d+'</span>').join('')}</div>`;
  const first=shift(month,-((month.getDay()-calendarI18n.weekStart+7)%7));
  for(let i=0;i<42;i++){
   const day=shift(first,i),info=dayStatus(day,usage,today()),b=document.createElement('button');
   b.className='date-cell '+info.kind+(day.getMonth()!==month.getMonth()?' outside':'')+(dateKey(day)===dateKey(today())?' today':'');
   b.style.setProperty('--intensity',info.item?.samples?(.10+(info.item.peak||0)/100*.34):0);
   b.textContent=day.getDate();
   if(info.kind!=='future'){const label=document.createElement(viewMode==='month'?'small':'i');label.className='date-status';label.textContent=viewMode==='month'?info.label:'';b.append(label)}
   b.title=day.toLocaleDateString(calendarI18n.locale)+' · '+info.label;b.setAttribute('aria-label',b.title);b.onclick=()=>openHistoryDay(day);section.querySelector('.month-grid').append(b);
  }
  container.append(section);
 }
 const foot=document.createElement('div');foot.className='overview-footnote';foot.textContent='点击日期查看记录';container.append(foot);$('.calendar').insertBefore(container,$('#history-legend'));
 $('#history-legend').innerHTML=historyLegendMarkup();$('#history-legend').hidden=!state?.signedIn;
}
