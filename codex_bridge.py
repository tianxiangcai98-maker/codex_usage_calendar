"""Official Codex managed OAuth and remote account APIs, isolated from ~/.codex."""
import json,os,pathlib,queue,shutil,subprocess,threading
class BridgeError(Exception):pass
class CodexBridge:
 def __init__(self,home,on_notification=None):
  self.home=pathlib.Path(home).resolve();self.on_notification=on_notification;self.process=None
  self.guard=threading.RLock();self.send_lock=threading.Lock();self.pending={};self.seq=0
 def start(self):
  with self.guard:
   if self.process and self.process.poll() is None:return
   self.home.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(self.home,0o700)
   bundled=pathlib.Path(__file__).parent/'bin/codex'
   executable=str(bundled) if bundled.is_file() else shutil.which('codex')
   if not executable:raise BridgeError('缺少 Codex 连接组件，请先安装 Codex CLI。')
   env=os.environ.copy();env['CODEX_HOME']=str(self.home)
   for key in ('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_BASE_URL'):env.pop(key,None)
   p=subprocess.Popen([executable,'app-server','--stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,cwd=str(self.home),text=True,bufsize=1)
   self.process=p
   threading.Thread(target=self.reader,args=(p,),daemon=True).start()
   self.request('initialize',{'clientInfo':{'name':'codex_usage_calendar','version':'0.4.0'}},start=False)
   self.send({'method':'initialized'})
 def send(self,msg):
  try:
   with self.send_lock:self.process.stdin.write(json.dumps(msg)+'\n');self.process.stdin.flush()
  except (OSError,ValueError,AttributeError):raise BridgeError('连接组件已断开，请重试。')
 def reader(self,p):
  try:
   for line in p.stdout:
    try:msg=json.loads(line)
    except ValueError:continue
    if 'id' in msg:
     pending=self.pending.get(msg['id'])
     if pending:pending.put(msg)
    elif self.on_notification:self.on_notification(msg.get('method'),msg.get('params',{}))
  finally:
   for pending in list(self.pending.values()):pending.put({'error':{'message':'Bridge disconnected'}})
 def request(self,method,params=None,start=True):
  if start:self.start()
  with self.send_lock:
   self.seq+=1;seq=self.seq;response=queue.Queue();self.pending[seq]=response
  msg={'id':seq,'method':method}
  if params is not None:msg['params']=params
  try:
   self.send(msg)
   try:result=response.get(timeout=30)
   except queue.Empty:raise BridgeError('ChatGPT 请求超时，请稍后重试。')
   if 'error' in result:raise BridgeError('ChatGPT 暂时无法完成请求，请检查登录状态或稍后重试。')
   return result['result']
  finally:self.pending.pop(seq,None)
 def close(self):
  if self.process and self.process.poll() is None:
   self.process.terminate()
   try:self.process.wait(timeout=3)
   except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
