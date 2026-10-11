from pathlib import Path
import shutil
root=Path(__file__).parent;out=root/'preview';out.mkdir(exist_ok=True)
s=(root/'index.html').read_text().replace('<script src="/overview.js">','<script src="/preview-data.js"></script><script src="/overview.js">',1)
s=s.replace("await fetch('/api/usage',{cache:'no-store'})", "({ok:true,json:async()=>previewState})")
a=s.index('function authUI()');b=s.index('async function authAction',a)
s=s[:a]+'''function authUI(){$('#auth-entry').hidden=true;$('#account-actions').hidden=true;$('#connection').textContent=planLabel(state?.latest?.planType)+' · 示例';$('#status').textContent='示例快照 · '+dateTime(previewState.asOf);$('#status').classList.remove('error');$('#refresh').disabled=true;$('#refresh').textContent='预览';}
'''+s[b:]
a=s.index('async function refreshOnVisit()');b=s.index("document.addEventListener('visibilitychange'",a)
s=s[:a]+"async function refreshOnVisit(){await sync()}\n"+s[b:]
s=s.replace('<h1>用量日历</h1>','<h1>用量日历 <small style="font-size:10px;color:#aaa3b3;font-weight:400">预览</small></h1>')
s=s.replace('当前账户 · 云端额度','界面预览 · 示例数据')
s=s.replace('云端活动','示例活动').replace('云端日期由 ChatGPT 账户接口返回；额度曲线来自登录后的定时查询。不读取本机 Codex 对话日志；云端未提供旧窗口的完整百分比曲线。','此页为固定时刻的虚构快照，不连接账户。五分钟采样、周消耗和活动日期由同一组示例生成。')
s=s.replace("zoomMode='auto'","zoomMode='60'",1).replace("count===1?0:-2","count===1?0:-4",1).replace("if(viewMode==='5')anchor=shift(anchor,-2)","if(viewMode==='5')anchor=shift(anchor,-4)")
s=s.replace('<div class="provider">','<p class="preview-note">交互演示 · 全部为虚构数据</p><label class="control-label preview-plan"><span>演示账户</span><select class="control" id="preview-plan"><option value="prolite">Pro $100 · 仅周额度</option><option value="plus">Plus · 五小时与周额度</option></select></label><div class="provider">',1)
s=s.replace('</body>',"<script>document.querySelector('#preview-plan').onchange=e=>{previewState=createPreviewState(previewState.asOf,e.target.value);selected=null;selectedDay=null;lastKey='';sync()};</script></body>")
(out/'index.html').write_text(s)
for name in ['i18n.js','quota-model.js','usage-shape.js','usage-estimates.js','overview.js','motion.css','motion.js','history-ui.js','history.css']:shutil.copy2(root/name,out/name)
(out/'assets').mkdir(exist_ok=True)
for asset in (root/'assets').glob('*.svg'):shutil.copy2(asset,out/'assets'/asset.name)
for legacy in (out/'assets').glob('*.png'):legacy.unlink()
(out/'vercel.json').write_text('{"version":2,"framework":null,"buildCommand":null,"outputDirectory":"."}')
