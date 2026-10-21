"""Localised texts for notifications, announcements, calls and the logbook."""

from __future__ import annotations

from typing import Any

_TEXTS: dict[str, dict[str, str]] = {
    # announcements (defaults, can be replaced in the options)
    "announce_triggered": {
        "de": "Der Alarm wurde ausgelöst!",
        "en": "The alarm has been triggered!",
    },
    "announce_pending": {
        "de": "Der Alarm wird in Kürze ausgelöst, bitte entschärfen Sie ihn schnell!",
        "en": "The alarm will go off shortly, please disarm it now!",
    },
    "announce_night_door": {"de": "Alarm Türe geöffnet", "en": "Alarm, door opened"},
    "announce_night_off": {"de": "Alarm ist deaktiviert", "en": "Alarm is disarmed"},
    # notifications
    "title_alarm": {"de": "ALARM", "en": "ALARM"},
    "title_pending": {"de": "Auslösung", "en": "Alarm pending"},
    "push_triggered": {
        "de": "Der Alarm wurde ausgelöst! Ursache: {cause}.",
        "en": "The alarm has been triggered! Cause: {cause}.",
    },
    "push_call_started": {"de": " Telefonanruf wird gestartet.", "en": " Calling now."},
    "title_arm_failed": {"de": "FEHLER", "en": "ERROR"},
    "push_arm_failed": {
        "de": "Der Alarm konnte im Moment nicht scharfgeschaltet werden, aufgrund von: {sensors}.",
        "en": "The alarm could not be armed because of: {sensors}.",
    },
    "title_armed": {"de": "Alarmanlage aktiviert", "en": "Alarm armed"},
    "push_bypassed": {
        "de": "Alarm aktiviert, folgende Sensoren sind offen und werden bis zum Unscharfschalten "
        "ignoriert: {sensors}.",
        "en": "Alarm armed, these open sensors are ignored until disarming: {sensors}.",
    },
    "title_lock_failed": {"de": "Tür nicht abgeschlossen", "en": "Door not locked"},
    "push_lock_retry": {
        "de": "Das Schloss hat sich nicht verriegelt. Die Alarmanlage bleibt scharf, "
        "Abschließen wird gleich noch einmal versucht.",
        "en": "The lock did not engage. The alarm stays armed, locking is retried shortly.",
    },
    "push_lock_failed": {
        "de": "Das Schloss hat sich wieder nicht verriegelt. Die Alarmanlage bleibt scharf, "
        "die Tür ist aber nicht abgeschlossen.",
        "en": "The lock did not engage again. The alarm stays armed, but the door is not locked.",
    },
    "title_prewarn": {"de": "Alarmanlage aktiviert bald", "en": "Alarm will arm soon"},
    "push_prewarn": {
        "de": "Niemand ist zuhause. Die Alarmanlage wird in {minutes} Minuten automatisch "
        'aktiviert, sofern "Kinder alleine zuhause" nicht eingeschaltet wird.',
        "en": "Nobody is at home. The alarm will arm automatically in {minutes} minutes "
        'unless "children alone at home" is switched on.',
    },
    "title_fault": {"de": "Bewegungsmelder unterdrückt", "en": "Motion suppressed"},
    "push_fault": {
        "de": "{sensor} meldet einen Fehler. Bewegungsmelder zählen nicht, solange er aktiv ist.",
        "en": "{sensor} reports a fault. Motion sensors do not count while it is active.",
    },
    "title_suppressed": {"de": "Bewegung unterdrückt", "en": "Motion suppressed"},
    "push_suppressed": {
        "de": "{sensor} hat Bewegung gemeldet, sie zählt wegen {fault} nicht. Alarm: {state}.",
        "en": "{sensor} reported motion, it does not count because of {fault}. Alarm: {state}.",
    },
    "title_person": {"de": "Person erkannt", "en": "Person detected"},
    "push_person": {"de": "{camera}: Person erkannt", "en": "{camera}: person detected"},
    "title_night_on": {"de": "Türalarm", "en": "Door alarm"},
    "push_night_on": {"de": "Türalarm ist aktiviert", "en": "Door alarm is on"},
    "title_garage": {"de": "Garage", "en": "Garage"},
    "push_garage": {
        "de": "{camera} hat Bewegung erkannt.",
        "en": "{camera} detected motion.",
    },
    "tts_garage": {
        "de": "Achtung. Bewegung in der Garage erkannt.",
        "en": "Attention. Motion detected in the garage.",
    },
    "title_unavailable": {"de": "Sensor nicht verfügbar", "en": "Sensor unavailable"},
    "push_unavailable": {
        "de": "{sensor} ist nicht verfügbar, während die Alarmanlage scharf ist. "
        "Bitte Batterie und Verbindung prüfen.",
        "en": "{sensor} is unavailable while the alarm is armed. "
        "Please check its battery and connection.",
    },
    "title_wrong_code": {"de": "Falscher Code", "en": "Wrong code"},
    "push_wrong_code": {
        "de": "An der Alarmzentrale wurde {count}-mal hintereinander ein falscher Code eingegeben.",
        "en": "A wrong code was entered {count} times in a row at the alarm panel.",
    },
    "title_test": {"de": "TEST Alarmanlage", "en": "TEST alarm"},
    "push_test": {
        "de": "Testmeldung. Offene Sensoren: {sensors}.",
        "en": "Test message. Open sensors: {sensors}.",
    },
    # test alarm
    "test_prefix": {"de": "[TEST] ", "en": "[TEST] "},
    "test_spoken": {
        "de": "Achtung, dies ist nur ein Test. ",
        "en": "Attention, this is only a test. ",
    },
    "test_cause": {"de": "Testauslösung", "en": "Test trigger"},
    # call
    "call_message": {
        "de": "Achtung die Alarmanlage hat ausgelöst. Einbruchalarm. Ursache: {cause}.",
        "en": "Attention, the alarm has been triggered. Burglary alarm. Cause: {cause}.",
    },
    "call_ack_message": {
        "de": "Achtung Alarmanlage ausgelöst. Ursache: {cause}. Zum Quittieren jetzt bitte "
        "Taste 1 drücken. Ohne Quittierung wird die nächste Nummer angerufen.",
        "en": "Attention, alarm triggered. Cause: {cause}. Press 1 to acknowledge. "
        "Without acknowledgement the next number is called.",
    },
    "call_ack_reply": {
        "de": "Alarm wurde quittiert. Es wird kein weiterer Anruf gestartet.",
        "en": "Alarm acknowledged. No further call is made.",
    },
    # cause
    "unknown": {"de": "unbekannt", "en": "unknown"},
    # logbook
    "log_armed": {"de": "Scharf geschaltet", "en": "Armed"},
    "log_armed_bypass": {
        "de": "Scharf geschaltet, ignoriert: {sensors}",
        "en": "Armed, ignored: {sensors}",
    },
    "log_arming": {"de": "Ausgangsverzögerung läuft", "en": "Exit delay running"},
    "log_arm_failed": {
        "de": "Scharfschalten nicht möglich: {sensors}",
        "en": "Arming not possible: {sensors}",
    },
    "log_disarmed": {"de": "Unscharf geschaltet", "en": "Disarmed"},
    "log_disarmed_lock": {
        "de": "Unscharf geschaltet durch Entriegeln",
        "en": "Disarmed by unlocking",
    },
    "log_pending": {"de": "Eingangsverzögerung: {sensor}", "en": "Entry delay: {sensor}"},
    "log_triggered": {"de": "ALARM: {cause}", "en": "ALARM: {cause}"},
    "log_trigger_end": {"de": "Auslösezeit vorbei", "en": "Trigger time over"},
    "log_prewarn": {
        "de": "Niemand zuhause: Vorwarnung, scharf in {minutes} min",
        "en": "Nobody home: warning, arming in {minutes} min",
    },
    "log_auto_armed": {"de": "Automatisch scharf geschaltet", "en": "Armed automatically"},
    "log_locked": {"de": "Tür abgeschlossen", "en": "Door locked"},
    "log_lock_failed": {
        "de": "Abschließen fehlgeschlagen, bleibt scharf",
        "en": "Locking failed, stays armed",
    },
    "log_call": {"de": "Anruf an {target}", "en": "Calling {target}"},
    "log_call_ack": {"de": "Anruf quittiert", "en": "Call acknowledged"},
    "log_kids_reset": {
        "de": "Kinder alleine zuhause zurückgesetzt",
        "en": "Children alone at home reset",
    },
    "log_night_on": {"de": "Türalarm an", "en": "Door alarm on"},
    "log_night_off": {"de": "Türalarm aus", "en": "Door alarm off"},
    "log_night_alarm": {"de": "Türalarm: Tür geöffnet", "en": "Door alarm: door opened"},
    "log_hint": {
        "de": "Tür geöffnet, Fenster offen: {sensors}",
        "en": "Door opened, windows open: {sensors}",
    },
    "log_garage_armed": {"de": "Garage scharf geschaltet", "en": "Garage armed"},
    "log_garage_disarmed": {"de": "Garage unscharf geschaltet", "en": "Garage disarmed"},
    "log_cover": {"de": "{name}: Rollo auf {position} %", "en": "{name}: cover to {position} %"},
    "log_unavailable": {
        "de": "Nicht verfügbar, während scharf: {sensor}",
        "en": "Unavailable while armed: {sensor}",
    },
    "log_wrong_code": {
        "de": "{count}-mal falscher Code eingegeben",
        "en": "Wrong code entered {count} times",
    },
    "log_test": {"de": "Testmeldung gesendet", "en": "Test message sent"},
}


def resolve_language(option: str | None, ha_language: str | None) -> str:
    """'de' or 'en' from the option ('auto' follows Home Assistant)."""
    lang = option if option in ("de", "en") else (ha_language or "en")
    return "de" if lang.lower().startswith("de") else "en"


def text(language: str, key: str, **kwargs: Any) -> str:
    """Return the localised text."""
    lang = "de" if language.lower().startswith("de") else "en"
    entry = _TEXTS.get(key)
    if entry is None:
        return key
    try:
        return entry[lang].format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return entry[lang]
