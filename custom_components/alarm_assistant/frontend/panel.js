// Alarm Assistant sidebar panel: overview and all settings on one page.
// Plain web component without build step; uses only the hass object and the
// WebSocket commands of the integration.

import { LABELS } from "./labels.js";

const UI = {
  de: {
    title: "Alarm Assistant",
    tabs: {
      overview: "Übersicht",
      test: "Testalarm",
      sensors: "Sensoren",
      alarm: "Alarm",
      reactions: "Bei Alarm",
      notify: "Meldungen & Anruf",
      presence: "Anwesenheit",
      door: "Tür & Extras",
      camera: "Kamera & Garage",
    },
    cards: {
      times: ["Alarmzeiten", "Verzögerungen und wie lange der Alarm dauert."],
      code: ["Code", "Optional. Wird zum Unscharfschalten verlangt."],
      motion: ["Bewegungsfilter", "Wann Bewegungsmelder nicht zählen."],
      armed: ["Solange scharf", "Was eingeschaltet ist, solange die Anlage scharf ist."],
      announce: ["Durchsage", "Text auf den Lautsprechern bei Alarm und bei Beginn der Eingangsverzögerung."],
      siren: ["Alarmton und Sprache", "Lautstärke hoch, Alarmton, gesprochener Text, danach Lautstärke zurück."],
      actions: ["Licht und Rollos", "Wird bei Alarm eingeschaltet bzw. geschlossen."],
      push: ["Push-Meldungen", "Wer welche Meldungen bekommt."],
      call: ["Telefonanruf", "Über das ha-sip-Add-on. Jede Nummer außer der letzten kann mit Taste 1 quittieren."],
      persons: ["Personen", "Zuhause, solange das Handy mit einem Heim-WLAN verbunden ist."],
      autoarm: ["Automatisch scharf", "Scharf, wenn niemand zuhause ist und keine Bewegung war. Vorher kommt eine Warnung."],
      lock: ["Türschloss", "Entriegeln schaltet unscharf, beim Scharfschalten wird abgeschlossen."],
      kids: ["Kinder alleine zuhause", "Verhindert automatisches Scharfschalten und Abschließen."],
      night: ["Nacht-Türalarm", "Eigener Schalter: beim Öffnen der Tür lokaler Alarm (kein Anruf, kein Push)."],
      nightoff: ["Nacht-Türalarm ausschalten", "Automatisch zu einer Uhrzeit und Ansage beim Ausschalten per Tag."],
      hint: ["Fenster-offen-Hinweis", "Haustür geht auf und ein Fenster ist offen: Licht leuchtet kurz."],
      cameras: ["Kameras", "Privatsphäre, Preset und Erkennung je nach Alarm, Kindern und Saugroboter."],
      garages: ["Garagen", "Zweite Alarmzentrale, die über das Garagen-WLAN geschaltet wird."],
      sensors: ["Sensoren", "Alle Kontakte und Bewegungsmelder der Alarmanlage."],
    },
    save: "Speichern",
    saved: "Gespeichert",
    cancel: "Abbrechen",
    delete: "Löschen",
    back: "Zurück",
    add: "Hinzufügen",
    edit: "Bearbeiten",
    confirmDelete: "Wirklich löschen?",
    notFound: "nicht gefunden",
    none: "–",
    advanced: "Erweitert",
    newCode: "Neuer Code",
    newCodeHelp: "4 bis 10 Ziffern. Leer lassen, um den bisherigen Code zu behalten.",
    codeConfirm: "Code wiederholen",
    removeCode: "Code entfernen",
    codeSet: "Code ist gesetzt",
    codeNotSet: "Kein Code",
    codeArm: "Code auch zum Scharfschalten",
    enterCode: "Code eingeben",
    arm: "Scharf (abwesend)",
    disarm: "Unscharf",
    test: "Testmeldung senden",
    testSent: "Testmeldung gesendet",
    states: {
      disarmed: "Unscharf",
      arming: "Wird scharf geschaltet",
      armed_away: "Scharf (abwesend)",
      pending: "Eingangsverzögerung",
      triggered: "ALARM",
      unavailable: "Nicht verfügbar",
    },
    open: "offen",
    closed: "zu",
    motionOn: "Bewegung",
    motionOff: "ruhig",
    home: "zuhause",
    away: "weg",
    openContacts: "Offene Kontakte",
    ignored: "Ignoriert bis zum Unscharfschalten",
    noneOpen: "Alles zu",
    lastAlarm: "Letzter Alarm",
    noAlarm: "Noch kein Alarm",
    warnings: "Hinweise",
    suppressed: "Bewegung wird gerade nicht gewertet (Saugroboter oder Fehler-Sensor)",
    prewarn: "Vorwarnung läuft, scharf um",
    missing: "Eingestellte Entitäten fehlen",
    noWarnings: "Keine Hinweise",
    switches: "Schalter",
    glance: "Auf einen Blick",
    glanceRows: {
      sensors: "Sensoren",
      persons: "Personen",
      push: "Push-Ziele",
      call: "Anrufziele",
      alarmon: "Bei Alarm",
      cameras: "Kameras",
      garages: "Garagen",
    },
    alarmOn: (a, l, c) => `${a} Durchsage-Ziele, ${l} Lichter/Schalter, ${c} Rollos`,
    behaviour: {
      use_entry_delay: "verzögert",
      immediate: "sofort",
      auto_bypass: "offen = ignorieren",
      allow_open: "darf aktiv sein",
      condition: "bedingt",
    },
    types: { door: "Tür", window: "Fenster", motion: "Bewegung", other: "Sonstiges" },
    presenceModes: { wifi: "WLAN der Handys", persons: "Home-Assistant-Personen" },
    languages: { auto: "Auto", de: "Deutsch", en: "English" },
    weekdays: { mon: "Mo", tue: "Di", wed: "Mi", thu: "Do", fri: "Fr", sat: "Sa", sun: "So" },
    columns: { name: "Name", type: "Typ", state: "Zustand", behaviour: "Verhalten" },
    noItems: "Noch nichts angelegt.",
    newItem: { sensor: "Neuer Sensor", person: "Neue Person", camera: "Neue Kamera", garage: "Neue Garage" },
    errors: {
      name_required: "Bitte einen Namen eingeben.",
      entity_required: "Bitte eine Entität wählen.",
      type_required: "Bitte einen Typ wählen.",
      code_invalid: "Der Code muss aus 4 bis 10 Ziffern bestehen.",
      code_mismatch: "Die beiden Codes stimmen nicht überein.",
    },
    fieldErrors: {
      out_of_range: "Wert außerhalb des erlaubten Bereichs",
      not_a_number: "bitte eine Zahl eingeben",
      not_a_list: "ungültige Liste",
      not_bool: "ungültiger Schalterwert",
      invalid_entity: "keine gültige Entitäts-ID (Format domain.name)",
      invalid_choice: "ungültige Auswahl",
      invalid_time: "ungültige Uhrzeit (HH:MM)",
      unknown_option: "unbekannte Einstellung",
      already_configured: "diese Entität ist bereits als Sensor angelegt",
    },
    loadError: "Konfiguration konnte nicht geladen werden",
    up: "nach oben",
    down: "nach unten",
    addValue: "Wert eingeben und Enter",
    testTitle: "Testalarm",
    testDesc:
      "Schaltet die Anlage testweise scharf. Löst danach ein Sensor aus (oder du simulierst die Auslösung), läuft alles wie bei einem echten Alarm, aber nur mit den hier angehakten Reaktionen. Push-Meldungen beginnen mit [TEST], Durchsagen und Anrufe mit „Achtung, dies ist nur ein Test“. Unscharf schalten beendet den Test.",
    testWhat: "Was soll beim Test passieren?",
    testArm: "Testweise scharf schalten",
    testTrigger: "Auslösung simulieren",
    testRunning: "Testalarm läuft",
    testNotDisarmed: "Die Anlage ist scharf (kein Test). Für einen Test erst unscharf schalten.",
    testOff: "Aus beim Test",
    allOn: "Alles an",
    allOff: "Alles aus",
    testBadge: "TEST",
    testGroups: {
      push: "Push-Meldungen",
      call: "Telefonanruf",
      announce: "Durchsage",
      volume: "Lautstärke hoch",
      sound: "Alarmton",
      speak: "Gesprochener Text",
      lights: "Licht und Schalter",
      covers: "Rollos schließen",
      lock: "Tür abschließen",
      arm_cover: "Rollo bei offenem bedingtem Kontakt",
      camera: "Kamera (Privatsphäre, Preset, Personenbild)",
      armed_on: "An, solange scharf",
    },
    errorsTest: { arm_failed: "Scharfschalten nicht möglich, offen:", not_disarmed: "Die Anlage ist nicht unscharf." },
  },
  en: {
    title: "Alarm Assistant",
    tabs: {
      overview: "Overview",
      test: "Test alarm",
      sensors: "Sensors",
      alarm: "Alarm",
      reactions: "On alarm",
      notify: "Messages & call",
      presence: "Presence",
      door: "Door & extras",
      camera: "Camera & garage",
    },
    cards: {
      times: ["Alarm times", "Delays and how long the alarm lasts."],
      code: ["Code", "Optional. Needed for disarming."],
      motion: ["Motion filter", "When motion sensors do not count."],
      armed: ["While armed", "What is on while the panel is armed."],
      announce: ["Announcement", "Text on the speakers on alarm and when the entry delay starts."],
      siren: ["Alarm sound and speech", "Volume up, alarm sound, spoken text, then volume back."],
      actions: ["Lights and covers", "Turned on or closed on alarm."],
      push: ["Push messages", "Who gets which messages."],
      call: ["Phone call", "Through the ha-sip add-on. Every number except the last can acknowledge with key 1."],
      persons: ["Persons", "At home while the phone is connected to a home network."],
      autoarm: ["Automatic arming", "Armed when nobody is home and there was no motion. A warning comes first."],
      lock: ["Door lock", "Unlocking disarms, arming locks the door."],
      kids: ["Children alone at home", "Prevents automatic arming and locking."],
      night: ["Night door alarm", "Own switch: opening the door sounds locally (no call, no push)."],
      nightoff: ["Switching the night door alarm off", "Automatically at a time and announcement when switched off by tag."],
      hint: ["Window open hint", "Front door opens and a window is open: a light is on for a moment."],
      cameras: ["Cameras", "Privacy, preset and detection depending on alarm, children and vacuum."],
      garages: ["Garages", "Second alarm panel switched by the garage network."],
      sensors: ["Sensors", "All contacts and motion sensors of the alarm."],
    },
    save: "Save",
    saved: "Saved",
    cancel: "Cancel",
    delete: "Delete",
    back: "Back",
    add: "Add",
    edit: "Edit",
    confirmDelete: "Really delete?",
    notFound: "not found",
    none: "–",
    advanced: "Advanced",
    newCode: "New code",
    newCodeHelp: "4 to 10 digits. Leave empty to keep the current code.",
    codeConfirm: "Repeat code",
    removeCode: "Remove code",
    codeSet: "A code is set",
    codeNotSet: "No code",
    codeArm: "Code also for arming",
    enterCode: "Enter code",
    arm: "Arm (away)",
    disarm: "Disarm",
    test: "Send test message",
    testSent: "Test message sent",
    states: {
      disarmed: "Disarmed",
      arming: "Arming",
      armed_away: "Armed (away)",
      pending: "Entry delay",
      triggered: "ALARM",
      unavailable: "Unavailable",
    },
    open: "open",
    closed: "closed",
    motionOn: "motion",
    motionOff: "quiet",
    home: "home",
    away: "away",
    openContacts: "Open contacts",
    ignored: "Ignored until disarming",
    noneOpen: "All closed",
    lastAlarm: "Last alarm",
    noAlarm: "No alarm yet",
    warnings: "Notes",
    suppressed: "Motion does not count right now (vacuum or fault sensor)",
    prewarn: "Warning running, arming at",
    missing: "Configured entities are missing",
    noWarnings: "No notes",
    switches: "Switches",
    glance: "At a glance",
    glanceRows: {
      sensors: "Sensors",
      persons: "Persons",
      push: "Push targets",
      call: "Call targets",
      alarmon: "On alarm",
      cameras: "Cameras",
      garages: "Garages",
    },
    alarmOn: (a, l, c) => `${a} announcement targets, ${l} lights/switches, ${c} covers`,
    behaviour: {
      use_entry_delay: "delayed",
      immediate: "immediate",
      auto_bypass: "open = ignore",
      allow_open: "may be active",
      condition: "conditional",
    },
    types: { door: "Door", window: "Window", motion: "Motion", other: "Other" },
    presenceModes: { wifi: "Wi-Fi of the phones", persons: "Home Assistant persons" },
    languages: { auto: "Auto", de: "Deutsch", en: "English" },
    weekdays: { mon: "Mo", tue: "Tu", wed: "We", thu: "Th", fri: "Fr", sat: "Sa", sun: "Su" },
    columns: { name: "Name", type: "Type", state: "State", behaviour: "Behaviour" },
    noItems: "Nothing added yet.",
    newItem: { sensor: "New sensor", person: "New person", camera: "New camera", garage: "New garage" },
    errors: {
      name_required: "Please enter a name.",
      entity_required: "Please choose an entity.",
      type_required: "Please choose a type.",
      code_invalid: "The code must have 4 to 10 digits.",
      code_mismatch: "The two codes do not match.",
    },
    fieldErrors: {
      out_of_range: "value outside the allowed range",
      not_a_number: "please enter a number",
      not_a_list: "invalid list",
      not_bool: "invalid switch value",
      invalid_entity: "not a valid entity id (format domain.name)",
      invalid_choice: "invalid choice",
      invalid_time: "invalid time (HH:MM)",
      unknown_option: "unknown setting",
      already_configured: "this entity is already set up as a sensor",
    },
    loadError: "Could not load the configuration",
    up: "up",
    down: "down",
    addValue: "Type a value and press Enter",
    testTitle: "Test alarm",
    testDesc:
      "Arms the panel as a test. When a sensor trips afterwards (or you simulate the trigger), everything runs like a real alarm, but only with the reactions ticked here. Push messages start with [TEST], announcements and calls with \"Attention, this is only a test\". Disarming ends the test.",
    testWhat: "What should happen in the test?",
    testArm: "Arm as a test",
    testTrigger: "Simulate trigger",
    testRunning: "Test alarm running",
    testNotDisarmed: "The panel is armed (no test). Disarm it first for a test.",
    testOff: "Off in the test",
    allOn: "All on",
    allOff: "All off",
    testBadge: "TEST",
    testGroups: {
      push: "Push messages",
      call: "Phone call",
      announce: "Announcement",
      volume: "Volume up",
      sound: "Alarm sound",
      speak: "Spoken text",
      lights: "Lights and switches",
      covers: "Close covers",
      lock: "Lock the door",
      arm_cover: "Cover at an open conditional contact",
      camera: "Camera (privacy, preset, person image)",
      armed_on: "On while armed",
    },
    errorsTest: { arm_failed: "Cannot arm, open:", not_disarmed: "The panel is not disarmed." },
  },
};

const TABS = [
  ["overview", "mdi:view-dashboard-outline"],
  ["test", "mdi:test-tube"],
  ["sensors", "mdi:leak"],
  ["alarm", "mdi:shield-lock-outline"],
  ["reactions", "mdi:alarm-light-outline"],
  ["notify", "mdi:cellphone-message"],
  ["presence", "mdi:account-group-outline"],
  ["door", "mdi:door-closed-lock"],
  ["camera", "mdi:cctv"],
];

const SENSOR_TYPES = ["door", "window", "motion", "other"];
const TYPE_ICONS = {
  door: "mdi:door",
  window: "mdi:window-closed-variant",
  motion: "mdi:motion-sensor",
  other: "mdi:checkbox-blank-circle-outline",
};
const TYPE_DEFAULTS = {
  door: { use_entry_delay: true, use_exit_delay: true, auto_bypass: false, allow_open: false },
  motion: { use_entry_delay: true, use_exit_delay: true, auto_bypass: false, allow_open: true },
  window: { use_entry_delay: false, use_exit_delay: false, auto_bypass: true, allow_open: false },
  other: { use_entry_delay: false, use_exit_delay: false, auto_bypass: false, allow_open: false },
};
const STATE_ICONS = {
  disarmed: ["mdi:shield-off-outline", "var(--success-color, #43a047)"],
  arming: ["mdi:shield-sync-outline", "var(--warning-color, #ffa600)"],
  armed_away: ["mdi:shield-lock", "var(--error-color, #db4437)"],
  pending: ["mdi:shield-alert-outline", "var(--warning-color, #ffa600)"],
  triggered: ["mdi:bell-ring", "var(--error-color, #db4437)"],
};
const WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];

// Settings cards per tab: [key, type, options]
const SETTINGS = {
  alarm: [
    {
      id: "times",
      icon: "mdi:timer-outline",
      fields: [
        ["entry_delay", "number", { unit: "s", min: 0, max: 600 }],
        ["exit_delay", "number", { unit: "s", min: 0, max: 600 }],
        ["trigger_time", "number", { unit: "s", min: 0, max: 7200 }],
        ["disarm_after_trigger", "bool"],
      ],
    },
    { id: "code", icon: "mdi:dialpad", special: "code" },
    {
      id: "motion",
      icon: "mdi:robot-vacuum",
      fields: [
        ["vacuum", "entity", { domains: ["vacuum"] }],
        ["vacuum_charging", "entity", { domains: ["binary_sensor"] }],
        ["dock_grace", "number", { unit: "s", min: 0, max: 1800 }],
        ["fault_sensor", "entity", { domains: ["binary_sensor"] }],
        ["notify_suppressed_motion", "bool"],
      ],
    },
    { id: "armed", icon: "mdi:toggle-switch-outline", fields: [["armed_on_entities", "entities", {}]] },
  ],
  reactions: [
    {
      id: "announce",
      icon: "mdi:bullhorn-outline",
      fields: [
        ["announce_entities", "entities", { domains: ["notify"] }],
        ["text_triggered", "textarea"],
        ["text_pending", "textarea"],
      ],
    },
    {
      id: "siren",
      icon: "mdi:volume-high",
      fields: [
        ["volume_players", "entities", { domains: ["media_player"] }],
        ["alarm_volume", "number", { min: 0, max: 1, step: 0.01 }],
        ["reset_volume", "number", { min: 0, max: 1, step: 0.01 }],
        ["reset_volume_after", "number", { unit: "s", min: 0, max: 600 }],
        ["sound_devices", "devices"],
        ["sound", "text"],
        ["speak_services", "services"],
      ],
    },
    {
      id: "actions",
      icon: "mdi:lightbulb-group-outline",
      fields: [
        ["turn_on_entities", "entities", {}],
        ["close_covers", "entities", { domains: ["cover"] }],
      ],
    },
  ],
  notify: [
    {
      id: "push",
      icon: "mdi:cellphone-message",
      fields: [
        ["notify_services", "services"],
        ["notify_alarm_services", "services"],
        ["notify_admin_services", "services"],
        ["language", "select", { choices: "languages" }],
      ],
    },
    {
      id: "call",
      icon: "mdi:phone-alert",
      fields: [
        ["call_addon", "text"],
        ["call_targets", "list", { ordered: true }],
        ["call_acknowledge", "bool"],
        ["call_wait", "number", { unit: "s", min: 0, max: 600 }],
        ["call_tts", "entity", { domains: ["tts"] }],
        ["call_language", "text"],
        ["call_cooldown", "number", { unit: "s", min: 0, max: 3600 }],
      ],
    },
  ],
  presence: [
    { id: "persons", icon: "mdi:account-group-outline", special: "sub", sub: "person" },
    {
      id: "autoarm",
      icon: "mdi:shield-home-outline",
      fields: [
        ["home_networks", "list", {}],
        ["presence_mode", "select", { choices: "presenceModes" }],
        ["wifi_sensors", "entities", { domains: ["sensor"] }],
        ["persons", "entities", { domains: ["person"] }],
        ["quiet_time", "number", { unit: "min", min: 0, max: 240 }],
        ["prewarn_time", "number", { unit: "min", min: 0, max: 60 }],
        ["retry_after_disarm", "number", { unit: "min", min: 0, max: 120 }],
        ["presence_stable", "number", { unit: "min", min: 0, max: 60 }],
      ],
    },
  ],
  door: [
    {
      id: "lock",
      icon: "mdi:lock-outline",
      fields: [
        ["lock", "entity", { domains: ["lock"] }],
        ["lock_door_sensor", "entity", { domains: ["binary_sensor"] }],
        ["disarm_on_unlock", "bool"],
        ["lock_on_arm", "bool"],
      ],
    },
    {
      id: "kids",
      icon: "mdi:human-child",
      fields: [
        ["kids_reset_after_unlock", "number", { unit: "min", min: 0, max: 240 }],
        ["kids_reset_time", "time"],
      ],
    },
    {
      id: "night",
      icon: "mdi:door-closed-lock",
      fields: [
        ["night_door_sensor", "entity", { domains: ["binary_sensor"] }],
        ["night_tag", "tag"],
        ["night_turn_on_entities", "entities", {}],
        ["night_volume_players", "entities", { domains: ["media_player"] }],
        ["night_sound_devices", "devices"],
        ["night_speak_services", "services"],
        ["night_text", "text"],
        ["night_reset_volume_after", "number", { unit: "s", min: 0, max: 600 }],
      ],
    },
    {
      id: "nightoff",
      icon: "mdi:clock-outline",
      fields: [
        ["night_off_time", "time"],
        ["night_off_days", "weekdays"],
        ["night_off_speak_services", "services"],
        ["night_off_volume_players", "entities", { domains: ["media_player"] }],
        ["night_off_volume", "number", { min: 0, max: 1, step: 0.01 }],
      ],
    },
    {
      id: "hint",
      icon: "mdi:window-open-variant",
      fields: [
        ["hint_door_sensor", "entity", { domains: ["binary_sensor"] }],
        ["hint_windows", "entities", { domains: ["binary_sensor"] }],
        ["hint_entity", "entity", { domains: ["switch", "light", "input_boolean"] }],
        ["hint_duration", "number", { unit: "s", min: 1, max: 600 }],
      ],
    },
  ],
  camera: [
    { id: "cameras", icon: "mdi:cctv", special: "sub", sub: "camera" },
    { id: "garages", icon: "mdi:garage", special: "sub", sub: "garage" },
  ],
};

// Fields of the sub items (name is the title)
const SUBS = {
  sensor: {
    icon: (d) => TYPE_ICONS[d.type] || TYPE_ICONS.other,
    fields: [
      ["name", "text"],
      ["entity", "entity", { domains: ["binary_sensor", "input_boolean"] }],
      ["type", "select", { choices: "types" }],
      ["use_entry_delay", "bool"],
      ["use_exit_delay", "bool"],
      ["auto_bypass", "bool"],
      ["allow_open", "bool"],
    ],
    advanced: [
      ["only_when_unavailable", "entity", {}],
      ["arm_cover", "entity", { domains: ["cover"] }],
      ["arm_cover_position", "number", { unit: "%", min: 0, max: 100 }],
      ["camera_preset", "text"],
    ],
    defaults: { type: "window", arm_cover_position: 20, ...TYPE_DEFAULTS.window },
  },
  person: {
    icon: () => "mdi:account",
    fields: [
      ["name", "text"],
      ["wifi_sensor", "entity", { domains: ["sensor"] }],
    ],
    defaults: {},
  },
  camera: {
    icon: () => "mdi:cctv",
    fields: [
      ["name", "text"],
      ["privacy_switch", "entity", { domains: ["switch"] }],
      ["ptz_select", "entity", { domains: ["select"] }],
      ["ptz_home_preset", "text"],
      ["privacy_delay", "number", { unit: "min", min: 0, max: 60 }],
      ["record_switches", "entities", { domains: ["switch"] }],
      ["detect_switches", "entities", { domains: ["switch"] }],
      ["person_sensor", "entity", { domains: ["binary_sensor"] }],
      ["person_count_sensor", "entity", { domains: ["sensor"] }],
      ["person_image", "entity", { domains: ["image", "camera"] }],
      ["person_push", "bool"],
    ],
    defaults: { privacy_delay: 2, person_push: true, record_switches: [], detect_switches: [] },
  },
  garage: {
    icon: () => "mdi:garage",
    fields: [
      ["name", "text"],
      ["garage_panel", "entity", { domains: ["alarm_control_panel"] }],
      ["garage_networks", "list", {}],
      ["garage_arm_delay", "number", { unit: "min", min: 0, max: 60 }],
      ["garage_motion", "entities", { domains: ["binary_sensor"] }],
      ["garage_tts_services", "services"],
      ["garage_tts_text", "text"],
      ["garage_tts_repeat", "number", { min: 0, max: 10 }],
    ],
    defaults: { garage_arm_delay: 2, garage_tts_repeat: 2, garage_networks: [], garage_motion: [] },
  },
};

const prettyService = (svc) =>
  String(svc)
    .replace(/^notify\./, "")
    .replace(/^mobile_app_/, "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

const esc = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const clone = (value) => JSON.parse(JSON.stringify(value ?? null));

class AlarmAssistantPanel extends HTMLElement {
  constructor() {
    super();
    this._tab = "overview";
    this._drafts = {};
    this._edit = null;
    this._cfg = null;
    this._error = null;
    this._sig = "";
    this._testDisabled = null;
    this.attachShadow({ mode: "open" });
    this.shadowRoot.addEventListener("click", (ev) => this._onClick(ev));
    this.shadowRoot.addEventListener("input", (ev) => this._onInput(ev));
    this.shadowRoot.addEventListener("change", (ev) => this._onInput(ev, true));
    this.shadowRoot.addEventListener("keydown", (ev) => this._onKey(ev));
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) {
      this._load();
    } else {
      this._live();
    }
  }

  get hass() {
    return this._hass;
  }

  set narrow(value) {
    this._narrow = value;
    const btn = this.shadowRoot.querySelector(".menu");
    if (btn) btn.style.display = value ? "" : "none";
  }

  set panel(value) {
    this._panel = value;
  }

  // ------------------------------------------------------------------ texts

  get lang() {
    const language = this._hass?.locale?.language || this._hass?.language || "en";
    return language.startsWith("de") ? "de" : "en";
  }

  get ui() {
    return UI[this.lang];
  }

  label(key) {
    return (LABELS[this.lang] || LABELS.en)[key] || [key, ""];
  }

  // ------------------------------------------------------------------ data

  async _load() {
    try {
      this._cfg = await this._hass.callWS({ type: "alarm_assistant/config" });
      if (this._testDisabled === null) this._testDisabled = new Set(this._cfg.test_last || []);
      this._error = null;
    } catch (err) {
      this._error = err.message || String(err);
    }
    this._render();
  }

  _ws(msg) {
    return this._hass.callWS(msg);
  }

  _state(entityId) {
    return entityId ? this._hass.states[entityId] : undefined;
  }

  _name(entityId) {
    const st = this._state(entityId);
    return st?.attributes?.friendly_name || entityId;
  }

  _subs(type) {
    return (this._cfg?.subentries || []).filter((s) => s.type === type);
  }

  // ------------------------------------------------------------------ rendering

  _render() {
    const ui = this.ui;
    const root = this.shadowRoot;
    root.innerHTML = `
      <style>${STYLE}</style>
      <div class="toolbar">
        <button class="menu icon-btn" data-action="menu" style="${this._narrow ? "" : "display:none"}"><ha-icon icon="mdi:menu"></ha-icon></button>
        <div class="title"><ha-icon icon="mdi:shield-home"></ha-icon>${esc(ui.title)}</div>
      </div>
      <div class="tabs">
        ${TABS.map(
          ([id, icon]) =>
            `<button class="tab ${this._tab === id ? "active" : ""}" data-tab="${id}"><ha-icon icon="${icon}"></ha-icon><span>${esc(ui.tabs[id])}</span></button>`,
        ).join("")}
      </div>
      <div class="content">${this._content()}</div>
      <div class="datalists">${this._datalists()}</div>
      <div class="toast" hidden></div>`;
    this._sig = this._signature();
  }

  _content() {
    if (this._error) return `<div class="card error">${esc(this.ui.loadError)}: ${esc(this._error)}</div>`;
    if (!this._cfg) return `<div class="card">…</div>`;
    if (this._edit) return this._editor();
    if (this._tab === "overview") return this._overview();
    if (this._tab === "sensors") return this._sensorsTab();
    if (this._tab === "test") return this._testTab();
    return (SETTINGS[this._tab] || []).map((card) => this._settingsCard(card)).join("");
  }

  _datalists() {
    if (!this._hass) return "";
    const domains = new Map();
    for (const id of Object.keys(this._hass.states)) {
      const domain = id.split(".")[0];
      if (!domains.has(domain)) domains.set(domain, []);
      domains.get(domain).push(id);
    }
    const option = (id) => `<option value="${esc(id)}">${esc(this._name(id))}</option>`;
    let html = `<datalist id="dl-all">${Object.keys(this._hass.states).sort().map(option).join("")}</datalist>`;
    for (const [domain, ids] of domains) {
      html += `<datalist id="dl-${esc(domain)}">${ids.sort().map(option).join("")}</datalist>`;
    }
    const services = this._cfg?.notify_services || [];
    html += `<datalist id="dl-services">${services.map((s) => `<option value="${esc(s)}"></option>`).join("")}</datalist>`;
    const tags = Object.values(this._hass.states).filter((s) => s.entity_id.startsWith("tag.") && s.attributes.tag_id);
    html += `<datalist id="dl-tags">${tags
      .map((s) => `<option value="${esc(s.attributes.tag_id)}">${esc(s.attributes.friendly_name || s.entity_id)}</option>`)
      .join("")}</datalist>`;
    return html;
  }

  _listId(opts) {
    const domains = opts?.domains;
    if (!domains || !domains.length) return "dl-all";
    if (domains.length === 1) return `dl-${domains[0]}`;
    return "dl-all";
  }

  // ------------------------------------------------------------------ overview

  _signature() {
    if (!this._hass || !this._cfg) return "";
    const ids = [
      ...Object.values(this._cfg.entities || {}),
      ...Object.values(this._cfg.presence || {}),
      ...this._subs("sensor").map((s) => s.data.entity),
      ...this._subs("person").map((s) => s.data.wifi_sensor),
    ];
    return ids
      .map((id) => {
        const st = this._state(id);
        return st
          ? `${id}=${st.state}|${JSON.stringify(st.attributes.open_sensors || "")}|${st.attributes.arms_at || ""}|${st.attributes.test_mode || ""}`
          : `${id}=-`;
      })
      .join(";");
  }

  _live() {
    const sig = this._signature();
    if (sig === this._sig) return;
    this._sig = sig;
    if (this._edit) return;
    if (this._tab === "overview" || this._tab === "test") {
      const content = this.shadowRoot.querySelector(".content");
      if (content) content.innerHTML = this._tab === "overview" ? this._overview() : this._testTab();
      return;
    }
    for (const el of this.shadowRoot.querySelectorAll("[data-live]")) {
      const [kind, id] = el.dataset.live.split("|");
      const [textValue, cls] = this._liveValue(kind, id);
      el.textContent = textValue;
      el.className = `pill ${cls}`;
    }
  }

  _liveValue(kind, id) {
    const ui = this.ui;
    const st = this._state(id);
    if (!st || ["unavailable", "unknown"].includes(st.state)) return [ui.states.unavailable, "muted"];
    if (kind === "sensor") {
      const sub = this._subs("sensor").find((s) => s.data.entity === id);
      const motion = sub?.data.type === "motion";
      if (st.state === "on") return [motion ? ui.motionOn : ui.open, "warn"];
      return [motion ? ui.motionOff : ui.closed, "ok"];
    }
    if (kind === "person") return [st.state === "on" ? ui.home : ui.away, st.state === "on" ? "ok" : "muted"];
    return [st.state, ""];
  }

  _overview() {
    const ui = this.ui;
    const ent = this._cfg.entities || {};
    const panel = this._state(ent.panel);
    const state = panel?.state || "unavailable";
    const [icon, color] = STATE_ICONS[state] || ["mdi:shield-off-outline", "var(--disabled-text-color)"];
    const attrs = panel?.attributes || {};
    const sensorName = (id) => this._subs("sensor").find((s) => s.data.entity === id)?.title || this._name(id);
    const open = attrs.open_sensors || [];
    const bypassed = (attrs.bypassed_sensors || []).map(sensorName);
    const isDisarmed = state === "disarmed";

    const status = `
      <div class="card status">
        <div class="status-main">
          <ha-icon icon="${icon}" style="color:${color}" class="${state === "triggered" ? "blink" : ""}"></ha-icon>
          <div>
            <div class="status-text" style="color:${color}">${esc(ui.states[state] || state)}${attrs.test_mode ? ` <span class="badge test">${esc(ui.testBadge)}</span>` : ""}</div>
            <div class="muted">${open.length ? `${esc(ui.openContacts)}: ${esc(open.join(", "))}` : esc(ui.noneOpen)}</div>
            ${bypassed.length ? `<div class="muted">${esc(ui.ignored)}: ${esc(bypassed.join(", "))}</div>` : ""}
          </div>
        </div>
        <div class="status-actions">
          ${isDisarmed
            ? `<button class="btn primary danger" data-action="arm"><ha-icon icon="mdi:shield-lock"></ha-icon>${esc(ui.arm)}</button>`
            : `<button class="btn primary" data-action="disarm"><ha-icon icon="mdi:shield-off-outline"></ha-icon>${esc(ui.disarm)}</button>`}
        </div>
      </div>`;

    const switchKeys = [
      ["auto_arm", "mdi:shield-home"],
      ["kids_home", "mdi:human-child"],
      ["night_door", "mdi:door-closed-lock"],
      ["live_mode", "mdi:cctv"],
      ["garage_auto", "mdi:garage-lock"],
    ].filter(([key]) => ent[key]);
    const switches = `
      <div class="card">
        <h2><ha-icon icon="mdi:toggle-switch-outline"></ha-icon>${esc(ui.switches)}</h2>
        <div class="tiles">
          ${switchKeys
            .map(([key, ic]) => {
              const st = this._state(ent[key]);
              const on = st?.state === "on";
              const name = (st?.attributes?.friendly_name || key).replace(/^Alarm Assistant\s*/, "");
              return `<button class="tile ${on ? "on" : ""}" data-action="toggle" data-entity="${esc(ent[key])}">
                <ha-icon icon="${ic}"></ha-icon><span>${esc(name)}</span><span class="switch ${on ? "on" : ""}"></span></button>`;
            })
            .join("")}
        </div>
      </div>`;

    const persons = this._subs("person");
    const presence = persons.length
      ? `<div class="card">
          <h2><ha-icon icon="mdi:account-group-outline"></ha-icon>${esc(ui.cards.persons[0])}</h2>
          <div class="rows">
            ${persons
              .map((p) => {
                const pres = this._state(this._cfg.presence?.[p.id]);
                const home = pres?.state === "on";
                const wifi = this._state(p.data.wifi_sensor)?.state || ui.none;
                return `<div class="row"><ha-icon icon="${home ? "mdi:home-account" : "mdi:account-arrow-right"}"></ha-icon>
                  <span class="grow">${esc(p.title)}</span><span class="muted">${esc(wifi)}</span>
                  <span class="pill ${home ? "ok" : "muted"}">${esc(home ? ui.home : ui.away)}</span></div>`;
              })
              .join("")}
          </div></div>`
      : "";

    const warnings = [];
    if (this._state(ent.motion_suppressed)?.state === "on") warnings.push(ui.suppressed);
    const warn = this._state(ent.auto_arm_warning);
    if (warn?.state === "on" && warn.attributes.arms_at) {
      warnings.push(`${ui.prewarn} ${new Date(warn.attributes.arms_at).toLocaleTimeString(this._hass.language)}`);
    }
    if ((this._cfg.missing || []).length) warnings.push(`${ui.missing}: ${this._cfg.missing.join(", ")}`);
    const cause = this._state(ent.cause)?.state;
    const last = this._state(ent.last_triggered)?.state;
    const lastText =
      last && !["unknown", "unavailable"].includes(last)
        ? `${new Date(last).toLocaleString(this._hass.language)} – ${cause || ""}`
        : ui.noAlarm;
    const info = `
      <div class="card">
        <h2><ha-icon icon="mdi:information-outline"></ha-icon>${esc(ui.warnings)}</h2>
        ${warnings.length ? warnings.map((w) => `<div class="row warn-row"><ha-icon icon="mdi:alert-outline"></ha-icon><span>${esc(w)}</span></div>`).join("") : `<div class="muted">${esc(ui.noWarnings)}</div>`}
        <div class="row"><ha-icon icon="mdi:clock-alert-outline"></ha-icon><span class="grow">${esc(ui.lastAlarm)}</span><span class="muted">${esc(lastText)}</span></div>
        <div class="actions"><button class="btn" data-action="test"><ha-icon icon="mdi:message-alert-outline"></ha-icon>${esc(ui.test)}</button></div>
      </div>`;

    const o = this._cfg.options;
    const g = ui.glanceRows;
    const glanceRows = [
      ["sensors", "mdi:leak", g.sensors, `${this._subs("sensor").length}`],
      ["presence", "mdi:account-group-outline", g.persons, persons.map((p) => p.title).join(", ") || ui.none],
      ["notify", "mdi:cellphone-message", g.push, [...new Set([...o.notify_services, ...o.notify_alarm_services])].map(prettyService).join(", ") || ui.none],
      ["notify", "mdi:phone-alert", g.call, `${(o.call_targets || []).length}`],
      ["reactions", "mdi:alarm-light-outline", g.alarmon, ui.alarmOn(o.announce_entities.length, o.turn_on_entities.length, o.close_covers.length)],
      ["camera", "mdi:cctv", g.cameras, this._subs("camera").map((c) => c.title).join(", ") || ui.none],
      ["camera", "mdi:garage", g.garages, this._subs("garage").map((c) => c.title).join(", ") || ui.none],
    ];
    const glance = `
      <div class="card">
        <h2><ha-icon icon="mdi:format-list-checks"></ha-icon>${esc(ui.glance)}</h2>
        <div class="rows">
          ${glanceRows
            .map(([tab, ic, label, value]) => `<button class="row link" data-tab="${tab}"><ha-icon icon="${ic}"></ha-icon><span class="grow">${esc(label)}</span><span class="muted">${esc(value)}</span><ha-icon icon="mdi:chevron-right"></ha-icon></button>`)
            .join("")}
        </div>
      </div>`;
    return `<div class="grid">${status}${switches}${presence}${info}${glance}</div>`;
  }

  // ------------------------------------------------------------------ test alarm

  _testGroups() {
    const o = this._cfg.options;
    const pretty = prettyService;
    const entityItems = (list) => (list || []).map((id) => [id, this._name(id)]);
    const devices = new Map((this._cfg.alexa_devices || []).map((d) => [d.id, d.name]));
    const push = [...new Set([...(o.notify_services || []), ...(o.notify_alarm_services || []), ...(o.notify_admin_services || [])])];
    const armCovers = [...new Set(this._subs("sensor").filter((s) => s.data.arm_cover && s.data.only_when_unavailable).map((s) => s.data.arm_cover))];
    const groups = [
      ["push", "mdi:cellphone-message", push.map((s) => [s, pretty(s)])],
      ["call", "mdi:phone-alert", o.call_addon ? (o.call_targets || []).map((t, i) => [t, `${i + 1}. ${t}`]) : []],
      ["announce", "mdi:bullhorn-outline", entityItems(o.announce_entities)],
      ["volume", "mdi:volume-high", entityItems(o.volume_players)],
      ["sound", "mdi:alarm-bell", (o.sound_devices || []).map((id) => [id, devices.get(id) || id])],
      ["speak", "mdi:account-voice", (o.speak_services || []).map((s) => [s, pretty(s)])],
      ["lights", "mdi:lightbulb-group-outline", entityItems(o.turn_on_entities)],
      ["covers", "mdi:window-shutter", entityItems(o.close_covers)],
      ["lock", "mdi:lock-outline", o.lock && o.lock_on_arm ? entityItems([o.lock]) : []],
      ["arm_cover", "mdi:window-shutter-alert", entityItems(armCovers)],
      ["camera", "mdi:cctv", this._subs("camera").map((c) => [c.id, c.title])],
      ["armed_on", "mdi:toggle-switch-outline", entityItems(o.armed_on_entities)],
    ];
    return groups.filter(([, , items]) => items.length);
  }

  _testTab() {
    const ui = this.ui;
    const panel = this._state(this._cfg.entities.panel);
    const state = panel?.state || "unavailable";
    const attrs = panel?.attributes || {};
    const disabled = attrs.test_mode ? new Set(attrs.test_disabled || []) : this._testDisabled;
    const locked = state !== "disarmed";
    const groups = this._testGroups();
    let status;
    if (attrs.test_mode) {
      const [icon, color] = STATE_ICONS[state] || ["mdi:shield-off-outline", "var(--disabled-text-color)"];
      status = `<div class="card test-running">
        <div class="status-main"><ha-icon icon="${icon}" style="color:${color}"></ha-icon>
          <div><div class="status-text">${esc(ui.testRunning)}</div><div class="muted">${esc(ui.states[state] || state)}</div></div></div>
        <div class="status-actions">
          ${["armed_away", "pending"].includes(state) ? `<button class="btn primary danger" data-action="test-trigger"><ha-icon icon="mdi:bell-ring-outline"></ha-icon>${esc(ui.testTrigger)}</button>` : ""}
          <button class="btn primary" data-action="disarm"><ha-icon icon="mdi:shield-off-outline"></ha-icon>${esc(ui.disarm)}</button>
        </div></div>`;
    } else if (locked) {
      status = `<div class="card"><div class="row warn-row"><ha-icon icon="mdi:alert-outline"></ha-icon><span>${esc(ui.testNotDisarmed)}</span></div></div>`;
    } else {
      status = "";
    }
    const groupHtml = groups
      .map(([key, icon, items]) => {
        const groupOn = !disabled.has(key);
        const rows = items
          .map(([item, label]) => {
            const on = groupOn && !disabled.has(`${key}:${item}`);
            return `<label class="check ${groupOn ? "" : "dim"}"><input type="checkbox" data-test-key="${esc(`${key}:${item}`)}" ${on ? "checked" : ""} ${groupOn && !locked ? "" : "disabled"}>${esc(label)}</label>`;
          })
          .join("");
        return `<div class="test-group">
          <label class="toggle-row"><span class="lbl"><ha-icon icon="${icon}"></ha-icon> ${esc(ui.testGroups[key] || key)}</span>
            <input type="checkbox" class="switch-input" data-test-key="${esc(key)}" ${groupOn ? "checked" : ""} ${locked ? "disabled" : ""}><span class="switch ${groupOn ? "on" : ""}"></span></label>
          <div class="checks test-items">${rows}</div>
        </div>`;
      })
      .join("");
    return `${status}<div class="card" data-card="test">
      <h2><ha-icon icon="mdi:test-tube"></ha-icon>${esc(ui.testTitle)}</h2>
      <p class="desc">${esc(ui.testDesc)}</p>
      <div class="test-head"><span class="lbl">${esc(ui.testWhat)}</span>
        ${locked ? "" : `<span><button class="btn" data-action="test-all-on">${esc(ui.allOn)}</button> <button class="btn" data-action="test-all-off">${esc(ui.allOff)}</button></span>`}</div>
      <div class="test-groups">${groupHtml}</div>
      <div class="actions"><span class="msg"></span>
        <button class="btn primary danger" data-action="test-arm" ${locked ? "disabled" : ""}><ha-icon icon="mdi:shield-lock"></ha-icon>${esc(ui.testArm)}</button></div>
    </div>`;
  }

  // ------------------------------------------------------------------ sensors

  _sensorsTab() {
    const ui = this.ui;
    const [title, desc] = ui.cards.sensors;
    const sensors = this._subs("sensor").sort((a, b) => SENSOR_TYPES.indexOf(a.data.type) - SENSOR_TYPES.indexOf(b.data.type) || a.title.localeCompare(b.title));
    const rows = sensors
      .map((s) => {
        const d = { ...TYPE_DEFAULTS[s.data.type || "other"], ...s.data };
        const badges = [
          d.use_entry_delay ? ui.behaviour.use_entry_delay : ui.behaviour.immediate,
          d.auto_bypass ? ui.behaviour.auto_bypass : null,
          d.allow_open && s.data.type !== "motion" ? ui.behaviour.allow_open : null,
          d.only_when_unavailable ? ui.behaviour.condition : null,
        ].filter(Boolean);
        const [stText, stCls] = this._liveValue("sensor", d.entity);
        return `<tr data-edit="sensor" data-id="${esc(s.id)}">
          <td class="c-icon"><ha-icon icon="${TYPE_ICONS[d.type] || TYPE_ICONS.other}"></ha-icon></td>
          <td class="c-name"><div>${esc(s.title)}</div><div class="muted small entity-id">${esc(d.entity)}</div></td>
          <td class="hide-narrow">${esc(ui.types[d.type] || d.type)}</td>
          <td class="hide-narrow">${badges.map((b) => `<span class="badge">${esc(b)}</span>`).join("")}</td>
          <td class="c-state"><span class="pill ${stCls}" data-live="sensor|${esc(d.entity)}">${esc(stText)}</span></td>
          <td class="c-edit hide-narrow"><ha-icon icon="mdi:pencil-outline" class="muted"></ha-icon></td>
        </tr>`;
      })
      .join("");
    return `<div class="card">
      <h2><ha-icon icon="mdi:leak"></ha-icon>${esc(title)}</h2><p class="desc">${esc(desc)}</p>
      ${sensors.length
        ? `<div class="table-wrap"><table><thead><tr><th class="c-icon"></th><th class="c-name">${esc(ui.columns.name)}</th><th class="hide-narrow c-type">${esc(ui.columns.type)}</th><th class="hide-narrow c-beh">${esc(ui.columns.behaviour)}</th><th class="c-state">${esc(ui.columns.state)}</th><th class="c-edit hide-narrow"></th></tr></thead><tbody>${rows}</tbody></table></div>`
        : `<div class="muted">${esc(ui.noItems)}</div>`}
      <div class="actions"><button class="btn primary" data-new="sensor"><ha-icon icon="mdi:plus"></ha-icon>${esc(ui.add)}</button></div>
    </div>`;
  }

  // ------------------------------------------------------------------ settings cards

  _value(cardId, key) {
    const draft = this._drafts[cardId];
    if (draft && key in draft) return draft[key];
    return this._cfg.options[key];
  }

  _settingsCard(card) {
    const ui = this.ui;
    const [title, desc] = ui.cards[card.id] || [card.id, ""];
    const head = `<h2><ha-icon icon="${card.icon}"></ha-icon>${esc(title)}</h2>${desc ? `<p class="desc">${esc(desc)}</p>` : ""}`;
    if (card.special === "sub") return `<div class="card">${head}${this._subList(card.sub)}</div>`;
    if (card.special === "code") return this._codeCard(card, head);
    const dirty = !!this._drafts[card.id];
    const fields = card.fields.map(([key, type, opts]) => this._field(card.id, key, type, opts || {}, this._value(card.id, key))).join("");
    return `<div class="card" data-card="${card.id}">${head}<div class="fields">${fields}</div>
      <div class="actions"><span class="msg"></span>
        ${dirty ? `<button class="btn" data-cancel="${card.id}">${esc(ui.cancel)}</button>` : ""}
        <button class="btn primary" data-save="${card.id}" ${dirty ? "" : "disabled"}>${esc(ui.save)}</button></div></div>`;
  }

  _codeCard(card, head) {
    const ui = this.ui;
    const draft = this._drafts.code || {};
    const dirty = !!this._drafts.code;
    const codeArm = "code_arm_required" in draft ? draft.code_arm_required : this._cfg.options.code_arm_required;
    return `<div class="card" data-card="code">${head}
      <div class="fields">
        <div class="field"><span class="pill ${this._cfg.has_code ? "ok" : "muted"}">${esc(this._cfg.has_code ? ui.codeSet : ui.codeNotSet)}</span></div>
        <label class="field"><span class="lbl">${esc(ui.newCode)}</span>
          <input type="password" inputmode="numeric" autocomplete="new-password" data-card-id="code" data-k="new_code" value="${esc(draft.new_code || "")}">
          <small>${esc(ui.newCodeHelp)}</small></label>
        <label class="field"><span class="lbl">${esc(ui.codeConfirm)}</span>
          <input type="password" inputmode="numeric" autocomplete="new-password" data-card-id="code" data-k="code_confirm" value="${esc(draft.code_confirm || "")}"></label>
        ${this._toggle("code", "remove_code", ui.removeCode, "", !!draft.remove_code)}
        ${this._toggle("code", "code_arm_required", ui.codeArm, "", !!codeArm)}
      </div>
      <div class="actions"><span class="msg"></span>
        ${dirty ? `<button class="btn" data-cancel="code">${esc(ui.cancel)}</button>` : ""}
        <button class="btn primary" data-save="code" ${dirty ? "" : "disabled"}>${esc(ui.save)}</button></div></div>`;
  }

  _toggle(cardId, key, name, help, on) {
    return `<label class="field toggle-row"><span><span class="lbl">${esc(name)}</span>${help ? `<small>${esc(help)}</small>` : ""}</span>
      <input type="checkbox" class="switch-input" data-card-id="${cardId}" data-k="${key}" data-type="bool" ${on ? "checked" : ""}><span class="switch ${on ? "on" : ""}"></span></label>`;
  }

  _field(cardId, key, type, opts, value) {
    const ui = this.ui;
    const [name, help] = this.label(key);
    const attrs = `data-card-id="${cardId}" data-k="${key}" data-type="${type}"`;
    const helpHtml = help ? `<small>${esc(help)}</small>` : "";
    switch (type) {
      case "bool":
        return this._toggle(cardId, key, name, help, !!value);
      case "number":
        return `<label class="field"><span class="lbl">${esc(name)}</span><span class="with-unit">
          <input type="number" ${attrs} value="${esc(value ?? "")}" min="${opts.min ?? ""}" max="${opts.max ?? ""}" step="${opts.step ?? 1}">
          ${opts.unit ? `<span class="unit">${esc(opts.unit)}</span>` : ""}</span>${helpHtml}</label>`;
      case "text":
        return `<label class="field"><span class="lbl">${esc(name)}</span><input type="text" ${attrs} value="${esc(value ?? "")}">${helpHtml}</label>`;
      case "textarea":
        return `<label class="field"><span class="lbl">${esc(name)}</span><textarea rows="3" ${attrs}>${esc(value ?? "")}</textarea>${helpHtml}</label>`;
      case "time":
        return `<label class="field"><span class="lbl">${esc(name)}</span><input type="time" step="1" ${attrs} value="${esc(value ?? "")}">${helpHtml}</label>`;
      case "tag":
        return `<label class="field"><span class="lbl">${esc(name)}</span><input type="text" list="dl-tags" ${attrs} value="${esc(value ?? "")}">${helpHtml}</label>`;
      case "select": {
        const choices = ui[opts.choices] || {};
        return `<label class="field"><span class="lbl">${esc(name)}</span><select ${attrs}>
          ${Object.entries(choices).map(([k, v]) => `<option value="${esc(k)}" ${k === value ? "selected" : ""}>${esc(v)}</option>`).join("")}
          </select>${helpHtml}</label>`;
      }
      case "entity": {
        const st = value ? this._state(value) : null;
        const hint = value ? (st ? this._name(value) : `⚠ ${ui.notFound}`) : "";
        return `<label class="field"><span class="lbl">${esc(name)}</span>
          <input type="text" list="${this._listId(opts)}" ${attrs} value="${esc(value ?? "")}" placeholder="${esc((opts.domains || ["entity"])[0])}.…" autocomplete="off">
          <span class="entity-hint ${value && !st ? "bad" : ""}">${esc(hint)}</span>${helpHtml}</label>`;
      }
      case "entities":
      case "services":
      case "list": {
        const list = Array.isArray(value) ? value : [];
        const listId = type === "services" ? "dl-services" : type === "entities" ? this._listId(opts) : "";
        const chips = list
          .map((item, i) => {
            let label = item;
            let bad = false;
            if (type === "entities") {
              const st = this._state(item);
              label = st ? this._name(item) : item;
              bad = !st;
            }
            const order = opts.ordered
              ? `<button class="chip-btn" data-move="-1" data-index="${i}" ${attrs} title="${esc(ui.up)}">▲</button><button class="chip-btn" data-move="1" data-index="${i}" ${attrs} title="${esc(ui.down)}">▼</button>`
              : "";
            return `<span class="chip ${bad ? "bad" : ""}" title="${esc(item)}">${opts.ordered ? `<b>${i + 1}.</b>` : ""}${esc(label)}${order}<button class="chip-btn" data-remove="${i}" ${attrs}>✕</button></span>`;
          })
          .join("");
        return `<div class="field"><span class="lbl">${esc(name)}</span>
          <div class="chips">${chips}</div>
          <input type="text" ${listId ? `list="${listId}"` : ""} data-add="1" ${attrs} placeholder="${esc(ui.addValue)}" autocomplete="off">${helpHtml}</div>`;
      }
      case "devices": {
        const list = Array.isArray(value) ? value : [];
        const devices = this._cfg.alexa_devices || [];
        const known = new Set(devices.map((d) => d.id));
        const extra = list.filter((id) => !known.has(id)).map((id) => ({ id, name: `${id} (${ui.notFound})` }));
        return `<div class="field"><span class="lbl">${esc(name)}</span><div class="checks">
          ${[...devices, ...extra]
            .map((d) => `<label class="check"><input type="checkbox" data-device="${esc(d.id)}" ${attrs} ${list.includes(d.id) ? "checked" : ""}>${esc(d.name)}</label>`)
            .join("")}</div>${helpHtml}</div>`;
      }
      case "weekdays": {
        const list = Array.isArray(value) ? value : [];
        return `<div class="field"><span class="lbl">${esc(name)}</span><div class="days">
          ${WEEKDAYS.map((d) => `<button class="day ${list.includes(d) ? "on" : ""}" data-day="${d}" ${attrs}>${esc(ui.weekdays[d])}</button>`).join("")}
          </div>${helpHtml}</div>`;
      }
      default:
        return "";
    }
  }

  // ------------------------------------------------------------------ sub items

  _subList(type) {
    const ui = this.ui;
    const def = SUBS[type];
    const items = this._subs(type);
    const rows = items
      .map((s) => {
        let extra = "";
        if (type === "person") {
          const [txt, cls] = this._liveValue("person", this._cfg.presence?.[s.id]);
          const wifi = this._state(s.data.wifi_sensor)?.state || ui.none;
          extra = `<span class="muted">${esc(wifi)}</span><span class="pill ${cls}" data-live="person|${esc(this._cfg.presence?.[s.id] || "")}">${esc(txt)}</span>`;
        } else if (type === "garage") {
          extra = `<span class="muted">${esc(this._state(s.data.garage_panel)?.state || ui.none)}</span>`;
        }
        return `<button class="row link" data-edit="${type}" data-id="${esc(s.id)}"><ha-icon icon="${def.icon(s.data)}"></ha-icon>
          <span class="grow">${esc(s.title)}</span>${extra}<ha-icon icon="mdi:pencil-outline" class="muted"></ha-icon></button>`;
      })
      .join("");
    return `<div class="rows">${rows || `<div class="muted">${esc(ui.noItems)}</div>`}</div>
      <div class="actions"><button class="btn primary" data-new="${type}"><ha-icon icon="mdi:plus"></ha-icon>${esc(ui.add)}</button></div>`;
  }

  _editor() {
    const ui = this.ui;
    const e = this._edit;
    const def = SUBS[e.type];
    const values = { ...e.data, name: e.title };
    const field = ([key, type, opts]) => this._field("edit", key, type, opts || {}, values[key]);
    const title = e.id ? e.title || ui.edit : ui.newItem[e.type];
    return `<div class="card" data-card="edit">
      <h2><button class="icon-btn" data-action="close-edit"><ha-icon icon="mdi:arrow-left"></ha-icon></button>
        <ha-icon icon="${def.icon(values)}"></ha-icon>${esc(title)}</h2>
      <div class="fields">${def.fields.map(field).join("")}</div>
      ${def.advanced
        ? `<details ${e.showAdvanced ? "open" : ""} data-advanced="1"><summary>${esc(ui.advanced)}</summary><div class="fields">${def.advanced.map(field).join("")}</div></details>`
        : ""}
      <div class="actions"><span class="msg"></span>
        ${e.id ? `<button class="btn danger" data-action="delete-sub">${esc(ui.delete)}</button>` : ""}
        <span class="grow"></span>
        <button class="btn" data-action="close-edit">${esc(ui.cancel)}</button>
        <button class="btn primary" data-action="save-sub">${esc(ui.save)}</button></div>
    </div>`;
  }

  // ------------------------------------------------------------------ events

  _setValue(cardId, key, value) {
    if (cardId === "edit") {
      if (key === "name") {
        this._edit.title = value;
      } else {
        if (key === "type" && this._edit.type === "sensor" && value !== this._edit.data.type) {
          Object.assign(this._edit.data, TYPE_DEFAULTS[value] || {});
          this._edit.data.type = value;
          this._rerenderContent();
          return;
        }
        this._edit.data[key] = value;
      }
      return;
    }
    this._drafts[cardId] = this._drafts[cardId] || {};
    this._drafts[cardId][key] = value;
    const card = this.shadowRoot.querySelector(`[data-card="${cardId}"]`);
    if (card) {
      const save = card.querySelector(`[data-save="${cardId}"]`);
      if (save) save.disabled = false;
    }
  }

  _currentList(cardId, key) {
    const value = cardId === "edit" ? this._edit.data[key] : this._value(cardId, key);
    return Array.isArray(value) ? [...value] : [];
  }

  _onInput(ev, isChange = false) {
    const el = ev.target;
    if (el.dataset.testKey !== undefined) {
      if (!isChange) return;
      const key = el.dataset.testKey;
      if (el.checked) this._testDisabled.delete(key);
      else this._testDisabled.add(key);
      this._rerenderContent();
      return;
    }
    if (el.dataset.add) {
      if (isChange) this._addListValue(el);
      return;
    }
    const cardId = el.dataset.cardId;
    const key = el.dataset.k;
    if (!cardId || !key) return;
    const type = el.dataset.type;
    if (el.dataset.device !== undefined) {
      const list = this._currentList(cardId, key).filter((id) => id !== el.dataset.device);
      if (el.checked) list.push(el.dataset.device);
      this._setValue(cardId, key, list);
      return;
    }
    let value;
    if (type === "bool" || el.type === "checkbox") {
      value = el.checked;
      const sw = el.nextElementSibling;
      if (sw?.classList.contains("switch")) sw.classList.toggle("on", value);
    } else if (type === "number") {
      value = el.value === "" ? null : Number(el.value);
    } else {
      value = el.value;
    }
    if (type === "entity") {
      const hint = el.parentElement.querySelector(".entity-hint");
      if (hint) {
        const st = value ? this._state(value) : null;
        hint.textContent = value ? (st ? this._name(value) : `⚠ ${this.ui.notFound}`) : "";
        hint.classList.toggle("bad", !!value && !st);
      }
    }
    this._setValue(cardId, key, value);
  }

  _onKey(ev) {
    const el = ev.target;
    if (ev.key === "Enter" && el.dataset.add) {
      ev.preventDefault();
      this._addListValue(el);
    }
  }

  _addListValue(el) {
    const value = el.value.trim();
    if (!value) return;
    const { cardId, k: key } = el.dataset;
    const list = this._currentList(cardId, key);
    if (!list.includes(value)) list.push(value);
    this._setValue(cardId, key, list);
    this._rerenderContent(`[data-add][data-k="${key}"]`);
  }

  _rerenderContent(focusSelector) {
    const content = this.shadowRoot.querySelector(".content");
    if (!content) return;
    if (this._edit) {
      const details = content.querySelector("details[data-advanced]");
      if (details) this._edit.showAdvanced = details.open;
    }
    const scroll = content.scrollTop;
    content.innerHTML = this._content();
    content.scrollTop = scroll;
    if (focusSelector) content.querySelector(focusSelector)?.focus();
  }

  async _onClick(ev) {
    const el = ev.target.closest("button, [data-edit], [data-tab]");
    if (!el || el.disabled) return;
    const d = el.dataset;
    if (d.tab) {
      this._tab = d.tab;
      this._edit = null;
      this._render();
      return;
    }
    if (d.remove !== undefined) {
      ev.preventDefault();
      const list = this._currentList(d.cardId, d.k);
      list.splice(Number(d.remove), 1);
      this._setValue(d.cardId, d.k, list);
      this._rerenderContent();
      return;
    }
    if (d.move !== undefined) {
      ev.preventDefault();
      const list = this._currentList(d.cardId, d.k);
      const i = Number(d.index);
      const j = i + Number(d.move);
      if (j >= 0 && j < list.length) {
        [list[i], list[j]] = [list[j], list[i]];
        this._setValue(d.cardId, d.k, list);
        this._rerenderContent();
      }
      return;
    }
    if (d.day) {
      ev.preventDefault();
      const list = this._currentList(d.cardId, d.k);
      const next = list.includes(d.day) ? list.filter((x) => x !== d.day) : [...list, d.day];
      this._setValue(d.cardId, d.k, WEEKDAYS.filter((x) => next.includes(x)));
      el.classList.toggle("on");
      return;
    }
    if (d.save) return this._saveCard(d.save, el);
    if (d.cancel) {
      delete this._drafts[d.cancel];
      this._rerenderContent();
      return;
    }
    if (d.new) {
      this._edit = { type: d.new, id: null, title: "", data: clone(SUBS[d.new].defaults) };
      this._rerenderContent();
      return;
    }
    if (d.edit) {
      const sub = this._subs(d.edit).find((s) => s.id === d.id);
      if (sub) {
        this._edit = { type: d.edit, id: sub.id, title: sub.title, data: { ...clone(SUBS[d.edit].defaults), ...clone(sub.data) } };
        if (d.edit === "sensor") this._edit.data = { ...TYPE_DEFAULTS[sub.data.type || "other"], ...this._edit.data };
        this._rerenderContent();
      }
      return;
    }
    switch (d.action) {
      case "menu":
        this.dispatchEvent(new Event("hass-toggle-menu", { bubbles: true, composed: true }));
        break;
      case "arm":
      case "disarm":
        await this._armDisarm(d.action);
        break;
      case "toggle": {
        const st = this._state(d.entity);
        await this._hass.callService("switch", st?.state === "on" ? "turn_off" : "turn_on", { entity_id: d.entity });
        break;
      }
      case "test":
        await this._hass.callService("button", "press", { entity_id: this._cfg.entities.test });
        this._toast(this.ui.testSent);
        break;
      case "test-all-on":
        this._testDisabled = new Set();
        this._rerenderContent();
        break;
      case "test-all-off":
        this._testDisabled = new Set(this._testGroups().map(([key]) => key));
        this._rerenderContent();
        break;
      case "test-arm":
        el.disabled = true;
        try {
          await this._ws({ type: "alarm_assistant/test_arm", disabled: [...this._testDisabled] });
          this._cfg.test_last = [...this._testDisabled];
        } catch (err) {
          el.disabled = false;
          const code = err.code || "";
          const prefix = this.ui.errorsTest[code];
          this._cardMessage(el, prefix ? `${prefix} ${err.message}` : err.message || String(err), true);
        }
        break;
      case "test-trigger":
        try {
          await this._ws({ type: "alarm_assistant/test_trigger" });
        } catch (err) {
          this._toast(err.message || String(err), true);
        }
        break;
      case "close-edit":
        this._edit = null;
        this._rerenderContent();
        break;
      case "save-sub":
        await this._saveSub(el);
        break;
      case "delete-sub":
        if (confirm(this.ui.confirmDelete)) {
          try {
            this._cfg = await this._ws({ type: "alarm_assistant/delete_subentry", subentry_id: this._edit.id });
            this._edit = null;
            this._render();
            this._toast(this.ui.saved);
          } catch (err) {
            this._cardMessage(el, err.message || String(err), true);
          }
        }
        break;
      default:
        break;
    }
  }

  async _armDisarm(action) {
    const panelId = this._cfg.entities.panel;
    const attrs = this._state(panelId)?.attributes || {};
    const data = { entity_id: panelId };
    const needCode = attrs.code_format && (action === "disarm" || attrs.code_arm_required);
    if (needCode) {
      const code = prompt(this.ui.enterCode);
      if (code === null) return;
      data.code = code;
    }
    try {
      await this._hass.callService("alarm_control_panel", action === "arm" ? "alarm_arm_away" : "alarm_disarm", data);
    } catch (err) {
      this._toast(err.message || String(err), true);
    }
  }

  async _saveCard(cardId, button) {
    const draft = this._drafts[cardId];
    if (!draft) return;
    const msg = { type: "alarm_assistant/save_options", options: {} };
    if (cardId === "code") {
      if (draft.remove_code) msg.remove_code = true;
      else if (draft.new_code) {
        if (String(draft.new_code) !== String(draft.code_confirm || "")) {
          this._cardMessage(button, this.ui.errors.code_mismatch, true);
          return;
        }
        msg.code = String(draft.new_code);
      }
      if ("code_arm_required" in draft) msg.options.code_arm_required = draft.code_arm_required;
    } else {
      msg.options = { ...draft };
    }
    button.disabled = true;
    try {
      this._cfg = await this._ws(msg);
      delete this._drafts[cardId];
      this._rerenderContent();
      this._toast(this.ui.saved);
    } catch (err) {
      button.disabled = false;
      this._cardMessage(button, this._errorText(err), true);
    }
  }

  async _saveSub(button) {
    const e = this._edit;
    const data = {};
    const def = SUBS[e.type];
    for (const [key] of [...def.fields, ...(def.advanced || [])]) {
      if (key === "name") continue;
      const value = e.data[key];
      if (value !== undefined && value !== null && value !== "") data[key] = value;
    }
    const msg = { type: "alarm_assistant/save_subentry", subentry_type: e.type, title: e.title || "", data };
    if (e.id) msg.subentry_id = e.id;
    button.disabled = true;
    try {
      const result = await this._ws(msg);
      this._cfg = result.config;
      this._edit = null;
      this._render();
      this._toast(this.ui.saved);
    } catch (err) {
      button.disabled = false;
      this._cardMessage(button, this._errorText(err), true);
    }
  }

  _errorText(err) {
    const message = err?.message || String(err);
    if (this.ui.errors[message]) return this.ui.errors[message];
    const [field, code] = message.split(":");
    if (code && this.ui.fieldErrors[code]) return `${this.label(field)[0]}: ${this.ui.fieldErrors[code]}`;
    return message;
  }

  _cardMessage(el, text, bad = false) {
    const msg = el.closest(".card")?.querySelector(".msg");
    if (msg) {
      msg.textContent = text;
      msg.classList.toggle("bad", bad);
    }
  }

  _toast(text, bad = false) {
    const toast = this.shadowRoot.querySelector(".toast");
    if (!toast) return;
    toast.textContent = text;
    toast.classList.toggle("bad", bad);
    toast.hidden = false;
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => (toast.hidden = true), 2500);
  }
}

const STYLE = `
:host { display:block; min-height:100vh; overflow-x:hidden; background:var(--primary-background-color); color:var(--primary-text-color); font-family:var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
* { box-sizing:border-box; }
.toolbar { display:flex; align-items:center; height:56px; padding:0 12px; background:var(--app-header-background-color, var(--primary-color)); color:var(--app-header-text-color, #fff); gap:8px; }
.title { display:flex; align-items:center; gap:10px; font-size:20px; font-weight:400; }
.tabs { display:flex; overflow-x:auto; background:var(--app-header-background-color, var(--primary-color)); padding:0 8px; scrollbar-width:none; }
.tab { display:flex; align-items:center; gap:6px; background:none; border:none; color:var(--app-header-text-color, #fff); opacity:.75; padding:10px 14px; cursor:pointer; border-bottom:2px solid transparent; font-size:14px; white-space:nowrap; }
.tab.active { opacity:1; border-bottom-color:var(--app-header-text-color, #fff); }
.tab ha-icon { --mdc-icon-size:20px; }
.content { padding:16px; max-width:1200px; margin:0 auto; }
.grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(340px, 1fr)); gap:16px; align-items:start; }
.content > .card { margin-bottom:16px; }
.card { min-width:0; overflow-wrap:anywhere; background:var(--ha-card-background, var(--card-background-color, #fff)); border-radius:var(--ha-card-border-radius, 12px); border:1px solid var(--divider-color, #e0e0e0); padding:16px; box-shadow:var(--ha-card-box-shadow, none); }
.card.error { color:var(--error-color); }
h2 { display:flex; align-items:center; gap:10px; margin:0 0 4px; font-size:18px; font-weight:500; }
h2 ha-icon { color:var(--state-icon-color, var(--primary-color)); }
.desc { margin:0 0 12px; color:var(--secondary-text-color); font-size:14px; }
.fields { display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:12px 20px; margin-top:8px; }
.field { display:flex; flex-direction:column; gap:4px; font-size:14px; }
.lbl { font-weight:500; }
small { color:var(--secondary-text-color); font-size:12px; line-height:1.3; }
input[type=text], input[type=number], input[type=time], input[type=password], select, textarea {
  font:inherit; color:var(--primary-text-color); background:var(--input-fill-color, var(--secondary-background-color, #f5f5f5));
  border:1px solid var(--divider-color, #ccc); border-radius:8px; padding:8px 10px; width:100%; }
input:focus, select:focus, textarea:focus { outline:2px solid var(--primary-color); outline-offset:-1px; }
.with-unit { display:flex; align-items:center; gap:6px; }
.unit { color:var(--secondary-text-color); min-width:24px; }
.entity-hint { font-size:12px; color:var(--secondary-text-color); min-height:14px; }
.entity-hint.bad, .chip.bad, .msg.bad { color:var(--error-color, #db4437); }
.toggle-row { flex-direction:row; align-items:center; justify-content:space-between; gap:12px; cursor:pointer; }
.toggle-row > span:first-child { display:flex; flex-direction:column; gap:2px; }
.switch-input { display:none; }
.switch { position:relative; flex:none; width:36px; height:20px; border-radius:10px; background:var(--switch-unchecked-track-color, #9e9e9e); transition:background .2s; }
.switch::after { content:""; position:absolute; top:2px; left:2px; width:16px; height:16px; border-radius:50%; background:#fff; transition:left .2s; }
.switch.on { background:var(--switch-checked-track-color, var(--primary-color)); }
.switch.on::after { left:18px; }
.chips { display:flex; flex-wrap:wrap; gap:6px; }
.chip { max-width:100%; overflow-wrap:anywhere; display:inline-flex; align-items:center; gap:4px; background:var(--secondary-background-color, #eee); border-radius:16px; padding:3px 4px 3px 10px; font-size:13px; }
.chip b { margin-right:2px; }
.chip-btn { border:none; background:none; cursor:pointer; color:var(--secondary-text-color); padding:0 4px; font-size:12px; }
.checks { display:flex; flex-direction:column; gap:4px; }
.check { display:flex; align-items:center; gap:8px; }
.days { display:flex; gap:4px; flex-wrap:wrap; }
.day { border:1px solid var(--divider-color); background:none; color:var(--primary-text-color); border-radius:16px; padding:4px 10px; cursor:pointer; }
.day.on { background:var(--primary-color); color:var(--text-primary-color, #fff); border-color:var(--primary-color); }
.actions { display:flex; align-items:center; justify-content:flex-end; gap:8px; margin-top:16px; flex-wrap:wrap; }
.msg { margin-right:auto; font-size:13px; color:var(--secondary-text-color); }
.grow { flex:1; }
.btn { display:inline-flex; align-items:center; gap:6px; font:inherit; font-weight:500; border-radius:18px; padding:8px 16px; cursor:pointer; border:1px solid var(--divider-color); background:none; color:var(--primary-color); }
.btn ha-icon { --mdc-icon-size:18px; }
.btn.primary { background:var(--primary-color); color:var(--text-primary-color, #fff); border-color:var(--primary-color); }
.btn.danger { color:var(--error-color, #db4437); border-color:var(--error-color, #db4437); }
.btn.primary.danger { background:var(--error-color, #db4437); color:#fff; }
.btn:disabled { opacity:.45; cursor:default; }
.icon-btn { background:none; border:none; color:inherit; cursor:pointer; padding:4px; display:inline-flex; }
.status { display:flex; flex-direction:column; gap:16px; }
.status-main { display:flex; align-items:center; gap:16px; }
.status-main ha-icon { --mdc-icon-size:56px; }
.status-text { font-size:24px; font-weight:500; }
.status-actions { display:flex; gap:8px; flex-wrap:wrap; }
.blink { animation:blink 1s infinite; }
@keyframes blink { 50% { opacity:.3; } }
.tiles { display:grid; grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); gap:8px; margin-top:8px; }
.tile { display:flex; align-items:center; gap:8px; padding:10px; border-radius:10px; border:1px solid var(--divider-color); background:none; color:var(--primary-text-color); cursor:pointer; text-align:left; font:inherit; font-size:14px; }
.tile span:nth-child(2) { flex:1; }
.tile.on { border-color:var(--primary-color); }
.tile.on ha-icon { color:var(--primary-color); }
.rows { display:flex; flex-direction:column; }
.row { display:flex; align-items:center; gap:10px; padding:8px 4px; border-bottom:1px solid var(--divider-color); font:inherit; font-size:14px; color:var(--primary-text-color); background:none; border-left:none; border-right:none; border-top:none; text-align:left; width:100%; }
.row:last-child { border-bottom:none; }
.row > span { min-width:0; overflow-wrap:anywhere; }
.row > span.grow { flex:1 1 40%; min-width:7em; overflow-wrap:normal; }
.row > span.muted { flex:0 1 auto; text-align:right; }
.row.link { cursor:pointer; }
.row.link:hover, tbody tr:hover { background:var(--secondary-background-color, #f5f5f5); }
.warn-row ha-icon { color:var(--warning-color, #ffa600); }
.muted { color:var(--secondary-text-color); }
.small { font-size:12px; }
.pill { display:inline-block; border-radius:12px; padding:2px 10px; font-size:12px; background:var(--secondary-background-color, #eee); white-space:nowrap; }
.pill.ok { background:rgba(67,160,71,.15); color:var(--success-color, #2e7d32); }
.pill.warn { background:rgba(255,166,0,.18); color:var(--warning-color, #b26a00); }
.pill.muted { color:var(--secondary-text-color); }
.badge { display:inline-block; font-size:11px; border:1px solid var(--divider-color); border-radius:10px; padding:1px 8px; margin:1px 4px 1px 0; color:var(--secondary-text-color); }
.table-wrap { width:100%; overflow-x:auto; }
table { width:100%; border-collapse:collapse; font-size:14px; table-layout:fixed; }
th.c-icon { width:40px; } th.c-type { width:110px; } th.c-beh { width:34%; } th.c-state { width:92px; } th.c-edit { width:32px; }
td.c-name div { overflow-wrap:anywhere; }
th { text-align:left; font-weight:500; color:var(--secondary-text-color); padding:6px 8px; border-bottom:1px solid var(--divider-color); }
td { padding:8px; border-bottom:1px solid var(--divider-color); vertical-align:middle; }
tbody tr { cursor:pointer; }
details { margin-top:16px; }
summary { cursor:pointer; font-weight:500; color:var(--primary-color); }
.test-groups { display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:12px; margin-top:8px; }
.test-group { border:1px solid var(--divider-color); border-radius:10px; padding:10px 12px; }
.test-group > .toggle-row { display:flex; cursor:pointer; }
.test-group .toggle-row > span.lbl { display:flex; flex-direction:row; align-items:center; gap:8px; text-align:left; }
.test-group .lbl ha-icon { --mdc-icon-size:20px; color:var(--state-icon-color, var(--primary-color)); }
.test-items { margin-top:8px; padding-left:4px; font-size:14px; }
.check.dim { opacity:.45; }
.test-head { display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap; margin-top:8px; }
.test-running { border-color:var(--warning-color, #ffa600); margin-bottom:16px; display:flex; flex-direction:column; gap:12px; }
.badge.test { background:var(--warning-color, #ffa600); color:#000; border:none; font-size:12px; vertical-align:middle; }
.toast { position:fixed; bottom:24px; left:50%; transform:translateX(-50%); background:var(--primary-text-color); color:var(--primary-background-color); padding:10px 18px; border-radius:8px; z-index:10; }
.toast.bad { background:var(--error-color, #db4437); color:#fff; }
@media (max-width: 700px) {
  .hide-narrow { display:none; } .content { padding:8px; } .grid { grid-template-columns:1fr; }
  .tab span { display:none; } .tab.active span { display:inline; } .tab { padding:10px 12px; }
  .fields, .test-groups { grid-template-columns:1fr; }
  th.c-icon { width:32px; } th.c-state { width:80px; }
  td { padding:8px 4px; } .entity-id { font-size:11px; }
  .card { padding:12px; }
}
`;

if (!customElements.get("alarm-assistant-panel")) {
  customElements.define("alarm-assistant-panel", AlarmAssistantPanel);
}
