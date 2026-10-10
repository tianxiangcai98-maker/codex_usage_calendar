/* API slots are not quota types: a weekly-only account can put its week in primary. */
function quotaWindows(row) {
  const windows = [row?.primary, row?.secondary].filter(w =>
    w && Number.isFinite(w.usedPercent) && Number.isFinite(w.windowDurationMins) && w.windowDurationMins > 0);
  return {
    primary: windows.find(w => w.windowDurationMins < 10080) || null,
    weekly: windows.find(w => w.windowDurationMins === 10080) || null
  };
}
function normalizeQuotaRow(row) {
  if (!row) return null;
  const {primary, weekly} = quotaWindows(row);
  return {...row, primary, secondary: weekly};
}
function planLabel(plan) {
  return ({prolite:'Pro $100',pro:'Pro',plus:'Plus',free:'Free',team:'Business',business:'Business',enterprise:'Enterprise',edu:'Edu'})[plan] || plan || 'ChatGPT';
}
if(typeof module !== 'undefined') module.exports={quotaWindows,normalizeQuotaRow,planLabel};
