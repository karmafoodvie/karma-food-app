/* Testdaten, die sich am heutigen Datum orientieren (läuft beim ersten Start der Test-Datenbank im Browser).
   Hier eigene Beispieldaten ergänzen, wenn ein neuer Bereich Daten zum Ausprobieren braucht.
   Spalten müssen zur Tabelle passen (siehe data/meta.json). */
(function () {
  window.KF_FIXTURES = function (seed) {
    var now = new Date();
    function iso(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }
    var today = iso(now), tomorrow = iso(new Date(now.getTime() + 864e5)), stamp = now.toISOString();
    seed.geburtstage = [
      { id: 1, name: 'Testperson', tag: now.getDate(), monat: now.getMonth() + 1, jahr: 1990, created_at: stamp },
      { id: 2, name: 'Beispiel Eva', tag: 25, monat: 2, jahr: null, created_at: stamp }
    ];
    seed.stadtgemeinde_stellen = [{ id: 1, name: 'Stadtgemeinde Testhausen', token: 't1', aktiv: true, created_at: stamp, adresse: 'Hauptplatz 1', slug: 'testhausen' }];
    seed.stadtgemeinde_bestellungen = [{ id: 1, liefer_datum: tomorrow, name: 'Max Mustermann', items: [{ name: 'Veggie Curry', menge: 2, preis: 9.9 }], summe: 19.8, zahlung: 'bar', notiz: null, storniert: false, created_at: stamp, stelle_id: 1 }];
    seed.sweets_nachtraege = [{ id: 1, store_id: '1020', order_date: today, text: '2x Brownie extra', status: 'offen', created_at: stamp }];
    seed.notstand_meldungen = [{ id: 1, store_id: 'lb', article_id: null, produkt: 'Curry Boxen', notiz: 'aus', status: 'offen', gemeldet_von: 'Test', created_at: stamp, erledigt_am: null, menge: 5, benoetigt_bis: tomorrow }];
    // erledigter Notruf (ein offener würde als roter Vollbild-Alarm über der Filiale liegen)
    seed.essen_notruf = [{ id: 1, von_store: '3400', an_stores: ['1020', 'lb', 'boerse'], erstellt_am: stamp, erledigt: true, erledigt_am: stamp, gerichte: ['Veggie Curry'], mengen: { 'Veggie Curry': 10 }, status: 'erledigt', absagen: [], zusage_von: null, zusage_menge: null, zusage_am: null, ankunft: null, uber_link: null, uber_am: null }];
    return seed;
  };
})();
