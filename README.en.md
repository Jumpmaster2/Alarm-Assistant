# Alarm Assistant

[Deutsche Version](README.md)

Custom integration for Home Assistant: an alarm panel with everything that otherwise lives in many automations, scripts and helpers. Arming and disarming (also automatically when everybody is away), entry and exit delay, ignoring open windows, announcements and alarm sound on Alexa devices, lights and covers on alarm, phone call with acknowledgement through the ha-sip add-on, door lock, camera control, garage cameras, a night door alarm and a window open hint at the front door. Everything is set up in the UI, no own automations are needed.

> Status: version 0.4.0.

## How it works

The integration is event driven: it only reacts to state changes of the configured entities, scanned NFC tags and calculated points in time (end of entry or exit delay, trigger time, automatic arming, daily resets). Every action is written to the logbook with its reason.

### Alarm panel

* Mode **away** with exit delay (0 = armed immediately), entry delay and trigger time. Afterwards armed again or, if set, disarmed.
* Optional code (for disarming, optionally also for arming). Only a hash is stored.
* **Sensors** are added one by one (sub item "Sensor"): door (delayed), window (immediate), motion (delayed, may be active at arming) or other. Every property can be changed per sensor.
* **Open windows** are ignored from arming until disarming, a notification lists them. An open door prevents arming (with a notification), except during an exit delay.
* A sensor that becomes unavailable does not trigger. If it was closed before and comes back open, it triggers.
* **Conditional contacts:** a sensor can count only while another entity is unavailable, e.g. a balcony door that is open for the hose of a portable air conditioner. If it is open at arming and does not count, a cover can move to a position.
* After a restart an armed panel stays armed. A running alarm is not repeated.

### Motion filter

* Motion does not count while the vacuum cleans or returns, and for a configurable time after docking.
* A **fault sensor** (e.g. the vacuum bridge fails) suppresses motion while it is on or unavailable. Technical notifications report the fault and every suppressed motion while armed.

### On alarm

* Announcement to notify entities (e.g. Alexa announcement everywhere) with an own text, also when the entry delay starts.
* Alarm sound: volume up, sound on Alexa devices, spoken text, volume back after a while.
* Turn on lights and switches, close covers.
* **Phone call** through the ha-sip add-on: numbers in order. Every number except the last can acknowledge with key 1 (the button "Acknowledge call" is pressed), then nobody else is called. The first call starts before the push messages. No new call within the cool down.
* Push to the phones and additional services (e.g. Pushover) with the **cause**: the sensors that tripped and, if a camera sees a person right now, that one too.

### Automatic arming

* Presence by **persons** (sub item "Person"): every person has the Wi-Fi sensor of their phone. While the phone is connected to a home network the person is at home; each person gets a presence sensor. Alternatively Home Assistant persons (`person.*`).
* When nobody is at home (for a minimum time), there was no motion for a while and "children alone at home" is off, a warning is sent. If everything is still true afterwards and there was no motion, the panel is armed. After disarming it waits before checking again.
* Can be switched off with the switch **Automatic arming**.

### Door lock and children

* Unlocking or opening the lock disarms.
* Arming locks the door when it is closed and no children are alone at home.
* **Children alone at home** (switch) prevents automatic arming and locking and controls the camera. It is reset a configurable time after unlocking and at night.

### Camera (sub item "Camera")

* Armed or children alone at home: privacy mode off, default preset.
* Disarmed: privacy mode on again after a delay (not with children or live view).
* Motion while armed: preset of that motion sensor.
* Detection and recording switches (e.g. Frigate): off for live view and children, only detection off while the vacuum drives.
* Person detected while not disarmed: push with image.
* Switch **Camera live view**.

### Garage (sub item "Garage")

* A second alarm panel (e.g. Blink) is disarmed while a phone is connected to the garage network and armed again some time after leaving.
* Motion while armed: push and spoken warning on the phones (companion app).
* Switch **Garage automatic**.

### Night door alarm

* Independent of the alarm panel. When on (switch or NFC tag), opening the door sounds a local alarm: lights on, alarm sound, spoken text. No call, no push.
* The same tag switches it off (with an announcement). Automatic switch off at a time on chosen weekdays.

### Window open hint

* When the front door opens and a window is open, a light is on for a configurable time.

## Installation with HACS

1. Open HACS, menu "Custom repositories".
2. Add `https://github.com/Jumpmaster2/Alarm-Assistant` as type "Integration".
3. Install "Alarm Assistant" and restart Home Assistant.
4. Add the integration under Settings > Devices & services.

## Configuration

After the setup the sidebar has the page **Alarm Assistant** (administrators only, similar to Alarmo):

* **Overview:** state with arm/disarm, switches, persons (home/away), open contacts, notes, last alarm, test message and a summary of the settings.
* **Test alarm:** arm as a test and choose what should happen: every reaction can be switched on or off (e.g. no announcement, no push to one phone, no lights, no covers, only the first call number). When a sensor trips or the trigger is simulated, everything runs like a real alarm, but only with the chosen reactions. Push messages start with [TEST], announcements and calls with "Attention, this is only a test". Disarming ends the test, a restart does not.
* **Sensors:** all contacts and motion sensors as a table with type, behaviour and current state; click to edit.
* **Alarm, On alarm, Messages & call, Presence, Door & extras, Camera & garage:** all settings by topic in cards, each card is saved on its own.

The settings can still be changed through the config flow as well:

* **Setup:** notifications, alarm times and code.
* **Options** (menu): notifications, alarm times and code, motion filter, reactions on alarm, phone call, automatic arming, door lock, night door alarm, children and hints.
* **Sub items:** sensor, person, camera, garage (as many as needed).

Configured entities or services that do not exist are reported under Repairs after the start.

## Entities

| Entity | Meaning |
|---|---|
| Alarm panel | armed away/disarmed, attributes: open and ignored sensors, cause |
| Switches automatic arming, children alone at home | kept over restarts |
| Switches night door alarm, camera live view, garage automatic | only when set up |
| Binary sensors motion, contacts open, motion suppressed, warning | |
| Binary sensor "<name> at home" | per person, from the phone's Wi-Fi |
| Sensors cause, last alarm | |
| Buttons acknowledge call, test message | the test message only sends a push with the open sensors |

The panel is used with the standard actions `alarm_control_panel.alarm_arm_away` and `alarm_control_panel.alarm_disarm`, e.g. from a button blueprint.

## Moving over

See [docs/migration.md](docs/migration.md).

## Development

```bash
pip install -r requirements_test.txt ruff
ruff check custom_components tests scripts
pytest -q
```

The tests with Home Assistant run on Linux. Before publishing, `scripts/check_privacy.py` checks with a local pattern list that no private data ends up in the repository.

## License

MIT
