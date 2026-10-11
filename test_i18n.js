const assert=require('node:assert/strict');
const {translate:t,messages,resolveLanguage,number}=require('./i18n');
assert.equal(new Set(messages.map(row=>row[0])).size,messages.length,'Duplicate source messages');
for(const row of messages){
 assert.equal(row.length,4);
 const slots=s=>[...s.matchAll(/\{\d+\}/g)].map(m=>m[0]).sort();
 for(const text of row.slice(1)){assert.ok(text.trim());assert.deepEqual(slots(text),slots(row[0]),row[0]);}
}
for(const [input,expected] of [['fr-CA','fr'],['ja-JP','ja'],['zh-TW','zh'],['en-GB','en'],['de-DE',null]])assert.equal(resolveLanguage(input),expected);
assert.equal(t('64.4% 剩余','fr'),'64,4\u00a0% restant');
assert.equal(t('4 天 2 小时后','en'),'in 4d 2h');
assert.equal(t('约 1.5 小时','fr'),'≈ 1,5 h');
assert.equal(t('10/6, 8:37 AM – 9:17 AM · 38% 剩余','en'),'10/6, 8:37 AM – 9:17 AM · 38% left');
assert.equal(t('刷新失败 · 显示上次数据。连接暂时不可用，请稍后重试。','en'),'Refresh failed · Showing previous data. Connection unavailable. Try again later.');
assert.equal(t('2026年 · 第 4 季度','fr'),'T4 2026');
assert.equal(t('64.4% 剩余','ja'),'残り 64.4%');
assert.equal(t('已连接 · Pro $100','en'),'Connected · Pro $100');
assert.equal(t('未知','zh'),'未知');
assert.equal(number('1234.5','fr-FR'),'1\u202f234,5');
// Every backend-owned error message must have a translation, without inspecting account data.
const fs=require('node:fs');
for(const file of ['server.py','codex_bridge.py'])for(const m of fs.readFileSync(file,'utf8').matchAll(/'([^'\n]*[\u4e00-\u9fff][^'\n]*)'/g))for(const lang of ['en','fr'])assert.ok(!/[\u4e00-\u9fff]/.test(t(m[1],lang)),file+': '+m[1]);
console.log('PASS: locale catalogs, placeholders, regional numbers, nested errors and backend coverage');
const vm=require('node:vm'),source=fs.readFileSync('i18n.js','utf8');
function settings(stored={},browser=['en-GB']){
 const context={Intl,navigator:{languages:browser},localStorage:{getItem:k=>stored[k]},document:{readyState:'loading',addEventListener(){}},module:{exports:{}}};
 vm.runInNewContext(source,context);return context.module.exports;
}
let regional=settings();assert.equal(regional.language,'en');assert.equal(regional.locale,'en-GB');assert.equal(regional.weekStart,1);
regional=settings({'calendar-language':'ja','calendar-clock':'12'});assert.equal(regional.weekStart,0);assert.equal(regional.timeOptions.hourCycle,'h12');
regional=settings({'calendar-language':'en','calendar-region':'fr-FR','calendar-clock':'24'});assert.equal(regional.locale,'fr-FR');assert.equal(regional.translate('64.4% 剩余'),'64,4\u00a0% left');assert.equal(regional.timeOptions.hourCycle,'h23');
regional=settings({'calendar-language':'zh','calendar-region':'fr-FR'});assert.equal(regional.translate('64.4% 剩余'),'64,4\u00a0% 剩余');
regional=settings({'calendar-language':'bad','calendar-region':'bad','calendar-clock':'bad'},['de-DE']);assert.equal(regional.language,'en');assert.equal(regional.locale,'en-US');assert.equal(regional.weekStart,0);
regional=settings({'calendar-language':'fr'},['fr-CA','en-US']);assert.equal(regional.locale,'fr-CA');assert.equal(regional.weekStart,0);
console.log('PASS: browser language fallback, independent region, clock override and first weekday');
