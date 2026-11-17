# Sends Web Push messages to friends when someone plays the daily (runs every 10 min in GitHub Actions, free).
# VAPID key lives only in the Actions cache (.nfp-push), the public half is published to the database.
import json, os, base64, datetime, urllib.request
from zoneinfo import ZoneInfo
from py_vapid import Vapid01
from pywebpush import webpush, WebPushException
from cryptography.hazmat.primitives import serialization

DB = 'https://need-for-pete-default-rtdb.europe-west1.firebasedatabase.app'
ST = '.nfp-push'
SEASON_T = 1794933800186
SITE = 'https://timketterle.github.io/need-for-pete/'

def get(p):
    with urllib.request.urlopen(DB + p + '.json', timeout=20) as r:
        return json.loads(r.read() or b'null')

def patch(d):
    req = urllib.request.Request(DB + '/.json', data=json.dumps(d).encode(), method='PATCH')
    urllib.request.urlopen(req, timeout=20).read()

def put_str(key, p, val):
    meta = get(f'/gm/{key}/{p}') or {}
    m = (meta.get('m') or 0) + 1
    patch({f'gd/{key}/{p}': val, f'gm/{key}/{p}': {'n': 'push', 'm': m, 'v': 'f1', 'dr': 'pete', 't': {'.sv': 'timestamp'}}})

os.makedirs(ST, exist_ok=True)
pem = ST + '/vapid.pem'
if os.path.exists(pem):
    v = Vapid01.from_file(pem)
else:
    v = Vapid01(); v.generate_keys(); v.save_key(pem)
raw = v.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint)
pub = base64.urlsafe_b64encode(raw).decode().rstrip('=')
if get('/gd/push-cfg/k') != pub:
    put_str('push-cfg', 'k', pub)
    print('published new public key')

date = datetime.datetime.now(ZoneInfo('Europe/Berlin')).strftime('%Y-%m-%d')
sf = ST + '/state.json'
state = json.load(open(sf)) if os.path.exists(sf) else None
board = get('/daily/' + date) or {}
board = {k: e for k, e in board.items() if isinstance(e, dict) and isinstance(e.get('s'), (int, float)) and e.get('t', 0) >= SEASON_T}
top = max(board.items(), key=lambda kv: kv[1]['s'])[0] if board else None

msgs = []  # (player key, text)
if state is None or state.get('date') != date:
    if state is None:  # first run or lost cache: remember silently
        state = {'date': date, 'seen': list(board), 'leader': top}
    else:
        state = {'date': date, 'seen': [], 'leader': None}
for k, e in board.items():
    if k not in state['seen']:
        state['seen'].append(k)
        msgs.append((k, f"{e.get('n', k)} hat das Daily gespielt: {int(e.get('m', 0))} m, {int(e['s'])} Punkte. Schaffst du mehr?"))
if top and state.get('leader') and top != state['leader'] and top in state['seen']:
    e = board[top]
    if not any(k == top for k, _ in msgs):
        msgs.append((top, f"{e.get('n', top)} ist jetzt Tages-Erster mit {int(e['s'])} Punkten!"))
state['leader'] = top
json.dump(state, open(sf, 'w'))

if msgs:
    subs = []
    for a in ['1', '2', '3']:
        d = get(f'/gd/push-sub-{a}/s')
        try:
            o = json.loads(d) if isinstance(d, str) else None
        except Exception:
            o = None
        if o and o.get('k') == pub and o.get('sub'):
            subs.append(o)
    for who, text in msgs:
        for o in subs:
            if o.get('key') == who:
                continue
            try:
                webpush(subscription_info=o['sub'], data=json.dumps({'title': 'Need For Pete', 'body': text, 'tag': 'daily-' + who}),
                        vapid_private_key=pem, vapid_claims={'sub': SITE})
                print('sent to', o.get('key'))
            except WebPushException as ex:
                print('push failed', o.get('key'), str(ex)[:200])
print('done', date, len(board), 'entries', len(msgs), 'messages')
