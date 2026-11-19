# Arbeitsumgebung (Test) für die Karma Food App

Hier wird an der App gearbeitet und ausprobiert, **ohne die laufende App und ihre echten Daten zu berühren**.

## Was sie ist

- Eine eigenständige Test-Seite, gebaut aus `public/index.html` (der aktuellen App).
- Sie hat eine **eigene Test-Datenbank im Browser** (`src/mem-core.js`). Alles, was man dort eingibt, bleibt nur im Browser (localStorage) und ist mit „Daten zurücksetzen“ (oranger Streifen oben) weg.
- Startdaten: 7 Filialen, 40 Artikel, Checklisten (`data/seed.json`) plus Beispieldaten, die sich am heutigen Datum orientieren (`src/fixtures.js`: Geburtstag, Online-Bestellung, Sweets-Nachtrag, Dringend-Meldung).
- Die Struktur aller 109 Tabellen steht in `data/meta.json` (Stand 19.11.2026, abgeglichen mit der echten Datenbank).
- **Login in der Testumgebung: Filiale wählen, PIN `1234`** (gilt für alle Filialen). Die echten PINs stehen bewusst nicht im Repo und funktionieren hier nicht.

## Sicherheit (warum die echte App nicht berührt wird)

1. `build.js` biegt **jede** Supabase-Adresse auf eine Pseudo-Adresse um, die nur die Test-Datenbank in der Seite abfängt. Bleibt irgendeine Adresse übrig, **bricht der Bau ab** (getestet).
2. E-Mails (EmailJS) sind gesperrt und werden nur in die Konsole geschrieben.
3. Edge Functions (Asana, Online-Bestellung …) und Storage (Fotos) gibt es im Test nicht; sie antworten mit Fehler 501.
4. Der Ordner liegt außerhalb von `public/`. Vercel liefert nur `public/**` aus, also kommt nichts davon in die echte App.

## Benutzen

```bash
bash test-env/serve.sh          # baut und startet auf http://localhost:8082/index.html
node test-env/build.js          # nur bauen (Ergebnis: test-env/dist/)
node test-env/tests/regress.js  # alle Ansichten, 5 Rollen, Handy + Desktop durchklicken (Playwright nötig)
```

In Claude Code: „Baue die Testumgebung und veröffentliche sie“ – ich baue `dist/` und lege die Seite als privaten Link ab, auf dem du dich durchklicken kannst.

## Arbeitsweise

1. Änderungen entstehen auf dem Branch **`entwicklung`** (oder einem Unter-Branch davon), **nie direkt auf `main`**.
2. Nach jeder Änderung: `APP_VERSION` hochzählen, Syntax prüfen (siehe `CLAUDE.md`, Regel 9), Testumgebung neu bauen, `regress.js` laufen lassen, durchklicken.
3. Erst nach ausdrücklichem „Live“ wird nach `main` gemergt (Vercel deployt dann automatisch). Außerhalb der Betriebszeiten (Regel 7).
4. **Achtung Vercel-Preview:** Ein Preview-Link eines Branches nutzt die **echte Datenbank**, weil die Adresse fest in `index.html` steht. Preview nur zum Ansehen verwenden, **nicht** zum Eingeben von Daten. Zum Ausprobieren immer diese Testumgebung nehmen.

## Eigene Testdaten / neue Tabellen

- Neue Beispieldaten: `src/fixtures.js` ergänzen (Spalten müssen zu `data/meta.json` passen).
- Neue Tabelle in der echten Datenbank: Eintrag in `data/meta.json` ergänzen (Spalten, Primärschlüssel `pk`, Unique-Schlüssel `uq`; Identity-Spalten mit `"id": true` und `"d": null`). Tabellen, die in `meta.json` fehlen, antwortet die Test-Datenbank mit 404.
- Abgleich mit der echten Datenbank (nur lesen): Anzahl der Spalten je Tabelle aus `information_schema.columns` vergleichen.

## Grenzen

- Die Test-Datenbank ist kein echtes Postgres: Fremdschlüssel und Check-Constraints werden nicht geprüft, Funktionen (RPC) gibt es nur für `check_store_pin`. Fehler, die nur von Datenbankregeln kommen (z. B. RLS), zeigt der Test nicht.
- Cron-Jobs, Edge Functions und Asana-Anbindung lassen sich hier nicht testen.
- Echte Geräte (iPhone, Android-Tablets in den Filialen) ersetzt das nicht: vor einem Livegang auf einem echten Gerät kurz prüfen.
- Eine **echte** getrennte Test-Datenbank (eigenes Supabase-Projekt) wäre mit dem aktuellen Gratis-Tarif (2 aktive Projekte) nicht möglich. `reference/schema_v6.99.248.sql` ist das nachgebaute Postgres-Schema (Stand 6.99.248) für den Fall, dass später ein zweites Projekt angelegt wird.
