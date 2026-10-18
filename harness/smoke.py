import subprocess, time, json, pathlib, re, xml.etree.ElementTree as ET, os
out=pathlib.Path('test-results');out.mkdir(exist_ok=True)
report={'runId':os.environ['GITHUB_RUN_ID'],'apkSha256':os.environ['APK_SHA256'],'version':os.environ['APK_VERSION'],'apiLevel':35,'checks':[],'screenshots':[],'limitations':['Guest smoke tests only. Login, crew approval, chat, identity and purchases are not exercised.']}
def adb(*args):return subprocess.check_output(['adb',*args],timeout=40)
def screen(name):
 data=adb('exec-out','screencap','-p');assert data.startswith(b'\x89PNG');(out/(name+'.png')).write_bytes(data);report['screenshots'].append(name+'.png')
def nodes():
 adb('shell','uiautomator','dump','/sdcard/qa.xml');return ET.fromstring(adb('shell','cat','/sdcard/qa.xml'))
def find(text,timeout=25):
 end=time.time()+timeout
 while time.time()<end:
  try:root=nodes()
  except (subprocess.SubprocessError,ET.ParseError):
   time.sleep(2);continue
  for n in root.iter('node'):
   if n.get('text')==text or n.get('content-desc')==text:return n
  time.sleep(1)
 raise AssertionError('Accessible control not found: '+text)
def tap(text):
 n=find(text);coords=list(map(int,re.findall(r'\d+',n.get('bounds',''))));assert len(coords)==4
 adb('shell','input','tap',str((coords[0]+coords[2])//2),str((coords[1]+coords[3])//2));time.sleep(2)
def check(name,fn):
 try:fn();report['checks'].append({'name':name,'status':'passed'})
 except Exception as e:
  report['checks'].append({'name':name,'status':'failed','message':str(e)[:180]});screen('failure')
  (out/'device-log.txt').write_bytes(adb('logcat','-d','-t','500'))
  (out/'activity.txt').write_bytes(adb('shell','dumpsys','activity','activities'))
  raise
completed=False
try:
 check('APK installation',lambda:adb('install','-r','app.apk'))
 adb('shell','input','keyevent','KEYCODE_WAKEUP');adb('shell','wm','dismiss-keyguard');adb('shell','svc','power','stayon','true')
 adb('logcat','-c')
 def launch():
  adb('shell','am','start','-W','-n','com.arrivetogether.app/.MainActivity');find('Explore',45);screen('01-explore')
 check('Launch and render shared interface',launch)
 for label,name in [('Profile','02-profile'),('My crews','03-crews'),('Estimate','04-estimate'),('Explore','05-return')]:
  check('Navigate to '+label,lambda label=label,name=name:(tap(label),find({'Profile':'Sign in & explore Canada','My crews':'Shared travel plans','Estimate':'Fare estimator','Explore':'Same airport. Same way home.'}[label]),screen(name)))
 def relaunch():
  adb('shell','am','force-stop','com.arrivetogether.app');launch()
 check('Cold relaunch',relaunch)
 def crashes():
  log=adb('logcat','-d','-s','AndroidRuntime:E').decode(errors='replace');assert 'FATAL EXCEPTION' not in log,'Android runtime crash detected'
 check('No Android runtime crash',crashes)
 completed=True
finally:
 report['status']='passed' if completed and report['checks'] and all(c['status']=='passed' for c in report['checks']) else 'failed'
 (out/'latest.json').write_text(json.dumps(report,indent=2))
