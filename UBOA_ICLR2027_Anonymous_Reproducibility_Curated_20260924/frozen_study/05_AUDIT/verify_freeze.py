from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
manifest_path=ROOT/'01_FREEZE'/'SCIENTIFIC_FREEZE_MANIFEST.json'
manifest=json.loads(manifest_path.read_text())
errors=[]
for rel,expected in manifest['files_sha256'].items():
    p=ROOT/rel
    if not p.is_file():
        errors.append(f'missing:{rel}')
        continue
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got!=expected:
        errors.append(f'hash:{rel}:{got}:{expected}')
allowed_unhashed={
    '01_FREEZE/SCIENTIFIC_FREEZE_MANIFEST.json',
    '01_FREEZE/MANIFEST_ID.txt',
}
actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
expected_set=set(manifest['files_sha256']) | allowed_unhashed
extra=sorted(x for x in (actual-expected_set) if not x.startswith(('10_IMPLEMENTATION/','11_PREEXEC_AUDIT/','12_POSTRUN_AUDIT/')))
missing=sorted(expected_set-actual)
if extra: errors.append('unlisted_files:'+repr(extra))
if missing: errors.append('missing_expected_files:'+repr(missing))
out_files=sorted(str(p.relative_to(ROOT)) for p in (ROOT/'09_OUTPUTS').rglob('*') if p.is_file())
if out_files != ['09_OUTPUTS/README.md']:
    errors.append('unexpected_outputs:'+repr(out_files))
manifest_id=hashlib.sha256(json.dumps(manifest['files_sha256'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
if manifest_id != manifest['manifest_id']:
    errors.append('manifest_id_internal_mismatch')
mid=(ROOT/'01_FREEZE'/'MANIFEST_ID.txt').read_text().strip()
if mid != manifest['manifest_id']:
    errors.append('manifest_id_file_mismatch')
if errors:
    print('SCIENTIFIC_FREEZE_VERIFY=FAIL')
    for e in errors: print(e)
    sys.exit(1)
print('SCIENTIFIC_FREEZE_VERIFY=PASS')
print('manifest_id=',manifest['manifest_id'])
