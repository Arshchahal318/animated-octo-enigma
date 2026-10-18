"""Private-input native UI checks. Never save signed-in screenshots or UI trees."""
import os,subprocess,time,re,shlex,json,pathlib,xml.etree.ElementTree as ET
checks=[]
def adb(*args):
 r=subprocess.run(['adb',*args],capture_output=True,timeout=40)
 if r.returncode:raise RuntimeError('Android command failed; private output suppressed')
 return r.stdout
def nodes():
 adb('shell','uiautomator','dump','/sdcard/qa-private.xml')
 try:return list(ET.fromstring(adb('shell','cat','/sdcard/qa-private.xml')).iter('node'))
 finally:adb('shell','rm','-f','/sdcard/qa-private.xml')
def norm(s):return ' '.join((s or '').split()).casefold()
def find(text,seconds=35,last=False):
 end=time.time()+seconds
 while time.time()<end:
  try:
   matches=[n for n in nodes() if any(norm(n.get(k))==norm(text) for k in ['text','content-desc'])]
   if matches:return matches[-1] if last else matches[0]
  except (RuntimeError,ET.ParseError):pass
  time.sleep(1)
 raise RuntimeError('Expected screen/control unavailable')
def tapnode(n):
 coords=list(map(int,re.findall(r'\d+',n.get('bounds',''))))
 if len(coords)!=4:raise RuntimeError('Control bounds unavailable')
 adb('shell','input','tap',str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2));time.sleep(1)
def tap(text,last=False):tapnode(find(text,last=last))
def fill(password,value):
 end=time.time()+20
 while time.time()<end:
  fields=[n for n in nodes() if n.get('class')=='android.widget.EditText' and (n.get('password')=='true')==password]
  if fields:
   tapnode(fields[0]);adb('shell','input','text',shlex.quote(value.replace(' ','%s')));adb('shell','input','keyevent','KEYCODE_BACK');return
  adb('shell','input','swipe','400','1100','400','400','350');time.sleep(1)
 raise RuntimeError('Login input unavailable')
def check(name,fn):
 try:fn();checks.append({'name':name,'status':'passed'})
 except Exception:checks.append({'name':name,'status':'failed'});raise RuntimeError('Native authenticated check failed; private details suppressed') from None
completed=False
try:
 for number in [1,2]:
  email=os.environ.get('QA_EMAIL_'+str(number),'');password=os.environ.get('QA_PASSWORD_'+str(number),'')
  if not email or not password:raise RuntimeError('Configure encrypted QA_EMAIL_1/2 and QA_PASSWORD_1/2 secrets first')
  adb('shell','pm','clear','com.arrivetogether.app');adb('shell','am','start','-W','-n','com.arrivetogether.app/.MainActivity')
  find('Explore',60);tap('Profile');find('Sign in & explore Canada');fill(False,email);fill(True,password);tap('Sign in',last=True)
  def signed_in():
   time.sleep(3);tap('Profile');find('Your account')
  check('QA account '+str(number)+' native login',signed_in)
  def trips():tap('My crews');find('Shared travel plans')
  check('QA account '+str(number)+' signed-in crews screen',trips)
  def sign_out():
   tap('Profile')
   for _ in range(12):
    try:tapnode(find('Sign out',seconds=1));break
    except RuntimeError:adb('shell','input','swipe','400','1400','400','400','300')
   find('Sign in & explore Canada')
  check('QA account '+str(number)+' native logout',sign_out)
 completed=True
finally:
 adb('shell','am','force-stop','com.arrivetogether.app');adb('shell','pm','clear','com.arrivetogether.app')
 out=pathlib.Path('test-results');out.mkdir(exist_ok=True)
 (out/'native-auth.json').write_text(json.dumps({'runId':os.environ['GITHUB_RUN_ID'],'apkSha256':os.environ.get('APK_SHA256'),'transport':'Android UI','status':'passed' if completed else 'failed','checks':checks,'limitations':['No signed-in screenshots or UI trees are retained.','Crew approval/chat business rules are covered by the separate live backend test report.','No payment charge or identity document submission.']},indent=2))
