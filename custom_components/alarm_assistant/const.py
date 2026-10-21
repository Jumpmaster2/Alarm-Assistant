"""Constants for Alarm Assistant."""

from __future__ import annotations

import logging
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "alarm_assistant"
NAME: Final = "Alarm Assistant"
LOGGER = logging.getLogger(__package__)

PLATFORMS: Final = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.SWITCH,
]

SUBENTRY_SENSOR: Final = "sensor"
SUBENTRY_CAMERA: Final = "camera"
SUBENTRY_GARAGE: Final = "garage"
SUBENTRY_PERSON: Final = "person"
STORAGE_VERSION: Final = 1
EVENT_LOGBOOK: Final = f"{DOMAIN}_logbook"

LANGUAGE_OPTIONS: Final = ["auto", "de", "en"]

# ---------- general
CONF_LANGUAGE = "language"
CONF_NOTIFY = "notify_services"
CONF_NOTIFY_ALARM = "notify_alarm_services"
CONF_NOTIFY_ADMIN = "notify_admin_services"

# ---------- alarm
CONF_ENTRY_DELAY = "entry_delay"
CONF_EXIT_DELAY = "exit_delay"
CONF_TRIGGER_TIME = "trigger_time"
CONF_DISARM_AFTER_TRIGGER = "disarm_after_trigger"
CONF_CODE = "code"
CONF_CODE_ARM = "code_arm_required"
CONF_ARM_ON_ENTITIES = "armed_on_entities"
CONF_NOTIFY_UNAVAILABLE = "notify_unavailable"
CONF_UNAVAILABLE_DELAY = "unavailable_delay"

# ---------- motion
CONF_VACUUM = "vacuum"
CONF_VACUUM_CHARGING = "vacuum_charging"
CONF_DOCK_GRACE = "dock_grace"
CONF_FAULT_SENSOR = "fault_sensor"
CONF_NOTIFY_SUPPRESSED = "notify_suppressed_motion"

# ---------- reactions on alarm
CONF_ANNOUNCE_ENTITIES = "announce_entities"
CONF_SPEAK_SERVICES = "speak_services"
CONF_SOUND_DEVICES = "sound_devices"
CONF_SOUND = "sound"
CONF_VOLUME_PLAYERS = "volume_players"
CONF_ALARM_VOLUME = "alarm_volume"
CONF_RESET_VOLUME = "reset_volume"
CONF_RESET_AFTER = "reset_volume_after"
CONF_TEXT_TRIGGERED = "text_triggered"
CONF_TEXT_PENDING = "text_pending"
CONF_TURN_ON = "turn_on_entities"
CONF_CLOSE_COVERS = "close_covers"

# ---------- call
CONF_CALL_ADDON = "call_addon"
CONF_CALL_TARGETS = "call_targets"
CONF_CALL_ACK = "call_acknowledge"
CONF_CALL_WAIT = "call_wait"
CONF_CALL_TTS = "call_tts"
CONF_CALL_LANGUAGE = "call_language"
CONF_CALL_COOLDOWN = "call_cooldown"

# ---------- automatic arming
CONF_PRESENCE_MODE = "presence_mode"
CONF_WIFI_SENSORS = "wifi_sensors"
CONF_HOME_NETWORKS = "home_networks"
CONF_PERSONS = "persons"
CONF_QUIET = "quiet_time"
CONF_PREWARN = "prewarn_time"
CONF_RETRY = "retry_after_disarm"
CONF_PRESENCE_STABLE = "presence_stable"

# ---------- lock
CONF_LOCK = "lock"
CONF_LOCK_DOOR = "lock_door_sensor"
CONF_DISARM_ON_UNLOCK = "disarm_on_unlock"
CONF_LOCK_ON_ARM = "lock_on_arm"

# ---------- children alone at home
CONF_KIDS_RESET_AFTER = "kids_reset_after_unlock"
CONF_KIDS_RESET_TIME = "kids_reset_time"

# ---------- night door alarm
CONF_NIGHT_DOOR = "night_door_sensor"
CONF_NIGHT_TAG = "night_tag"
CONF_NIGHT_OFF_TIME = "night_off_time"
CONF_NIGHT_OFF_DAYS = "night_off_days"
CONF_NIGHT_TURN_ON = "night_turn_on_entities"
CONF_NIGHT_SOUND_DEVICES = "night_sound_devices"
CONF_NIGHT_VOLUME_PLAYERS = "night_volume_players"
CONF_NIGHT_SPEAK = "night_speak_services"
CONF_NIGHT_TEXT = "night_text"
CONF_NIGHT_OFF_SPEAK = "night_off_speak_services"
CONF_NIGHT_OFF_VOLUME = "night_off_volume"
CONF_NIGHT_OFF_VOLUME_PLAYERS = "night_off_volume_players"
CONF_NIGHT_RESET_AFTER = "night_reset_volume_after"

# ---------- window open hint at the door
CONF_HINT_DOOR = "hint_door_sensor"
CONF_HINT_WINDOWS = "hint_windows"
CONF_HINT_ENTITY = "hint_entity"
CONF_HINT_DURATION = "hint_duration"

DEFAULTS: Final[dict[str, object]] = {
    CONF_LANGUAGE: "auto",
    CONF_NOTIFY: [],
    CONF_NOTIFY_ALARM: [],
    CONF_NOTIFY_ADMIN: [],
    CONF_ENTRY_DELAY: 30,
    CONF_EXIT_DELAY: 0,
    CONF_TRIGGER_TIME: 1800,
    CONF_DISARM_AFTER_TRIGGER: False,
    CONF_CODE_ARM: False,
    CONF_ARM_ON_ENTITIES: [],
    CONF_NOTIFY_UNAVAILABLE: True,
    CONF_UNAVAILABLE_DELAY: 60,
    CONF_DOCK_GRACE: 120,
    CONF_NOTIFY_SUPPRESSED: True,
    CONF_ANNOUNCE_ENTITIES: [],
    CONF_SPEAK_SERVICES: [],
    CONF_SOUND_DEVICES: [],
    CONF_SOUND: "amzn_sfx_scifi_alarm_04",
    CONF_VOLUME_PLAYERS: [],
    CONF_ALARM_VOLUME: 0.51,
    CONF_RESET_VOLUME: 0.2,
    CONF_RESET_AFTER: 10,
    CONF_TURN_ON: [],
    CONF_CLOSE_COVERS: [],
    CONF_CALL_TARGETS: [],
    CONF_CALL_ACK: True,
    CONF_CALL_WAIT: 50,
    CONF_CALL_LANGUAGE: "de",
    CONF_CALL_COOLDOWN: 180,
    CONF_PRESENCE_MODE: "wifi",
    CONF_WIFI_SENSORS: [],
    CONF_HOME_NETWORKS: [],
    CONF_PERSONS: [],
    CONF_QUIET: 10,
    CONF_PREWARN: 5,
    CONF_RETRY: 2,
    CONF_PRESENCE_STABLE: 2,
    CONF_DISARM_ON_UNLOCK: True,
    CONF_LOCK_ON_ARM: True,
    CONF_KIDS_RESET_AFTER: 10,
    CONF_KIDS_RESET_TIME: "03:00:00",
    CONF_NIGHT_OFF_TIME: "05:00:00",
    CONF_NIGHT_OFF_DAYS: ["mon", "tue", "wed", "thu", "fri"],
    CONF_NIGHT_TURN_ON: [],
    CONF_NIGHT_SOUND_DEVICES: [],
    CONF_NIGHT_VOLUME_PLAYERS: [],
    CONF_NIGHT_SPEAK: [],
    CONF_NIGHT_OFF_SPEAK: [],
    CONF_NIGHT_OFF_VOLUME: 0.3,
    CONF_NIGHT_OFF_VOLUME_PLAYERS: [],
    CONF_NIGHT_RESET_AFTER: 5,
    CONF_HINT_WINDOWS: [],
    CONF_HINT_DURATION: 30,
}

# Options without a default (entities or texts that may be empty).
OPTIONAL_TEXT_KEYS: Final = (
    CONF_VACUUM,
    CONF_VACUUM_CHARGING,
    CONF_FAULT_SENSOR,
    CONF_TEXT_TRIGGERED,
    CONF_TEXT_PENDING,
    CONF_CALL_ADDON,
    CONF_CALL_TTS,
    CONF_LOCK,
    CONF_LOCK_DOOR,
    CONF_NIGHT_DOOR,
    CONF_NIGHT_TAG,
    CONF_NIGHT_TEXT,
    CONF_HINT_DOOR,
    CONF_HINT_ENTITY,
)

# ---------- sensor (subentry)
CONF_NAME = "name"
CONF_ENTITY = "entity"
CONF_TYPE = "type"
CONF_USE_ENTRY = "use_entry_delay"
CONF_USE_EXIT = "use_exit_delay"
CONF_AUTO_BYPASS = "auto_bypass"
CONF_ALLOW_OPEN = "allow_open"
CONF_ONLY_UNAVAILABLE = "only_when_unavailable"
CONF_ARM_COVER = "arm_cover"
CONF_ARM_COVER_POSITION = "arm_cover_position"
CONF_CAMERA_PRESET = "camera_preset"

SENSOR_DEFAULTS: Final[dict[str, object]] = {
    CONF_ARM_COVER_POSITION: 20,
}

# ---------- camera (subentry)
CONF_PRIVACY = "privacy_switch"
CONF_PTZ = "ptz_select"
CONF_PTZ_HOME = "ptz_home_preset"
CONF_PRIVACY_DELAY = "privacy_delay"
CONF_RECORD_SWITCHES = "record_switches"
CONF_DETECT_SWITCHES = "detect_switches"
CONF_PERSON_SENSOR = "person_sensor"
CONF_PERSON_COUNT = "person_count_sensor"
CONF_PERSON_IMAGE = "person_image"
CONF_PERSON_PUSH = "person_push"

CAMERA_DEFAULTS: Final[dict[str, object]] = {
    CONF_PRIVACY_DELAY: 2,
    CONF_RECORD_SWITCHES: [],
    CONF_DETECT_SWITCHES: [],
    CONF_PERSON_PUSH: True,
}

# ---------- person (subentry)
CONF_PERSON_WIFI = "wifi_sensor"

# ---------- garage (subentry)
CONF_GARAGE_PANEL = "garage_panel"
CONF_GARAGE_NETWORKS = "garage_networks"
CONF_GARAGE_DELAY = "garage_arm_delay"
CONF_GARAGE_MOTION = "garage_motion"
CONF_GARAGE_TTS = "garage_tts_services"
CONF_GARAGE_TTS_TEXT = "garage_tts_text"
CONF_GARAGE_TTS_REPEAT = "garage_tts_repeat"

GARAGE_DEFAULTS: Final[dict[str, object]] = {
    CONF_GARAGE_NETWORKS: [],
    CONF_GARAGE_DELAY: 2,
    CONF_GARAGE_MOTION: [],
    CONF_GARAGE_TTS: [],
    CONF_GARAGE_TTS_REPEAT: 2,
}

# ---------- number ranges: (min, max, step, unit), used by the flows and the panel API
RANGES: Final[dict[str, tuple[float, float, float, str | None]]] = {
    CONF_ENTRY_DELAY: (0, 600, 1, "s"),
    CONF_EXIT_DELAY: (0, 600, 1, "s"),
    CONF_TRIGGER_TIME: (0, 7200, 1, "s"),
    CONF_UNAVAILABLE_DELAY: (0, 3600, 1, "s"),
    CONF_DOCK_GRACE: (0, 1800, 1, "s"),
    CONF_ALARM_VOLUME: (0, 1, 0.01, None),
    CONF_RESET_VOLUME: (0, 1, 0.01, None),
    CONF_RESET_AFTER: (0, 600, 1, "s"),
    CONF_CALL_WAIT: (0, 600, 1, "s"),
    CONF_CALL_COOLDOWN: (0, 3600, 1, "s"),
    CONF_QUIET: (0, 240, 1, "min"),
    CONF_PREWARN: (0, 60, 1, "min"),
    CONF_RETRY: (0, 120, 1, "min"),
    CONF_PRESENCE_STABLE: (0, 60, 1, "min"),
    CONF_NIGHT_RESET_AFTER: (0, 600, 1, "s"),
    CONF_NIGHT_OFF_VOLUME: (0, 1, 0.01, None),
    CONF_KIDS_RESET_AFTER: (0, 240, 1, "min"),
    CONF_HINT_DURATION: (1, 600, 1, "s"),
    CONF_ARM_COVER_POSITION: (0, 100, 1, "%"),
    CONF_PRIVACY_DELAY: (0, 60, 1, "min"),
    CONF_GARAGE_DELAY: (0, 60, 1, "min"),
    CONF_GARAGE_TTS_REPEAT: (0, 10, 1, None),
}
