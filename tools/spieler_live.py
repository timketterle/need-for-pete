#!/usr/bin/env python3
# Live-Spielerdaten Need For Pete direkt aus Firebase (sekundengenau).
# Nutzung: python3 spieler_live.py            -> alle Spieler, online zuerst
#          python3 spieler_live.py niki       -> nur Spieler, deren Name "niki" enthält
#          python3 spieler_live.py --json     -> Rohdaten
import json, sys, urllib.request, datetime, time
from zoneinfo import ZoneInfo
DB = 'https://need-for-pete-default-rtdb.europe-west1.firebasedatabase.app'
TZ = ZoneInfo('Europe/Berlin')
def get(p):
    with urllib.request.urlopen(DB + p + '.json', timeout=20) as r:
        return json.loads(r.read() or b'null')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
q = args[0].lower() if args else ''
meta = get('/gm/st') or {}
now = time.time() * 1000
out = []
for k, m in meta.items():
    if q and q not in str(m.get('n', '')).lower(): continue
    try: r = json.loads(get(f'/gd/st/{k}') or '{}')
    except Exception: r = {}
    age = (now - m.get('t', 0)) / 1000
    r.update(k=k, n=m.get('n') or r.get('n'), t=m.get('t', 0), age_s=round(age), online=age < 200 and not str(m.get('v','')).startswith('X'), v=m.get('v', ''))
    out.append(r)
out.sort(key=lambda e: (not e['online'], -e['t']))
if '--json' in sys.argv:
    print(json.dumps(out, ensure_ascii=False, indent=1)); sys.exit()
def dur(s):
    s = int(s or 0); h, mi = s // 3600, s % 3600 // 60
    return f'{h} h {mi:02d} min' if h else f'{mi} min'
def doing(v):
    return {'R': 'wartet im Raum ' + v[1:5], 'P': 'fährt gerade', 'M': 'im Menü'}.get(v[:1], v)
today = datetime.datetime.now(TZ).strftime('%Y-%m-%d')
print(f'Stand {datetime.datetime.now(TZ).strftime("%d.%m. %H:%M:%S")} · online: {sum(e["online"] for e in out)} von {len(out)}')
for e in out:
    last = datetime.datetime.fromtimestamp(e['t'] / 1000, TZ).strftime('%d.%m. %H:%M')
    st = f'ONLINE, {doing(e["v"])} (Lebenszeichen vor {e["age_s"]} s)' if e['online'] else f'offline, zuletzt {last}'
    d = (e.get('daily') or {}).get(today)
    print(f'- {e["n"]}{" (Gast)" if e.get("guest") else ""}: {st} · Level {e.get("lv","?")} · {e.get("xp",0)} XP · {e.get("coins",0)} Münzen · Spielzeit {dur(e.get("play"))} (gefahren {dur(e.get("drive"))}) · {e.get("runs",0)} Fahrten · Daily heute: ' + (f'{d["n"]}x, bis {d["m"]} m, {d["pts"]} P' if d else 'nein') + f' · Fahrer {e.get("dr","")} · {e.get("dev","?")}')
    tr = sorted((e.get('tr') or {}).items(), key=lambda x: -x[1].get('n', 0))
    if q:
        print('  Daily-Verlauf: ' + (' · '.join(f'{k}: {o["n"]}x, {o["m"]} m, {o["pts"]} P' for k, o in sorted((e.get('daily') or {}).items(), reverse=True)) or 'noch nie'))
        print('  Eigene Level: ' + (' · '.join(f'{k}: {o["n"]}x, bis {o["m"]} m' for k, o in tr) or 'noch keine'))
