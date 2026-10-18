import os,json,urllib.request,urllib.error,base64,pathlib
repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GH_TOKEN'];base='https://api.github.com/repos/'+repo+'/contents/results/'
def call(method,url,data=None):
 r=urllib.request.Request(url,method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'},data=None if data is None else json.dumps(data).encode())
 return json.load(urllib.request.urlopen(r,timeout=30))
for p in sorted(pathlib.Path('test-results').glob('*'),key=lambda p:p.name=='latest.json'):
 if p.suffix not in ['.png','.json']:continue
 url=base+p.name;payload={'message':'Publish APK smoke test evidence','content':base64.b64encode(p.read_bytes()).decode()}
 try:payload['sha']=call('GET',url)['sha']
 except urllib.error.HTTPError as e:
  if e.code!=404:raise
 call('PUT',url,payload)
print('Published guest-only test evidence.')
