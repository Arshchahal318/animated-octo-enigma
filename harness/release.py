import urllib.request,json,hashlib,os,pathlib
origin='https://arrivetogether.info'
# Release metadata is derived from the public immutable APK response.
with urllib.request.urlopen(urllib.request.Request(origin+'/download/releases/cee5813db90805ceecd7b679ea0d98ca2737a89254445a19fe0501759fb33ecd/ArriveTogether-Canada-v0.34.0-Release.apk',headers={'User-Agent':'Mozilla/5.0 (compatible; ArriveTogether-QA/1.0)'}),timeout=90) as r:
 data=r.read(60*1024*1024+1)
assert len(data)<60*1024*1024 and data[:2]==b'PK','Invalid APK download'
sha=hashlib.sha256(data).hexdigest();assert sha=='cee5813db90805ceecd7b679ea0d98ca2737a89254445a19fe0501759fb33ecd','Release checksum mismatch';pathlib.Path('app.apk').write_bytes(data)
# aapt provides the installed package version without trusting filenames.
import subprocess,re,glob
bins=sorted(glob.glob(os.environ['ANDROID_HOME']+'/build-tools/*/aapt'))
assert bins,'Android build tools unavailable'
badging=subprocess.check_output([bins[-1],'dump','badging','app.apk'],text=True)
assert "name='com.arrivetogether.app'" in badging
version=re.search("versionName='([^']+)'",badging)[1]
with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('sha='+sha+'\nversion='+version+'\n')
print('Validated APK '+version+' SHA-256 '+sha)
