# Umstieg / Moving over

[Deutsch](#deutsch) | [English](#english)

## Deutsch

Alarm Assistant ersetzt eine Alarmzentrale wie Alarmo samt der Automationen und Skripte drumherum. Vorgehen:

1. Backup der bisherigen Automationen, Skripte und der Alarmzentrale.
2. Integration installieren und einrichten, jeden Sensor als Unterpunkt anlegen.
3. Testmeldung senden, die neue Zentrale ohne Reaktionen scharf und unscharf schalten.
4. Alte Automationen **ausschalten** (nicht löschen), Knöpfe und Dashboards auf die neue Zentrale umstellen.
5. Einige Tage beobachten (Logbuch), danach Altes löschen.

### Typische Zuordnung

| Bisher | Alarm Assistant |
|---|---|
| Alarmo-Bereich mit Modus Abwesend, Verzögerungen | Optionen **Alarmzeiten und Code** |
| Alarmo-Sensoren (Tür, Fenster, Bewegung, "automatisch ignorieren") | Unterpunkt **Sensor** je Kontakt/Melder |
| Template-Sensor "Bewegung ohne Saugroboter" | Sensoren vom Typ Bewegung + **Bewegungsfilter** |
| Template-Kontakt "zählt nur ohne Klimaanlage" | Sensor: **Zählt nur, wenn nicht verfügbar** |
| Alarmo-Aktionen Lichter, Rollos, Durchsagen | Optionen **Reaktionen bei Alarm** |
| Skript Alarmton auf Echo-Geräten | Reaktionen: Alarmton und Sprache |
| Alarmo-Benachrichtigung "Scharfschalten fehlgeschlagen", Automation "offene Fenster melden" | eingebaut (Push an die Handys) |
| Automation Telefonanruf, Skripte mit ha-sip, Sperr-Helfer | Optionen **Telefonanruf**, Button **Anruf quittieren** |
| Automation "automatisch scharf bei Abwesenheit" | Optionen **Automatisch scharf**, Schalter |
| Automation "Schloss entriegelt -> unscharf", "scharf -> abschließen" | Optionen **Türschloss** |
| Helfer "Kinder alleine zuhause" + Reset-Automation | Schalter **Kinder alleine zuhause**, Optionen **Kinder und Hinweise** |
| Kamera-Automationen (Privatsphäre, PTZ, Frigate, Live-Modus, Personenbild) | Unterpunkt **Kamera**, Schalter **Kamera Live-Ansicht** |
| Blink-Automationen über Garagen-WLAN | Unterpunkt **Garage** |
| Helfer "Türalarm" mit NFC-Tag, Zeit-Aus | Optionen **Nacht-Türalarm**, Schalter |
| Automation "Tür auf und Fenster offen -> Licht" | Optionen **Kinder und Hinweise** |

## English

Alarm Assistant replaces an alarm panel such as Alarmo together with the automations and scripts around it:

1. Back up the existing automations, scripts and the alarm panel.
2. Install and set up the integration, add every sensor as a sub item.
3. Send a test message, arm and disarm the new panel without reactions.
4. **Turn off** (do not delete) the old automations, point buttons and dashboards to the new panel.
5. Watch for some days (logbook), then delete the old parts.

The table above maps the usual parts: panel and delays to **Alarm times and code**, each contact or motion sensor to a **Sensor** sub item, vacuum filters to the **Motion filter**, reactions and announcements to **Reactions on alarm**, ha-sip scripts to **Phone call**, presence based arming to **Automatic arming**, lock automations to **Door lock**, camera automations to a **Camera** sub item, Blink automations to a **Garage** sub item, the door alarm helper to **Night door alarm** and the window hint to **Children and hints**.
