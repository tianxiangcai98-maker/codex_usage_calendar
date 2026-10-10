import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import server
class CollectorTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();initial={**server.STATE,'account':None,'signedIn':False,'refreshing':False,'loginPending':False,'error':None,'loginId':None,'loginUrl':None}
  self.patches=[patch.object(server,'DB',Path(self.tmp.name)/'test.sqlite3'),patch.object(server,'STATE',initial),patch.object(server,'sync_cloud')]
  for p in self.patches:p.start()
  self.payload={'primary':{'usedPercent':42,'windowDurationMins':300,'resetsAt':1800000000},'secondary':None,'planType':'plus'}
 def tearDown(self):
  for p in reversed(self.patches):p.stop()
  self.tmp.cleanup()
 def capture(self,identity='a'):
  with patch.object(server,'read_usage',return_value=(identity,self.payload)):server.collect()
 def test_persistence_and_interval(self):
  self.capture();r=server.state();self.assertEqual(r['latest']['primary']['usedPercent'],42);self.assertEqual(len(r['history']),1);self.assertNotIn('account',r);self.assertNotIn('loginUrl',r);self.assertAlmostEqual(r['nextPoll']-r['latest']['at'],300,delta=2)
 def test_failure_preserves_data(self):
  self.capture()
  with patch.object(server,'read_usage',side_effect=server.QuotaError('Offline')):server.collect()
  r=server.state();self.assertEqual(r['error'],'Offline');self.assertEqual(len(r['history']),1);self.assertFalse(r['refreshing'])
 def test_account_isolation(self):
  self.capture('a');self.capture('b');self.assertEqual(len(server.state()['history']),1);self.capture('a');self.assertEqual(len(server.state()['history']),2)
 def test_signed_out_hides_cached_account(self):
  self.capture()
  with patch.object(server,'read_usage',side_effect=server.SignInRequired('Sign in')):server.collect()
  r=server.state();self.assertFalse(r['signedIn']);self.assertEqual(r['history'],[]);self.assertEqual(r['cloudDays'],[])
 def test_no_error_leak(self):
  with patch.object(server,'read_usage',side_effect=RuntimeError('secret-value')):server.collect()
  self.assertNotIn('secret-value',json.dumps(server.state()));self.assertIsNone(server.state()['latest'])
 def test_polling_loop(self):
  with patch.object(server,'collect') as collect,patch.object(server.WAKE,'wait',side_effect=InterruptedError) as wait:
   with self.assertRaises(InterruptedError):server.polling()
   collect.assert_called_once();wait.assert_called_once_with(300)
 def test_no_parallel_refresh_or_during_login(self):
  server.STATE['refreshing']=True
  with patch.object(server,'read_usage') as read:server.collect();read.assert_not_called()
  server.STATE['refreshing']=False;server.STATE['loginPending']=True
  with patch.object(server,'read_usage') as read:server.collect();read.assert_not_called()
 def test_cloud_sanitization_discards_token_counts(self):
  r=server.sanitize_activity({'summary':{'lifetimeTokens':999},'dailyUsageBuckets':[{'startDate':'2026-09-12','tokens':3456},{'startDate':'not-a-date','tokens':10}]})
  self.assertEqual(r,[{'date':'2026-09-12','active':True}]);self.assertNotIn('tokens',json.dumps(r));self.assertIsNone(server.sanitize_activity({}))
 def test_login_and_cancel(self):
  with patch.object(server.BRIDGE,'request',return_value={'loginId':'test','authUrl':'https://auth.openai.com/authorize?state=test'}) as rpc:
   r=server.login_start();self.assertTrue(server.STATE['loginPending']);rpc.assert_called_once_with('account/login/start',{'type':'chatgpt'});self.assertTrue(r['authUrl'].startswith('https://auth.openai.com/'))
  with patch.object(server.BRIDGE,'request',return_value={}) as rpc:server.login_cancel();rpc.assert_called_once_with('account/login/cancel',{'loginId':'test'})
  self.assertFalse(server.STATE['loginPending'])
 def test_disallows_untrusted_auth_url(self):
  with patch.object(server.BRIDGE,'request',return_value={'loginId':'test','authUrl':'https://evil.example/'}):
   with self.assertRaises(server.QuotaError):server.login_start()
 def test_logout_does_not_delete_history(self):
  self.capture()
  with patch.object(server.BRIDGE,'request',return_value={}):server.logout()
  self.assertEqual(server.state()['history'],[])
  self.capture();self.assertEqual(len(server.state()['history']),2)

class PlanWindowTests(unittest.TestCase):
 def test_weekly_primary_is_not_a_five_hour_window(self):
  raw={'primary':{'usedPercent':37,'windowDurationMins':10080,'resetsAt':1800604800},'secondary':None,'planType':'prolite'}
  n=server.normalize_quota(raw)
  self.assertIsNone(n['primary']);self.assertEqual(n['secondary'],raw['primary']);self.assertEqual(n['planType'],'prolite')
 def test_account_plan_fallback_and_codex_bucket(self):
  replies=[{'account':{'type':'chatgpt','email':'fixture@example.test','planType':'prolite'}},{'rateLimitsByLimitId':{'codex':{'primary':{'usedPercent':37,'windowDurationMins':10080,'resetsAt':1800604800}},'other':{'primary':{'usedPercent':9,'windowDurationMins':300}}}}]
  with patch.object(server.BRIDGE,'request',side_effect=replies) as rpc:
   _,payload=server.read_usage()
  self.assertEqual(payload['planType'],'prolite');self.assertIsNone(payload['primary']);self.assertEqual(payload['secondary']['usedPercent'],37)
  self.assertEqual(rpc.call_args_list[0].args[0],'account/read')
 def test_plan_change_does_not_reuse_old_short_window(self):
  old={'primary':{'usedPercent':70,'windowDurationMins':300},'secondary':{'usedPercent':25,'windowDurationMins':10080}}
  new={'primary':{'usedPercent':37,'windowDurationMins':10080},'secondary':None}
  self.assertIsNotNone(server.normalize_quota(old)['primary']);self.assertIsNone(server.normalize_quota(new)['primary'])


class HistoryEvidenceTests(unittest.TestCase):
 def test_missing_values_are_unknown_not_unused(self):
  values=[0,20,None,-1,True,float('nan')]
  rows=server.sanitize_activity({'dailyUsageBuckets':[{'startDate':f'2026-10-{i+1:02d}','tokens':v} for i,v in enumerate(values)]})
  self.assertEqual([r['active'] for r in rows],[False,True,None,None,None,None])
  self.assertEqual(server.sanitize_activity({'dailyUsageBuckets':[]}),[])
  self.assertIsNone(server.sanitize_activity({}))
 def test_backfill_preserves_dates_and_unknowns_without_token_totals(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(server,'DB',Path(tmp)/'history.sqlite3'),patch.object(server,'STATE',{**server.STATE,'account':'fixture','signedIn':True}):
   result={'summary':{'lifetimeTokens':999999},'dailyUsageBuckets':[{'startDate':'2026-05-18','tokens':100},{'startDate':'2026-05-19','tokens':0},{'startDate':'2026-05-20','tokens':None}]}
   with patch.object(server.BRIDGE,'request',return_value=result) as rpc:
    server.sync_cloud('fixture');rpc.assert_called_once_with('account/usage/read')
   rows=server.state()['cloudDays'];self.assertEqual([r['active'] for r in rows],[True,False,None]);self.assertNotIn('tokens',json.dumps(rows))
   with patch.object(server.BRIDGE,'request',side_effect=server.BridgeError('offline')):server.sync_cloud('fixture')
   self.assertEqual(server.state()['cloudDays'],rows,'failed refresh must preserve existing history')
 def test_legacy_zero_is_unknown_until_verified(self):
  import sqlite3
  with tempfile.TemporaryDirectory() as tmp,patch.object(server,'DB',Path(tmp)/'legacy.sqlite3'),patch.object(server,'STATE',{**server.STATE,'account':'fixture','signedIn':True}):
   with sqlite3.connect(server.DB) as c:
    c.execute('CREATE TABLE cloud_activity (account TEXT,day TEXT,active INTEGER,fetched REAL,PRIMARY KEY(account,day))')
    c.executemany('INSERT INTO cloud_activity VALUES (?,?,?,?)',[('fixture','2026-05-18',1,0),('fixture','2026-05-19',0,0)])
   self.assertEqual([r['active'] for r in server.state()['cloudDays']],[True,None])

if __name__=='__main__':unittest.main()
