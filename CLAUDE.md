# Karma Food App – Projekt-Notizen für Claude Code

Internes Bestell-/Betriebssystem für die Karma-Food-Filialen (Raihmann GmbH). Sprache in UI, Kommentaren und Commits: Deutsch (Österreich). Begriff "Lunch-Location" statt "Restaurant".

## Architektur
- **Kein Build-Schritt.** Eine riesige Single-File-PWA: `public/index.html` (~15.600 Zeilen, ~1,5 MB, Vanilla JS, Inline-CSS/-JS). Hosting: Vercel (statisch), siehe `vercel.json`.
- **`public/` ist die Wahrheit.** Vercel liefert nur `public/**` aus. Die Dateien im Repo-Root (`index.html`, `menu_data.js`, `menu_sommer.js`, `manifest.json`, `icon-512.png`) sind ältere Kopien. Nicht dort editieren, bevor das geklärt ist.
- `public/bestellen.html`: separate Bestellseite, wird per Host-Routing unter `bestellen.karmafood.at` / `karma-bestellen.vercel.app` ausgeliefert.
- `public/menu_data.js`, `public/menu_sommer.js`: Menüdaten (Minified, eine Zeile). Werden von `tools/menu_check.py` gegen das Leading Sheet geprüft.
- Externe Libs per CDN: `@emailjs/browser@4`, `xlsx@0.18.5`.

## Backend: Supabase
- Projekt **"Karma Food"**, Ref `fkliyqjxnttzyuzogrng`, eu-west-1. (Andere Projekte: "Karma Food Finanzen" `trkilwskstkeeitfolmj`, "Onboarding Chefcook" inaktiv.)
- Zugriff aus der App per REST über den Helper `api(path, opts)` (~Zeile 1790) mit publishable Anon-Key (steht absichtlich im Client, ist öffentlich). Storage-Bucket `gericht-fotos`.
- Login in der App läuft über Filial-PINs (Tabelle `stores`), nicht über Supabase Auth. Das heißt: **RLS-Policies sind die einzige echte Zugriffskontrolle.**
- ~100 Tabellen im `public`-Schema. Schema-Änderungen als SQL-Datei im Repo-Root ablegen (Muster `supabase_*.sql`, `update_*.sql`) und per Supabase-MCP (`apply_migration`) einspielen.
- **Offener Security-Punkt:** RLS ist deaktiviert bei `freitag_checkliste`, `samosa_lock`, `rabatt_codes`, `wochen_erkenntnisse`, `page_views`, `essen_notruf`, `tg_artikel`. Mit dem Anon-Key kann jeder lesen und schreiben. Nur mit Freigabe von Gurl ändern, weil die App sonst Zugriff verliert (Policies müssen zuerst definiert werden).

## Konventionen
- Version: `APP_VERSION` in `public/index.html` (~Zeile 1592, aktuell 6.99.248). Bei jeder Änderung hochzählen. Die App erkennt neue Versionen selbst und zeigt ein Update-Banner. Commit-Message endet mit der Version, z. B. `…, v6.99.249`.
- Der Regex für den Versions-Check darf nicht so geändert werden, dass er sich selbst trifft (siehe Kommentar ~Zeile 1904).
- `api()` setzt `Prefer: return=representation`, `cache: no-store` und 10 s Timeout. Eigene Header immer **zusätzlich** übergeben, nicht ersetzen (Kommentar im Code).
- Ein Fix pro Commit, auf Deutsch, kurz.
- CI/Branding: Boldonse (Headings), Geist (Body); Farben Neongelb #D4FF3F, Orange #E94E1B, Dark Ink, Cream. Die interne App nutzt aktuell Grün (#0F6E56, siehe `manifest.json`), nicht umstellen ohne Rückfrage.

## Tools
- `python3 tools/menu_check.py <sheet.xlsm> [overrides.json] [--epoche …]`: Menü-Gegencheck gegen Drive-Sheet (benötigt `openpyxl`). Nur lesend.
- `python3 tools/schrankerl_check.py <sheet.xlsm> <schrankerl_menu.json>`: Schrankerl-Menü gegen Sheet. Nur lesend.

## Lokal testen
Statisch servieren und im Browser öffnen: `cd public && python3 -m http.server 8080`. Playwright/Chromium ist in der Cloud-Umgebung vorinstalliert. Gegen die echte Produktiv-DB: keine Testdaten schreiben, nichts löschen.

## Hinweise
- `ANLEITUNG.md` ist die alte Setup-Anleitung (verweist noch auf `public/index.html` mit Platzhalter-Keys). Inhaltlich teils veraltet.
- Die Datei ist riesig: gezielt mit `grep -n` suchen und nur Ausschnitte lesen (`Read` mit offset/limit), nicht ganz laden.
