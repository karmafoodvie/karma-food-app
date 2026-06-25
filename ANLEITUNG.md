# Karma Food App — Setup Anleitung
# Dauer: ca. 10–15 Minuten, keine Programmierkenntnisse nötig

## SCHRITT 1: Supabase einrichten (Datenbank)

1. Gehe auf https://supabase.com → "Start your project" → kostenlos registrieren
2. Neues Projekt erstellen:
   - Name: karma-food
   - Passwort: ein sicheres Passwort (aufschreiben!)
   - Region: Central EU (Frankfurt)
3. Warte ca. 2 Minuten bis das Projekt bereit ist
4. Gehe zu: SQL Editor (linke Seitenleiste)
5. Klicke "New query"
6. Öffne die Datei `supabase_setup.sql` aus diesem Ordner
7. Den gesamten Inhalt kopieren und in den SQL Editor einfügen
8. Klicke "Run" — du siehst "Success"
9. Gehe zu: Settings → API
10. Notiere dir:
    - "Project URL" → das ist deine SUPABASE_URL
    - "anon public" Key → das ist dein SUPABASE_ANON_KEY

## SCHRITT 2: Keys in die App eintragen

1. Öffne die Datei `public/index.html` in einem Texteditor (z.B. Notepad)
2. Suche nach diesen zwei Zeilen (ganz oben im Script-Bereich):
   ```
   const SUPABASE_URL = 'DEINE_SUPABASE_URL';
   const SUPABASE_ANON_KEY = 'DEIN_SUPABASE_ANON_KEY';
   ```
3. Ersetze die Platzhalter mit deinen echten Werten aus Schritt 1
4. Speichern

## SCHRITT 3: Vercel einrichten (Hosting)

1. Gehe auf https://vercel.com → kostenlos registrieren (mit GitHub oder E-Mail)
2. "Add New Project" → "Upload" (nicht GitHub nötig)
3. Den gesamten Ordner `karma-food-app` hochladen
4. Deploy klicken
5. Nach ca. 30 Sekunden bekommst du eine URL wie:
   `https://karma-food-app.vercel.app`

## SCHRITT 4: App verteilen

Jede Filiale bekommt die URL per WhatsApp/E-Mail.

### Am iPhone (Safari):
- Link öffnen → Teilen-Symbol (unten) → "Zum Home-Bildschirm" → "Hinzufügen"
- → App erscheint am Homescreen wie eine echte App

### Am Android (Chrome):
- Link öffnen → Drei-Punkte-Menü → "Zur Startseite hinzufügen"
- → App erscheint am Homescreen

## PINS der Filialen (kannst du in Supabase jederzeit ändern)

| Filiale              | PIN  |
|----------------------|------|
| 1070 Wien            | 1070 |
| 1020 Wien            | 1020 |
| Börse                | 2626 |
| 3400 Klosterneuburg  | 3400 |
| Klosterneuburg 2     | 4400 |
| LB Laurenzerberg     | 5500 |
| Zentrale/Transporter | 9999 |

PINs ändern: Supabase → Table Editor → stores → Zeile bearbeiten

## Lagerbestand aktualisieren

Supabase → Table Editor → stock → Quantity Werte anpassen

## Artikel hinzufügen/ändern

Supabase → Table Editor → articles → Zeile hinzufügen oder bearbeiten
App aktualisiert sich automatisch beim nächsten Öffnen.

## Checklisten anpassen

Supabase → Table Editor → checklist_templates → Punkte hinzufügen/ändern
list_type: oeffnung / reinigung / abschluss

## Kosten

- Supabase: kostenlos (bis 50.000 Zeilen — ihr erreicht das nie)
- Vercel: kostenlos (bis 100 GB Bandbreite/Monat — mehr als genug)
- Gesamt: 0 €/Monat
