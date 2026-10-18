import pathlib,os,json,urllib.request,urllib.error,base64
p=pathlib.Path('test-results/native-auth.json');data=p.read_bytes();assert len(data)<64000
report=json.loads(data);assert report['status'] in ['passed','failed']
u='https://api.github.com/repos/'+os.environ['GITHUB_REPOSITORY']+'/contents/results/native-auth.json'
headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json'}
body={'message':'Publish sanitized native account test status','content':base64.b64encode(data).decode()}
try:body['sha']=json.load(urllib.request.urlopen(urllib.request.Request(u,headers=headers),timeout=30))['sha']
except urllib.error.HTTPError as e:
 if e.code!=404:raise
with urllib.request.urlopen(urllib.request.Request(u,headers=headers,method='PUT',data=json.dumps(body).encode()),timeout=30) as r:assert r.status in [200,201]
