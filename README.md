# Need For Pete

Comic-Bergrennspiel für den Browser. Spielen: https://timketterle.github.io/need-for-pete/

- Am iPhone in Safari öffnen, Teilen → „Zum Home-Bildschirm“, dann läuft es wie eine App (Vollbild, offline, Neigesteuerung).
- Duell: Einer tippt DUELL → CODE ERSTELLEN, der andere gibt den Code ein. Verbindung direkt zwischen den Geräten (PeerJS).
- Steuerung am PC: Pfeiltasten rechts/links, Item mit Pfeil hoch oder Leertaste.

## Aufbau
- `src/game.html` ist die Quelle des Spiels. `src/build.py` baut daraus `index.html` und `sw.js` (aus `src/sw.template.js`).
- `peerjs.min.js` (PeerJS 1.5.4) liegt lokal bei.
