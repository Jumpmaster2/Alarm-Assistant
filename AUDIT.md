# Audit: Alarm Assistant (Version 0.4.5)

Stand: 21.10.2026 · Geprüft: alle Dateien des Repositories (Python, JSON, JavaScript, Workflows, Doku, Tests).
Werkzeuge: `ruff check` (sauber), `ruff format --check` (1 Datei), `pytest` (68 von 68 bestanden, lokal mit Home Assistant 2026.2.3 / Python 3.13).
Jeder Fund mit „bestätigt“ wurde mit einem temporären Test gegen die laufende Integration nachgestellt (der Test ist nicht im Repository).

---

## 1. Zusammenfassung und Gesamtbewertung

**Zweck:** Alarm Assistant ist eine rein lokal rechnende Alarmzentrale (`iot_class: calculated`) für Home Assistant. Sie ersetzt Alarmo plus die üblichen Automationen drumherum: Scharf/Unscharf (Modus „Abwesend“), Ein-/Ausgangsverzögerung, offene Fenster ignorieren, automatisches Scharfschalten bei Abwesenheit, Reaktionen bei Alarm (Durchsage, Alexa-Alarmton, Licht, Rollos), Anrufkette über das ha-sip-Add-on, Türschloss, Kamera-/Frigate-Regeln, Garage (zweite Zentrale), Nacht-Türalarm per NFC und einen Fenster-offen-Hinweis.

**Architektur:**

| Schicht | Dateien | Aufgabe |
|---|---|---|
| Einstieg | `__init__.py` | Engine erzeugen, Gerät anlegen, Plattformen laden, WebSocket-API und Seitenleisten-Panel registrieren |
| Engine | `engine.py` (1770 Zeilen) | `DataUpdateCoordinator` ohne Polling als Ereignis-Hub: Zustandslistener, Timer, Hintergrund-Tasks, Speicherung in `.storage` |
| Reine Logik | `logic/*.py` | Zustandsautomat, Auto-Scharf-Regeln, Anrufplan, Kamera-Regeln, Sensorfilter – ohne HA-Importe, gut testbar |
| Plattformen | `alarm_control_panel.py`, `binary_sensor.py`, `sensor.py`, `switch.py`, `button.py`, `entity.py` | Dünne Entitäten, lesen den Zustand aus der Engine |
| Einstellungen | `config_flow.py`, `websocket.py`, `frontend/panel.js`, `frontend/labels.js` | Config Flow (2 Schritte), Options Flow (Menü mit 9 Seiten), 4 Subentry-Typen (Sensor, Person, Kamera, Garage) und zusätzlich ein eigenes Admin-Panel über WebSocket |
| Sonstiges | `diagnostics.py`, `logbook.py`, `messages.py`, `const.py`, `icons.json`, `strings.json`, `translations/` | Diagnose, Logbuch, Meldungstexte DE/EN |

**Datenfluss:** Zustandswechsel konfigurierter Entitäten / `tag_scanned` / Zeitpunkte → Engine-Callback → Logik-Funktion entscheidet → Engine ruft HA-Dienste (`notify.*`, `alexa_devices.send_sound`, `media_player.volume_set`, `hassio.addon_stdin`, `lock.lock`, `switch.*`, `cover.*`, `select.select_option`, `alarm_control_panel.*`) → `async_update_listeners()` aktualisiert die Entitäten → Zustand wird verzögert in `.storage/alarm_assistant.<entry_id>` gespeichert.

**Externe Schnittstellen:** Keine Cloud, keine eigenen Netzwerkverbindungen, keine `requirements`. Abhängig (optional) von: Alexa Devices (Alarmton), Alexa Media o. ä. (Sprachausgabe), ha-sip-Add-on über Supervisor (Anruf), Companion App (WLAN-Sensoren, TTS-Push), Frigate (Schalter), Blink o. ä. (Garage).

**Gesamtbewertung: gut, mit einigen ernsten Lücken.**
Die Codebasis ist sauber strukturiert, vollständig asynchron, ohne blockierende Aufrufe, die reine Logik ist sauber getrennt und gut getestet. Timer, Listener und Tasks werden beim Entladen aufgeräumt. Übersetzungen DE/EN sind schlüsselgleich. Schwächen:

* **Sicherheit/Logik bei einem Alarmsystem:** Unscharfschalten stoppt die laufende Anrufkette nicht; ein Schloss, das nach „nicht verfügbar“ als „entriegelt“ zurückkommt, schaltet die Anlage unscharf; Diagnosedaten enthalten den (ungesalzenen, leicht knackbaren) Code-Hash, Telefonnummern, WLAN-Namen und die NFC-Tag-ID.
* **Validierung:** Die WebSocket-API des Panels umgeht alle Bereichsgrenzen des Options Flows; ein falscher Wert kann die Integration beim Start abstürzen lassen.
* **Allgemeingültigkeit:** Alarmton nur über Alexa Devices, Anrufsprache fest „de“, TTS-Parameter nur für Android, Standardwerte aus einem konkreten Haushalt.
* **UI:** 69 von 131 Formularfeldern ohne Erklärung, mehrere Freitextfelder, wo ein Selektor möglich wäre, keine Prüfung abhängiger Felder.
* **Doku/Tests:** README ohne manuelle Installation, Debug-Logging und Fehlerbehebung; Versionsangabe veraltet; Fehlerfälle von Flows und WebSocket kaum getestet.

Keine hartcodierten Passwörter, Tokens, IPs, Hostnamen oder Ports gefunden. SSL wird nirgends abgeschaltet. Es werden keine eigenen Dienste registriert; alle WebSocket-Befehle verlangen Admin-Rechte; das Panel ist `require_admin`. `ConfigEntryNotReady`/`ConfigEntryAuthFailed`/`UpdateFailed`/Reauth sind für eine rein berechnende Integration ohne Zugangsdaten **nicht anwendbar** (kein Fund).

---

## 2. Tabelle aller Funde

Schweregrad: **K** = Kritisch, **H** = Hoch, **M** = Mittel, **N** = Niedrig.

### 2.1 Fehler, Logik, Sicherheit

| ID | Kategorie | Schwere | Datei:Zeile | Problem | Auswirkung | Lösungsvorschlag |
|---|---|---|---|---|---|---|
| F01 | Logikfehler | **H** (bestätigt) | `engine.py:998-1022`, `engine.py:1136-1174` | `disarm()` bricht die laufenden Tasks `call`, `siren`, `announce`, `announce_pending`, `reactions` nicht ab. Die Anrufkette prüft nur `call_acked`, nicht den Zustand. Test: Unscharf nach dem 1. Anruf → Nummer 2 und 3 werden trotzdem angerufen. | Nach Unscharfschalten werden weiter Angehörige mit „Einbruchalarm“ angerufen, Sirene/Durchsage laufen weiter. | In `disarm()` die Alarm-Tasks abbrechen (`self._tasks[...]`), danach Lautstärke zurücksetzen; in der Anrufschleife zusätzlich `if self.state != sm.TRIGGERED: break`. Test ergänzen. |
| F02 | Sicherheit / Logik | **H** (bestätigt) | `engine.py:1293-1305` | `_on_lock` wertet auch den Übergang `unavailable/unknown/None → unlocked` als Entriegeln. Test: Schloss beim Scharfschalten nicht verfügbar, meldet sich „unlocked“ zurück → Anlage unscharf. | Funkabbruch, Bridge-Neustart oder Akkuwechsel am Schloss schaltet die Alarmanlage ohne Zutun unscharf. | Nur echte Wechsel aus einem gültigen Zustand werten (`old.state in ("locked","locking","jammed")`); Übergänge aus `INVALID` ignorieren. Test ergänzen. |
| F03 | Sicherheit / Datenschutz | **H** (bestätigt) | `diagnostics.py:16` | `entry.as_dict()` wird ungeschwärzt ausgegeben: Code-Hash, `call_targets` (Telefonnummern/SIP), `home_networks`/`garage_networks` (SSIDs), `night_tag` (NFC-ID schaltet den Türalarm), `call_addon`. Der Docstring behauptet „contains no secrets“. | Diagnosedateien werden oft öffentlich in GitHub-Issues angehängt → personenbezogene Daten und ein in Millisekunden knackbarer PIN-Hash (s. F04) werden veröffentlicht. | `async_redact_data()` mit `TO_REDACT = {code, call_targets, home_networks, garage_networks, night_tag, call_addon, title}` auf Optionen und Subentries; Test, dass diese Werte als `**REDACTED**` erscheinen. |
| F04 | Sicherheit | **M** | `engine.py:183-184`, `config_flow.py:471,552`, `websocket.py:177` | Code wird als ungesalzener SHA-256 gespeichert. Bei 4-6 Ziffern sind das ≤ 10⁶ Versuche (Sekundenbruchteile). | Wer die Config-Entry-Daten oder Diagnosen sieht, kennt den PIN. | PBKDF2-HMAC-SHA256 mit zufälligem Salt (`hashlib.pbkdf2_hmac`, ≥ 100 000 Runden), Format `pbkdf2$runden$salt$hash`; alte Hashes beim nächsten richtigen Code migrieren. Vergleich mit `hmac.compare_digest`. |
| F05 | Sicherheit | **N** | `engine.py:812` | Vergleich mit `==` statt `hmac.compare_digest`. | Theoretisches Timing-Leck (lokal kaum ausnutzbar). | Zusammen mit F04 beheben. |
| F06 | Sicherheit | **N** | `alarm_control_panel.py:69-71` | Keine Begrenzung/Meldung bei falschen Code-Eingaben. | Durchprobieren über Dashboard möglich, bleibt unbemerkt. | Nach z. B. 5 Fehlversuchen Logbuch-Eintrag + Admin-Push; optional kurze Sperre. |
| F07 | Fehlerbehandlung / Validierung | **M** (bestätigt) | `websocket.py:217-239`, `engine.py:352` | `save_subentry` speichert `data` ungeprüft. Test: `arm_cover_position: "abc"` → `ValueError` in `_build()` → Config Entry `SETUP_ERROR`. | Ein Tippfehler im Panel legt die komplette Alarmanlage still. | Je Subentry-Typ ein `vol.Schema` (Typen, Bereiche, erlaubte Schlüssel, Entitäts-Domain) und in `websocket.py` und `config_flow.py` gemeinsam nutzen; `_build()` zusätzlich defensiv (`_as_int`). |
| F08 | Validierung | **M** (bestätigt) | `websocket.py:75-89, 159-170` | `save_options` prüft nur den Typ, keine Bereiche/Auswahlwerte. Test: `entry_delay: -50`, `alarm_volume: 7`, `night_off_days: ["xyz"]` werden gespeichert. `bool("false")` ergäbe `True`. | Ungültige Lautstärken (Dienst schlägt bei Alarm fehl), negative Zeiten (Timer in der Vergangenheit), stille Fehlkonfiguration. | Ein zentrales Options-Schema (gleiche Grenzen wie die `NumberSelector` im Options Flow) für Flow **und** WebSocket; Fehler mit Feldnamen zurückgeben. |
| F09 | Logik / Allgemeingültigkeit | **M** | `const.py:143`, `engine.py:1153`, `logic/call.py:16` | Anrufsprache standardmäßig fest `"de"`, während der Anruftext der Meldungssprache folgt. | Englische Nutzer bekommen englischen Text mit deutscher Sprachausgabe. | Standard leer = Sprache aus `resolve_language()` (`de`→`de`, sonst `en`), als Select-Selektor anbieten. |
| F10 | Logik | **M** (zu prüfen, ob gewollt) | `engine.py:1085-1087`, `engine.py:1143-1146` | Die Anruf-Sperrzeit (`call_cooldown`, 180 s) unterdrückt auch **alle Push-Meldungen** eines zweiten Alarms – auch nach Unscharf + erneutem Scharf. Der Test `test_call_chain_with_acknowledge` bestätigt das Verhalten. | Ein echter zweiter Einbruch kurz nach einem Fehlalarm wird nicht gemeldet. | Sperrzeit nur für Anrufe; Push immer senden; Sperrzeit beim Unscharfschalten zurücksetzen (oder Option). |
| F11 | Sicherheit (Funktion fehlt) | **M** | `engine.py:755-765` | Ein Sensor, der im scharfen Zustand `unavailable` wird (Sabotage, leere Batterie, Funkausfall), löst keine Meldung aus. | Ausgefallene Melder bleiben unbemerkt, die Anlage ist löchrig. | Option „Ausfall melden“: bei `unavailable` > X s im Zustand scharf eine Admin-Push und Hinweis im Panel; beim Scharfschalten nicht verfügbare Sensoren nennen. |
| F12 | Logik | **N** | `engine.py:973-979` | Rückfall-Erkennung des Schlosses nur für `unlocked`; `jammed` (HA-Standardzustand) wird nicht behandelt. | Klemmendes Schloss → keine Meldung „nicht abgeschlossen“. | `jammed` wie fehlgeschlagenes Abschließen behandeln. |
| F13 | Logik | **N** (bestätigt) | `config_flow.py:609-635`, `websocket.py:222`, `logic/state_machine.py:129-134` | Dieselbe Entität kann mehrfach als Sensor angelegt werden; `SensorTracker` ist nach `entity_id` geschlüsselt, daher löst nur der erste Eintrag aus, der zweite wird still ignoriert. | Verwirrendes, von der Reihenfolge abhängiges Verhalten. | Doppelte Entität im Flow und in der WebSocket-API mit Fehler `already_configured` ablehnen. |
| F14 | Logik | **N** | `config_flow.py:264` | `trigger_time` darf 0 sein → Alarm endet sofort, Sirene/Anruf laufen trotzdem. | Unklare Wirkung. | Minimum 10 s oder Hinweis in `data_description`. |
| F15 | Logik (zu prüfen) | **N** | `logic/auto_arm.py:13-16` | Ein nicht verfügbarer WLAN-Sensor zählt als „abwesend“ (Handy-Akku leer zuhause). Nur die Bewegungs-Ruhezeit verhindert Fehl-Scharfschalten. | Scharfschalten, obwohl jemand ruhig zuhause ist (z. B. schläft). | Option „Nicht verfügbar zählt als: abwesend/anwesend“ (Standard anwesend) und in README erklären. |
| F16 | Logik | **N** | `engine.py:1640-1641`, `engine.py:551-552` | Die Garage nutzt nur WLAN-Sensoren; mit Anwesenheitsmodus „Personen“ ohne WLAN-Sensoren ist die Garage nie unscharf. | Funktion stumm wirkungslos. | Im Garage-Subentry prüfen und Fehler „Garage braucht WLAN-Sensoren“ anzeigen. |
| F17 | Ressourcen | **N** | `engine.py:650, 929, 950, 971, 1010, 1653, 1670, 1703` | `hass.async_create_task` statt `config_entry.async_create_background_task` / `_task()`. | Beim Entladen/Neuladen werden diese Aufrufe nicht abgebrochen (kurzlebig, daher gering). | Einheitlich über `config_entry.async_create_task` bzw. `_task()` starten. |
| F18 | Aufräumen | **N** (bestätigt) | `__init__.py:37-48` | Das Reparatur-Issue `missing_entities` bleibt nach dem Entfernen der Integration bestehen; das Panel bleibt nach dem Deaktivieren sichtbar. | Verwaiste Meldung unter Reparaturen. | In `async_remove_entry` `ir.async_delete_issue(...)`; Panel in `async_unload_entry` entfernen, wenn der Eintrag deaktiviert wird (oder bewusst lassen und dokumentieren). |
| F19 | Robustheit (zu prüfen) | **N** | `websocket.py:67-72, 273` | `_entry()` liefert auch einen nicht geladenen Eintrag; `test_arm`/`test_trigger` arbeiten dann evtl. mit einer veralteten `runtime_data`-Engine ohne Listener. | Testalarm auf einer „toten“ Engine (abhängig davon, ob HA `runtime_data` beim Entladen entfernt). | Für Befehle mit Engine nur `ConfigEntryState.LOADED` akzeptieren, sonst Fehler `not_loaded`. |
| F20 | Wartbarkeit | **N** | `config_flow.py:469`, `websocket.py:168` | Bei der Einrichtung werden **alle** `DEFAULTS` in die Optionen geschrieben. | Spätere Änderungen von Standardwerten erreichen bestehende Installationen nie. | Nur abweichende Werte speichern; `engine.opt()` mischt `DEFAULTS` ohnehin dazu. |

### 2.2 Home-Assistant-Konformität, Performance, Codequalität

| ID | Kategorie | Schwere | Datei:Zeile | Problem | Auswirkung | Lösungsvorschlag |
|---|---|---|---|---|---|---|
| F21 | HA-Konformität | **M** | `engine.py:676`, `const.py:133`, `config_flow.py:202-203, 304` | Alarmton nur über `alexa_devices.send_sound` mit Alexa-Soundnamen. Kein Weg für `siren.*`-Entitäten oder `media_player.play_media`. | Ohne Echo-Geräte gibt es keinen Alarmton. | Zusätzliche Optionen „Sirenen“ (`siren.turn_on`) und „Alarmton-Datei/URL auf Lautsprechern“ (`media_player.play_media`); Alexa bleibt eine Variante. |
| F22 | Allgemeingültigkeit | **M** | `engine.py:1716-1720` | Garagen-TTS sendet fest `media_stream: alarm_stream_max` (nur Android Companion App) und `tts_language` nur `de-DE`/`en-US`. | iOS-Nutzer bekommen keine gesprochene Warnung. | Plattform-Hinweis in der UI; `media_stream` als Option; iOS-Variante (`push.sound` / kritische Benachrichtigung) dokumentieren. |
| F23 | Fehlerbehandlung | **M** | `engine.py:625-631`, `engine.py:477` | Ohne Supervisor (Container/Core) gibt es `hassio.addon_stdin` nicht; der Anruf scheitert erst beim Alarm mit einer Log-Warnung. `_check_missing` prüft den Dienst nicht. | Nutzer glaubt, der Anruf sei eingerichtet. | Beim Start prüfen: Anruf konfiguriert und `hassio.addon_stdin` fehlt → Reparatur-Issue; im Options Flow Fehler `supervisor_required`. |
| F24 | Fehlerbehandlung | **N** | `engine.py:625-631` | Fehler einzelner Reaktionen landen nur im Log. | Ein kaputtes Notify-Ziel fällt erst im Ernstfall auf. | Fehlgeschlagene Reaktionen sammeln und im Panel/Diagnose anzeigen; Testmeldung meldet Fehler zurück. |
| F25 | HA-Konformität | **N** | `binary_sensor.py:42`, `button.py:34`, `sensor.py` | Keine `entity_category`: „Testmeldung“ sollte `CONFIG`, „Bewegung unterdrückt“ `DIAGNOSTIC` sein. | Unnötige Entitäten in Standard-Dashboards. | `_attr_entity_category` setzen. |
| F26 | HA-Konformität | **N** | `switch.py:25`, `button.py:21` | Schalter „Automatisch scharf“ und Button „Anruf quittieren“ entstehen immer, auch wenn Auto-Scharf/Anruf nicht eingerichtet sind. | Wirkungslose Entitäten. | Nur anlegen, wenn konfiguriert (wie `night_door`), oder `entity_registry_enabled_default=False`. |
| F27 | Quality Scale / HACS | **N** | Repository | Kein `quality_scale.yaml`; keine Git-Tags/Releases (HACS zeigt dann Commit-Hashes statt Versionen); `hacs.json` verlangt HA 2026.10.0, lokal getestet nur mit 2026.2.3 (CI mit Python 3.14 nutzt neuere Version). | Versionsverfolgung und Update-Hinweise in HACS fehlen. | Releases mit Tag `v0.4.x` per Workflow; `quality_scale.yaml` (Bronze-Regeln abhaken); Mindestversion bewusst wählen und im CI fest testen. |
| F28 | Dokumentation | **N** | `README.md:7` | „Status: Version 0.4.3“, `manifest.json` sagt 0.4.5. | Verwirrung. | Version im README entfernen oder automatisch pflegen. |
| F29 | Performance | **N** | `engine.py:294-299, 739-765` | `opts` baut bei jedem `opt()`-Aufruf ein neues Dict; jede Zustandsänderung eines Eingangs (auch Attribute des Saugroboters wie Akku) ruft `_evaluate_sensors` + `_changed()` → Speichern + Update aller Entitäten. | Geringe Last, viele unnötige Zustands-Schreibvorgänge bei großen Setups. | `opts` bei Engine-Erzeugung einmal cachen (Reload bei Änderung ist vorhanden); `_changed()` nur bei tatsächlicher Änderung; Saugroboter-Ereignisse ohne Zustandswechsel ignorieren. |
| F30 | Performance | **N** | `frontend/panel.js:684-704` | Bei jedem kompletten Rendern werden Datalists aller Entitäten gebaut. | Spürbar bei mehreren tausend Entitäten. | Datalists einmal bauen und nur bei Tabwechsel aktualisieren. |
| F31 | Frontend | **N** | `frontend/panel.js:5`, `panel.py:37` | `labels.js` wird ohne Versionsparameter importiert (`cache_headers=False` hilft nur teilweise). | Nach Update evtl. veraltete Beschriftungen im Browser-Cache. | `import(\`./labels.js?v=${version}\`)` oder beide Dateien zu einer bündeln. |
| F32 | Frontend / Sicherheit | **N** | `frontend/panel.js:1399` | Code-Eingabe über `prompt()` – Eingabe ist sichtbar. | Code kann mitgelesen werden. | Eigener Dialog mit `type=password inputmode=numeric`. |
| F33 | Codequalität | **N** | `frontend/labels.js:1` | „Generated from the translation source, do not edit by hand“, aber kein Generator-Skript im Repository. | Beschriftungen im Panel und in `strings.json` laufen auseinander. | Skript `scripts/build_labels.py` ergänzen und im CI prüfen, dass `labels.js` aktuell ist. |
| F34 | Codequalität | **N** | `messages.py:49`, `messages.py:108` | `ruff format` meldet `messages.py` (fehlendes Leerzeichen); Text `last_active` wird nirgends verwendet. | Kosmetik, toter Code. | Formatieren, Text entfernen; `ruff format --check` ins CI. |
| F35 | Codequalität | **N** | `engine.py:160` / `logic/sensors.py:5`; `engine.py:1546-1554`; `engine.py:352` | `INVALID` doppelt definiert; `_frigate_switches`/`_frigate_split` lesen dieselben Listen doppelt; Standard 20 für Rollo-Position doppelt (`SENSOR_DEFAULTS` wird schon gemischt). | Kleine Duplikate. | Zusammenführen. |
| F36 | Codequalität | **N** | `config_flow.py:468`, `alarm_control_panel.py:48` | Code wird nicht als Ziffernfolge geprüft, das Panel meldet aber `CodeFormat.NUMBER`. | Ein Buchstaben-Code ist im Ziffernblock nicht eingebbar (zu prüfen je Frontend-Version). | Code auf 4-10 Ziffern prüfen (Fehler `code_invalid`) oder `CodeFormat.TEXT` bei Nicht-Ziffern. |
| F37 | Sicherheit (Standard überdenken) | **N** | `const.py:153` | `disarm_on_unlock` ist standardmäßig an: jedes Entriegeln (auch per App, Schlüssel, Bluetooth eines Dritten) schaltet ohne Code unscharf. | Bequem, aber für fremde Systeme ein riskanter Standard. | Standard „aus“ für neue Installationen, mit Erklärung in `data_description`. |

**Ausdrücklich geprüft und ohne Befund:** keine blockierenden I/O-Aufrufe im Event Loop (`_version()` läuft im Executor), Listener/Timer/Tasks werden in `async_shutdown` aufgeräumt, `has_entity_name` überall, eindeutige `unique_id`s, Device-Registry-Eintrag vorhanden, `device_class` sinnvoll (Bewegung, Öffnung, Anwesenheit, Zeitstempel), keine Einheiten bei Sensoren nötig, keine veralteten APIs (`AddConfigEntryEntitiesCallback`, `runtime_data`, `async_schedule_reload`, `OptionsFlow` ohne `__init__` sind aktuell), Zeitzonen über `dt_util.as_local`/`async_track_time_change` korrekt, HTML-Ausgabe im Panel konsequent mit `esc()` maskiert, keine eigenen HA-Dienste, WebSocket-Befehle mit `require_admin`.

---

## 3. Systemspezifische Werte und vorgeschlagene Einstellungen

Gefunden wurden keine hartcodierten IPs, Hostnamen, Ports, Benutzernamen oder Pfade. Die Zuschnitte auf ein bestimmtes System stecken in **Standardwerten, festen Diensten und internen Konstanten**:

| Wert | Ort | Heute | Vorschlag | Wo | Validierung / Erklärung |
|---|---|---|---|---|---|
| Alarmton-Dienst | `engine.py:676` | fest `alexa_devices.send_sound` | Auswahl „Alarmton über“: Alexa Devices / Sirenen-Entitäten / Lautsprecher (Datei/URL) | Options Flow „Reaktionen“ | Je nach Auswahl Device-, Entity- (`siren`) oder Media-Selektor |
| Alarmton-Name | `const.py:133` | `amzn_sfx_scifi_alarm_04` | Select-Selektor mit den Alexa-Sounds (custom_value erlaubt) | Options Flow | Nur sichtbar bei Alexa |
| Anrufsprache | `const.py:143` | `de` | leer = folgt Meldungssprache | Options Flow „Telefonanruf“ | Select `de`/`en`/… |
| ha-sip-Add-on | `config_flow.py:326` | Freitext Slug | Select mit installierten Add-ons (Supervisor-Info), Slug enthält `ha-sip`; automatisch vorbelegen | Options Flow | Fehler `addon_not_found`, `supervisor_required` |
| Annahme-Timeout Anruf | `logic/call.py:17` | 30 s fest | Option „Wartezeit auf Taste 1“ | Options Flow (erweitert) | 5-120 s |
| Mobile-App-TTS-Stream | `engine.py:1718` | `alarm_stream_max` | Option, Standard `alarm_stream_max`, Hinweis „nur Android“ | Garage-Subentry | Select `alarm_stream`/`alarm_stream_max`/`music_stream` |
| TTS-Sprache Garage | `engine.py:1719` | `de-DE`/`en-US` | aus HA-Sprache + Land (`hass.config.country`) ableiten | intern | – |
| Anwesenheitsmodus | `const.py:145` | `wifi` | Standard `persons` (jede HA-Installation hat `person.*`) | Options Flow „Automatisch scharf“ | Bei `wifi` Fehler, wenn keine Heimnetze/Sensoren |
| WLAN-Sensor-Filter | `config_flow.py:341, 781` | jeder `sensor` | Entity-Selektor mit `integration: mobile_app` | Options/Person-Subentry | – |
| Heim-WLANs | `config_flow.py:342` | Freitext | Select mit aktuell gemeldeten SSIDs der gewählten Sensoren als Vorschläge (custom_value) | Options Flow | mind. 1, wenn Modus WLAN |
| „Nicht verfügbar“ bei WLAN | `logic/auto_arm.py:16` | zählt als abwesend | Option „Unbekanntes Handy zählt als“ | Options Flow (erweitert) | Standard „anwesend“ |
| Kinder-Reset nachts | `const.py:156` | 03:00 | bleibt, aber mit Beschreibung | Options Flow | Time-Selektor (vorhanden) |
| Türalarm aus | `const.py:157-158` | 05:00, Mo-Fr | bleibt, Beschreibung ergänzen | Options Flow | – |
| Alarm-Lautstärke | `const.py:135` | 0,51 | 0,7 als runderer Standard, in % anzeigen | Options Flow | Number 0-100 % |
| Schloss-Nachlaufzeit | `engine.py:164-165` | 20 s / Wiederholung 10 s | Option „Schloss: Rückfall-Erkennung“ | Options Flow „Türschloss“ (erweitert) | 5-120 s |
| Pausen in Abläufen | `engine.py:167-169` | 2/4/3 s | Option „Kamera-Aufwachzeit“ (PTZ/Privatsphäre) | Kamera-Subentry | 0-30 s |
| Frigate-Neusetzen | `engine.py:173-175` | 10 s, 3×/10 min | bleibt intern (sinnvolle Sicherung), dokumentieren | – | – |
| NFC-Doppelscan-Sperre | `logic/misc.py:26` | 10 s | bleibt intern | – | – |
| NFC-Tag | `config_flow.py:367` | Freitext | Select aus vorhandenen `tag.*`-Entitäten (wie im Panel) | Options Flow | – |
| Sound/Sprache „Alexa Media“ | `strings.json:144` | Beispiel nennt Alexa Media | neutral formulieren: „notify-Dienste oder TTS-Entitäten“ | Übersetzungen | – |

**Config Flow vs. Options Flow:** Grundeinstellungen (Sprache, Benachrichtigungen, Zeiten, Code) sind bereits im Config Flow, alles Weitere im Options Flow bzw. in Subentries – das Prinzip stimmt. Es fehlt: ein optionaler dritter Einrichtungsschritt **„Sensoren übernehmen“** (siehe Discovery).

**Einrichtung ohne Vorwissen / Auto-Discovery:** Klassische Discovery (zeroconf/SSDP) ist nicht sinnvoll, da kein Gerät. Sinnvoll sind Vorschläge aus der eigenen Installation:
1. Im Config Flow ein Schritt mit Multi-Entity-Selektor, vorgefiltert auf `binary_sensor` mit `device_class` `door`/`window`/`garage_door`/`opening`/`motion`/`occupancy`; daraus Sensor-Subentries mit passendem Typ anlegen.
2. ha-sip-Add-on, Alexa-Geräte, `mobile_app`-WLAN-Sensoren und `person.*` automatisch vorschlagen.
3. Nach der Einrichtung eine Reparatur-/Hinweiskarte „Noch keine Sensoren angelegt“.

---

## 4. UI/UX-Prüfung und Verbesserungen

### 4.1 Config Flow und Options Flow

| # | Vorher | Nachher |
|---|---|---|
| U1 | 69 von 131 Feldern ohne `data_description` (u. a. alle Lautstärken, Auto-Scharf-Zeiten, `dock_grace`, `call_wait`, `call_tts`, `call_language`, `lock`, `disarm_on_unlock`, fast alle Kamera- und Garage-Felder, Subentry-Namen). | Jedes Feld bekommt eine Beschreibung mit Beispiel, z. B. `quiet_time`: „Wie lange keine Bewegung gemeldet sein darf, bevor die Vorwarnung startet. Beispiel: 10 min.“ |
| U2 | Fachbegriffe ohne Erklärung: „Slug“, „SIP“, „PTZ“, „Preset“, „TTS“, „Frigate“, „Ignorieren (Bypass)“. | Kurz erklären: „Slug = interner Name des Add-ons, zu finden unter Einstellungen › Add-ons › ha-sip (z. B. `1234abcd_ha-sip`).“ |
| U3 | Freitext für Add-on, Alarmton, Anrufsprache, NFC-Tag, Kamera-Preset. | Select-Selektoren (Add-ons, Alexa-Sounds, Sprachen, Tags; Presets aus den `options` der gewählten `select`-Entität). |
| U4 | Keine Prüfung abhängiger Felder: Modus WLAN ohne Heimnetz, Anruf ohne Nummern, Hinweis-Tür ohne Licht, Garage ohne WLAN-Sensoren – alles wird still gespeichert und wirkt nicht. | Fehler mit Lösung, z. B. `home_networks_required`: „Für ‚WLAN der Handys‘ mindestens ein Heim-WLAN eintragen oder Modus ‚Personen‘ wählen.“ |
| U5 | Code: kein Bestätigungsfeld, keine Formatprüfung. | „Neuer Code“ + „Code wiederholen“; Fehler `code_mismatch` / `code_invalid` („4-10 Ziffern“). |
| U6 | Einheiten gemischt: Verzögerungen in s, Auto-Scharf in min, Kamera/Garage in min; Lautstärke 0-1. | Einheitlich `DurationSelector` (zeigt h:m:s) oder klar beschriftet; Lautstärke in %. |
| U7 | Options-Menü „Kinder und Hinweise“ mischt zwei Themen; „Bewegungsfilter“ sitzt getrennt vom Sensor. | Menüpunkte nach Häufigkeit ordnen: Alarm & Code → Benachrichtigungen → Reaktionen → Automatisch scharf → Türschloss → Telefonanruf → Kameras/Bewegungsfilter → Nacht-Türalarm → Fenster-Hinweis; seltene Felder in einklappbare Abschnitte („Erweitert“, `collapsed: true`). |
| U8 | Sensor-Subentry: Felder „Eingangsverzögerung“/„Ausgangsverzögerung“ sind Ja/Nein, aber gleich benannt wie die Zeiten. | „Eingangsverzögerung nutzen“ / „Darf während der Ausgangsverzögerung offen sein“. |
| U9 | Dieselbe Entität kann zweimal als Sensor angelegt werden (F13). | Fehler `already_configured`: „Dieser Sensor ist bereits als ‚Küchenfenster‘ angelegt.“ |
| U10 | Fehlertexte der WebSocket-API sind englische Codes (`invalid`, `unknown option x`), nur 3 werden im Panel übersetzt. | Fehler mit Feld und Code zurückgeben (`{"field": "alarm_volume", "error": "out_of_range"}`), im Panel übersetzen. |

### 4.2 Entitäten

| # | Vorher | Nachher |
|---|---|---|
| U11 | „Testmeldung“ und „Bewegung unterdrückt“ ohne Kategorie. | `entity_category` CONFIG bzw. DIAGNOSTIC. |
| U12 | „Automatisch scharf“ und „Anruf quittieren“ existieren immer. | Nur wenn eingerichtet (oder standardmäßig deaktiviert). |
| U13 | EN „Garage automatic“, DE „Privatsphäre an nach Unscharf“, „Push mit Bild, wenn nicht unscharf“. | „Garage automation“, „Privatsphäre-Modus nach dem Unscharfschalten wieder an nach“, „Push mit Bild, solange scharf“. |
| U14 | Push-Text „Folgende **Fenster** sind offen und wurden ignoriert“ – gilt auch für andere Sensortypen. | „Folgende Sensoren sind offen und werden ignoriert“. |
| U15 | DE `push_prewarn`: „…wenn Kinder alleine zuhause nicht aktiviert wird.“ (grammatisch holprig). | „…automatisch scharf, sofern ‚Kinder alleine zuhause‘ nicht eingeschaltet wird.“ |
| U16 | Icons vorhanden und sinnvoll; Presence-Sensoren nutzen die Geräteklasse. | Kein Handlungsbedarf. |

### 4.3 Übersetzungen

`strings.json`, `translations/en.json` (identisch) und `translations/de.json` sind schlüsselgleich (geprüft). Es fehlen inhaltlich nur die Beschreibungen aus U1/U2 und Fehlertexte für die neuen Prüfungen (U4/U5/U9). `labels.js` (Panel) muss aus denselben Quellen erzeugt werden (F33).

---

## 5. Dokumentation und Tests

### 5.1 README – was fehlt

* **Installation manuell** (Ordner `custom_components/alarm_assistant` kopieren, Neustart).
* **Voraussetzungen je Funktion:** Alexa Devices (Alarmton), Supervisor + ha-sip (Anruf), Companion App (WLAN-Sensoren, Android für TTS-Stream), Frigate (optional).
* **Alle Optionen** mit Standardwert und Wirkung als Tabelle (heute nur Fließtext).
* **Beispiele:** typische Einrichtung „Wohnung mit Tür, 3 Fenstern, 1 Bewegungsmelder“; Knopf-/NFC-Beispiel; Dashboard-Karte.
* **Fehlerbehebung:** „Scharfschalten nicht möglich“, „Kein Alarmton“, „Anruf kommt nicht“, „Automatisch scharf greift nicht“ (Checkliste: Modus, Heimnetz, Ruhezeit, Kinder-Schalter).
* **Debug-Logging aktivieren:**
  ```yaml
  logger:
    logs:
      custom_components.alarm_assistant: debug
  ```
  bzw. über „Debug-Protokollierung aktivieren“ in der Integrationsansicht; Diagnose herunterladen (nach F03 geschwärzt).
* **Entfernen** der Integration (was bleibt: nichts nach F18).
* Version im README (F28) streichen; Changelog/Releases verlinken.
* `docs/migration.md`: englischer Teil verweist auf „the table above“, die nur im deutschen Teil steht.

### 5.2 Tests – kritische Lücken

Vorhanden: 68 Tests, gute Abdeckung der Logik und vieler Engine-Szenarien. Ungetestet sind vor allem Fehler- und Randfälle:

| Bereich | Fehlender Test |
|---|---|
| Engine | Unscharf während Anrufkette/Sirene (F01); Schloss kommt aus `unavailable` als `unlocked` (F02); zweiter Alarm in der Sperrzeit bekommt Push (F10); Sensor wird im scharfen Zustand `unavailable` (F11); Ausgangsverzögerung > 0 mit offener Tür und Ablauf; `disarm_after_trigger=True`; Neustart im Zustand `arming`/`pending`; Nacht-Aus über Sommerzeitwechsel; Kinder-Reset nach Entriegeln und nachts. |
| Diagnose | Schwärzung sensibler Felder (F03). |
| Code | Code mit falschem Format; Code zum Scharfschalten (`code_arm_required`); neues Hash-Format und Migration (F04). |
| Config Flow | Abbruch bei zweiter Einrichtung (`single_instance_allowed`); Einrichtung ohne Code. |
| Options Flow | Jede Menüseite mindestens einmal (heute: alarm, reactions, lock, night_door); Fehlerfälle der neuen Abhängigkeitsprüfungen (U4); Code entfernen + neuen setzen gleichzeitig. |
| Subentries | Person/Garage-Reconfigure mit leerem Namen; doppelte Sensor-Entität (F13); Garage ohne WLAN-Sensoren (F16). |
| WebSocket | Ungültige Zahlen/Bereiche (F08); ungültige Subentry-Daten dürfen den Start nicht brechen (F07); Nicht-Admin wird abgewiesen; Befehle bei nicht geladenem Eintrag (F19); `delete_subentry` mit unbekannter ID. |
| Lebenszyklus | Entladen beendet laufende Tasks; `async_remove_entry` löscht Store und Issue (F18). |
| CI | `ruff format --check`; Prüfung, dass `labels.js` aktuell ist (F33); Test gegen die in `hacs.json` genannte Mindestversion. |

---

## 6. Priorisierte Reihenfolge der Behebung

Jeder Schritt = ein eigener kleiner Commit mit Test, `ruff check`/`ruff format` und `pytest` grün, Übersetzungen DE/EN und README nachgezogen, Version in `manifest.json` erhöht.

| Schritt | Inhalt | Funde | Version |
|---|---|---|---|
| 1 | Unscharf beendet Anrufkette, Sirene, Durchsagen; Lautstärke zurück | F01 | 0.4.6 |
| 2 | Schloss: Übergänge aus „nicht verfügbar“ ignorieren, `jammed` behandeln | F02, F12 | 0.4.6 |
| 3 | Diagnose schwärzen | F03 | 0.4.6 |
| 4 | Code: gesalzener PBKDF2-Hash mit Migration, `compare_digest`, Formatprüfung, Fehlversuche melden | F04, F05, F06, F36 | 0.5.0 |
| 5 | Gemeinsame Validierungsschemata für Options Flow, Subentries und WebSocket; defensives `_build()`; doppelte Sensoren ablehnen | F07, F08, F13, F14, U9, U10 | 0.5.0 |
| 6 | Push nicht mehr durch Anruf-Sperrzeit unterdrücken (nach Rückfrage, da evtl. gewollt) | F10 | 0.5.0 |
| 7 | Sensor-Ausfall im scharfen Zustand melden | F11 | 0.5.0 |
| 8 | Allgemeingültigkeit: Anrufsprache, Alarmton über Sirenen/Lautsprecher, TTS-Stream-Option, Supervisor-Prüfung, Garage-Prüfung, Standard Anwesenheitsmodus, unbekanntes Handy | F09, F15, F16, F21, F22, F23, Abschnitt 3 | 0.6.0 |
| 9 | UI: Beschreibungen für alle Felder, Selektoren statt Freitext, Abhängigkeitsprüfungen, Menüreihenfolge, Einheiten, Texte | U1-U8, U13-U15 | 0.6.0 |
| 10 | Entitäten: `entity_category`, nur konfigurierte Entitäten | F25, F26, U11, U12 | 0.6.0 |
| 11 | Einrichtungsschritt „Sensoren übernehmen“ (Vorschläge nach `device_class`) | Abschnitt 3 Discovery | 0.6.0 |
| 12 | Aufräumen: Tasks über Entry, Issue beim Entfernen löschen, `_entry()` nur geladen, nur abweichende Optionen speichern | F17, F18, F19, F20 | 0.6.x |
| 13 | Codequalität/Performance: Formatierung, toter Text, Duplikate, `opts`-Cache, weniger Updates, Panel-Datalists, `labels.js`-Generator und Cache, Code-Dialog | F29-F35 | 0.6.x |
| 14 | README, Migration, Releases/Tags, `quality_scale.yaml`, CI-Erweiterungen | F27, F28, Abschnitt 5 | 0.6.x |

**Offene Fragen vor der Umsetzung:**
1. F10: Soll ein zweiter Alarm innerhalb der Sperrzeit wirklich ohne Push bleiben? (Vorschlag: Push immer, nur Anruf sperren.)
2. F37: Soll „Entriegeln schaltet unscharf“ für neue Installationen standardmäßig aus sein? Bestehende Installationen behalten ihren Wert.
3. F15: Soll ein nicht verfügbares Handy künftig standardmäßig als „anwesend“ zählen?
4. Schritt 4 ändert das Speicherformat des Codes; bestehende Codes werden beim nächsten richtigen Unscharfschalten migriert. Einverstanden?

---

## 7. Umsetzungsstand (nach Freigabe)

Entscheidungen: (1) Push bei jedem Alarm, Sperrzeit nur für Anrufe; (2) „Entriegeln schaltet unscharf“ bleibt standardmäßig an (F37 entfällt); (3) unbekanntes Handy zählt standardmäßig als zuhause, einstellbar; (4) gesalzener Hash mit Migration.

| Schritt | Funde | Version | Stand |
|---|---|---|---|
| 1 | F01 | 0.4.6 | erledigt |
| 2 | F02, F12 | 0.4.6 | erledigt |
| 3 | F03 | 0.4.6 | erledigt |
| 4 | F04, F05, F06, F36, U5, F33 (Generator) | 0.5.0 | erledigt |
| 5 | F07, F08, F13, U9, U10 | 0.5.0 | erledigt; F14 nur als Hinweis im Feld (Minimum bewusst nicht erhöht, damit gespeicherte Werte gültig bleiben) |
| 6 | F10 | 0.5.0 | erledigt |
| 7 | F11 | 0.5.0 | erledigt |
| 8 | F09, F15, F16, F21, F22, F23 | 0.6.0 | erledigt; Standard-Anwesenheitsmodus bleibt „WLAN“, da die Unterpunkte Person nur in diesem Modus wirken |
| 9 | U1–U4, U6 (Beschreibungen), U7, U8, U13–U15 | 0.6.0 | erledigt; Alexa-Soundliste und Kamera-Presets bleiben Freitext (keine verlässliche Liste verfügbar) |
| 10 | F25, F26, U11, U12 | 0.6.0 | erledigt, inkl. Entfernen verwaister Entitäten |
| 11 | Sensoren bei der Einrichtung übernehmen | 0.6.0 | erledigt |
| 12 | F17–F20 | 0.6.1 | erledigt |
| 13 | F29, F31, F32, F34, F35 | 0.6.1 | erledigt; F30 ohne Änderung (Datalists werden nur beim vollständigen Neuzeichnen gebaut, nicht bei jedem Zustandswechsel) |
| 14 | F28, README, Migration, CI | 0.6.1 | erledigt; Releases/Tags und `quality_scale.yaml` nicht angelegt (Tags/Releases sind eine Aktion des Repository-Inhabers, eine Quality-Scale-Selbsteinstufung ohne Review wäre nicht belastbar) |

Tests: 93 (vorher 68), `ruff check`, `ruff format --check` und `build_labels.py --check` sauber.
