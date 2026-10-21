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
   "Wie lange der Alarm ausgelöst bleibt."
  ],
  "disarm_after_trigger": [
   "Nach der Auslösezeit unscharf",
   "Aus: danach wieder scharf."
  ],
  "code_arm_required": [
   "Code auch zum Scharfschalten",
   ""
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
   ""
  ],
  "notify_unavailable": [
   "Ausgefallene Sensoren melden",
   "Push, wenn ein Sensor nicht verfügbar ist, während die Anlage scharf ist (leere Batterie, Funkproblem, Sabotage)."
  ],
  "unavailable_delay": [
   "Wartezeit vor der Meldung",
   "Kurze Aussetzer innerhalb dieser Zeit werden nicht gemeldet. 0 = sofort melden."
  ],
  "new_code": [
   "Neuer Code",
   "4 bis 10 Ziffern. Leer lassen, um den bisherigen Code zu behalten."
  ],
  "remove_code": [
   "Code entfernen",
   ""
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
   ""
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
   ""
  ],
  "alarm_volume": [
   "Alarm-Lautstärke",
   ""
  ],
  "reset_volume": [
   "Lautstärke danach",
   ""
  ],
  "reset_volume_after": [
   "Lautstärke zurück nach",
   ""
  ],
  "sound_devices": [
   "Alexa-Geräte für den Alarmton",
   ""
  ],
  "sound": [
   "Alarmton",
   "Sound-Name von Alexa Devices."
  ],
  "speak_services": [
   "Gesprochener Text",
   "Benachrichtigungsdienste, die den Alarmtext sprechen (z. B. Alexa Media)."
  ],
  "turn_on_entities": [
   "Einschalten",
   "Lichter, Schalter, Kameras."
  ],
  "close_covers": [
   "Rollos schließen",
   ""
  ],
  "call_addon": [
   "ha-sip-Add-on",
   "Slug des Add-ons, z. B. 1234abcd_ha-sip. Leer = kein Anruf."
  ],
  "call_targets": [
   "Nummern der Reihe nach",
   "SIP-Adressen oder Nummern, je Eintrag eine."
  ],
  "call_acknowledge": [
   "Quittieren mit Taste 1",
   "Jede Nummer außer der letzten kann die Kette beenden."
  ],
  "call_wait": [
   "Warten bis zur nächsten Nummer",
   ""
  ],
  "call_tts": [
   "Sprachausgabe für den Anruf",
   ""
  ],
  "call_language": [
   "Sprache des Anrufs",
   ""
  ],
  "call_cooldown": [
   "Kein neuer Anruf für",
   "Innerhalb dieser Zeit nach einem Alarm startet keine neue Anrufkette. Push-Meldungen kommen immer."
  ],
  "presence_mode": [
   "Anwesenheit über",
   ""
  ],
  "wifi_sensors": [
   "Weitere WLAN-Sensoren",
   "Handys ohne Unterpunkt Person. Personen werden als Unterpunkt \"Person\" angelegt."
  ],
  "home_networks": [
   "Heim-WLANs",
   "Namen der WLANs zuhause."
  ],
  "persons": [
   "Personen",
   ""
  ],
  "quiet_time": [
   "Keine Bewegung seit",
   ""
  ],
  "prewarn_time": [
   "Vorwarnung vor dem Scharfschalten",
   ""
  ],
  "retry_after_disarm": [
   "Warten nach dem Unscharfschalten",
   ""
  ],
  "presence_stable": [
   "Abwesend seit mindestens",
   ""
  ],
  "lock": [
   "Türschloss",
   ""
  ],
  "lock_door_sensor": [
   "Türkontakt",
   "Abgeschlossen wird nur bei geschlossener Tür."
  ],
  "disarm_on_unlock": [
   "Entriegeln schaltet unscharf",
   ""
  ],
  "lock_on_arm": [
   "Beim Scharfschalten abschließen",
   "Nicht, wenn Kinder alleine zuhause sind."
  ],
  "night_door_sensor": [
   "Türkontakt",
   "Leer = kein Türalarm."
  ],
  "night_tag": [
   "NFC-Tag-ID",
   "Scannen schaltet den Türalarm an und aus."
  ],
  "night_turn_on_entities": [
   "Einschalten",
   "Lichter auf 100 %."
  ],
  "night_volume_players": [
   "Lautsprecher für Lautstärke",
   ""
  ],
  "night_sound_devices": [
   "Alexa-Geräte für den Alarmton",
   ""
  ],
  "night_speak_services": [
   "Gesprochener Text",
   ""
  ],
  "night_text": [
   "Text",
   "Leer = Standardtext."
  ],
  "night_reset_volume_after": [
   "Lautstärke zurück nach",
   ""
  ],
  "night_off_time": [
   "Ausschalten um",
   ""
  ],
  "night_off_days": [
   "An diesen Tagen",
   ""
  ],
  "night_off_speak_services": [
   "Ansage beim Ausschalten per Tag",
   ""
  ],
  "night_off_volume_players": [
   "Lautsprecher für diese Ansage",
   ""
  ],
  "night_off_volume": [
   "Lautstärke dieser Ansage",
   ""
  ],
  "kids_reset_after_unlock": [
   "Zurücksetzen nach dem Entriegeln",
   ""
  ],
  "kids_reset_time": [
   "Nachts zurücksetzen um",
   ""
  ],
  "hint_door_sensor": [
   "Türkontakt",
   "Leer = kein Hinweis."
  ],
  "hint_windows": [
   "Fenster",
   ""
  ],
  "hint_entity": [
   "Hinweis-Licht",
   ""
  ],
  "hint_duration": [
   "Dauer",
   ""
  ],
  "name": [
   "Name",
   ""
  ],
  "entity": [
   "Sensor",
   ""
  ],
  "type": [
   "Typ",
   ""
  ],
  "use_entry_delay": [
   "Eingangsverzögerung",
   "Aus: löst sofort aus."
  ],
  "use_exit_delay": [
   "Ausgangsverzögerung",
   "Darf während der Ausgangszeit offen sein."
  ],
  "auto_bypass": [
   "Beim Scharfschalten offen = ignorieren",
   "Offene Fenster werden bis zum Unscharfschalten ignoriert statt zu blockieren."
  ],
  "allow_open": [
   "Darf beim Scharfschalten aktiv sein",
   "Für Bewegungsmelder."
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
   ""
  ],
  "camera_preset": [
   "Kamera-Preset",
   "Preset, wenn dieser Bewegungsmelder scharf Bewegung meldet."
  ],
  "privacy_switch": [
   "Schalter Privatsphäre-Modus",
   ""
  ],
  "ptz_select": [
   "PTZ-Preset-Auswahl",
   ""
  ],
  "ptz_home_preset": [
   "Standard-Preset",
   ""
  ],
  "privacy_delay": [
   "Privatsphäre an nach Unscharf",
   ""
  ],
  "record_switches": [
   "Aufnahme-Schalter",
   "Bleiben an, solange der Saugroboter fährt."
  ],
  "detect_switches": [
   "Erkennungs-Schalter",
   "Aus, solange der Saugroboter fährt."
  ],
  "person_sensor": [
   "Person erkannt",
   ""
  ],
  "person_count_sensor": [
   "Anzahl Personen",
   ""
  ],
  "person_image": [
   "Personenbild",
   ""
  ],
  "person_push": [
   "Push mit Bild, wenn nicht unscharf",
   ""
  ],
  "wifi_sensor": [
   "WLAN-Sensor des Handys",
   "Zeigt den Namen des verbundenen WLANs (Companion App)."
  ],
  "garage_panel": [
   "Alarmzentrale Garage",
   ""
  ],
  "garage_networks": [
   "Garagen-WLANs",
   "Unscharf, solange ein Handy verbunden ist (WLAN-Sensoren der Personen und die weiteren)."
  ],
  "garage_arm_delay": [
   "Scharf nach dem Verlassen",
   ""
  ],
  "garage_motion": [
   "Bewegungssensoren",
   ""
  ],
  "garage_tts_services": [
   "Gesprochene Warnung auf Handys",
   "Benachrichtigungsdienste der Companion App."
  ],
  "garage_tts_text": [
   "Gesprochener Text",
   "Leer = Standardtext."
  ],
  "garage_tts_repeat": [
   "Wiederholen",
   ""
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
   "How long the alarm stays triggered."
  ],
  "disarm_after_trigger": [
   "Disarm after the trigger time",
   "Off: armed again afterwards."
  ],
  "code_arm_required": [
   "Code also for arming",
   ""
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
   ""
  ],
  "notify_unavailable": [
   "Report unavailable sensors",
   "Push when a sensor is unavailable while armed (empty battery, radio problem, sabotage)."
  ],
  "unavailable_delay": [
   "Delay before the report",
   "Short drop-outs within this time are not reported. 0 = report at once."
  ],
  "new_code": [
   "New code",
   "4 to 10 digits. Leave empty to keep the current code."
  ],
  "remove_code": [
   "Remove code",
   ""
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
   ""
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
   ""
  ],
  "alarm_volume": [
   "Alarm volume",
   ""
  ],
  "reset_volume": [
   "Volume afterwards",
   ""
  ],
  "reset_volume_after": [
   "Reset volume after",
   ""
  ],
  "sound_devices": [
   "Alexa devices for the alarm sound",
   ""
  ],
  "sound": [
   "Alarm sound",
   "Sound name of Alexa Devices."
  ],
  "speak_services": [
   "Spoken text",
   "Notify services that speak the alarm text (e.g. Alexa Media)."
  ],
  "turn_on_entities": [
   "Turn on",
   "Lights, switches, cameras."
  ],
  "close_covers": [
   "Close covers",
   ""
  ],
  "call_addon": [
   "ha-sip add-on",
   "Slug of the add-on, e.g. 1234abcd_ha-sip. Empty = no call."
  ],
  "call_targets": [
   "Numbers in order",
   "SIP addresses or numbers, one per entry."
  ],
  "call_acknowledge": [
   "Acknowledge with key 1",
   "Every number except the last can stop the chain."
  ],
  "call_wait": [
   "Wait before the next number",
   ""
  ],
  "call_tts": [
   "Speech for the call",
   ""
  ],
  "call_language": [
   "Language of the call",
   ""
  ],
  "call_cooldown": [
   "No new call for",
   "No new call chain within this time after an alarm. Push messages are always sent."
  ],
  "presence_mode": [
   "Presence by",
   ""
  ],
  "wifi_sensors": [
   "Additional Wi-Fi sensors",
   "Phones without a person sub item. Persons are added as sub item \"Person\"."
  ],
  "home_networks": [
   "Home networks",
   "Names of the networks at home."
  ],
  "persons": [
   "Persons",
   ""
  ],
  "quiet_time": [
   "No motion for",
   ""
  ],
  "prewarn_time": [
   "Warning before arming",
   ""
  ],
  "retry_after_disarm": [
   "Wait after disarming",
   ""
  ],
  "presence_stable": [
   "Away for at least",
   ""
  ],
  "lock": [
   "Door lock",
   ""
  ],
  "lock_door_sensor": [
   "Door contact",
   "Locked only when the door is closed."
  ],
  "disarm_on_unlock": [
   "Unlocking disarms",
   ""
  ],
  "lock_on_arm": [
   "Lock when armed",
   "Not while children are alone at home."
  ],
  "night_door_sensor": [
   "Door contact",
   "Empty = no door alarm."
  ],
  "night_tag": [
   "NFC tag ID",
   "Scanning switches the door alarm on and off."
  ],
  "night_turn_on_entities": [
   "Turn on",
   "Lights at 100 %."
  ],
  "night_volume_players": [
   "Speakers for volume",
   ""
  ],
  "night_sound_devices": [
   "Alexa devices for the alarm sound",
   ""
  ],
  "night_speak_services": [
   "Spoken text",
   ""
  ],
  "night_text": [
   "Text",
   "Empty = standard text."
  ],
  "night_reset_volume_after": [
   "Reset volume after",
   ""
  ],
  "night_off_time": [
   "Switch off at",
   ""
  ],
  "night_off_days": [
   "On these days",
   ""
  ],
  "night_off_speak_services": [
   "Announce when switched off by tag",
   ""
  ],
  "night_off_volume_players": [
   "Speakers for this announcement",
   ""
  ],
  "night_off_volume": [
   "Volume of this announcement",
   ""
  ],
  "kids_reset_after_unlock": [
   "Reset after unlocking",
   ""
  ],
  "kids_reset_time": [
   "Reset at night",
   ""
  ],
  "hint_door_sensor": [
   "Door contact",
   "Empty = no hint."
  ],
  "hint_windows": [
   "Windows",
   ""
  ],
  "hint_entity": [
   "Hint light",
   ""
  ],
  "hint_duration": [
   "Duration",
   ""
  ],
  "name": [
   "Name",
   ""
  ],
  "entity": [
   "Sensor",
   ""
  ],
  "type": [
   "Type",
   ""
  ],
  "use_entry_delay": [
   "Entry delay",
   "Off: triggers immediately."
  ],
  "use_exit_delay": [
   "Exit delay",
   "May be open during the exit time."
  ],
  "auto_bypass": [
   "Ignore when open at arming",
   "Open windows are ignored until disarming instead of blocking."
  ],
  "allow_open": [
   "May be active at arming",
   "For motion sensors."
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
   ""
  ],
  "camera_preset": [
   "Camera preset",
   "Preset when this motion sensor reports motion while armed."
  ],
  "privacy_switch": [
   "Privacy mode switch",
   ""
  ],
  "ptz_select": [
   "PTZ preset select",
   ""
  ],
  "ptz_home_preset": [
   "Default preset",
   ""
  ],
  "privacy_delay": [
   "Privacy on after disarming",
   ""
  ],
  "record_switches": [
   "Recording switches",
   "Stay on while the vacuum drives."
  ],
  "detect_switches": [
   "Detection switches",
   "Off while the vacuum drives."
  ],
  "person_sensor": [
   "Person detected",
   ""
  ],
  "person_count_sensor": [
   "Person count",
   ""
  ],
  "person_image": [
   "Person image",
   ""
  ],
  "person_push": [
   "Push with image when not disarmed",
   ""
  ],
  "wifi_sensor": [
   "Wi-Fi sensor of the phone",
   "Shows the name of the connected network (companion app)."
  ],
  "garage_panel": [
   "Garage alarm panel",
   ""
  ],
  "garage_networks": [
   "Garage networks",
   "Disarmed while a phone is connected (Wi-Fi sensors of the persons and the additional ones)."
  ],
  "garage_arm_delay": [
   "Arm after leaving",
   ""
  ],
  "garage_motion": [
   "Motion sensors",
   ""
  ],
  "garage_tts_services": [
   "Spoken warning on phones",
   "Companion app notify services."
  ],
  "garage_tts_text": [
   "Spoken text",
   "Empty = standard text."
  ],
  "garage_tts_repeat": [
   "Repeat",
   ""
  ]
 }
};
