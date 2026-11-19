# Karma Food App — Übergabe & Entwicklerleitfaden

Stand: 19.11.2026 · App-Version 6.99.307 · Zweck: Wer an der App weiterarbeitet (Mensch oder Claude Code), findet hier alles Wichtige an einem Ort.
Diese Datei kann 1:1 als `CLAUDE.md` im Repo-Root verwendet werden.

---

## 1. Was ist die App?

Interne **PWA** (Progressive Web App) für Karma Food (Raihmann GmbH, Wien). Sie ist das zentrale Betriebs-Tool für alle Filialen, die Küche, den Transporter und die Organisation:

- Bestellungen der Filialen (Transporter-Liste, Küche, Sweets, Samosas, Verpackungen)
- Forecast und Produktionsplanung der Küche
- Menü, Zutaten, Allergene (inkl. Meldungen der Filialen)
- Team-Feedback und Gäste-Feedback zu den Gerichten
- Hygiene, Daily Check, Reinigung, Mängel, Kontrollen
- Lager (Küchenlager, Inventur), Entsorgung
- Notruf-Funktionen (Essen-Notruf, dringende Produkt-Meldung)
- Organisation: Rollen, Dienstplan, Geburtstage, Broadcasts, Auswertungen

Sprache der Oberfläche: Deutsch, per Schalter auch Englisch (die Küche und Stadtplatz arbeiten teils auf Englisch).
Marke: **"Lunch-Location"** statt "Restaurant". CI: Boldonse (Überschriften), Geist (Fließtext), Neongelb `#D4FF3F`, Orange `#E94E1B`, Dark Ink `#1a1a18`, Cream.

---

## 2. Stack und Deploy

| Teil | Wo |
|---|---|
| Frontend | **Eine einzige Datei** `public/index.html` (Vanilla HTML/CSS/JS, ca. 22.800 Zeilen, kein Build-Schritt, kein Framework) |
| Hosting | Vercel, Auto-Deploy bei Push auf `main` (Repo `karmafoodvie/karma-food-app`) |
| Datenbank/Backend | Supabase, Projekt `fkliyqjxnttzyuzogrng` (PostgreSQL, REST, Edge Functions, pg_cron) |
| Aufgaben/Reports | Asana (Edge Functions legen Tasks an) |
| Mails | EmailJS (Benachrichtigungen an tini@karmafood.at) |
| Excel-Import | SheetJS im Browser (Odoo-Umsatzdaten) |
| Kassensystem | Odoo 17 Enterprise (Odoo.sh, Brain-Tec), Upgrade-Deadline März 2027 |

`vercel.json`: Alle Pfade gehen auf `public/`; die Hosts `karma-bestellen.vercel.app` und `bestellen.karmafood.at` liefern `public/bestellen.html` (öffentliche Online-Bestellung, z. B. für Stadtgemeinde).

### Repo-Struktur

```
public/index.html      ← DIE App (live). Hier wird entwickelt.
public/bestellen.html  ← Online-Bestellseite (Stadtgemeinde & Co.)
public/menu_data.js    ← Menüplan (Epochen, Wochen, Tage, Gerichte) — live
public/menu_sommer.js  ← alter Sommer-Menüplan
public/images/         ← Gerichtefotos, Hero, Küchen-Supply
public/manifest.json   ← PWA-Manifest
index.html (Root)      ← ALTE Kopie, wird NICHT ausgeliefert. Nicht bearbeiten.
menu_data.js (Root)    ← alte Kopie, ebenfalls nicht live
*.sql                  ← historische Setup-/Migrationsskripte (Referenz, nicht der aktuelle Stand)
ANLEITUNG.md           ← uraltes Setup-Dokument (Erst-Einrichtung)
tools/                 ← menu_check.py, schrankerl_check.py (Menü-Abgleich, lokal)
```

Achtung: Wenn du "index.html" sagst, ist immer `public/index.html` gemeint.

---

## 3. Stores, Rollen, Login

Login erfolgt über Store-Auswahl + PIN. Die PIN wird **serverseitig** geprüft: `checkPin()` ruft `rpc/check_store_pin` (Supabase-Funktion, liest `stores.pin`; die Spalte `pin` ist für den Anon-Key nicht lesbar). Im Frontend-Code steht **kein** PIN-Wert (Stand 6.99.303 geprüft). Nach erfolgreichem Login merkt sich der Browser nur `{id,name}` in `localStorage.kf_store` (kein Token): Das Login schützt also die Oberfläche, **nicht die Daten** (siehe Abschnitt 11). Filiale `1070` ist im Code als geschlossen gesperrt. PINs stehen bewusst nicht in dieser Datei.

| store_id | Standort / Rolle |
|---|---|
| `1020` | Ausstellungsstraße |
| `3400` | Stadtplatz (arbeitet auf Englisch) |
| `boerse` | Börse |
| `lb` | Laurenzerberg |
| `kitchen` | Küche (Kitchen 3401, englischsprachig) |
| `zentrale` | **Organisation** (Management; sieht alles, hat Admin-Funktionen) |

Weitere Rollen als Ansichten/Konten: **Transporter** (Liefer-/Packliste, früher "Michi" genannt — im Text "Transporter" verwenden), **Kassa/Sweets** (Rolle heißt "Kassa", Tabelle `org_roles`), Ines (Shop-Produkte, Packen), Everton (Küche).
Team (Stand Nov 2026): Adi (Koch, Gründer), Simone (Chefin/Admin), Tini (Operations/Architektin der App), Dinesh und Nooru (Küche), Dayan (Stadtplatz), Vincent (Laurenzerberg), Anna (Ausstellungsstraße).

---

## 4. Wie der Code aufgebaut ist

- **Navigation:** `currentView` (Variable) + `goTo(view)`. Jede Ansicht hat eine `renderXyz()`-Funktion, die HTML als String baut und in `#v-xyz` schreibt. Wichtige: `renderHome`, `renderOrder` (+ `ORDER_TABS`: transporter, kc, sweets, kueche, samosas, forecast), `renderKitchen` / `renderKitchenDaily(Html)`, `renderPack` (Transporter-Bestellliste), `renderOrg*` (Organisation), `renderSweets`, `renderKuechenlager`, `renderGeburtstage`, `renderEssenFeedback`, `renderMenuKontrolle`, `renderZutatenManagerBody`.
- **Datenzugriff:** `api(path, {method, body})` ist der Supabase-REST-Helper (PostgREST-Syntax, z. B. `orders?store_id=eq.lb&select=*`). Für große Abfragen **`apiAllPages()`** (Supabase kappt bei ~1000 Zeilen, auch wenn `&limit=` größer ist).
- **Globale Leisten** unter der Topbar: `#bday-banner` (Geburtstag), `#sg-global` (Online-Bestellungen), `#np-global` (Notruf). Sie werden unabhängig von der Ansicht befüllt.
- **Übersetzung:** Inhalte sind in der DB **deutsch**. Bei englischer App-Sprache übersetzt `translateEl()` dynamisch. Bei Zutaten gilt: gespeichert wird Deutsch; angezeigt wird Englisch über `getEffectiveEn()` (Spalte `zutaten_master.name_en`) und sonst `txToEnglish()`. Neue/gemeldete Zutaten werden mit `txToGerman()` (Glossar `ZUTAT_EN_DE`, danach maschinelle Übersetzung) auf Deutsch gespeichert. Elemente mit `data-no-translate` werden nicht übersetzt.
- **Toasts:** `showToast(msg, isError)`.
- **Version:** `const APP_VERSION='6.99.xxx'` (ca. Zeile 1602). Bei **jeder** Änderung hochzählen (Cache-/Update-Erkennung der PWA, Support-Gespräche beziehen sich auf die Nummer).
- **Menü:** `menu_data.js` (Epochen/Wochen/Tage) + Tabelle `menu_overrides` (kurzfristige Änderungen je Epoche/Woche/Tag mit `gueltig_ab`). Epochen-Wechsel (Sommer → Herbst/Winter 07.09.26) hat einmal alle Stores live zerlegt — siehe Regeln.

---

## 5. Datenmodell (die wichtigsten Tabellen)

| Tabelle | Inhalt / Besonderheit |
|---|---|
| `stores`, `articles` | Artikel mit `category` (Verpackungen, Alltag, Food & Drinks, Reinigung, Sweets, Kuechenlager …), `image_url`, `lieferant`, Küchenlager-Felder (`kuechenlager_bestand`, `kuechenlager_notiz`, `bestand_stabil`) |
| `orders` | `store_id, article_id, order_date, quantity, eingepackt`. **`order_date` = Eintragstag.** Die Transporter-Liste zeigt die Einträge des **vorigen Werktags** (`bestellDateStr`). |
| `standing_orders` | Fixbestellungen; werden werktags 04:00 automatisch als Bestellung des Vortags eingetragen, wenn noch keine Zeile existiert |
| `sweets_nachtraege` | Nachträge nach 14:00 (Status offen/ja/nein). "eingearbeitet" (ja) schreibt die Menge in `orders` des Tages und blendet den Nachtrag aus |
| `allergene_rezepturen` | je Gericht `zutaten` (Text, Komma-getrennt, Abschnitt "DIP/SAUCE/TOPPINGS:"), `allergene_codes`, `zkey` (z. B. `3_di_gericht1` = Woche 3, Dienstag, Gericht 1), `crew_bestaetigt`, `aktualisiert_am` |
| `zutaten_master` | Zutaten-Stammdaten: `name`, `kategorie`, **`allergene_codes`**, `name_en`, `base_zutat_id` (Synonyme zeigen auf eine Basis). Die App liest `allergene_codes`; die ältere Spalte `allergene` ist ein Altlast und wird **nicht** ausgewertet. |
| `zutaten_meldungen` | Meldungen der Filialen (typ add/remove/neu; Status offen/bestaetigt/abgelehnt/ueberholt/erledigt). Bestätigen läuft über `zmConfirm`. Sichtbar/bestätigbar nur in der Organisation. |
| `menu_overrides`, `menu_sheet_diffs`, `menu_check_runs` | Menü-Korrekturen und der Abgleich Sheet ↔ App |
| `essen_feedback` | Team-Feedback: `ratings` = `{Gericht: {v:1-5, tags:[…], improve:"Text"}}` (ältere Zeilen: Zahl statt Objekt) |
| `gaeste_feedback` | Gäste-Feedback (Sync alle 10 Min aus dem Gäste-Formular), `kunden_feedback` (Shopify-Link, anonym) |
| `kuechenlager_verlauf` | Wochen-Snapshots der Lagerbestände (Verbrauch = Vorbestand + Zugang − Bestand) |
| `stadtgemeinde_*` | Online-Bestellungen, Preise, Menü, Stellen, Gepackt-Status |
| `essen_notruf`, `notstand_meldungen` | Notruf (Essen übrig/knapp) und Dringend-Meldungen (Produkt fehlt) |
| `org_roles`, `geburtstage`, `org_broadcasts`, `dienstplan_*`, `maengel`, `hygiene_*`, `disposal`, `forecast_*`, `sales_data` | Organisation, Dienstplan, Mängel, Hygiene, Entsorgung, Forecast, Umsatz |

### Allergen-Codes (`ALLERGEN_NAMES`)
A Gluten · B Krebstiere · C Eier · D Fisch · E Erdnüsse · F Soja · G Milch · **H Nüsse** · L Sellerie · M Senf · N Sesam · O Sulfite · P Lupinen · R Weichtiere

Wichtig:
- Beim Speichern eines Gerichts werden die Allergene **aus den Zutaten berechnet und mit den bestehenden vereinigt** (`existing ∪ auto`). Es wird dabei **nie etwas entfernt**. Wird eine Zutat gestrichen, muss der Code ggf. per SQL korrigiert werden.
- Der **Vegan-Badge** wird live aus dem Zutaten-Text berechnet (kein gespeichertes Feld).
- Glutenfrei/Vegan-Aussagen sind rechtlich relevant: Änderungen an `zutaten_master.allergene_codes` immer gegenprüfen (Beispiel 18.11.: Mandeln hatten keinen Code, Cashew nur in der falschen Spalte).

---

## 6. Fachliche Regeln (so ist es gewollt)

- **Sweets:** keine Bestellung für Samstag/Sonntag (`navSweetsDate` überspringt Wochenenden). Nachträge nach 14:00 gehen über `sweets_nachtraege`; "nicht mehr möglich" wird nicht eingetragen. Sweets erscheinen in der Transporter-Liste als eigener Block "🍰 Sweets — Verteilung".
- **Transporter-Liste:** Kategorien `TRANSPORTER_CATS = ['Verpackungen','Alltag','Food & Drinks','Reinigung']` + Sweets; Zeile mit Artikelfoto. Zweiter Reiter "📦 Inventur Verpackungen & Lager" = zentrales Küchenlager (die frühere Filial-Inventur gibt es nicht mehr; die Funktion `renderInventurTab` ist unbenutzt).
- **Kitchen:** Dienstags erscheint der Hinweis zur Küchenlager-Inventur.
- **Töne/Signale:** siehe eigenen Abschnitt 6a.
- **Zutaten-Meldungen der Filialen:** Stadtplatz meldet "fehlt/angepasst". Die Meldung ist sofort für alle Filialen sichtbar (Overlay), die Karte "ZUTATENLISTE — Änderungen aus den Filialen" erscheint **nur in der Organisation** (Küche ist damit nicht belastet). Bestätigen schreibt in `allergene_rezepturen`. Bei englischer Sprache wird die Zutat englisch angezeigt, gespeichert wird deutsch.
- **Zutaten-Editor (Küche):** Änderungen gelten erst nach Klick auf "💾 Speichern". Tap daneben oder "Abbrechen" verwirft still. Freitext-Zutaten, die nicht in der Master-Liste stehen, werden nicht gespeichert (kurzer Toast). → Bekannter Schwachpunkt (siehe Abschnitt 9).
- **Geburtstage:** Tabelle `geburtstage` (name, tag, monat, jahr optional). Banner mit Boldonse, Konfetti-Burst einmal pro Tag und Gerät.
- **Wechselgeld:** Anfrage an den Transporter, nicht mehr als ca. 150 € in der Kassa; Ablauf-Info als Aufklapper (Kuvert für den Fahrer, Münzen einsortieren, **nicht in den Safe**).
- **Weniger Klicks:** Bei "Start your shift" und Daily Check-up so wenige Abfragen wie möglich — sonst wird nichts mehr ausgefüllt.


### 6a. Töne und Signale (Web Audio, seit 18./19.11.2026)

Alle Töne werden im Browser erzeugt (Web Audio API, **keine Audiodateien**), über den gemeinsamen `AudioContext` `_notrufCtx`, der beim ersten Tippen/Tastendruck entsperrt wird (`notrufUnlockAudio`).

| Funktion | Klang | Wird ausgelöst bei |
|---|---|---|
| `kfBing()` | zwei weiche Sinus-Töne (880 Hz, dann 1318 Hz nach 0,16 s), ca. 0,7 s, Vibration kurz | **Essen-Notruf** (Wiener Locations, wiederholt alle 5 s bis zur Antwort), **Notruf-Info** für Stadtplatz/Kitchen/Organisation, **Dringend-Meldung** (🚨 Produkt fehlt) in der Organisation |
| `notrufBeep()` | ruft nur noch `kfBing()` auf (der frühere schrille Dreifach-Alarmton ist entfernt, 19.11.) | Essen-Notruf-Alarm (`showEssenNotrufAlarm` → `notrufBeep` + `notrufStartLoop`) |
| `kfChime()` | aufsteigender Dreiklang (C5 523 Hz, E5 659 Hz, G5 784 Hz, Dreieckwelle), je ca. 1,1 s ausklingend, Vibration kurz | **Neue Online-Bestellung** (Stadtgemeinde, KH, Essl, Baubehörde u. a. über `bestellen.html`) in der Kitchen |

Details und Regeln:
- **Online-Bestellungen:** `kdSgPopupCheck(false)` (Kitchen, Abfrage jede Minute) vergleicht die offenen Bestellungen mit `localStorage['kf_sg_bing_<Datum>']`. Nur neue IDs lösen `kfChime()` aus — pro Gerät und Tag einmal je Bestellung, nach einem Neuladen kein erneuter Ton. Wenn das Bestell-Pop-up schon offen ist, kommt kein zweiter Ton.
- **Essen-Notruf:** Empfänger sind `NOTRUF_WIEN = ['lb','boerse','1020']` (ohne den Absender, ohne Standorte, die abgesagt haben) mit Alarm-Overlay und Antwort-Buttons. Alle anderen Standorte (Stadtplatz `3400`, `kitchen`, `zentrale`) bekommen über `notrufInfoPing(rows)` ein einmaliges Bing plus Toast "🆘 Notruf: <Standort> braucht Essen" — ohne Overlay und ohne Antwort-Buttons. Beim ersten Laden der Seite gibt es keinen Ton für bereits offene Notrufe (`_notrufPingInit`).
- **Abfrage-Takt:** `checkEssenNotruf` läuft alle 10 s (`setInterval(checkEssenNotruf, 10000)`), Online-Bestellungen jede Minute (`_kdSgGlobalTimer`).
- **Dringend-Meldung (`renderNotstandZentrale`):** Toast + Bing nur in der Organisation, nicht beim allerersten Laden (`window._notstandInit`).
- **Grenzen:** Browser erlauben Ton erst nach der ersten Interaktion mit der Seite; bei gesperrtem Bildschirm oder geschlossener App kommt **kein** Ton; auf iPhone/iPad hängt die Lautstärke am Stumm-Schalter. Abhilfe wären echte Push-Benachrichtigungen (Service Worker + Web Push) — noch nicht gebaut.
- **Hörproben:** Die Töne lassen sich als WAV nachrechnen (Parameter siehe oben); für Änderungen nur die Zahlen in `kfBing()`/`kfChime()` anpassen (`frequency`, Anstieg `0.02`/`0.03` s, Ausklang `0.7`/`1.1` s, Lautstärke `0.35`/`0.3`).
- **Wenn der Ton fehlt:** 1) Wurde nach dem App-Start einmal getippt? 2) Stumm-Schalter/Lautstärke? 3) Ist die Bestellung/der Notruf wirklich neu (Gerät hat die ID schon gemerkt)? 4) Konsole auf Fehler prüfen (`try/catch` schluckt Fehler absichtlich).

---

## 7. Edge Functions und Cron (Supabase)

| Function | Zweck |
|---|---|
| `kuechenlager-wochenreport` | Dienstag 15:00 (Wien): Snapshot, Verbrauch, Bestellvorschlag, Asana-Task für Simone (Projekt SHOPS) |
| `dish-retrospektive` | **NEU (Test):** Wochen-Retrospektive je Gericht aus Team-/Gäste-/Online-Feedback, mit Zusammenfassung für Adi und Ausblick. Legt einen Asana-Task an (Standard: Tini). Aufruf per POST mit Header `x-cron-secret`; Parameter `von`, `bis`, `assignee`, `dry_run`. **Noch kein Cron-Job** — geplant: freitags nachmittags. |
| `asana-wochenbestellung`, `nachschub-sammelbestellung`, `asana-nachschub-anfrage`, `asana-sonderbestellung` | Bestell-/Nachschub-Tasks in Asana |
| `asana-schadensmeldung` (+ `-sync`, `-sync-all`) | Schadensmeldungen/Mängel nach Asana |
| `stadtgemeinde-bestellung` | Online-Bestellung der Stadtgemeinde |
| `gaeste-feedback-sync` | Holt Gäste-Feedback alle 10 Min in `gaeste_feedback` |
| `kunden-feedback-read` | Liest anonymes Kunden-Feedback |

pg_cron-Jobs (Stand 19.11.): `asana-schaeden-sync-0700`, `forecast-fallback-6-30-vienna`, `gaeste-feedback-sync` (alle 10 Min), `kuechenlager-wochenreport-di-1500`, `kunden-feedback-retention`, `nachschub-involo-1500`, `stadtgemeinde-anonymisieren`, `standing-orders-0400` (Mo–Fr), `supply-vorwoche-0410`. Einige laufen stündlich in UTC und prüfen die Wiener Uhrzeit — Details im jeweiligen Job (`select * from cron.job`).

Asana: Simone `1205949823315374`, Tini `1208203554133464`, Adi `1206121517642047`, Ines `1206056052548139`; Projekt SHOPS `1206467470914728`. Hinweis: `search_tasks` in Asana ist Premium; Dinesh hat keinen Asana-Zugang.

---

## 8. Entwicklungsregeln (hart erkauft)

1. **Datenbank-Fehler zuerst diagnostizieren, dann Code ändern.** Bei "duplicate key"/"constraint": erst Diagnose-SQL (`pg_constraint`, `GROUP BY … HAVING COUNT(*)>1`), Ursache an echten Daten bestätigen, dann Fix.
2. **Kein Upsert bei `forecast_qty` & Co.:** erst DELETE (auch `groesse is null`), dann INSERT. Gleichzeitige Speicherungen aus verschiedenen App-Versionen überschreiben sich still.
3. **Supabase-Limit ~1000 Zeilen:** `apiAllPages()` nutzen, bei Forecast explizit hohe Limits.
4. **Keine verschachtelten Backtick-Templates** für HTML. Stattdessen Funktionen auslagern oder Strings verketten. Variablen, die in Templates gebraucht werden, im äußeren Scope deklarieren (sonst weißer Bildschirm).
5. **Zeitzonen:** Österreich ist UTC+1/+2. Datumsrechnung nur mit dem vorhandenen Helper (`dateMinusDays()`), nie `getTime()-N*86400000` + `toISOString()`.
6. **Zutaten-Matching:** immer den längsten/spezifischsten Master-Eintrag nehmen ("Paprika pulver" ≠ "Paprika").
7. **Keine strukturellen/großen Änderungen im Betrieb** (Mo–Fr ca. 07–15 Uhr). Ein Epochen-Umbau mitten am Tag hat einmal alle Stores lahmgelegt. Vor größeren Deploys alle Ansichten durchklicken.
8. **Minimal-invasiv ändern:** Küche, Everton, Transporter und Ines-Screens dürfen durch Änderungen an anderen Bereichen nicht kaputtgehen.
9. **Vor jedem Commit:** Inline-Scripts auf Syntax prüfen, z. B.
   ```bash
   node -e "const s=require('fs').readFileSync('public/index.html','utf8');const m=[...s.matchAll(/<script(?![^>]*src)[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]).join('\n');try{new Function(m);console.log('syntax ok')}catch(e){console.log('ERR',e.message)}"
   ```
10. **Commit-Stil:** `vX.Y.Z: kurze Beschreibung` (siehe Git-Log), APP_VERSION im selben Commit hochzählen, dann `git push` → Vercel deployt automatisch.
11. **SQL:** DML (Daten) per SQL-Editor/MCP; DDL-Migrationen mit Vorsicht (ein `apply_migration` für `onboarding_program` ist zweimal hängen geblieben).

---

## 9. Changelog (Auszug, neueste zuerst)

- **6.99.307** Eigener Dreiklang (`kfChime`) für neue Online-Bestellungen in der Kitchen
- **6.99.306** Notruf-Alarm: schriller Alarmton ersetzt, überall nur noch das sanfte Bing
- **6.99.305** Notruf-Info (Bing + Hinweis) auch für Stadtplatz, Kitchen und Organisation
- **6.99.304** Kashmiri Kokos Curry: "Glutenfrei ohne Chili Crisp" statt "ohne geröstete Zwiebel"; Chili-Crisp-Foto statt Chilischote auf den Gerichte-Karten (`dishTopIconHtml`)
- **6.99.303** Wechselgeld-Ablauf als aufklappbare Info
- **6.99.302** Zutaten-Anfragen der Filialen nur noch in der Organisation (nicht mehr in der Küche)
- **6.99.301** Zutaten-Änderungen bei englischer Sprache auf Englisch angezeigt
- **6.99.300** Transporter-Reiter "Inventur Verpackungen & Lager" besser auffindbar
- **6.99.299** "Bing" bei neuen Online-Bestellungen, Alarmton bei neuer Dringend-Meldung
- **6.99.298** Neue/fehlende Zutaten aus englischer Eingabe werden deutsch gespeichert
- **6.99.297** Artikelfotos in der Transporter-Bestellliste
- **6.99.296** Bestell-Verlauf für Filialen (letzte 14 Tage)
- **6.99.295** Sweets in der Transporter-Liste, Küchenlager-Hinweis in Kitchen
- **6.99.294** Sweets-Nachtrag "eingearbeitet" trägt in die Tabelle ein
- **6.99.293** Sweets ohne Samstag/Sonntag
- **6.99.291/292** Geburtstags-Banner (Boldonse, Konfetti, Lauftext, Burst)
- **6.99.284–290** Online-Bestellungen (globale Leiste, "nicht verfügbar" je Gericht/Tag), Nachproduktion, Kitchen-Zeile in Mengen-Tabellen

Direkte DB-Änderungen der letzten Tage (nicht im Code): Geburtstage Samer (25.02.) und Anna (17.11.); Rolle Kassa/Sweets heißt "Kassa"; Butter Veggie Curry (vegan-Namen entfernt, Allergen G); Nuss-Allergene (`H`) bei Mandeln/Cashew in `zutaten_master` und bei 11 Gerichten nachgetragen, Erdnuss (`E`) beim Satay-Curry.

---

## 10. Offene Punkte und Ideen

**Zutaten-Pflege (Dayan korrigiert täglich neu):** Ursache ist sehr wahrscheinlich, dass in der Küche nicht gespeichert wird (nur "💾 Speichern" zählt; ohne Warnung beim Verwerfen). Vorschläge: Warnung "Änderungen nicht gespeichert", Zeile "zuletzt gespeichert HH:MM von Küche" je Gericht, Meldungen der Filialen automatisch übernehmen, Hinweis "wartet auf Bestätigung" für Filialen.

**Weitere offene Themen:**
- `dish-retrospektive` als wöchentlichen Cron (Freitag) einrichten; Empfänger festlegen (Tini/Adi). Ausblick ist aktuell regelbasiert aus Tags (kein freier Text).
- Onboarding für Transporter: Tabelle `onboarding_program` fehlt noch (Migration hing), Entwurf in `claude/transporter_onboarding_entwurf.md` im Projekt.
- Asana-Reminder für Ines (Deckel/Becher): Link zur Liste ergänzen — Task im Asana noch nicht identifiziert.
- Breitere Artikelspalte/größere Fotos in der Transporter-Liste; Test-Button für den Geburtstags-Burst.
- Push-Notifications (Ton bei geschlossener App/gesperrtem Bildschirm) — Töne laufen derzeit nur bei geöffneter App (siehe 6a).
- Wochen-Forecast-Modul (Organisation plant, Stores sehen/ändern mit Log; Salat als Sonderfall), Marktamtkontrolle-Modul (Konzept fertig, kein Code).
- Weitere: Samosa/Chutney-Preise, Wareneingangskontrolle-Fehler (Ausstellungsstraße, Fehlertext fehlt), Sojabohnen-Inventur, Becher-/Deckel-Zählung, ENLIT-Mengenanpassung, doppelte `alt_zahlungen`-Zeilen (ids 7, 10, 11).
- Kunden-Allergenkennzeichnung: Älteren Wochen und weitere Nuss-Zutaten (Pesto, Marzipan …) auf fehlende `H`-Codes prüfen.

---

## 11. Sicherheitshinweise

- **RLS ist bei diesen Tabellen aus** (für den Anon-Key les-/schreibbar): `freitag_checkliste`, `samosa_lock`, `rabatt_codes`, `wochen_erkenntnisse`, `page_views`, `essen_notruf`, `tg_artikel`. Entscheidung nötig: RLS aktivieren und Policies ergänzen (sonst sperrt man die App aus) oder bewusst offen lassen.
- Der Supabase-Anon-Key steht im Frontend (normal bei Supabase); alle Schreibrechte hängen an den RLS-Policies — deshalb obige Liste prüfen.
- Mehrere Edge Functions (`kuechenlager-wochenreport`, `dish-retrospektive`) haben einen **fest eingetragenen Fallback für das Cron-Secret** im Quellcode. Empfehlung: nur noch Umgebungsvariable `CRON_SECRET` verwenden, den Fallback entfernen und das Secret rotieren.
- **Kein Rate-Limit bei `check_store_pin`:** Mit dem öffentlichen Anon-Key sind 4-stellige PINs (10.000 Kombinationen) durchprobierbar. Idee: Fehlversuche je Filiale zählen und nach 5 Fehlversuchen 10 Minuten sperren (Umsetzung in der Funktion, gleiche PINs bleiben gültig).
- **RLS-Vorschlag liegt bereit:** `supabase_rls_fix.sql` (Repo-Root) aktiviert RLS für die 7 offenen Tabellen mit genau den Rechten, die `public/index.html` pro Tabelle nutzt. **Noch nicht angewendet.** Vor dem Einspielen mit dem Team abstimmen und danach alle Ansichten durchklicken. Rollback: `ALTER TABLE public.<tabelle> DISABLE ROW LEVEL SECURITY;`
- Echten Schutz gibt es erst mit Token statt reinem Anon-Key (PIN → Edge Function → signiertes Token, RLS je Filiale). Größeres Projekt, nicht kurzfristig.
- Keine PINs, Tokens oder Schlüssel in diese Datei oder in Commits schreiben.

---

## 12. Mit Claude Code an der App arbeiten

- Dieses Dokument als `CLAUDE.md` in den Repo-Root legen.
- Vor jeder Änderung: betroffene `renderXyz()`-Funktion lesen (`grep -n "function renderXyz" public/index.html`), nicht die ganze 1,6-MB-Datei laden.
- Änderungen klein halten, APP_VERSION erhöhen, Syntax prüfen, committen, pushen — außerhalb der Betriebszeiten, wenn die Änderung groß ist.
- Datenfragen mit der Supabase-MCP-Verbindung prüfen (`execute_sql`), erst lesen, dann schreiben.
- Das Team schickt Probleme per Screenshot/WhatsApp-Auszug: zuerst in den Daten nachsehen (`orders`, `allergene_rezepturen`, `zutaten_meldungen` …), dann den Code anfassen.

---

## 13. Apple-Design (Option, Stand 19.11.2026)

- Branch **`claude/apple-design`** (Version 6.99.308, Basis 6.99.307): iOS-„Liquid Glass“-Optik als **Option**. Standardmäßig **aus**; einschalten mit `?design=apple` an der Adresse (merkt sich der Browser in `localStorage.kf_design`), ausschalten mit `?design=off`. Alles Design-CSS steht in `<style id="apple-skin">` und wirkt nur mit der Klasse `html.apple`. Keine Logik-, Daten- oder Login-Änderung.
- **Schriftarten bleiben unverändert** (Boldonse für Überschriften wie bisher). Das Design ändert nur Flächen, Glas, Farben, Abstände.
- Glas nur auf der Funktionsebene (obere Leiste, Tab-Leiste, Menüs, Toast), Inhalt in ruhigen Flächen; Rückfälle für „Transparenz reduzieren“, „Kontrast erhöhen“, „Bewegung reduzieren“, fehlende Unterstützung und schwache Geräte (`html.apple.noglass`, auch per `localStorage.kf_glass='off'`). Kein Dunkelmodus (viele Inline-Farben sind fest hell).
- Geprüft in einer lokalen Test-Umgebung (nicht im Repo): 40 Ansichten × 5 Rollen × Handy/Desktop, jeweils mit und ohne Design: kein Überlauf, keine neuen JS-Fehler. **Nicht geprüft:** echte Geräte (iPhone, Android-Tablets) und die Vercel-Preview.
- Livegang-Plan: Vercel-Preview mit `?design=apple` durchklicken, zuerst auf einem Gerät pilotieren, dann für alle einschalten; nur außerhalb der Betriebszeiten (Regel 7). Rückweg: `?design=off` oder Revert/Rollback in Vercel.
- Vor dem Merge den Branch auf den aktuellen `main` rebasen und `APP_VERSION` neu setzen (andere Commits zählen die Version hoch).
