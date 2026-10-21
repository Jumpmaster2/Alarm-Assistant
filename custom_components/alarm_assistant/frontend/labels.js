// Generated from the translation source, do not edit by hand.
// Run python scripts/build_labels.py after changing the translations.
export const LABELS = {
 "de": {
  "language": [
   "Sprache der Meldungen",
   "Auto folgt Home Assistant."
  ],
  "notify_services": [
   "Push-Benachrichtigungen",
   "Handys, die alle Meldungen bekommen (Alarm, Scharfschalten, Warnungen)."
  ],
  "notify_alarm_services": [
   "Zusätzliche Alarm-Benachrichtigungen",
   "Bekommen nur den Alarm selbst (z. B. Pushover)."
  ],
  "notify_admin_services": [
   "Technische Benachrichtigungen",
   "Fehler des Bewegungsfilters und unterdrückte Bewegung."
  ],
  "entry_delay": [
   "Eingangsverzögerung",
   "Zeit zum Entschärfen, nachdem ein verzögerter Sensor (Tür, Bewegung) ausgelöst hat."
  ],
  "exit_delay": [
   "Ausgangsverzögerung",
   "0 = sofort scharf."
  ],
  "trigger_time": [
   "Auslösezeit",
   "Wie lange der Alarm ausgelöst bleibt (Sirenen, Zustand ALARM). Beispiel: 1800 s = 30 min. 0 beendet den Alarm sofort wieder (nicht empfohlen)."
  ],
  "disarm_after_trigger": [
   "Nach der Auslösezeit unscharf",
   "Aus: danach wieder scharf."
  ],
  "code_arm_required": [
   "Code auch zum Scharfschalten",
   "Aus: Scharfschalten geht ohne Code, nur Unscharfschalten braucht ihn."
  ],
  "armed_on_entities": [
   "An, solange scharf",
   "Beim Scharfschalten an, beim Unscharfschalten aus (z. B. Bewegungserkennung von Kameras)."
  ],
  "code": [
   "Code (optional)",
   "4 bis 10 Ziffern. Zum Unscharfschalten nötig. Leer = kein Code."
  ],
  "code_confirm": [
   "Code wiederholen",
   "Denselben Code noch einmal eingeben."
  ],
  "notify_unavailable": [
   "Ausgefallene Sensoren melden",
   "Push, wenn ein Sensor nicht verfügbar ist, während die Anlage scharf ist (leere Batterie, Funkproblem, Sabotage)."
  ],
  "unavailable_delay": [
   "Wartezeit vor der Meldung",
   "Kurze Aussetzer innerhalb dieser Zeit werden nicht gemeldet. 0 = sofort melden."
  ],
  "sensors": [
   "Sensoren",
   "Angeboten werden nur Binärsensoren mit der Geräteklasse Tür, Garagentor, Fenster, Öffnung, Bewegung, Belegung oder Anwesenheit. Leer = Sensoren später anlegen."
  ],
  "new_code": [
   "Neuer Code",
   "4 bis 10 Ziffern. Leer lassen, um den bisherigen Code zu behalten."
  ],
  "remove_code": [
   "Code entfernen",
   "An: Der Code wird gelöscht, danach geht Unscharfschalten ohne Code."
  ],
  "vacuum": [
   "Saugroboter",
   "Bewegung zählt nicht, solange er saugt oder zurückfährt."
  ],
  "vacuum_charging": [
   "Ladesensor Saugroboter",
   "Wird für die Kamera-Regeln verwendet."
  ],
  "dock_grace": [
   "Nachlauf nach dem Andocken",
   "So lange nach dem Andocken zählt Bewegung noch nicht (der Roboter fährt oft noch nach). Beispiel: 120 s."
  ],
  "fault_sensor": [
   "Fehler-Sensor",
   "Solange an (oder nicht verfügbar) zählt Bewegung nicht, z. B. wenn die Saugroboter-Anbindung ausfällt."
  ],
  "notify_suppressed_motion": [
   "Unterdrückte Bewegung melden",
   "Technische Meldung bei jeder Bewegung, solange scharf und der Fehler-Sensor an ist."
  ],
  "announce_entities": [
   "Durchsage-Ziele",
   "Benachrichtigungs-Entitäten (z. B. Alexa-Durchsage auf allen Geräten)."
  ],
  "text_triggered": [
   "Text bei Alarm",
   "Leer = Standardtext."
  ],
  "text_pending": [
   "Text bei Eingangsverzögerung",
   "Leer = Standardtext."
  ],
  "volume_players": [
   "Lautsprecher für Lautstärke",
   "Lautsprecher, deren Lautstärke für den Alarm hochgesetzt wird; auf ihnen läuft auch die Alarmton-Datei."
  ],
  "alarm_volume": [
   "Alarm-Lautstärke",
   "0 = stumm, 1 = maximal. Beispiel: 0,7."
  ],
  "reset_volume": [
   "Lautstärke danach",
   "Lautstärke, auf die nach dem Alarmton zurückgestellt wird (0 bis 1)."
  ],
  "reset_volume_after": [
   "Lautstärke zurück nach",
   "Wartezeit vom Alarmton bis zum Zurückstellen der Lautstärke."
  ],
  "sirens": [
   "Sirenen",
   "Sirenen-Entitäten (z. B. Zigbee-Sirenen). Bei Alarm an, aus beim Unscharfschalten oder nach der Auslösezeit."
  ],
  "sound_devices": [
   "Alexa-Geräte für den Alarmton",
   "Echo-Geräte der Integration Alexa Devices, die den Alarmton spielen. Leer lassen ohne Alexa."
  ],
  "sound": [
   "Alarmton",
   "Sound-Name der Integration Alexa Devices, z. B. amzn_sfx_scifi_alarm_04. Nur für Alexa-Geräte."
  ],
  "sound_media": [
   "Alarmton-Datei auf den Lautsprechern",
   "Wird auf den Lautsprechern für die Lautstärke abgespielt, z. B. media-source://media_source/local/alarm.mp3 oder eine URL. Leer = keine Datei."
  ],
  "speak_services": [
   "Gesprochener Text",
   "Benachrichtigungsdienste, die den Alarmtext sprechen, z. B. notify.alexa_media_kueche. TTS = Text-to-Speech (Sprachausgabe)."
  ],
  "turn_on_entities": [
   "Einschalten",
   "Lichter, Schalter oder Szenen, die bei Alarm eingeschaltet werden."
  ],
  "close_covers": [
   "Rollos schließen",
   "Rollos, die bei Alarm geschlossen werden."
  ],
  "call_addon": [
   "ha-sip-Add-on",
   "Slug = interner Name des ha-sip-Add-ons, zu sehen in der Adresszeile unter Einstellungen › Add-ons › ha-sip (z. B. 1234abcd_ha-sip). Leer = kein Anruf. Braucht Home Assistant OS oder Supervised."
  ],
  "call_targets": [
   "Nummern der Reihe nach",
   "Telefonnummern oder SIP-Adressen (Internet-Telefonie), je Eintrag eine, z. B. +491701234567 oder sip:**610@fritz.box. Reihenfolge = Anrufreihenfolge."
  ],
  "call_acknowledge": [
   "Quittieren mit Taste 1",
   "Jede Nummer außer der letzten kann die Kette beenden."
  ],
  "call_wait": [
   "Warten bis zur nächsten Nummer",
   "Wartezeit zwischen zwei Anrufen, damit der Angerufene quittieren kann. Beispiel: 50 s."
  ],
  "call_tts": [
   "Sprachausgabe für den Anruf",
   "TTS-Entität (Sprachausgabe), mit der ha-sip den Text spricht. Leer = Standard des Add-ons."
  ],
  "call_language": [
   "Sprache des Anrufs",
   "Sprache der Sprachausgabe im Anruf. 'Wie die Meldungen' folgt der Spracheinstellung; andere Kürzel (z. B. fr) können eingetippt werden."
  ],
  "call_cooldown": [
   "Kein neuer Anruf für",
   "Innerhalb dieser Zeit nach einem Alarm startet keine neue Anrufkette. Push-Meldungen kommen immer."
  ],
  "presence_mode": [
   "Anwesenheit über",
   "WLAN der Handys: über die Unterpunkte Person bzw. WLAN-Sensoren der Companion App. Personen: über die Home-Assistant-Personen (person.*)."
  ],
  "wifi_sensors": [
   "Weitere WLAN-Sensoren",
   "Sensoren mit dem Namen des verbundenen WLANs (Companion App: sensor.handy_wifi_connection) für Handys ohne Unterpunkt Person."
  ],
  "home_networks": [
   "Heim-WLANs",
   "Namen (SSID) der WLANs zuhause, genau wie vom WLAN-Sensor gemeldet, z. B. MeinWLAN."
  ],
  "persons": [
   "Personen",
   "Nur für Modus Personen: alle, die zuhause sein können."
  ],
  "quiet_time": [
   "Keine Bewegung seit",
   "So lange darf keine Bewegung gemeldet sein, bevor die Vorwarnung startet. Beispiel: 10 min."
  ],
  "prewarn_time": [
   "Vorwarnung vor dem Scharfschalten",
   "Zeit zwischen Vorwarnung (Push) und Scharfschalten. Beispiel: 5 min."
  ],
  "retry_after_disarm": [
   "Warten nach dem Unscharfschalten",
   "Nach dem Unscharfschalten wird so lange nicht automatisch scharf geschaltet."
  ],
  "presence_stable": [
   "Abwesend seit mindestens",
   "Alle müssen mindestens so lange weg sein (filtert kurze WLAN-Aussetzer)."
  ],
  "unknown_presence": [
   "Handy ohne bekannten Zustand zählt als",
   "Ein Handy, das aus ist, einen leeren Akku hat oder nichts meldet (nicht verfügbar/unbekannt). Zuhause ist sicherer: Es wird nicht scharf geschaltet, solange vielleicht noch jemand da ist."
  ],
  "lock": [
   "Türschloss",
   "Smartes Türschloss. Leer = keine Schloss-Funktionen."
  ],
  "lock_door_sensor": [
   "Türkontakt",
   "Abgeschlossen wird nur bei geschlossener Tür."
  ],
  "disarm_on_unlock": [
   "Entriegeln schaltet unscharf",
   "Entriegeln oder Öffnen des Schlosses schaltet ohne Code unscharf. Meldungen nach einem Verbindungsabbruch zählen nicht."
  ],
  "lock_on_arm": [
   "Beim Scharfschalten abschließen",
   "Beim Scharfschalten abschließen (nicht, wenn Kinder alleine zuhause sind)."
  ],
  "night_door_sensor": [
   "Türkontakt",
   "Leer = kein Türalarm."
  ],
  "night_tag": [
   "NFC-Tag-ID",
   "ID des NFC-Tags (Einstellungen › Tags). Scannen schaltet den Türalarm an und aus."
  ],
  "night_turn_on_entities": [
   "Einschalten",
   "Lichter auf 100 %."
  ],
  "night_volume_players": [
   "Lautsprecher für Lautstärke",
   "Lautsprecher, deren Lautstärke für den Türalarm hochgesetzt wird."
  ],
  "night_sirens": [
   "Sirenen",
   "An, wenn die Tür aufgeht, aus nach 'Lautstärke zurück nach'."
  ],
  "night_sound_devices": [
   "Alexa-Geräte für den Alarmton",
   "Echo-Geräte (Alexa Devices) für den Alarmton."
  ],
  "night_speak_services": [
   "Gesprochener Text",
   "Benachrichtigungsdienste, die den Text sprechen."
  ],
  "night_text": [
   "Text",
   "Leer = Standardtext."
  ],
  "night_reset_volume_after": [
   "Lautstärke zurück nach",
   "Danach wird die Lautstärke zurückgestellt und die Sirenen gehen aus."
  ],
  "night_off_time": [
   "Ausschalten um",
   "Uhrzeit, zu der der Türalarm automatisch ausgeht."
  ],
  "night_off_days": [
   "An diesen Tagen",
   "Wochentage für das automatische Ausschalten. Keiner = nie automatisch."
  ],
  "night_off_speak_services": [
   "Ansage beim Ausschalten per Tag",
   "Wird der Türalarm per Tag ausgeschaltet, sagen diese Dienste das an."
  ],
  "night_off_volume_players": [
   "Lautsprecher für diese Ansage",
   "Lautsprecher, deren Lautstärke für diese Ansage gesetzt wird."
  ],
  "night_off_volume": [
   "Lautstärke dieser Ansage",
   "0 = stumm, 1 = maximal."
  ],
  "kids_reset_after_unlock": [
   "Zurücksetzen nach dem Entriegeln",
   "Der Schalter Kinder alleine zuhause geht so lange nach dem Entriegeln aus (ein Erwachsener kommt heim)."
  ],
  "kids_reset_time": [
   "Nachts zurücksetzen um",
   "Der Schalter geht zusätzlich jede Nacht um diese Uhrzeit aus."
  ],
  "hint_door_sensor": [
   "Türkontakt",
   "Leer = kein Hinweis."
  ],
  "hint_windows": [
   "Fenster",
   "Fenster, die geprüft werden, wenn die Tür aufgeht."
  ],
  "hint_entity": [
   "Hinweis-Licht",
   "Licht oder Schalter, der kurz angeht, wenn ein Fenster offen ist."
  ],
  "hint_duration": [
   "Dauer",
   "Wie lange das Hinweis-Licht an bleibt."
  ],
  "name": [
   "Name",
   "Wird in Meldungen und als Ursache genannt. Leer = Name der Entität."
  ],
  "entity": [
   "Sensor",
   "Kontakt oder Bewegungsmelder (binary_sensor, auch input_boolean zum Testen)."
  ],
  "type": [
   "Typ",
   "Legt sinnvolle Vorgaben für das Verhalten fest; jede lässt sich im nächsten Schritt ändern."
  ],
  "use_entry_delay": [
   "Eingangsverzögerung nutzen",
   "An: Auslösen startet erst die Eingangsverzögerung. Aus: sofortiger Alarm."
  ],
  "use_exit_delay": [
   "Darf in der Ausgangsverzögerung offen sein",
   "Darf während der Ausgangsverzögerung offen sein bzw. auslösen (z. B. Haustür beim Gehen)."
  ],
  "auto_bypass": [
   "Beim Scharfschalten offen = ignorieren",
   "Ist der Sensor beim Scharfschalten offen, wird er bis zum Unscharfschalten ignoriert (Bypass), statt das Scharfschalten zu verhindern."
  ],
  "allow_open": [
   "Darf beim Scharfschalten aktiv sein",
   "Darf beim Scharfschalten aktiv sein und zählt erst nach dem nächsten Wechsel, z. B. Bewegungsmelder."
  ],
  "only_when_unavailable": [
   "Zählt nur, wenn nicht verfügbar",
   "Der Sensor zählt nur, solange diese Entität nicht verfügbar ist (z. B. Tür, die für den Klimaschlauch offen steht)."
  ],
  "arm_cover": [
   "Rollo, wenn ignoriert",
   "Beim Scharfschalten offen, zählt aber nicht: dieses Rollo fahren."
  ],
  "arm_cover_position": [
   "Rollo-Position",
   "Position in %, auf die das Rollo fährt (0 = zu)."
  ],
  "camera_preset": [
   "Kamera-Preset",
   "Name der gespeicherten Kameraposition (PTZ-Preset), auf die die Kameras schwenken, wenn dieser Bewegungsmelder scharf Bewegung meldet."
  ],
  "privacy_switch": [
   "Schalter Privatsphäre-Modus",
   "Schalter, der das Kamerabild abschaltet (Privatsphäre-Modus). An = kein Bild."
  ],
  "ptz_select": [
   "PTZ-Preset-Auswahl",
   "Auswahl-Entität der Kamera mit den gespeicherten Positionen (PTZ = schwenken, neigen, zoomen)."
  ],
  "ptz_home_preset": [
   "Standard-Preset",
   "Position beim Scharfschalten, genau wie in der Auswahl-Entität geschrieben."
  ],
  "privacy_delay": [
   "Privatsphäre wieder an nach",
   "So lange nach dem Unscharfschalten geht der Privatsphäre-Modus wieder an."
  ],
  "record_switches": [
   "Aufnahme-Schalter",
   "Aufnahme-Schalter (z. B. Frigate, eine lokale Videoanalyse). Bleiben an, solange der Saugroboter fährt."
  ],
  "detect_switches": [
   "Erkennungs-Schalter",
   "Erkennungs-Schalter (z. B. Frigate). Aus, solange der Saugroboter fährt, bei Live-Ansicht und Kindern."
  ],
  "person_sensor": [
   "Person erkannt",
   "Binärsensor 'Person erkannt' der Kamera; zählt auch für die Ursache eines Alarms."
  ],
  "person_count_sensor": [
   "Anzahl Personen",
   "Sensor mit der Anzahl erkannter Personen (alternativ zum Binärsensor)."
  ],
  "person_image": [
   "Personenbild",
   "Bild- oder Kamera-Entität; ihr Bild wird mit der Push-Meldung geschickt."
  ],
  "person_push": [
   "Push mit Bild, wenn scharf",
   "Push mit Bild, wenn die Kamera eine Person erkennt und die Anlage nicht unscharf ist."
  ],
  "wifi_sensor": [
   "WLAN-Sensor des Handys",
   "Zeigt den Namen des verbundenen WLANs (Companion App)."
  ],
  "garage_panel": [
   "Alarmzentrale Garage",
   "Zweite Alarmzentrale der Garage, z. B. von Blink."
  ],
  "garage_networks": [
   "Garagen-WLANs",
   "Unscharf, solange ein Handy verbunden ist (WLAN-Sensoren der Personen und die weiteren)."
  ],
  "garage_arm_delay": [
   "Scharf nach dem Verlassen",
   "So lange nach dem Verlassen des Garagen-WLANs wird scharf geschaltet."
  ],
  "garage_motion": [
   "Bewegungssensoren",
   "Bewegungssensoren der Garagen-Kameras; melden nur, solange die Garage scharf ist."
  ],
  "garage_tts_services": [
   "Gesprochene Warnung auf Handys",
   "Benachrichtigungsdienste der Companion App (Android), die die Warnung sprechen."
  ],
  "garage_tts_text": [
   "Gesprochener Text",
   "Leer = Standardtext."
  ],
  "garage_tts_repeat": [
   "Wiederholen",
   "Wie oft die Warnung gesprochen wird."
  ],
  "garage_tts_stream": [
   "Audio-Stream (Android)",
   "Stream der Android Companion App; alarm_stream_max ist auch im Lautlos-Modus laut. iPhones ignorieren dieses Feld."
  ]
 },
 "en": {
  "language": [
   "Language of messages",
   "Auto follows Home Assistant."
  ],
  "notify_services": [
   "Push notifications",
   "Phones that get all messages (alarm, arming, warnings)."
  ],
  "notify_alarm_services": [
   "Additional alarm notifications",
   "Only get the alarm itself (e.g. Pushover)."
  ],
  "notify_admin_services": [
   "Technical notifications",
   "Faults of the motion filter and suppressed motion."
  ],
  "entry_delay": [
   "Entry delay",
   "Time to disarm after a delayed sensor (door, motion) tripped."
  ],
  "exit_delay": [
   "Exit delay",
   "0 = armed immediately."
  ],
  "trigger_time": [
   "Trigger time",
   "How long the alarm stays triggered (sirens, state ALARM). Example: 1800 s = 30 min. 0 ends the alarm at once (not recommended)."
  ],
  "disarm_after_trigger": [
   "Disarm after the trigger time",
   "Off: armed again afterwards."
  ],
  "code_arm_required": [
   "Code also for arming",
   "Off: arming works without the code, only disarming needs it."
  ],
  "armed_on_entities": [
   "On while armed",
   "Turned on when armed, off when disarmed (e.g. camera motion detection)."
  ],
  "code": [
   "Code (optional)",
   "4 to 10 digits. Needed to disarm. Leave empty for no code."
  ],
  "code_confirm": [
   "Repeat code",
   "Enter the same code again."
  ],
  "notify_unavailable": [
   "Report unavailable sensors",
   "Push when a sensor is unavailable while armed (empty battery, radio problem, sabotage)."
  ],
  "unavailable_delay": [
   "Delay before the report",
   "Short drop-outs within this time are not reported. 0 = report at once."
  ],
  "sensors": [
   "Sensors",
   "Only binary sensors with the device class door, garage door, window, opening, motion, occupancy or presence are offered. Empty = add sensors later."
  ],
  "new_code": [
   "New code",
   "4 to 10 digits. Leave empty to keep the current code."
  ],
  "remove_code": [
   "Remove code",
   "On: the code is deleted, disarming works without a code afterwards."
  ],
  "vacuum": [
   "Vacuum",
   "Motion does not count while it cleans or returns."
  ],
  "vacuum_charging": [
   "Vacuum charging sensor",
   "Used by the camera rules."
  ],
  "dock_grace": [
   "Grace time after docking",
   "Motion does not count for this time after docking (the robot often still moves). Example: 120 s."
  ],
  "fault_sensor": [
   "Fault sensor",
   "While on (or unavailable) motion does not count, e.g. when the vacuum bridge fails."
  ],
  "notify_suppressed_motion": [
   "Report suppressed motion",
   "Technical notification for every motion while armed and the fault sensor is on."
  ],
  "announce_entities": [
   "Announcement targets",
   "Notify entities (e.g. Alexa announcement on all devices)."
  ],
  "text_triggered": [
   "Text on alarm",
   "Empty = standard text."
  ],
  "text_pending": [
   "Text at entry delay",
   "Empty = standard text."
  ],
  "volume_players": [
   "Speakers for volume",
   "Speakers whose volume is raised for the alarm; the alarm sound file plays on them too."
  ],
  "alarm_volume": [
   "Alarm volume",
   "0 = mute, 1 = maximum. Example: 0.7."
  ],
  "reset_volume": [
   "Volume afterwards",
   "Volume set after the alarm sound (0 to 1)."
  ],
  "reset_volume_after": [
   "Reset volume after",
   "Time from the alarm sound until the volume is set back."
  ],
  "sirens": [
   "Sirens",
   "Siren entities (e.g. Zigbee sirens). On at the alarm, off when disarmed or the trigger time is over."
  ],
  "sound_devices": [
   "Alexa devices for the alarm sound",
   "Echo devices of the Alexa Devices integration that play the alarm sound. Leave empty without Alexa."
  ],
  "sound": [
   "Alarm sound",
   "Sound name of the Alexa Devices integration, e.g. amzn_sfx_scifi_alarm_04. Only used with Alexa devices."
  ],
  "sound_media": [
   "Alarm sound file on the speakers",
   "Played on the speakers for volume, e.g. media-source://media_source/local/alarm.mp3 or a URL. Empty = no file."
  ],
  "speak_services": [
   "Spoken text",
   "Notify services that speak the alarm text, e.g. notify.alexa_media_kitchen. TTS = text-to-speech."
  ],
  "turn_on_entities": [
   "Turn on",
   "Lights, switches or scenes turned on at the alarm."
  ],
  "close_covers": [
   "Close covers",
   "Covers that are closed on alarm."
  ],
  "call_addon": [
   "ha-sip add-on",
   "Slug = internal name of the ha-sip add-on, shown in the address bar under Settings › Add-ons › ha-sip (e.g. 1234abcd_ha-sip). Empty = no call. Needs Home Assistant OS or Supervised."
  ],
  "call_targets": [
   "Numbers in order",
   "Phone numbers or SIP addresses (internet telephony), one per entry, e.g. +441234567890 or sip:**610@fritz.box. Order = call order."
  ],
  "call_acknowledge": [
   "Acknowledge with key 1",
   "Every number except the last can stop the chain."
  ],
  "call_wait": [
   "Wait before the next number",
   "Time between two calls so the callee can acknowledge. Example: 50 s."
  ],
  "call_tts": [
   "Speech for the call",
   "TTS entity (text-to-speech) ha-sip uses to speak the text. Empty = default of the add-on."
  ],
  "call_language": [
   "Language of the call",
   "Language of the speech in the call. 'Like the messages' follows the language setting; other codes (e.g. fr) can be typed in."
  ],
  "call_cooldown": [
   "No new call for",
   "No new call chain within this time after an alarm. Push messages are always sent."
  ],
  "presence_mode": [
   "Presence by",
   "Wi-Fi of the phones: by the person sub items or Wi-Fi sensors of the companion app. Persons: by the Home Assistant persons (person.*)."
  ],
  "wifi_sensors": [
   "Additional Wi-Fi sensors",
   "Sensors with the name of the connected network (companion app: sensor.phone_wifi_connection) for phones without a person sub item."
  ],
  "home_networks": [
   "Home networks",
   "Names (SSID) of the networks at home, exactly as the Wi-Fi sensor reports them, e.g. MyWifi."
  ],
  "persons": [
   "Persons",
   "Only for the mode persons: everybody who can be at home."
  ],
  "quiet_time": [
   "No motion for",
   "No motion may be reported for this time before the warning starts. Example: 10 min."
  ],
  "prewarn_time": [
   "Warning before arming",
   "Time between the warning (push) and arming. Example: 5 min."
  ],
  "retry_after_disarm": [
   "Wait after disarming",
   "After disarming, no automatic arming for this time."
  ],
  "presence_stable": [
   "Away for at least",
   "Everybody must be away for at least this time (filters short Wi-Fi drop-outs)."
  ],
  "unknown_presence": [
   "Phone without a known state counts as",
   "A phone that is switched off, has an empty battery or does not report (unavailable/unknown). At home is safer: the panel is not armed while someone may be at home."
  ],
  "lock": [
   "Door lock",
   "Smart door lock. Empty = no lock functions."
  ],
  "lock_door_sensor": [
   "Door contact",
   "Locked only when the door is closed."
  ],
  "disarm_on_unlock": [
   "Unlocking disarms",
   "Unlocking or opening the lock disarms without a code. States after a lost connection do not count."
  ],
  "lock_on_arm": [
   "Lock when armed",
   "Lock when armed (not while children are alone at home)."
  ],
  "night_door_sensor": [
   "Door contact",
   "Empty = no door alarm."
  ],
  "night_tag": [
   "NFC tag ID",
   "ID of the NFC tag (Settings › Tags). Scanning switches the door alarm on and off."
  ],
  "night_turn_on_entities": [
   "Turn on",
   "Lights at 100 %."
  ],
  "night_volume_players": [
   "Speakers for volume",
   "Speakers whose volume is raised for the door alarm."
  ],
  "night_sirens": [
   "Sirens",
   "On when the door opens, off after 'Reset volume after'."
  ],
  "night_sound_devices": [
   "Alexa devices for the alarm sound",
   "Echo devices (Alexa Devices) for the alarm sound."
  ],
  "night_speak_services": [
   "Spoken text",
   "Notify services that speak the text."
  ],
  "night_text": [
   "Text",
   "Empty = standard text."
  ],
  "night_reset_volume_after": [
   "Reset volume after",
   "Afterwards the volume is set back and the sirens go off."
  ],
  "night_off_time": [
   "Switch off at",
   "Time when the door alarm switches off automatically."
  ],
  "night_off_days": [
   "On these days",
   "Weekdays for switching off automatically. None = never automatically."
  ],
  "night_off_speak_services": [
   "Announce when switched off by tag",
   "When the door alarm is switched off by tag, these services announce it."
  ],
  "night_off_volume_players": [
   "Speakers for this announcement",
   "Speakers whose volume is set for this announcement."
  ],
  "night_off_volume": [
   "Volume of this announcement",
   "0 = mute, 1 = maximum."
  ],
  "kids_reset_after_unlock": [
   "Reset after unlocking",
   "The switch children alone at home turns off this long after unlocking (an adult comes home)."
  ],
  "kids_reset_time": [
   "Reset at night",
   "The switch also turns off every night at this time."
  ],
  "hint_door_sensor": [
   "Door contact",
   "Empty = no hint."
  ],
  "hint_windows": [
   "Windows",
   "Windows checked when the door opens."
  ],
  "hint_entity": [
   "Hint light",
   "Light or switch that turns on briefly while a window is open."
  ],
  "hint_duration": [
   "Duration",
   "How long the hint light stays on."
  ],
  "name": [
   "Name",
   "Used in messages and as cause. Empty = name of the entity."
  ],
  "entity": [
   "Sensor",
   "Contact or motion sensor (binary_sensor, also input_boolean for testing)."
  ],
  "type": [
   "Type",
   "Sets sensible defaults for the behaviour; each can be changed in the next step."
  ],
  "use_entry_delay": [
   "Use entry delay",
   "On: tripping starts the entry delay first. Off: immediate alarm."
  ],
  "use_exit_delay": [
   "May be open during the exit delay",
   "May be open or trip during the exit delay (e.g. the front door when leaving)."
  ],
  "auto_bypass": [
   "Ignore when open at arming",
   "If the sensor is open when arming it is ignored until disarming (bypass) instead of blocking the arming."
  ],
  "allow_open": [
   "May be active at arming",
   "May be active when arming and counts after its next change, e.g. motion sensors."
  ],
  "only_when_unavailable": [
   "Counts only while unavailable",
   "The sensor counts only while this entity is unavailable (e.g. a door that is open for an air conditioner hose)."
  ],
  "arm_cover": [
   "Cover when ignored",
   "Open but not counting when armed: move this cover."
  ],
  "arm_cover_position": [
   "Cover position",
   "Position in % the cover moves to (0 = closed)."
  ],
  "camera_preset": [
   "Camera preset",
   "Name of the stored camera position (PTZ preset) the cameras turn to when this motion sensor reports motion while armed."
  ],
  "privacy_switch": [
   "Privacy mode switch",
   "Switch that turns the camera picture off (privacy mode). On = no picture."
  ],
  "ptz_select": [
   "PTZ preset select",
   "Select entity of the camera with the stored positions (PTZ = pan, tilt, zoom)."
  ],
  "ptz_home_preset": [
   "Default preset",
   "Position when armed, written exactly as in the select entity."
  ],
  "privacy_delay": [
   "Privacy on again after",
   "The privacy mode turns on again this long after disarming."
  ],
  "record_switches": [
   "Recording switches",
   "Recording switches (e.g. Frigate, a local video analysis). Stay on while the vacuum drives."
  ],
  "detect_switches": [
   "Detection switches",
   "Detection switches (e.g. Frigate). Off while the vacuum drives, in live view and with children."
  ],
  "person_sensor": [
   "Person detected",
   "Binary sensor 'person detected' of the camera; also counts for the cause of an alarm."
  ],
  "person_count_sensor": [
   "Person count",
   "Sensor with the number of detected persons (instead of the binary sensor)."
  ],
  "person_image": [
   "Person image",
   "Image or camera entity; its picture is sent with the push message."
  ],
  "person_push": [
   "Push with picture while armed",
   "Push with picture when the camera detects a person and the panel is not disarmed."
  ],
  "wifi_sensor": [
   "Wi-Fi sensor of the phone",
   "Shows the name of the connected network (companion app)."
  ],
  "garage_panel": [
   "Garage alarm panel",
   "Second alarm panel of the garage, e.g. from Blink."
  ],
  "garage_networks": [
   "Garage networks",
   "Disarmed while a phone is connected (Wi-Fi sensors of the persons and the additional ones)."
  ],
  "garage_arm_delay": [
   "Arm after leaving",
   "Armed this long after leaving the garage network."
  ],
  "garage_motion": [
   "Motion sensors",
   "Motion sensors of the garage cameras; report only while the garage is armed."
  ],
  "garage_tts_services": [
   "Spoken warning on phones",
   "Notify services of the companion app (Android) that speak the warning."
  ],
  "garage_tts_text": [
   "Spoken text",
   "Empty = standard text."
  ],
  "garage_tts_repeat": [
   "Repeat",
   "How often the warning is spoken."
  ],
  "garage_tts_stream": [
   "Audio stream (Android)",
   "Stream of the Android companion app; alarm_stream_max is loud even in silent mode. iPhones ignore this field."
  ]
 }
};
