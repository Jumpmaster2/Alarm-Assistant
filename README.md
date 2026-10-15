# Alarm Assistant

[English version](README.en.md)

Custom Integration für Home Assistant: eine Alarmzentrale mit allem, was sonst in vielen Automationen, Skripten und Helfern steckt. Scharf- und Unscharfschalten (auch automatisch bei Abwesenheit), Ein- und Ausgangsverzögerung, offene Fenster ignorieren, Durchsagen und Alarmton auf Alexa-Geräten, Licht und Rollos bei Alarm, Telefonanruf mit Quittierung über das ha-sip-Add-on, Türschloss, Kamera-Steuerung, Garagen-Kameras, ein Nacht-Türalarm und ein Fenster-offen-Hinweis an der Haustür. Alles wird in der Oberfläche eingestellt, es sind keine eigenen Automationen nötig.

> Status: Version 0.4.2.

## Funktionsweise

Die Integration arbeitet ereignisgesteuert: Sie reagiert nur auf Zustandswechsel der eingestellten Entitäten, gescannte NFC-Tags und berechnete Zeitpunkte (Ende der Ein- oder Ausgangsverzögerung, Auslösezeit, automatisches Scharfschalten, tägliche Rücksetzungen). Jede Aktion steht mit Grund im Logbuch.

### Alarmzentrale

* Modus **Abwesend** mit Ausgangsverzögerung (0 = sofort scharf), Eingangsverzögerung und Auslösezeit. Danach wieder scharf oder, wenn eingestellt, unscharf.
* Optionaler Code (zum Unscharfschalten, wahlweise auch zum Scharfschalten). Gespeichert wird nur ein Hash.
* **Sensoren** werden einzeln angelegt (Unterpunkt "Sensor"): Tür (verzögert), Fenster (sofort), Bewegung (verzögert, darf beim Scharfschalten aktiv sein) oder Sonstiges. Alle Eigenschaften lassen sich pro Sensor ändern.
* **Offene Fenster** werden beim Scharfschalten bis zum Unscharfschalten ignoriert, es kommt eine Benachrichtigung mit den offenen Fenstern. Eine offene Tür verhindert das Scharfschalten (mit Benachrichtigung), außer während einer Ausgangsverzögerung.
* Ein Sensor, der nicht verfügbar wird, löst nicht aus. War er vorher geschlossen und meldet sich offen zurück, löst er aus.
* **Bedingte Kontakte:** Ein Sensor kann so eingestellt werden, dass er nur zählt, solange eine andere Entität nicht verfügbar ist, z. B. eine Balkontür, die für den Schlauch einer mobilen Klimaanlage offen steht. Ist sie beim Scharfschalten offen und zählt nicht, kann ein Rollo auf eine Position fahren.
* Nach einem Neustart bleibt eine scharfe Anlage scharf. Ein laufender Alarm wird nicht wiederholt.

### Bewegungsfilter

* Bewegung zählt nicht, solange der Saugroboter saugt oder zurückfährt, und eine einstellbare Zeit nach dem Andocken.
* Ein **Fehler-Sensor** (z. B. Ausfall der Saugroboter-Anbindung) unterdrückt Bewegung, solange er an oder nicht verfügbar ist. Dazu gibt es technische Meldungen: beim Fehler und bei jeder unterdrückten Bewegung, solange scharf.

### Bei Alarm

* Durchsage an Benachrichtigungs-Entitäten (z. B. Alexa-Durchsage überall) mit eigenem Text, ebenso bei Beginn der Eingangsverzögerung.
* Alarmton: Lautstärke hoch, Sound auf Alexa-Geräten, gesprochener Text, Lautstärke nach einer Zeit zurück.
* Lichter und Schalter einschalten, Rollos schließen.
* **Telefonanruf** über das ha-sip-Add-on: Nummern der Reihe nach. Jede Nummer außer der letzten kann mit Taste 1 quittieren (der Button "Anruf quittieren" wird gedrückt), dann wird niemand mehr angerufen. Der erste Anruf startet vor den Push-Nachrichten. Innerhalb der Sperrzeit gibt es keinen neuen Anruf.
* Push an die Handys und zusätzliche Dienste (z. B. Pushover) mit der **Ursache**: die auslösenden Sensoren und, wenn eine Kamera gerade eine Person sieht, auch diese.

### Automatisch scharf

* Anwesenheit über **Personen** (Unterpunkt "Person"): Jede Person hat den WLAN-Sensor ihres Handys. Ist das Handy mit einem Heim-WLAN verbunden, ist die Person zuhause; dafür gibt es je Person einen Anwesenheitssensor. Alternativ HA-Personen (`person.*`).
* Ist niemand zuhause (seit einer Mindestzeit), war eine Weile keine Bewegung und ist "Kinder alleine zuhause" aus, kommt eine Vorwarnung. Ist danach immer noch alles erfüllt und keine Bewegung gewesen, wird scharf geschaltet. Nach einem Unscharfschalten wird erst nach einer Wartezeit wieder geprüft.
* Abschaltbar über den Schalter **Automatisch scharf**.

### Türschloss und Kinder

* Entriegeln oder Öffnen des Schlosses schaltet unscharf.
* Beim Scharfschalten wird abgeschlossen, wenn die Tür zu ist und keine Kinder alleine zuhause sind.
* **Kinder alleine zuhause** (Schalter) verhindert automatisches Scharfschalten und Abschließen und steuert die Kamera. Er wird eine einstellbare Zeit nach dem Entriegeln und nachts zurückgesetzt.

### Kamera (Unterpunkt "Kamera")

* Scharf oder Kinder alleine zuhause: Privatsphäre-Modus aus, Standard-Preset.
* Unscharf: Privatsphäre-Modus nach einer Wartezeit wieder an (nicht bei Kindern oder Live-Ansicht).
* Bewegung, solange scharf: Preset des jeweiligen Bewegungsmelders.
* Erkennungs- und Aufnahmeschalter (z. B. Frigate): bei Live-Ansicht und Kindern aus, solange der Saugroboter fährt nur die Erkennung aus.
* Person erkannt und nicht unscharf: Push mit Bild.
* Schalter **Kamera Live-Ansicht**.

### Garage (Unterpunkt "Garage")

* Eine zweite Alarmzentrale (z. B. Blink) wird unscharf geschaltet, solange ein Handy mit dem Garagen-WLAN verbunden ist, und eine Zeit nach dem Verlassen wieder scharf.
* Bewegung, solange scharf: Push und gesprochene Warnung auf den Handys (Companion App).
* Schalter **Garage Automatik**.

### Nacht-Türalarm

* Unabhängig von der Alarmzentrale. Eingeschaltet (Schalter oder NFC-Tag) ertönt beim Öffnen der Tür ein lokaler Alarm: Lichter an, Alarmton, gesprochener Text. Kein Anruf, kein Push.
* Derselbe Tag schaltet wieder aus (mit Ansage). Automatisches Ausschalten zu einer Uhrzeit an gewählten Wochentagen.

### Fenster-offen-Hinweis

* Geht die Haustür auf und ist ein Fenster offen, leuchtet ein Licht für eine einstellbare Zeit.

## Installation über HACS

1. HACS öffnen, Menü "Benutzerdefinierte Repositories".
2. `https://github.com/Jumpmaster2/Alarm-Assistant` als Typ "Integration" hinzufügen.
3. "Alarm Assistant" installieren und Home Assistant neu starten.
4. Unter Einstellungen > Geräte & Dienste die Integration hinzufügen.

## Konfiguration

Nach der Einrichtung gibt es in der Seitenleiste die Seite **Alarm Assistant** (nur für Administratoren, ähnlich wie bei Alarmo):

* **Übersicht:** Zustand mit Scharf/Unscharf, Schalter, Personen (zuhause/weg), offene Kontakte, Hinweise, letzter Alarm, Testmeldung und eine Zusammenfassung der Einstellungen.
* **Testalarm:** testweise scharf schalten und auswählen, was passieren soll: jede Reaktion einzeln an oder aus (z. B. keine Durchsage, kein Push an ein bestimmtes Handy, keine Lichter, keine Rollos, nur die erste Anrufnummer). Löst ein Sensor aus oder wird die Auslösung simuliert, läuft alles wie bei einem echten Alarm, nur mit den gewählten Reaktionen. Push-Meldungen beginnen mit [TEST], Durchsagen und Anrufe mit „Achtung, dies ist nur ein Test“. Unscharf schalten beendet den Test, ein Neustart nicht.
* **Sensoren:** alle Kontakte und Bewegungsmelder als Tabelle mit Typ, Verhalten und aktuellem Zustand; anklicken zum Bearbeiten.
* **Alarm, Bei Alarm, Meldungen & Anruf, Anwesenheit, Tür & Extras, Kamera & Garage:** alle Einstellungen nach Themen in Karten, jede Karte wird für sich gespeichert.

Die Einstellungen lassen sich weiterhin auch über den Einrichtungsdialog ändern:

* **Einrichtung:** Benachrichtigungen, Alarmzeiten und Code.
* **Optionen** (Menü): Benachrichtigungen, Alarmzeiten und Code, Bewegungsfilter, Reaktionen bei Alarm, Telefonanruf, Automatisch scharf, Türschloss, Nacht-Türalarm, Kinder und Hinweise.
* **Unterpunkte:** Sensor, Person, Kamera, Garage (beliebig viele).

Eingestellte Entitäten oder Dienste, die es nicht gibt, werden nach dem Start unter Reparaturen gemeldet.

## Entitäten

| Entität | Bedeutung |
|---|---|
| Alarmzentrale | Abwesend scharf/unscharf, Attribute: offene und ignorierte Sensoren, Ursache |
| Schalter Automatisch scharf, Kinder alleine zuhause | bleiben über Neustarts erhalten |
| Schalter Nacht-Türalarm, Kamera Live-Ansicht, Garage Automatik | nur wenn eingerichtet |
| Binärsensoren Bewegung, Kontakte offen, Bewegung unterdrückt, Vorwarnung | |
| Binärsensor "<Name> zuhause" | je Person, aus dem WLAN des Handys |
| Sensoren Ursache, Letzter Alarm | |
| Buttons Anruf quittieren, Testmeldung | Testmeldung schickt nur einen Push mit den offenen Sensoren |

Die Zentrale wird mit den normalen Diensten `alarm_control_panel.alarm_arm_away` und `alarm_control_panel.alarm_disarm` bedient, z. B. aus einem Knopf-Blueprint.

## Umstieg

Siehe [docs/migration.md](docs/migration.md).

## Entwicklung

```bash
pip install -r requirements_test.txt ruff
ruff check custom_components tests scripts
pytest -q
```

Die Tests mit Home Assistant laufen unter Linux. Vor jeder Veröffentlichung prüft `scripts/check_privacy.py` mit einer lokalen Musterliste, dass keine privaten Daten im Repository landen.

## Lizenz

MIT
