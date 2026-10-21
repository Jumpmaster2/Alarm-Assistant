# Alarm Assistant

[English version](README.en.md)

Custom Integration für Home Assistant: eine Alarmzentrale mit allem, was sonst in vielen Automationen, Skripten und Helfern steckt. Scharf- und Unscharfschalten (auch automatisch bei Abwesenheit), Ein- und Ausgangsverzögerung, offene Fenster ignorieren, Durchsagen und Alarmton (Sirenen, Lautsprecher oder Alexa-Geräte), Licht und Rollos bei Alarm, Telefonanruf mit Quittierung über das ha-sip-Add-on, Türschloss, Kamera-Steuerung, Garagen-Kameras, ein Nacht-Türalarm und ein Fenster-offen-Hinweis an der Haustür. Alles wird in der Oberfläche eingestellt, es sind keine eigenen Automationen nötig.

## Voraussetzungen

* Home Assistant 2026.10 oder neuer.
* Optional, je nach Funktion:
  * **Alarmton:** Sirenen-Entitäten (`siren.*`), Lautsprecher (`media_player.*`) für eine Ton-Datei und/oder Echo-Geräte über die Integration **Alexa Devices**.
  * **Gesprochene Texte:** ein `notify`-Dienst, der spricht (z. B. Alexa Media).
  * **Telefonanruf:** Home Assistant OS oder Supervised mit dem Add-on **ha-sip**.
  * **Anwesenheit über WLAN:** Companion App mit dem WLAN-Sensor (`sensor.<handy>_wifi_connection`); alternativ HA-Personen.
  * **Kameras:** Schalter für Privatsphäre/PTZ-Auswahl der Kamera, optional Frigate-Schalter.

## Funktionsweise

Die Integration arbeitet ereignisgesteuert: Sie reagiert nur auf Zustandswechsel der eingestellten Entitäten, gescannte NFC-Tags und berechnete Zeitpunkte (Ende der Ein- oder Ausgangsverzögerung, Auslösezeit, automatisches Scharfschalten, tägliche Rücksetzungen). Jede Aktion steht mit Grund im Logbuch.

### Alarmzentrale

* Modus **Abwesend** mit Ausgangsverzögerung (0 = sofort scharf), Eingangsverzögerung und Auslösezeit. Danach wieder scharf oder, wenn eingestellt, unscharf.
* Optionaler Code (zum Unscharfschalten, wahlweise auch zum Scharfschalten). Der Code hat 4 bis 10 Ziffern; gespeichert wird nur ein gesalzener Hash (PBKDF2). Codes älterer Versionen funktionieren weiter und werden beim nächsten richtigen Unscharfschalten umgestellt. Nach jeweils 5 falschen Eingaben hintereinander kommt eine Meldung.
* **Sensoren** werden einzeln angelegt (Unterpunkt "Sensor"): Tür (verzögert), Fenster (sofort), Bewegung (verzögert, darf beim Scharfschalten aktiv sein) oder Sonstiges. Alle Eigenschaften lassen sich pro Sensor ändern.
* **Offene Fenster** werden beim Scharfschalten bis zum Unscharfschalten ignoriert, es kommt eine Benachrichtigung mit den offenen Fenstern. Eine offene Tür verhindert das Scharfschalten (mit Benachrichtigung), außer während einer Ausgangsverzögerung.
* Ein Sensor, der nicht verfügbar wird, löst nicht aus. War er vorher geschlossen und meldet sich offen zurück, löst er aus. Ist ein Sensor im scharfen Zustand länger als die eingestellte Wartezeit (Standard 60 s) nicht verfügbar, kommt eine Push-Meldung (abschaltbar).
* **Bedingte Kontakte:** Ein Sensor kann so eingestellt werden, dass er nur zählt, solange eine andere Entität nicht verfügbar ist, z. B. eine Balkontür, die für den Schlauch einer mobilen Klimaanlage offen steht. Ist sie beim Scharfschalten offen und zählt nicht, kann ein Rollo auf eine Position fahren.
* Nach einem Neustart bleibt eine scharfe Anlage scharf. Ein laufender Alarm wird nicht wiederholt.

### Bewegungsfilter

* Bewegung zählt nicht, solange der Saugroboter saugt oder zurückfährt, und eine einstellbare Zeit nach dem Andocken.
* Ein **Fehler-Sensor** (z. B. Ausfall der Saugroboter-Anbindung) unterdrückt Bewegung, solange er an oder nicht verfügbar ist. Dazu gibt es technische Meldungen: beim Fehler und bei jeder unterdrückten Bewegung, solange scharf.

### Bei Alarm

* Durchsage an Benachrichtigungs-Entitäten (z. B. Alexa-Durchsage überall) mit eigenem Text, ebenso bei Beginn der Eingangsverzögerung.
* Alarmton: Lautstärke hoch, Sirenen-Entitäten (`siren.*`) an, Sound auf Alexa-Geräten und/oder eine Ton-Datei (z. B. `media-source://media_source/local/alarm.mp3`) auf den Lautsprechern, gesprochener Text, Lautstärke nach einer Zeit zurück. Sirenen gehen beim Unscharfschalten und nach der Auslösezeit aus. Alexa ist damit nicht mehr nötig.
* Lichter und Schalter einschalten, Rollos schließen.
* **Telefonanruf** über das ha-sip-Add-on: Nummern der Reihe nach. Jede Nummer außer der letzten kann mit Taste 1 quittieren (der Button "Anruf quittieren" wird gedrückt), dann wird niemand mehr angerufen. Der erste Anruf startet vor den Push-Nachrichten. Innerhalb der Sperrzeit gibt es keinen neuen Anruf; Push-Meldungen kommen bei jedem Alarm. Unscharf schalten beendet die Anrufkette, Alarmton und Durchsagen sofort, die Lautstärke wird zurückgesetzt.
* Push an die Handys und zusätzliche Dienste (z. B. Pushover) mit der **Ursache**: die auslösenden Sensoren und, wenn eine Kamera gerade eine Person sieht, auch diese.

### Automatisch scharf

* Anwesenheit über **Personen** (Unterpunkt "Person"): Jede Person hat den WLAN-Sensor ihres Handys. Ist das Handy mit einem Heim-WLAN verbunden, ist die Person zuhause; dafür gibt es je Person einen Anwesenheitssensor. Alternativ HA-Personen (`person.*`). Ein Handy (oder eine Person) ohne bekannten Zustand, z. B. ausgeschaltet oder mit leerem Akku, zählt standardmäßig als zuhause; einstellbar unter "Handy ohne bekannten Zustand zählt als".
* Ist niemand zuhause (seit einer Mindestzeit), war eine Weile keine Bewegung und ist "Kinder alleine zuhause" aus, kommt eine Vorwarnung. Ist danach immer noch alles erfüllt und keine Bewegung gewesen, wird scharf geschaltet. Nach einem Unscharfschalten wird erst nach einer Wartezeit wieder geprüft.
* Abschaltbar über den Schalter **Automatisch scharf**.

### Türschloss und Kinder

* Entriegeln oder Öffnen des Schlosses schaltet unscharf. Meldet sich ein Schloss nach "nicht verfügbar" (Funk, Bridge, Batterie) als entriegelt zurück, zählt das nicht als Entriegeln.
* Fällt das Schloss nach dem Abschließen zurück oder meldet es "blockiert", bleibt die Anlage scharf, es kommt eine Meldung und ein zweiter Versuch.
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
* Bewegung, solange scharf: Push und gesprochene Warnung auf den Handys (Companion App, gesprochen nur unter Android; der Audio-Stream ist einstellbar).
* Die Garage braucht WLAN-Sensoren (Unterpunkt Person oder weitere WLAN-Sensoren), sonst lehnt die Einrichtung die Garagen-WLANs ab.
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

## Manuelle Installation

1. Den Ordner `custom_components/alarm_assistant` aus diesem Repository (oder aus dem ZIP eines Releases) nach `<config>/custom_components/alarm_assistant` kopieren.
2. Home Assistant neu starten.
3. Unter Einstellungen > Geräte & Dienste > Integration hinzufügen > "Alarm Assistant" einrichten.

Update: Ordner ersetzen und neu starten. Entfernen: Integration unter Geräte & Dienste löschen (der gespeicherte Zustand und die Reparatur-Meldungen werden mit entfernt), danach den Ordner löschen.

## Konfiguration

Nach der Einrichtung gibt es in der Seitenleiste die Seite **Alarm Assistant** (nur für Administratoren, ähnlich wie bei Alarmo):

* **Übersicht:** Zustand mit Scharf/Unscharf, Schalter, Personen (zuhause/weg), offene Kontakte, Hinweise, letzter Alarm, Testmeldung und eine Zusammenfassung der Einstellungen.
* **Testalarm:** testweise scharf schalten und auswählen, was passieren soll: jede Reaktion einzeln an oder aus (z. B. keine Durchsage, kein Push an ein bestimmtes Handy, keine Lichter, keine Rollos, nur die erste Anrufnummer). Löst ein Sensor aus oder wird die Auslösung simuliert, läuft alles wie bei einem echten Alarm, nur mit den gewählten Reaktionen. Push-Meldungen beginnen mit [TEST], Durchsagen und Anrufe mit „Achtung, dies ist nur ein Test“. Unscharf schalten beendet den Test, ein Neustart nicht.
* **Sensoren:** alle Kontakte und Bewegungsmelder als Tabelle mit Typ, Verhalten und aktuellem Zustand; anklicken zum Bearbeiten.
* **Alarm, Bei Alarm, Meldungen & Anruf, Anwesenheit, Tür & Extras, Kamera & Garage:** alle Einstellungen nach Themen in Karten, jede Karte wird für sich gespeichert.

Die Einstellungen lassen sich weiterhin auch über den Einrichtungsdialog ändern:

* **Einrichtung:** Benachrichtigungen, Alarmzeiten und Code; optional werden vorhandene Tür-, Fenster- und Bewegungsmelder (nach Geräteklasse) direkt als Sensoren übernommen.
* **Optionen** (Menü): Alarmzeiten und Code, Benachrichtigungen, Reaktionen bei Alarm, Automatisch scharf, Türschloss, Telefonanruf, Bewegungsfilter, Nacht-Türalarm, Kinder und Hinweise. Jedes Feld hat eine Erklärung; unvollständige Angaben (z. B. Anruf ohne Nummer) werden mit einem Hinweis abgelehnt.
* **Unterpunkte:** Sensor, Person, Kamera, Garage (beliebig viele).

Eingestellte Entitäten oder Dienste, die es nicht gibt, werden nach dem Start unter Reparaturen gemeldet. Dazu gehört auch der Telefonanruf ohne Supervisor (Home Assistant Container/Core haben kein `hassio.addon_stdin`).

## Entitäten

| Entität | Bedeutung |
|---|---|
| Alarmzentrale | Abwesend scharf/unscharf, Attribute: offene und ignorierte Sensoren, Ursache |
| Schalter Kinder alleine zuhause | bleibt über Neustarts erhalten |
| Schalter Automatisch scharf, Nacht-Türalarm, Kamera Live-Ansicht, Garage Automatik | nur wenn eingerichtet, bleiben über Neustarts erhalten |
| Binärsensoren Bewegung, Kontakte offen, Vorwarnung | |
| Binärsensor Bewegung unterdrückt | Diagnose-Entität |
| Binärsensor "<Name> zuhause" | je Person, aus dem WLAN des Handys |
| Sensoren Ursache, Letzter Alarm | |
| Button Anruf quittieren | nur mit eingerichtetem Anruf (wird von ha-sip gedrückt) |
| Button Testmeldung | Konfigurations-Entität, schickt nur einen Push mit den offenen Sensoren |

Entitäten von Funktionen, die nicht mehr eingerichtet sind (oder gelöschter Personen), werden automatisch entfernt.

Die Zentrale wird mit den normalen Diensten `alarm_control_panel.alarm_arm_away` und `alarm_control_panel.alarm_disarm` bedient, z. B. aus einem Knopf-Blueprint.

## Optionen im Überblick

| Bereich | Option | Standard |
|---|---|---|
| Alarm | Eingangs- / Ausgangsverzögerung | 30 s / 0 s |
| | Auslösezeit, danach unscharf | 1800 s, aus (wieder scharf) |
| | Code (4–10 Ziffern), auch zum Scharfschalten | kein Code, aus |
| | Ausgefallene Sensoren melden, Wartezeit | an, 60 s |
| Benachrichtigungen | Sprache der Meldungen | Auto (wie Home Assistant) |
| | Push / zusätzliche Alarm-Meldungen / technische Meldungen | leer |
| Reaktionen | Alarm-Lautstärke, Lautstärke danach, zurück nach | 0,51, 0,2, 10 s |
| | Sirenen, Alexa-Ton, Ton-Datei | leer, `amzn_sfx_scifi_alarm_04`, leer |
| Automatisch scharf | Anwesenheit über | WLAN der Handys |
| | Keine Bewegung seit / Vorwarnung / Warten nach Unscharf / abwesend seit mindestens | 10 / 5 / 2 / 2 min |
| | Handy ohne bekannten Zustand zählt als | zuhause |
| Türschloss | Entriegeln schaltet unscharf, beim Scharfschalten abschließen | an, an |
| Telefonanruf | Quittieren mit Taste 1, Warten bis zur nächsten Nummer, Sprache, Sperrzeit | an, 50 s, wie die Meldungen, 180 s |
| Bewegungsfilter | Nachlauf nach dem Andocken, unterdrückte Bewegung melden | 120 s, an |
| Nacht-Türalarm | Ausschalten um, an Tagen | 05:00, Mo–Fr |
| Kinder und Hinweise | Zurücksetzen nach Entriegeln, nachts um, Hinweis-Dauer | 10 min, 03:00, 30 s |

Nur Werte, die vom Standard abweichen, werden gespeichert; ändert sich ein Standard in einer neuen Version, gilt er auch für bestehende Installationen.

## Beispiel: Wohnung

1. Einrichtung: Push an `notify.mobile_app_handy`, Eingangsverzögerung 30 s, Code `4711`; im letzten Schritt Haustür, drei Fenster und den Flur-Bewegungsmelder wählen.
2. Optionen › Reaktionen: Sirene `siren.flur`, Licht `light.flur` einschalten.
3. Unterpunkt Person je Handy mit dem WLAN-Sensor, Optionen › Automatisch scharf: Heim-WLAN eintragen.
4. Seite Alarm Assistant › Testalarm: testweise scharf schalten, Auslösung simulieren, prüfen, unscharf schalten.

## Fehlerbehebung

| Problem | Prüfen |
|---|---|
| "Scharfschalten nicht möglich" | Der genannte Sensor ist offen und darf es nicht sein. Für Fenster "Beim Scharfschalten offen = ignorieren" einschalten, für Türen eine Ausgangsverzögerung nutzen. |
| Kein Alarmton | Lautsprecher/Sirenen eingetragen? Bei Alexa: Geräte der Integration Alexa Devices gewählt und Sound-Name korrekt? Testalarm nutzen. |
| Kein Anruf | Reparaturen prüfen (`hassio.addon_stdin` fehlt = kein Supervisor), Slug des ha-sip-Add-ons und Nummern prüfen, Log des Add-ons ansehen. |
| Automatisch scharf greift nicht | Schalter "Automatisch scharf" an? "Kinder alleine zuhause" aus? Heim-WLAN genau wie im WLAN-Sensor geschrieben? Ein Handy ohne Zustand zählt als zuhause. Die Vorwarnung kommt erst nach der Ruhezeit ohne Bewegung. |
| Unscharf beim Wiederverbinden des Schlosses | Wird seit 0.4.6 ignoriert. Tritt es trotzdem auf, bitte ein Issue mit Debug-Log öffnen. |
| Entität fehlt | Funktionen ohne Einrichtung haben keine Entitäten (z. B. Schalter Automatisch scharf erst mit Heim-WLAN und Handy). |

### Debug-Logging

Unter Einstellungen > Geräte & Dienste > Alarm Assistant > "Debug-Protokollierung aktivieren", das Problem nachstellen und wieder ausschalten; das Log wird heruntergeladen. Alternativ in `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.alarm_assistant: debug
```

Für ein Issue zusätzlich die Diagnose herunterladen (Integration › drei Punkte › Diagnose herunterladen). Code-Hash, Telefonnummern, WLAN-Namen, Tag-ID und Namen sind darin geschwärzt.

## Umstieg

Siehe [docs/migration.md](docs/migration.md).

## Entwicklung

```bash
pip install -r requirements_test.txt ruff
ruff check custom_components tests scripts
ruff format --check custom_components tests scripts
python scripts/build_labels.py --check   # Panel-Beschriftungen aus den Übersetzungen
pytest -q
```

Nach Änderungen an `strings.json`/`translations` `python scripts/build_labels.py` ausführen.

Die Tests mit Home Assistant laufen unter Linux. Vor jeder Veröffentlichung prüft `scripts/check_privacy.py` mit einer lokalen Musterliste, dass keine privaten Daten im Repository landen.

## Lizenz

MIT
