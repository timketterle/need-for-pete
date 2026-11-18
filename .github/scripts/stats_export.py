# Exportiert die Spieler-Statistik (gm/st + gd/st) als spieler.json und spieler.md (läuft in GitHub Actions, kostenlos).
import json, urllib.request, datetime, sys
from zoneinfo import ZoneInfo
DB = 'https://need-for-pete-default-rtdb.europe-west1.firebasedatabase.app'
TZ = ZoneInfo('Europe/Berlin')
def get(p):
    with urllib.request.urlopen(DB + p + '.json', timeout=20) as r:
        return json.loads(r.read() or b'null')
now = datetime.datetime.now(TZ); now_ms = now.timestamp() * 1000
meta = get('/gm/st') or {}
out = []
for k, m in meta.items():
    try: rec = json.loads(get(f'/gd/st/{k}') or '{}')
    except Exception: rec = {}
    rec.update(k=k, n=rec.get('n') or m.get('n'), t=m.get('t', 0), online=(m.get('t', 0) > now_ms - 200000), v=m.get('v', ''))
    out.append(rec)
out.sort(key=lambda e: (-e['online'], -e['t']))
out_dir = sys.argv[1]
json.dump({'stand': now.isoformat(timespec='minutes'), 'spieler': out}, open(out_dir + '/spieler.json', 'w'), ensure_ascii=False, indent=1)
def dur(s):
    s = int(s or 0); h, m = s // 3600, s % 3600 // 60
    return f'{h} h {m:02d} min' if h else f'{m} min'
def when(t):
    return datetime.datetime.fromtimestamp(t / 1000, TZ).strftime('%d.%m. %H:%M') if t else '-'
today = now.strftime('%Y-%m-%d')
L = [f'# Need For Pete: Spieler-Statistik', f'Stand: {now.strftime("%d.%m.%Y %H:%M")} (deutsche Zeit). Online = Lebenszeichen in den letzten gut 3 Minuten.', '',
     f'Online jetzt: {sum(e["online"] for e in out)} · Spieler gesamt: {len(out)} · heute Daily gespielt: {sum(1 for e in out if today in (e.get("daily") or {}))}', '',
     '| Name | Online | Level | XP | Münzen | Spielzeit | gefahren | Fahrten | Daily heute | zuletzt | Fahrer |', '|---|---|---|---|---|---|---|---|---|---|---|']
for e in out:
    d = (e.get('daily') or {}).get(today)
    L.append(f'| {e.get("n")}{" (Gast)" if e.get("guest") else ""} | {"ja: " + str(e.get("what","")) if e["online"] else "nein"} | {e.get("lv","?")} | {e.get("xp",0)} | {e.get("coins",0)} | {dur(e.get("play"))} | {dur(e.get("drive"))} | {e.get("runs",0)} | {(str(d["n"])+"x, "+str(d["pts"])+" P, "+str(d["m"])+" m") if d else "-"} | {when(e["t"])} | {e.get("dr","")} |')
L += ['', '## Details pro Spieler']
for e in out:
    L.append(f'### {e.get("n")} (Schlüssel {e["k"]}{", Konto Nr. "+str(e["num"]) if e.get("num") else ""})')
    L.append(f'- Level {e.get("lv")} · {e.get("xp",0)} XP · {e.get("coins",0)} Münzen · Fahrzeug {e.get("veh")} · {e.get("flips",0)} Saltos · {e.get("sess",0)}x geöffnet · Gerät {e.get("dev","?")}{" (Home-Bildschirm)" if e.get("pwa") else ""} · dabei seit {when(e.get("first"))}')
    dl = e.get('daily') or {}
    L.append('- Daily: ' + (' · '.join(f'{k}: {o.get("n")}x, bis {o.get("m")} m, {o.get("pts")} P' for k, o in sorted(dl.items(), reverse=True)) or 'noch nie'))
    tr = sorted((e.get('tr') or {}).items(), key=lambda x: -x[1].get('n', 0))
    L.append('- Eigene Level: ' + (' · '.join(f'{k}: {o.get("n")}x, bis {o.get("m")} m, {o.get("fin",0)}x Ziel' for k, o in tr) or 'noch keine'))
    b = {k: v for k, v in (e.get('bests') or {}).items() if v}
    if b: L.append('- Bestweiten: ' + ', '.join(f'{k} {v} m' for k, v in b.items()))
open(out_dir + '/spieler.md', 'w').write('\n'.join(L) + '\n')
print(len(out), 'Spieler exportiert')
