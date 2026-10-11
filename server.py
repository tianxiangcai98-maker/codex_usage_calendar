#!/usr/bin/env python3
"""OAuth-connected quota tracker. No local Codex session-log reads."""
import datetime,math
import atexit,hashlib,json,os,pathlib,sqlite3,threading,time
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from codex_bridge import CodexBridge,BridgeError
ROOT=pathlib.Path(__file__).resolve().parent
DATA=ROOT/'data';DATA.mkdir(mode=0o700,exist_ok=True);os.chmod(DATA,0o700)
DB=DATA/'usage.sqlite3';INTERVAL=300;PORT=int(os.environ.get('CODEX_USAGE_PORT','8765'))
STATE={'refreshing':False,'error':None,'lastAttempt':None,'nextPoll':None,'account':None,'signedIn':False,'loginPending':False,'loginError':None,'loginId':None,'loginUrl':None,'cloudError':None}
LOCK=threading.RLock();AUTH_LOCK=threading.Lock();WAKE=threading.Event()
class QuotaError(Exception):pass
class SignInRequired(QuotaError):pass

def db():
 c=sqlite3.connect(DB)
 c.execute('CREATE TABLE IF NOT EXISTS snapshots (id INTEGER PRIMARY KEY, account TEXT NOT NULL, at REAL NOT NULL, payload TEXT NOT NULL)')
 c.execute('CREATE TABLE IF NOT EXISTS cloud_activity (account TEXT, day TEXT, active INTEGER, fetched REAL, PRIMARY KEY(account,day))')
 if 'activity_known' not in {r[1] for r in c.execute('PRAGMA table_info(cloud_activity)')}:
  c.execute('ALTER TABLE cloud_activity ADD COLUMN activity_known INTEGER NOT NULL DEFAULT 0')
 c.execute('CREATE TABLE IF NOT EXISTS cloud_sync (account TEXT PRIMARY KEY, at REAL)')
 return c
with db():pass
os.chmod(DB,0o600)

def notification(method,params):
 if method=='account/login/completed':
  with LOCK:
   if params.get('loginId')!=STATE['loginId']:return
   STATE['loginPending']=False;STATE['loginId']=None;STATE['loginUrl']=None
   STATE['loginError']=None if params.get('success') else '登录未完成，可以重新连接。'
  if params.get('success'):WAKE.set()
BRIDGE=CodexBridge(DATA/'codex-home',notification);atexit.register(BRIDGE.close)

def sanitize_window(value):
 if not value or not isinstance(value.get('usedPercent'),(int,float)):return None
 return {'usedPercent':max(0,min(100,value['usedPercent'])),'windowDurationMins':value.get('windowDurationMins'),'resetsAt':value.get('resetsAt')}

def normalize_quota(payload):
 windows=[sanitize_window(payload.get(k)) for k in ('primary','secondary')]
 windows=[w for w in windows if w and isinstance(w.get('windowDurationMins'),(int,float)) and w['windowDurationMins']>0]
 return {**payload,'primary':next((w for w in windows if w['windowDurationMins']<10080),None),'secondary':next((w for w in windows if w['windowDurationMins']==10080),None)}

def sanitize_activity(result):
 buckets=result.get('dailyUsageBuckets')
 if buckets is None:return None
 # Daily token totals cannot reconstruct quota percentages. Retain only an
 # explicit activity state; missing/invalid totals must not become zero usage.
 rows=[]
 for b in buckets:
  if not isinstance(b,dict):continue
  try:day=datetime.date.fromisoformat(b['startDate']).isoformat()
  except (ValueError,KeyError,TypeError):continue
  n=b.get('tokens');known=isinstance(n,(int,float)) and not isinstance(n,bool) and math.isfinite(n) and n>=0
  rows.append({'date':day,'active':n>0 if known else None})
 return rows

def read_usage():
 account=BRIDGE.request('account/read',{'refreshToken':False}).get('account')
 if not account or account.get('type')!='chatgpt':raise SignInRequired('请连接 ChatGPT 账户。')
 if not account.get('email'):raise QuotaError('无法识别当前账户，请重新连接。')
 identity=hashlib.sha256(account['email'].strip().lower().encode()).hexdigest()
 result=BRIDGE.request('account/rateLimits/read')
 buckets=result.get('rateLimitsByLimitId');limit=buckets.get('codex') if buckets else result.get('rateLimits')
 if not limit:raise QuotaError('当前账户没有可读取的 Codex 额度。')
 credits=result.get('rateLimitResetCredits') or {}
 payload=normalize_quota({'primary':limit.get('primary'),'secondary':limit.get('secondary'),'planType':limit.get('planType') or account.get('planType'),'resetCredits':{'availableCount':credits.get('availableCount'),'expiresAt':[c['expiresAt'] for c in credits.get('credits') or [] if c.get('status')=='available' and c.get('expiresAt')]}})
 if not payload['primary'] and not payload['secondary']:raise QuotaError('服务未返回额度窗口，请稍后重试。')
 return identity,payload

def sync_cloud(identity):
 try:
  activity=sanitize_activity(BRIDGE.request('account/usage/read'));now=time.time()
  if activity is None:
   with LOCK:STATE['cloudError']='云端未返回按日历史。'
   return
  with db() as c:
   c.executemany('INSERT OR REPLACE INTO cloud_activity(account,day,active,fetched,activity_known) VALUES(?,?,?,?,?)',[(identity,r['date'],None if r['active'] is None else int(r['active']),now,int(r['active'] is not None)) for r in activity])
   c.execute('INSERT OR REPLACE INTO cloud_sync(account,at) VALUES(?,?)',(identity,now))
  with LOCK:STATE['cloudError']=None
 except BridgeError:
  with LOCK:STATE['cloudError']='云端历史更新失败，保留上次按日记录。'

def collect():
 with LOCK:
  if STATE['refreshing'] or STATE['loginPending']:return
  STATE['refreshing']=True;STATE['lastAttempt']=time.time()
 try:
  with AUTH_LOCK:
   identity,payload=read_usage()
   with db() as c:c.execute('INSERT INTO snapshots(account,at,payload) VALUES(?,?,?)',(identity,time.time(),json.dumps(payload)))
   with LOCK:STATE['account']=identity;STATE['signedIn']=True;STATE['error']=None
   sync_cloud(identity)
 except SignInRequired:
  with LOCK:STATE['account']=None;STATE['signedIn']=False;STATE['error']=None
 except (QuotaError,BridgeError) as e:
  with LOCK:STATE['error']=str(e)
 except Exception:
  with LOCK:STATE['error']='连接暂时不可用，请稍后重试。'
 finally:
  with LOCK:STATE['refreshing']=False;STATE['nextPoll']=time.time()+INTERVAL

def polling():
 while True:
  collect();WAKE.wait(INTERVAL);WAKE.clear()

def state():
 with LOCK:status=dict(STATE)
 account=status['account'] if status['signedIn'] else None
 with db() as c:
  rows=c.execute('SELECT at,payload FROM snapshots WHERE account=? ORDER BY at',(account,)).fetchall()
  days=c.execute('SELECT day,active,activity_known FROM cloud_activity WHERE account=? ORDER BY day',(account,)).fetchall()
  sync=c.execute('SELECT at FROM cloud_sync WHERE account=?',(account,)).fetchone()
 history=[{'at':r[0],**normalize_quota(json.loads(r[1])),'source':'live','accountVerified':True} for r in rows]
 for key in ('account','loginId','loginUrl'):status.pop(key,None)
 return {**status,'interval':INTERVAL,'history':history,'latest':history[-1] if history else None,'cloudDays':[{'date':r[0],'active':True if r[1]==1 else False if r[1]==0 and r[2] else None} for r in days],'cloudSyncedAt':sync[0] if sync else None,'importedCount':0}

def login_start():
 with AUTH_LOCK:
  with LOCK:
   if STATE['signedIn']:raise QuotaError('请先退出此应用中的账户。')
   if STATE['loginPending'] and STATE['loginUrl']:return {'authUrl':STATE['loginUrl']}
  result=BRIDGE.request('account/login/start',{'type':'chatgpt'})
  url=result.get('authUrl','');parsed=urlparse(url)
  if parsed.scheme!='https' or parsed.hostname not in {'auth.openai.com','chatgpt.com'}:raise QuotaError('登录服务返回了无法识别的地址。')
  with LOCK:
   STATE['loginPending']=True;STATE['loginError']=None;STATE['loginId']=result['loginId'];STATE['loginUrl']=url
  return {'authUrl':url}

def login_cancel():
 with AUTH_LOCK:
  with LOCK:login_id=STATE['loginId']
  if login_id:BRIDGE.request('account/login/cancel',{'loginId':login_id})
  with LOCK:STATE['loginPending']=False;STATE['loginId']=None;STATE['loginUrl']=None;STATE['loginError']=None
 return {'ok':True}

def logout():
 login_cancel()
 with AUTH_LOCK:
  BRIDGE.request('account/logout')
  with LOCK:
   STATE['account']=None;STATE['signedIn']=False;STATE['error']=None;STATE['cloudError']=None
 return {'ok':True}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def allowed(self):return self.headers.get('Host') in {f'localhost:{PORT}',f'127.0.0.1:{PORT}'} and self.headers.get('Sec-Fetch-Site')!='cross-site'
 def output(self,code,data,kind='application/json'):
  self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY')
  self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
  self.end_headers();self.wfile.write(data if isinstance(data,bytes) else json.dumps(data).encode())
 def do_GET(self):
  if not self.allowed():return self.output(403,{'error':'Local access only'})
  if self.path=='/api/usage':return self.output(200,state())
  if self.path in {'/','/index.html'}:return self.output(200,(ROOT/'index.html').read_bytes(),'text/html; charset=utf-8')
  if self.path in {'/i18n.js','/quota-model.js','/usage-shape.js','/usage-estimates.js','/overview.js','/motion.js','/history-ui.js'}:return self.output(200,(ROOT/self.path[1:]).read_bytes(),'text/javascript; charset=utf-8')
  if self.path in {'/motion.css','/history.css'}:return self.output(200,(ROOT/self.path[1:]).read_bytes(),'text/css; charset=utf-8')
  if self.path in {'/assets/info.circle.svg','/assets/chevron.left.svg','/assets/chevron.right.svg','/assets/arrow.clockwise.svg','/assets/bell.svg'}:return self.output(200,(ROOT/self.path[1:]).read_bytes(),'image/svg+xml')
  if self.path=='/favicon.ico':return self.output(204,b'','image/x-icon')
  self.output(404,{'error':'Not found'})
 def do_POST(self):
  if not self.allowed() or self.headers.get('Origin') not in {f'http://localhost:{PORT}',f'http://127.0.0.1:{PORT}'}:return self.output(403,{'error':'Same-origin requests only'})
  try:
   actions={'/api/auth/login':login_start,'/api/auth/cancel':login_cancel,'/api/auth/logout':logout}
   if self.path in actions:return self.output(200,actions[self.path]())
   if self.path!='/api/refresh':return self.output(404,{'error':'Not found'})
   with LOCK:
    if STATE['refreshing'] or (STATE['lastAttempt'] and time.time()-STATE['lastAttempt']<10):return self.output(202,{'ok':True})
   WAKE.set();self.output(202,{'ok':True})
  except (QuotaError,BridgeError) as e:self.output(400,{'error':str(e)})
  except Exception:self.output(500,{'error':'操作未完成，请重试。'})

if __name__=='__main__':
 os.umask(0o077)
 server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
 threading.Thread(target=polling,daemon=True).start()
 print(f'Codex Usage: http://localhost:{PORT} · managed ChatGPT OAuth · 5-minute cloud quota reads',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:server.server_close();BRIDGE.close()
