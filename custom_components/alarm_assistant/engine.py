"""Event driven engine: the alarm panel and everything that belongs to it.

Nothing is polled. Every evaluation is caused by a state change of a configured
entity, a scanned tag or a calculated point in time (entry/exit delay, trigger
time, automatic arming, daily resets).
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Iterable
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import (
    CALLBACK_TYPE,
    Event,
    EventStateChangedData,
    HomeAssistant,
    State,
    callback,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import (
    async_track_point_in_time,
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.helpers.network import NoURLAvailableError, get_url
from homeassistant.helpers.start import async_at_started
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    CAMERA_DEFAULTS,
    CONF_ALARM_VOLUME,
    CONF_ALLOW_OPEN,
    CONF_ANNOUNCE_ENTITIES,
    CONF_ARM_COVER,
    CONF_ARM_COVER_POSITION,
    CONF_ARM_ON_ENTITIES,
    CONF_AUTO_BYPASS,
    CONF_CALL_ACK,
    CONF_CALL_ADDON,
    CONF_CALL_COOLDOWN,
    CONF_CALL_LANGUAGE,
    CONF_CALL_TARGETS,
    CONF_CALL_TTS,
    CONF_CALL_WAIT,
    CONF_CAMERA_PRESET,
    CONF_CLOSE_COVERS,
    CONF_CODE,
    CONF_CODE_ARM,
    CONF_DETECT_SWITCHES,
    CONF_DISARM_AFTER_TRIGGER,
    CONF_DISARM_ON_UNLOCK,
    CONF_DOCK_GRACE,
    CONF_ENTITY,
    CONF_ENTRY_DELAY,
    CONF_EXIT_DELAY,
    CONF_FAULT_SENSOR,
    CONF_GARAGE_DELAY,
    CONF_GARAGE_MOTION,
    CONF_GARAGE_NETWORKS,
    CONF_GARAGE_PANEL,
    CONF_GARAGE_TTS,
    CONF_GARAGE_TTS_REPEAT,
    CONF_GARAGE_TTS_TEXT,
    CONF_HINT_DOOR,
    CONF_HINT_DURATION,
    CONF_HINT_ENTITY,
    CONF_HINT_WINDOWS,
    CONF_HOME_NETWORKS,
    CONF_KIDS_RESET_AFTER,
    CONF_KIDS_RESET_TIME,
    CONF_LANGUAGE,
    CONF_LOCK,
    CONF_LOCK_DOOR,
    CONF_LOCK_ON_ARM,
    CONF_NIGHT_DOOR,
    CONF_NIGHT_OFF_DAYS,
    CONF_NIGHT_OFF_SPEAK,
    CONF_NIGHT_OFF_TIME,
    CONF_NIGHT_OFF_VOLUME,
    CONF_NIGHT_OFF_VOLUME_PLAYERS,
    CONF_NIGHT_RESET_AFTER,
    CONF_NIGHT_SOUND_DEVICES,
    CONF_NIGHT_SPEAK,
    CONF_NIGHT_TAG,
    CONF_NIGHT_TEXT,
    CONF_NIGHT_TURN_ON,
    CONF_NIGHT_VOLUME_PLAYERS,
    CONF_NOTIFY,
    CONF_NOTIFY_ADMIN,
    CONF_NOTIFY_ALARM,
    CONF_NOTIFY_SUPPRESSED,
    CONF_ONLY_UNAVAILABLE,
    CONF_PERSON_COUNT,
    CONF_PERSON_IMAGE,
    CONF_PERSON_PUSH,
    CONF_PERSON_SENSOR,
    CONF_PERSON_WIFI,
    CONF_PERSONS,
    CONF_PRESENCE_MODE,
    CONF_PRESENCE_STABLE,
    CONF_PREWARN,
    CONF_PRIVACY,
    CONF_PRIVACY_DELAY,
    CONF_PTZ,
    CONF_PTZ_HOME,
    CONF_QUIET,
    CONF_RECORD_SWITCHES,
    CONF_RESET_AFTER,
    CONF_RESET_VOLUME,
    CONF_RETRY,
    CONF_SOUND,
    CONF_SOUND_DEVICES,
    CONF_SPEAK_SERVICES,
    CONF_TEXT_PENDING,
    CONF_TEXT_TRIGGERED,
    CONF_TRIGGER_TIME,
    CONF_TURN_ON,
    CONF_TYPE,
    CONF_USE_ENTRY,
    CONF_USE_EXIT,
    CONF_VACUUM,
    CONF_VACUUM_CHARGING,
    CONF_VOLUME_PLAYERS,
    CONF_WIFI_SENSORS,
    DEFAULTS,
    DOMAIN,
    EVENT_LOGBOOK,
    GARAGE_DEFAULTS,
    LOGGER,
    NAME,
    SENSOR_DEFAULTS,
    STORAGE_VERSION,
    SUBENTRY_CAMERA,
    SUBENTRY_GARAGE,
    SUBENTRY_PERSON,
    SUBENTRY_SENSOR,
)
from .logic import auto_arm as aa
from .logic import camera as cam
from .logic import state_machine as sm
from .logic.call import CallSettings, dial_input, plan
from .logic.code import hash_code, is_legacy, verify_code
from .logic.misc import anyone_connected, join_names, next_daily, tag_action
from .logic.sensors import contact_counts, effective_state, motion_suppressed
from .messages import resolve_language, text

type AlarmConfigEntry = ConfigEntry[AlarmEngine]

INVALID = (STATE_UNAVAILABLE, STATE_UNKNOWN)
UNLOCKED_STATES = ("unlocked", "open", "opening")
STATE_JAMMED = "jammed"
# A lock that falls back to "unlocked" this soon after we locked it did not
# lock (bolt blocked); this is no unlocking by a person.
LOCK_SETTLE = 20
LOCK_RETRY = 10
# Short pauses inside reaction sequences (volume before sound, camera wake up).
PAUSE_SOUND = 2
PAUSE_CAMERA = 4
PAUSE_PTZ = 3
# A detection switch that comes back (Frigate restarted) or is switched by
# someone else is set again after this pause; at most a few times per window,
# so a switch that does not follow cannot cause a loop.
FRIGATE_RESYNC = 10
FRIGATE_RESYNC_MAX = 3
FRIGATE_RESYNC_WINDOW = timedelta(minutes=10)
# Every this many wrong codes in a row a message is sent.
WRONG_CODE_ALERT = 5
# Reaction sequences of an alarm that end with disarming.
ALARM_TASKS = ("call", "push", "siren", "announce", "announce_pending", "reactions")


async def _sleep(seconds: float) -> None:
    """Pause inside a reaction sequence (patched in tests)."""
    await asyncio.sleep(seconds)


def parse_time(value: Any, fallback: str = "00:00:00") -> time:
    """Parse 'HH:MM[:SS]'."""
    for candidate in (value, fallback):
        try:
            parts = [int(p) for p in str(candidate).split(":")]
            while len(parts) < 3:
                parts.append(0)
            return time(parts[0], parts[1], parts[2])
        except (TypeError, ValueError, IndexError):
            continue
    return time(0, 0)


@dataclass
class Sensor:
    """One alarm sensor (subentry)."""

    sensor_id: str
    conf: sm.SensorConf
    condition: str | None
    arm_cover: str | None
    arm_cover_position: int
    camera_preset: str | None


@dataclass
class Camera:
    """One camera (subentry) with its runtime tasks."""

    camera_id: str
    name: str
    conf: dict[str, Any]
    privacy_task: asyncio.Task | None = None
    ptz_task: asyncio.Task | None = None
    resyncs: list[datetime] = field(default_factory=list)


@dataclass
class Person:
    """A person whose phone tells by its Wi-Fi connection whether they are at home."""

    person_id: str
    name: str
    wifi_sensor: str


@dataclass
class Garage:
    """Garage cameras (subentry)."""

    garage_id: str
    name: str
    conf: dict[str, Any]


class AlarmEngine(DataUpdateCoordinator[None]):
    """The central engine of Alarm Assistant."""

    config_entry: AlarmConfigEntry

    def __init__(self, hass: HomeAssistant, entry: AlarmConfigEntry) -> None:
        super().__init__(hass, LOGGER, config_entry=entry, name=NAME)
        self.global_device_id: str | None = None
        self.sensors: dict[str, Sensor] = {}
        self.cameras: dict[str, Camera] = {}
        self.garages: dict[str, Garage] = {}
        self.persons: dict[str, Person] = {}
        # panel
        self.state: str = sm.DISARMED
        self.bypassed: list[str] = []
        self.trip_names: list[str] = []
        self.last_cause: str | None = None
        self.last_triggered: datetime | None = None
        self.disarmed_since: datetime | None = None
        self.tracker = sm.SensorTracker()
        # switches
        self.auto_arm_enabled = True
        self.kids_home = False
        self.night_door = False
        self.night_changed: datetime | None = None
        self.live_mode = False
        self.garage_auto = True
        # automatic arming
        self.away_since: datetime | None = None
        self.last_motion: datetime | None = None
        self.motion_active = False
        self.prewarn_until: datetime | None = None
        # door lock: when we last sent "lock" and whether we already retried
        self.lock_sent: datetime | None = None
        self.lock_retried = False
        # call
        self.call_block_until: datetime | None = None
        self.call_acked = False
        self.missing: list[str] = []
        # test alarm: reactions switched off (None: no test)
        self.test: set[str] | None = None
        self.test_last: list[str] = []
        self.wrong_codes = 0
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}"
        )
        self._unsubs: list[CALLBACK_TYPE] = []
        self._timers: dict[str, CALLBACK_TYPE] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._build()
        self._loaded = self._config_snapshot()

    # ------------------------------------------------------------------ config

    @property
    def opts(self) -> dict[str, Any]:
        return {**DEFAULTS, **self.config_entry.options}

    def opt(self, key: str) -> Any:
        return self.opts.get(key, DEFAULTS.get(key))

    def opt_list(self, key: str) -> list[str]:
        return [str(v) for v in (self.opt(key) or []) if str(v).strip()]

    @property
    def language(self) -> str:
        return resolve_language(self.opt(CONF_LANGUAGE), self.hass.config.language)

    def t(self, key: str, **kwargs: Any) -> str:
        return text(self.language, key, **kwargs)

    @property
    def code_required(self) -> bool:
        return bool(self.opt(CONF_CODE))

    @property
    def code_arm_required(self) -> bool:
        return self.code_required and bool(self.opt(CONF_CODE_ARM))

    @property
    def auto_arm_configured(self) -> bool:
        if self.opt(CONF_PRESENCE_MODE) == aa.MODE_PERSONS:
            return bool(self.opt_list(CONF_PERSONS))
        return bool(self.wifi_sensors()) and bool(self.opt_list(CONF_HOME_NETWORKS))

    @property
    def night_door_configured(self) -> bool:
        return bool(self.opt(CONF_NIGHT_DOOR))

    @property
    def call_configured(self) -> bool:
        return bool(self.opt(CONF_CALL_ADDON)) and bool(self.opt_list(CONF_CALL_TARGETS))

    def _config_snapshot(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Configuration the engine was built from (without the code hash)."""
        options = {k: v for k, v in self.config_entry.options.items() if k != CONF_CODE}
        subentries = {
            sub_id: (sub.subentry_type, sub.title, dict(sub.data))
            for sub_id, sub in self.config_entry.subentries.items()
        }
        return options, subentries

    def config_changed(self) -> bool:
        """Something besides the code changed (then the entry is reloaded)."""
        return self._config_snapshot() != self._loaded

    def _build(self) -> None:
        for sub_id, sub in self.config_entry.subentries.items():
            data = dict(sub.data)
            if sub.subentry_type == SUBENTRY_SENSOR:
                data = {**SENSOR_DEFAULTS, **data}
                defaults = sm.type_defaults(str(data.get(CONF_TYPE, sm.TYPE_WINDOW)))
                self.sensors[sub_id] = Sensor(
                    sensor_id=sub_id,
                    conf=sm.SensorConf(
                        entity_id=str(data[CONF_ENTITY]),
                        name=sub.title,
                        type=str(data.get(CONF_TYPE, sm.TYPE_WINDOW)),
                        entry_delay=bool(data.get(CONF_USE_ENTRY, defaults["entry_delay"])),
                        exit_delay=bool(data.get(CONF_USE_EXIT, defaults["exit_delay"])),
                        auto_bypass=bool(data.get(CONF_AUTO_BYPASS, defaults["auto_bypass"])),
                        allow_open=bool(data.get(CONF_ALLOW_OPEN, defaults["allow_open"])),
                    ),
                    condition=data.get(CONF_ONLY_UNAVAILABLE) or None,
                    arm_cover=data.get(CONF_ARM_COVER) or None,
                    arm_cover_position=_as_int(data.get(CONF_ARM_COVER_POSITION)),
                    camera_preset=str(data.get(CONF_CAMERA_PRESET) or "").strip() or None,
                )
            elif sub.subentry_type == SUBENTRY_CAMERA:
                self.cameras[sub_id] = Camera(sub_id, sub.title, {**CAMERA_DEFAULTS, **data})
            elif sub.subentry_type == SUBENTRY_GARAGE:
                self.garages[sub_id] = Garage(sub_id, sub.title, {**GARAGE_DEFAULTS, **data})
            elif sub.subentry_type == SUBENTRY_PERSON and data.get(CONF_PERSON_WIFI):
                self.persons[sub_id] = Person(sub_id, sub.title, str(data[CONF_PERSON_WIFI]))

    def wifi_sensors(self) -> list[str]:
        """Wi-Fi sensors of the persons and the additional ones from the options."""
        sensors = [p.wifi_sensor for p in self.persons.values()]
        sensors += [str(v) for v in (self.opt(CONF_WIFI_SENSORS) or []) if str(v).strip()]
        return list(dict.fromkeys(sensors))

    def person_home(self, person: Person) -> bool:
        """The phone of the person is connected to a home network."""
        return not aa.away_by_wifi(
            [self._value(person.wifi_sensor)], self.opt_list(CONF_HOME_NETWORKS)
        )

    def sensor_by_entity(self, entity_id: str) -> list[Sensor]:
        return [s for s in self.sensors.values() if s.conf.entity_id == entity_id]

    @property
    def motion_sensors(self) -> list[Sensor]:
        return [s for s in self.sensors.values() if s.conf.type == sm.TYPE_MOTION]

    # ------------------------------------------------------------------ setup

    async def _async_update_data(self) -> None:
        return None

    async def async_setup(self) -> None:
        """Load stored state, register listeners and timers."""
        stored = await self._store.async_load() or {}
        self._restore(stored)
        now = dt_util.utcnow()
        for sensor in self.sensors.values():
            self.tracker.update(sensor.conf.entity_id, self.effective(sensor))
        self.motion_active = self._motion_now()
        if self.motion_active:
            self.last_motion = now
        elif self.last_motion is None:
            self.last_motion = self._motion_last_changed()
        self.away_since = self._initial_away_since() if self._away_now() else None
        self._register_listeners()
        self._schedule_daily(now)
        self._schedule_dock_grace()
        self._unsubs.append(async_at_started(self.hass, self._async_started))

    async def _async_started(self, _hass: HomeAssistant) -> None:
        """Home Assistant runs: check entities, start the time based parts."""
        self._check_missing()
        now = dt_util.utcnow()
        self._auto_arm_check(now)
        for camera in self.cameras.values():
            self._apply_frigate(camera)
        for garage in self.garages.values():
            self._garage_check(garage, now, startup=True)

    def _restore(self, stored: dict[str, Any]) -> None:
        self.state = sm.restored_state(stored.get("state"))
        if self.state != sm.DISARMED:
            self.bypassed = [str(e) for e in stored.get("bypassed") or []]
            if stored.get("test") is not None:
                self.test = {str(k) for k in stored["test"]}
        self.test_last = [str(k) for k in stored.get("test_last") or []]
        self.last_cause = stored.get("last_cause")
        self.last_triggered = _to_datetime(stored.get("last_triggered"))
        self.disarmed_since = _to_datetime(stored.get("disarmed_since"))
        self.auto_arm_enabled = bool(stored.get("auto_arm", True))
        self.kids_home = bool(stored.get("kids_home", False))
        self.night_door = bool(stored.get("night_door", False))
        self.night_changed = _to_datetime(stored.get("night_changed"))
        self.live_mode = bool(stored.get("live_mode", False))
        self.garage_auto = bool(stored.get("garage_auto", True))
        self.last_motion = _to_datetime(stored.get("last_motion"))

    def _data_to_save(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "bypassed": self.bypassed,
            "test": sorted(self.test) if self.test is not None else None,
            "test_last": self.test_last,
            "last_cause": self.last_cause,
            "last_triggered": _iso(self.last_triggered),
            "disarmed_since": _iso(self.disarmed_since),
            "auto_arm": self.auto_arm_enabled,
            "kids_home": self.kids_home,
            "night_door": self.night_door,
            "night_changed": _iso(self.night_changed),
            "live_mode": self.live_mode,
            "garage_auto": self.garage_auto,
            "last_motion": _iso(self.last_motion),
        }

    def _save(self) -> None:
        self._store.async_delay_save(self._data_to_save, 2)

    def _changed(self) -> None:
        self._save()
        self.async_update_listeners()

    async def async_shutdown(self) -> None:
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        for unsub in self._timers.values():
            unsub()
        self._timers.clear()
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()
        for camera in self.cameras.values():
            for task in (camera.privacy_task, camera.ptz_task):
                if task:
                    task.cancel()
        await self._store.async_save(self._data_to_save())
        await super().async_shutdown()

    def _configured_entities(self) -> set[str]:
        """Entity ids and services referenced by the configuration."""
        refs: set[str] = set()
        skip = {CONF_CALL_ADDON, CONF_CALL_TARGETS, CONF_HOME_NETWORKS, CONF_NIGHT_TAG}
        for key, value in self.opts.items():
            if key in skip or key in (CONF_SOUND_DEVICES, CONF_NIGHT_SOUND_DEVICES):
                continue
            values = value if isinstance(value, list) else [value]
            refs.update(str(v) for v in values if _looks_like_entity(v))
        for sub in self.config_entry.subentries.values():
            for key, value in sub.data.items():
                if key in (CONF_GARAGE_NETWORKS, CONF_CAMERA_PRESET, CONF_PTZ_HOME):
                    continue
                values = value if isinstance(value, list) else [value]
                refs.update(str(v) for v in values if _looks_like_entity(v))
        return refs

    def _check_missing(self) -> None:
        registry = er.async_get(self.hass)
        missing = []
        for ref in sorted(self._configured_entities()):
            domain, _, name = ref.partition(".")
            if self.hass.states.get(ref) is not None or registry.async_get(ref) is not None:
                continue
            if self.hass.services.has_service(domain, name):
                continue
            missing.append(ref)
        self.missing = missing
        if missing:
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                "missing_entities",
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key="missing_entities",
                translation_placeholders={"entities": ", ".join(missing)},
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, "missing_entities")

    # ------------------------------------------------------------------ listeners

    def _track(
        self, entities: Iterable[str | None], handler: Callable[[Event[EventStateChangedData]], Any]
    ) -> None:
        ids = sorted({e for e in entities if e})
        if ids:
            self._unsubs.append(async_track_state_change_event(self.hass, ids, handler))

    def _register_listeners(self) -> None:
        sensor_inputs = {s.conf.entity_id for s in self.sensors.values()}
        sensor_inputs |= {s.condition for s in self.sensors.values() if s.condition}
        sensor_inputs |= {self.opt(CONF_VACUUM), self.opt(CONF_FAULT_SENSOR)}
        self._track(sensor_inputs, self._on_sensor_input)
        self._track([self.opt(CONF_FAULT_SENSOR)], self._on_fault)
        presence = (
            self.opt_list(CONF_PERSONS)
            if self.opt(CONF_PRESENCE_MODE) == aa.MODE_PERSONS
            else self.wifi_sensors()
        )
        self._track(presence, self._on_presence)
        self._track([self.opt(CONF_LOCK)], self._on_lock)
        self._track([self.opt(CONF_NIGHT_DOOR)], self._on_night_door_sensor)
        self._track([self.opt(CONF_HINT_DOOR)], self._on_hint_door)
        if self.opt(CONF_NIGHT_TAG):
            self._unsubs.append(self.hass.bus.async_listen("tag_scanned", self._on_tag))
        if self.cameras:
            cam_inputs = {self.opt(CONF_VACUUM), self.opt(CONF_VACUUM_CHARGING)}
            self._track(cam_inputs, self._on_camera_input)
            self._track(
                [c.conf.get(CONF_PERSON_SENSOR) for c in self.cameras.values()], self._on_person
            )
            self._track(
                [s for c in self.cameras.values() for s in self._frigate_switches(c)],
                self._on_frigate_switch,
            )
        if self.garages:
            self._track(self.wifi_sensors(), self._on_garage_wifi)
            self._track(
                [m for g in self.garages.values() for m in g.conf.get(CONF_GARAGE_MOTION) or []],
                self._on_garage_motion,
            )

    def _schedule_daily(self, now: datetime) -> None:
        reset = parse_time(self.opt(CONF_KIDS_RESET_TIME), "03:00")
        self._unsubs.append(
            async_track_time_change(
                self.hass,
                self._on_kids_nightly_reset,
                hour=reset.hour,
                minute=reset.minute,
                second=reset.second,
            )
        )
        self._schedule_night_off(now)

    def _schedule(
        self, key: str, when: datetime | None, handler: Callable[[datetime], Any]
    ) -> None:
        """Run ``handler`` at ``when`` (replaces a timer with the same key)."""
        self._cancel(key)
        if when is None:
            return

        @callback
        def fire(now: datetime) -> None:
            self._timers.pop(key, None)
            handler(now)

        self._timers[key] = async_track_point_in_time(self.hass, fire, when)

    def _stop_tasks(self, keys: Iterable[str]) -> list[str]:
        """Cancel running reaction sequences, return the keys that were running."""
        stopped = []
        for key in keys:
            task = self._tasks.pop(key, None)
            if task is not None and not task.done():
                task.cancel()
                stopped.append(key)
        return stopped

    def _cancel(self, key: str) -> None:
        if (old := self._timers.pop(key, None)) is not None:
            old()

    def _task(self, key: str, coro: Coroutine[Any, Any, Any], restart: bool = False) -> None:
        """Run a reaction sequence in the background (one per key)."""
        running = self._tasks.get(key)
        if running is not None and not running.done():
            if not restart:
                coro.close()
                return
            running.cancel()
        task = self.config_entry.async_create_background_task(self.hass, coro, f"{DOMAIN}_{key}")
        self._tasks[key] = task

    # ------------------------------------------------------------------ helpers

    def _state(self, entity_id: str | None) -> State | None:
        return self.hass.states.get(entity_id) if entity_id else None

    def _value(self, entity_id: str | None) -> str | None:
        state = self._state(entity_id)
        return state.state if state else None

    def _name(self, entity_id: str) -> str:
        state = self._state(entity_id)
        return state.name if state else entity_id

    def _log(self, key: str, **kwargs: Any) -> None:
        message = self._mark(self.t(key, **kwargs))
        LOGGER.debug(message)
        data: dict[str, Any] = {"name": NAME, "message": message}
        panel = er.async_get(self.hass).async_get_entity_id(
            "alarm_control_panel", DOMAIN, f"{self.config_entry.entry_id}_panel"
        )
        if panel:
            data["entity_id"] = panel
        self.hass.bus.async_fire(EVENT_LOGBOOK, data)

    async def _async_call(self, domain: str, service: str, data: dict[str, Any]) -> None:
        try:
            await self.hass.services.async_call(domain, service, data, blocking=True)
        except (HomeAssistantError, ValueError) as err:
            LOGGER.warning("%s.%s failed: %s", domain, service, err)
        except Exception:  # one failing step must not stop the alarm
            LOGGER.exception("%s.%s failed", domain, service)

    async def _async_notify(
        self, targets: Iterable[str], title: str, message: str, data: dict[str, Any] | None = None
    ) -> None:
        for target in targets:
            domain, _, service = str(target).partition(".")
            if not service:
                domain, service = "notify", domain
            payload: dict[str, Any] = {"message": message}
            if title:
                payload["title"] = title
            if data:
                payload["data"] = data
            await self._async_call(domain, service, payload)

    def _notify(self, targets: Iterable[str], title: str, message: str, **kw: Any) -> None:
        targets = list(targets)
        if targets:
            self.hass.async_create_task(self._async_notify(targets, title, message, **kw))

    async def _async_announce(self, message: str, title: str) -> None:
        for entity_id in self._filter("announce", self.opt_list(CONF_ANNOUNCE_ENTITIES)):
            await self._async_call(
                "notify",
                "send_message",
                {"entity_id": entity_id, "message": message, "title": title},
            )

    async def _async_speak(self, services: Iterable[str], message: str) -> None:
        for target in services:
            domain, _, service = str(target).partition(".")
            if not service:
                domain, service = "notify", domain
            await self._async_call(domain, service, {"message": message})

    async def _async_volume(self, players: list[str], volume: float) -> None:
        if players:
            await self._async_call(
                "media_player", "volume_set", {"entity_id": players, "volume_level": volume}
            )

    async def _async_sound(self, devices: list[str], sound: str) -> None:
        for device_id in devices:
            await self._async_call(
                "alexa_devices", "send_sound", {"sound": sound, "device_id": device_id}
            )

    async def _async_turn_on(
        self, entities: list[str], light_brightness: int | None = None
    ) -> None:
        for entity_id in entities:
            if entity_id.startswith("light.") and light_brightness is not None:
                await self._async_call(
                    "light", "turn_on", {"entity_id": entity_id, "brightness_pct": light_brightness}
                )
            else:
                await self._async_call("homeassistant", "turn_on", {"entity_id": entity_id})

    # ------------------------------------------------------------------ sensors

    def motion_suppressed(self) -> bool:
        vacuum = self._state(self.opt(CONF_VACUUM))
        ago = None
        if vacuum is not None:
            ago = (dt_util.utcnow() - vacuum.last_changed).total_seconds()
        return motion_suppressed(
            vacuum.state if vacuum else None,
            ago,
            self._value(self.opt(CONF_FAULT_SENSOR)),
            float(self.opt(CONF_DOCK_GRACE)),
        )

    def counts(self, sensor: Sensor) -> bool:
        if sensor.conf.type == sm.TYPE_MOTION:
            return not self.motion_suppressed()
        if sensor.condition:
            return contact_counts(self._value(sensor.condition))
        return True

    def effective(self, sensor: Sensor) -> str | None:
        return effective_state(self._value(sensor.conf.entity_id), self.counts(sensor))

    def open_sensors(self) -> list[Sensor]:
        return [s for s in self.sensors.values() if self.effective(s) == sm.ON]

    def _motion_now(self) -> bool:
        return any(self.effective(s) == sm.ON for s in self.motion_sensors)

    def _motion_last_changed(self) -> datetime | None:
        times = [
            state.last_changed
            for s in self.motion_sensors
            if (state := self._state(s.conf.entity_id)) is not None
        ]
        return max(times) if times else None

    def _schedule_dock_grace(self) -> None:
        """Re-evaluate motion when the grace time after docking is over."""
        vacuum = self._state(self.opt(CONF_VACUUM))
        if vacuum is None or vacuum.state != "docked":
            self._cancel("dock_grace")
            return
        end = vacuum.last_changed + timedelta(seconds=float(self.opt(CONF_DOCK_GRACE)))
        if end > dt_util.utcnow():
            self._schedule("dock_grace", end, lambda now: self._evaluate_sensors(now))

    @callback
    def _on_sensor_input(self, event: Event[EventStateChangedData]) -> None:
        now = dt_util.utcnow()
        entity_id = event.data["entity_id"]
        if entity_id == self.opt(CONF_VACUUM):
            self._schedule_dock_grace()
        new = event.data["new_state"]
        old = event.data["old_state"]
        if (
            new is not None
            and new.state == sm.ON
            and (old is None or old.state != sm.ON)
            and any(s.conf.type == sm.TYPE_MOTION for s in self.sensor_by_entity(entity_id))
        ):
            self._raw_motion(entity_id)
        self._evaluate_sensors(now)

    def _evaluate_sensors(self, now: datetime) -> None:
        for sensor in self.sensors.values():
            if self.tracker.update(sensor.conf.entity_id, self.effective(sensor)):
                self._handle_trip(sensor, now)
        motion = self._motion_now()
        if motion or self.motion_active:
            self.last_motion = now
        if motion != self.motion_active:
            self.motion_active = motion
            self._auto_arm_check(now)
        self._changed()

    def _raw_motion(self, entity_id: str) -> None:
        """A motion sensor reported motion (before filtering)."""
        fault = self.opt(CONF_FAULT_SENSOR)
        if (
            fault
            and self._value(fault) == sm.ON
            and self.state in (sm.ARMED_AWAY, sm.PENDING, sm.TRIGGERED)
            and self.opt(CONF_NOTIFY_SUPPRESSED)
        ):
            self._notify(
                self._push(CONF_NOTIFY_ADMIN),
                self._mark(self.t("title_suppressed")),
                self._mark(
                    self.t(
                        "push_suppressed",
                        sensor=self._name(entity_id),
                        fault=self._name(fault),
                        state=self.state,
                    )
                ),
            )
        if self.state == sm.ARMED_AWAY:
            preset = next(
                (s.camera_preset for s in self.sensor_by_entity(entity_id) if s.camera_preset), None
            )
            for camera in self._cameras():
                self._camera_task(camera, "ptz", self._async_ptz(camera, preset))

    @callback
    def _on_fault(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        if new is None or new.state != sm.ON or (old is not None and old.state == sm.ON):
            return
        self._notify(
            self._push(CONF_NOTIFY_ADMIN),
            self._mark(self.t("title_fault")),
            self._mark(self.t("push_fault", sensor=new.name)),
        )

    # ------------------------------------------------------------------ panel

    async def async_check_code(self, code: str | None, arming: bool) -> bool:
        if not self.code_required or (arming and not self.code_arm_required):
            return True
        stored = str(self.opt(CONF_CODE))
        if code is None or not await self.hass.async_add_executor_job(
            verify_code, str(code), stored
        ):
            self._wrong_code()
            return False
        self.wrong_codes = 0
        if is_legacy(stored):
            # hash of an older version: store the code with a salt now
            new = await self.hass.async_add_executor_job(hash_code, str(code))
            self.hass.config_entries.async_update_entry(
                self.config_entry, options={**self.config_entry.options, CONF_CODE: new}
            )
        return True

    def _wrong_code(self) -> None:
        self.wrong_codes += 1
        if self.wrong_codes % WRONG_CODE_ALERT:
            return
        self._log("log_wrong_code", count=self.wrong_codes)
        self._notify(
            self._push(CONF_NOTIFY),
            self._mark(self.t("title_wrong_code")),
            self._mark(self.t("push_wrong_code", count=self.wrong_codes)),
        )

    # ------------------------------------------------------------------ test alarm

    @property
    def test_mode(self) -> bool:
        return self.test is not None

    def _filter(self, group: str, items: Iterable[str]) -> list[str]:
        """Reaction targets without the ones switched off for a test alarm."""
        values = [str(i) for i in items]
        if self.test is None:
            return values
        if group in self.test:
            return []
        return [v for v in values if f"{group}:{v}" not in self.test]

    def _push(self, key: str) -> list[str]:
        return self._filter("push", self.opt_list(key))

    def _cameras(self) -> list[Camera]:
        allowed = set(self._filter("camera", self.cameras))
        return [c for c in self.cameras.values() if c.camera_id in allowed]

    def _mark(self, message: str) -> str:
        """Written messages of a test alarm start with [TEST]."""
        return self.t("test_prefix") + message if self.test is not None else message

    def _spoken(self, message: str) -> str:
        """Spoken messages of a test alarm say that it is a test."""
        return self.t("test_spoken") + message if self.test is not None else message

    def arm_test(self, disabled: Iterable[str]) -> sm.ArmCheck:
        """Arm as a test: the given reactions (group or group:target) stay off."""
        self.test_last = sorted({str(d) for d in disabled})
        return self.arm(test=self.test_last)

    def simulate_trigger(self) -> bool:
        """Trigger a test alarm without a sensor (only in test mode)."""
        if self.test is None or self.state not in (sm.ARMED_AWAY, sm.PENDING):
            return False
        self.trip_names.append(self.t("test_cause"))
        self._trigger(dt_util.utcnow())
        self._changed()
        return True

    # ------------------------------------------------------------------ arming

    def arm(
        self, force: bool = False, automatic: bool = False, test: Iterable[str] | None = None
    ) -> sm.ArmCheck:
        """Arm away. Returns the check result (not ok: nothing changed)."""
        if self.state != sm.DISARMED:
            return sm.ArmCheck()
        self.test = {str(t) for t in test} if test is not None else None
        now = dt_util.utcnow()
        open_ids = {s.conf.entity_id for s in self.open_sensors()}
        exit_delay = float(self.opt(CONF_EXIT_DELAY))
        check = sm.check_arm(
            [s.conf for s in self.sensors.values()], open_ids, exit_delay, force=force
        )
        if not check.ok:
            names = join_names((self.sensor_name(e) for e in check.blocking), self.t("unknown"))
            self._log("log_arm_failed", sensors=names)
            self._notify(
                self._push(CONF_NOTIFY),
                self._mark(self.t("title_arm_failed")),
                self._mark(self.t("push_arm_failed", sensors=names)),
            )
            self.test = None
            return check
        self._cancel_prewarn()
        self.bypassed = list(check.bypassed)
        self.trip_names = []
        self.disarmed_since = None
        self._arm_covers()
        for camera in self._cameras():
            self._camera_task(camera, "privacy", self._async_camera_armed(camera))
        if exit_delay > 0:
            self.state = sm.ARMING
            self._log("log_arming")
            self._schedule("exit", now + timedelta(seconds=exit_delay), self._exit_over)
        else:
            self._armed(automatic)
        self._camera_rules_changed()
        self._changed()
        return check

    def sensor_name(self, entity_id: str) -> str:
        sensors = self.sensor_by_entity(entity_id)
        return sensors[0].conf.name if sensors else self._name(entity_id)

    def _exit_over(self, now: datetime) -> None:
        if self.state != sm.ARMING:
            return
        self._armed(False)
        # sensors with exit delay that are still open count as a trip
        for sensor in self.open_sensors():
            if sensor.conf.exit_delay and sensor.conf.entity_id not in self.bypassed:
                self._handle_trip(sensor, now, from_state=sm.ARMED_AWAY)
        self._changed()

    def _armed(self, automatic: bool) -> None:
        self.state = sm.ARMED_AWAY
        if self.bypassed:
            names = join_names((self.sensor_name(e) for e in self.bypassed), "")
            self._log("log_armed_bypass", sensors=names)
            self._notify(
                self._push(CONF_NOTIFY),
                self._mark(self.t("title_armed")),
                self._mark(self.t("push_bypassed", sensors=names)),
            )
        else:
            self._log("log_auto_armed" if automatic else "log_armed")
        self.lock_retried = False
        self._lock_door()
        for entity_id in self._filter("armed_on", self.opt_list(CONF_ARM_ON_ENTITIES)):
            self.hass.async_create_task(
                self._async_call("homeassistant", "turn_on", {"entity_id": entity_id})
            )

    def _arm_covers(self) -> None:
        """Conditional contacts that are open but do not count: move their cover."""
        for sensor in self.sensors.values():
            if not sensor.arm_cover or not sensor.condition:
                continue
            if not self._filter("arm_cover", [sensor.arm_cover]):
                continue
            if self._value(sensor.conf.entity_id) != sm.ON or self.counts(sensor):
                continue
            cover = self._state(sensor.arm_cover)
            position = cover.attributes.get("current_position") if cover else None
            try:
                current = int(position) if position is not None else -1
            except (TypeError, ValueError):
                current = -1
            if current > sensor.arm_cover_position:
                self._log("log_cover", name=sensor.conf.name, position=sensor.arm_cover_position)
                self.hass.async_create_task(
                    self._async_call(
                        "cover",
                        "set_cover_position",
                        {"entity_id": sensor.arm_cover, "position": sensor.arm_cover_position},
                    )
                )

    def _lock_door(self) -> None:
        lock = self.opt(CONF_LOCK)
        if not lock or not self.opt(CONF_LOCK_ON_ARM) or self.kids_home:
            return
        if not self._filter("lock", [lock]):
            return
        door = self.opt(CONF_LOCK_DOOR)
        if door and self._value(door) != sm.OFF:
            return
        if self._value(lock) in ("locked", "locking", STATE_UNAVAILABLE, STATE_UNKNOWN, None):
            return
        self._log("log_locked")
        self.lock_sent = dt_util.utcnow()
        self.hass.async_create_task(self._async_call("lock", "lock", {"entity_id": lock}))

    def _lock_bounced(self, old: State | None, new: State) -> bool:
        """True if the lock fell back to unlocked right after our lock command."""
        if self.lock_sent is None or new.state != "unlocked":
            return False
        if old is None or old.state not in ("locking", "locked"):
            return False
        return dt_util.utcnow() - self.lock_sent <= timedelta(seconds=LOCK_SETTLE)

    def _lock_failed(self) -> None:
        self.lock_sent = None
        self._log("log_lock_failed")
        retry = not self.lock_retried
        self._notify(
            self._push(CONF_NOTIFY),
            self._mark(self.t("title_lock_failed")),
            self._mark(self.t("push_lock_retry" if retry else "push_lock_failed")),
        )
        if retry:
            self.lock_retried = True
            self._schedule(
                "lock_retry",
                dt_util.utcnow() + timedelta(seconds=LOCK_RETRY),
                lambda _now: self._lock_door() if self.state in sm.ARMED_STATES else None,
            )

    def disarm(self, by_lock: bool = False) -> None:
        if self.state == sm.DISARMED:
            return
        self.lock_sent = None
        for key in ("exit", "entry", "trigger_end", "lock_retry"):
            self._cancel(key)
        self.state = sm.DISARMED
        self.bypassed = []
        self.trip_names = []
        self.disarmed_since = dt_util.utcnow()
        self._log("log_disarmed_lock" if by_lock else "log_disarmed")
        # calls, sound and announcements of a running alarm end with disarming
        if "siren" in self._stop_tasks(ALARM_TASKS):
            players = self._filter("volume", self.opt_list(CONF_VOLUME_PLAYERS))
            if players:
                self._task(
                    "volume_reset", self._async_volume(players, float(self.opt(CONF_RESET_VOLUME)))
                )
        for entity_id in self._filter("armed_on", self.opt_list(CONF_ARM_ON_ENTITIES)):
            self.hass.async_create_task(
                self._async_call("homeassistant", "turn_off", {"entity_id": entity_id})
            )
        for camera in self._cameras():
            self._camera_task(camera, "privacy", self._async_camera_disarmed(camera))
        self.test = None
        self._camera_rules_changed()
        self._schedule(
            "auto_arm_retry",
            self.disarmed_since + timedelta(minutes=float(self.opt(CONF_RETRY))),
            self._auto_arm_check,
        )
        self._changed()

    def _handle_trip(self, sensor: Sensor, now: datetime, from_state: str | None = None) -> None:
        if sensor.conf.entity_id in self.bypassed:
            return
        entry_delay = float(self.opt(CONF_ENTRY_DELAY))
        new = sm.next_state_on_trip(from_state or self.state, sensor.conf, entry_delay)
        if new is None:
            return
        self.trip_names.append(sensor.conf.name)
        if new == sm.PENDING:
            self.state = sm.PENDING
            self._log("log_pending", sensor=sensor.conf.name)
            self._schedule("entry", now + timedelta(seconds=entry_delay), self._entry_over)
            text_pending = self._spoken(self.opt(CONF_TEXT_PENDING) or self.t("announce_pending"))
            self._task(
                "announce_pending", self._async_announce(text_pending, self.t("title_pending"))
            )
        else:
            self._trigger(now)
        self._changed()

    def _entry_over(self, now: datetime) -> None:
        if self.state == sm.PENDING:
            self._trigger(now)
            self._changed()

    def cause(self) -> str:
        names = list(self.trip_names)
        for camera in self.cameras.values():
            person = camera.conf.get(CONF_PERSON_SENSOR)
            count = camera.conf.get(CONF_PERSON_COUNT)
            if (person and self._value(person) == sm.ON) or _as_int(self._value(count)) > 0:
                names.append(self._name(person) if person else camera.name)
        return join_names(names, self.t("unknown"))

    def _trigger(self, now: datetime) -> None:
        self._cancel("entry")
        self.state = sm.TRIGGERED
        cause = self.cause()
        self.last_cause = cause
        self.last_triggered = now
        self._log("log_triggered", cause=cause)
        self._schedule(
            "trigger_end",
            now + timedelta(seconds=float(self.opt(CONF_TRIGGER_TIME))),
            self._trigger_over,
        )
        text_triggered = self._spoken(self.opt(CONF_TEXT_TRIGGERED) or self.t("announce_triggered"))
        self._task("announce", self._async_announce(text_triggered, self.t("title_alarm")))
        self._task(
            "siren",
            self._async_siren(
                players=self._filter("volume", self.opt_list(CONF_VOLUME_PLAYERS)),
                volume=float(self.opt(CONF_ALARM_VOLUME)),
                reset_volume=float(self.opt(CONF_RESET_VOLUME)),
                reset_after=float(self.opt(CONF_RESET_AFTER)),
                devices=self._filter("sound", self.opt_list(CONF_SOUND_DEVICES)),
                speak=self._filter("speak", self.opt_list(CONF_SPEAK_SERVICES)),
                message=text_triggered,
            ),
        )
        self._task("reactions", self._async_reactions())
        # the cool down only blocks a new call chain, the push is always sent
        call = self.call_block_until is None or now >= self.call_block_until
        if call and self.call_configured:
            self.call_block_until = now + timedelta(seconds=float(self.opt(CONF_CALL_COOLDOWN)))
        self._task(
            "call" if call else "push", self._async_alarm_messages(cause, call), restart=True
        )

    def _trigger_over(self, now: datetime) -> None:
        if self.state != sm.TRIGGERED:
            return
        self._log("log_trigger_end")
        if sm.state_after_trigger(bool(self.opt(CONF_DISARM_AFTER_TRIGGER))) == sm.DISARMED:
            self.disarm()
            return
        self.state = sm.ARMED_AWAY
        self.trip_names = []
        self._changed()

    async def _async_reactions(self) -> None:
        await self._async_turn_on(self._filter("lights", self.opt_list(CONF_TURN_ON)))
        for cover in self._filter("covers", self.opt_list(CONF_CLOSE_COVERS)):
            await self._async_call("cover", "close_cover", {"entity_id": cover})

    async def _async_siren(
        self,
        *,
        players: list[str],
        volume: float,
        reset_volume: float,
        reset_after: float,
        devices: list[str],
        speak: list[str],
        message: str,
        turn_on: list[str] | None = None,
    ) -> None:
        """Volume up, alarm sound, spoken message, volume back."""
        await self._async_volume(players, volume)
        if turn_on:
            await self._async_turn_on(turn_on, light_brightness=100)
        if players or turn_on:
            await _sleep(PAUSE_SOUND)
        await self._async_sound(devices, str(self.opt(CONF_SOUND)))
        if devices:
            await _sleep(PAUSE_SOUND)
        await self._async_speak(speak, message)
        if players:
            await _sleep(reset_after)
            await self._async_volume(players, reset_volume)

    def _ack_entity(self) -> str | None:
        return er.async_get(self.hass).async_get_entity_id(
            "button", DOMAIN, f"{self.config_entry.entry_id}_call_acknowledge"
        )

    async def _async_alarm_messages(self, cause: str, call_allowed: bool = True) -> None:
        """Phone call chain and push messages (the first call starts before the push)."""
        targets = self._filter("call", self.opt_list(CONF_CALL_TARGETS))
        call = call_allowed and self.call_configured and bool(targets)
        message = self._mark(self.t("push_triggered", cause=cause))
        push = message + (self.t("push_call_started") if call else "")
        title = self._mark(self.t("title_alarm"))
        if not call:
            await self._async_notify(self._push(CONF_NOTIFY), title, push)
            await self._async_notify(self._push(CONF_NOTIFY_ALARM), title, message)
            return
        settings = CallSettings(
            addon=str(self.opt(CONF_CALL_ADDON)),
            targets=tuple(targets),
            acknowledge=bool(self.opt(CONF_CALL_ACK)),
            wait=float(self.opt(CONF_CALL_WAIT)),
            platform=str(self.opt(CONF_CALL_TTS) or ""),
            language=str(self.opt(CONF_CALL_LANGUAGE) or "de"),
        )
        self.call_acked = False
        steps = plan(settings)
        for index, (target, ack) in enumerate(steps):
            if index > 0 and (self.call_acked or self.state == sm.DISARMED):
                break
            self._log("log_call", target=f"#{index + 1}")
            data = dial_input(
                settings,
                target,
                self._spoken(self.t("call_message", cause=cause)),
                ack_entity=self._ack_entity() if ack else None,
                ack_message=self._spoken(self.t("call_ack_message", cause=cause)),
                ack_reply=self.t("call_ack_reply"),
            )
            await self._async_call("hassio", "addon_stdin", data)
            if index == 0:
                await self._async_notify(self._push(CONF_NOTIFY), title, push)
                await self._async_notify(self._push(CONF_NOTIFY_ALARM), title, message)
            if index < len(steps) - 1:
                await _sleep(settings.wait)

    def acknowledge_call(self) -> None:
        self.call_acked = True
        self._log("log_call_ack")
        self._changed()

    async def async_send_test(self) -> None:
        names = join_names((s.conf.name for s in self.open_sensors()), "-")
        self._log("log_test")
        await self._async_notify(
            self.opt_list(CONF_NOTIFY), self.t("title_test"), self.t("push_test", sensors=names)
        )

    # ------------------------------------------------------------------ automatic arming

    def _away_now(self) -> bool:
        if self.opt(CONF_PRESENCE_MODE) == aa.MODE_PERSONS:
            return aa.away_by_persons(self._value(p) for p in self.opt_list(CONF_PERSONS))
        return aa.away_by_wifi(
            (self._value(s) for s in self.wifi_sensors()),
            self.opt_list(CONF_HOME_NETWORKS),
        )

    def _initial_away_since(self) -> datetime:
        entities = (
            self.opt_list(CONF_PERSONS)
            if self.opt(CONF_PRESENCE_MODE) == aa.MODE_PERSONS
            else self.wifi_sensors()
        )
        times = [st.last_changed for e in entities if (st := self._state(e)) is not None]
        return max(times) if times else dt_util.utcnow()

    @callback
    def _on_presence(self, event: Event[EventStateChangedData]) -> None:
        now = dt_util.utcnow()
        away = self._away_now()
        if away and self.away_since is None:
            self.away_since = now
        elif not away:
            self.away_since = None
        self._auto_arm_check(now)
        self.async_update_listeners()

    def auto_arm_state(self, now: datetime) -> aa.AutoArmState:
        def seconds(since: datetime | None) -> float | None:
            return None if since is None else (now - since).total_seconds()

        if self.motion_active:
            quiet = None
        elif self.last_motion is None:
            quiet = 1e9
        else:
            quiet = seconds(self.last_motion)
        return aa.AutoArmState(
            enabled=self.auto_arm_enabled and self.auto_arm_configured,
            disarmed=self.state == sm.DISARMED,
            disarmed_for=seconds(self.disarmed_since),
            away_for=seconds(self.away_since),
            kids_home=self.kids_home,
            quiet_for=quiet,
        )

    @property
    def auto_arm_settings(self) -> aa.AutoArmSettings:
        return aa.AutoArmSettings(
            quiet=float(self.opt(CONF_QUIET)) * 60,
            prewarn=float(self.opt(CONF_PREWARN)) * 60,
            retry_after_disarm=float(self.opt(CONF_RETRY)) * 60,
            presence_stable=float(self.opt(CONF_PRESENCE_STABLE)) * 60,
        )

    def _auto_arm_check(self, now: datetime) -> None:
        if self.prewarn_until is not None:
            return  # the warning runs, decided at its end
        state = self.auto_arm_state(now)
        settings = self.auto_arm_settings
        if aa.may_warn(state, settings):
            minutes = round(settings.prewarn / 60)
            self.prewarn_until = now + timedelta(seconds=settings.prewarn)
            self._cancel("auto_arm_check")
            self._log("log_prewarn", minutes=minutes)
            self._notify(
                self.opt_list(CONF_NOTIFY),
                self.t("title_prewarn"),
                self.t("push_prewarn", minutes=minutes),
            )
            self._schedule("prewarn", self.prewarn_until, self._prewarn_over)
            self._changed()
            return
        wait = aa.seconds_until_ready(state, settings)
        if wait is not None and wait > 0:
            self._schedule(
                "auto_arm_check", now + timedelta(seconds=wait + 1), self._auto_arm_check
            )
        else:
            self._cancel("auto_arm_check")

    def _prewarn_over(self, now: datetime) -> None:
        self.prewarn_until = None
        if aa.may_arm(self.auto_arm_state(now), self.auto_arm_settings):
            self.arm(automatic=True)
        self._changed()
        self._auto_arm_check(now)

    def _cancel_prewarn(self) -> None:
        self.prewarn_until = None
        self._cancel("prewarn")

    async def async_set_auto_arm(self, enabled: bool) -> None:
        self.auto_arm_enabled = enabled
        if not enabled:
            self._cancel_prewarn()
            self._cancel("auto_arm_check")
        self._changed()
        self._auto_arm_check(dt_util.utcnow())

    # ------------------------------------------------------------------ lock and children

    @callback
    def _on_lock(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        if new is None:
            return
        if new.state == STATE_JAMMED:
            if self.state in sm.ARMED_STATES and (old is None or old.state != STATE_JAMMED):
                self._lock_failed()
            return
        if new.state not in UNLOCKED_STATES:
            return
        # a lock that comes back (radio, bridge, battery) reports its state again,
        # this is no unlocking by a person
        if old is None or old.state in INVALID or old.state == new.state:
            return
        if self.state in sm.ARMED_STATES and self._lock_bounced(old, new):
            self._lock_failed()
            return
        if self.opt(CONF_DISARM_ON_UNLOCK) and self.state in sm.ARMED_STATES:
            self.disarm(by_lock=True)
        if self.kids_home:
            delay = timedelta(minutes=float(self.opt(CONF_KIDS_RESET_AFTER)))
            self._schedule("kids_reset", dt_util.utcnow() + delay, self._kids_reset)

    def _kids_reset(self, now: datetime) -> None:
        if self.kids_home:
            self._log("log_kids_reset")
            self._set_kids(False)

    @callback
    def _on_kids_nightly_reset(self, now: datetime) -> None:
        self._cancel("kids_reset")
        if self.kids_home:
            self._kids_reset(now)

    async def async_set_kids(self, home: bool) -> None:
        self._set_kids(home)

    def _set_kids(self, home: bool) -> None:
        if home == self.kids_home:
            return
        self.kids_home = home
        if not home:
            self._cancel("kids_reset")
        else:
            self._cancel_prewarn()
        for camera in self.cameras.values():
            coro = (
                self._async_camera_kids_on(camera) if home else self._async_camera_kids_off(camera)
            )
            self._camera_task(camera, "privacy", coro)
        self._camera_rules_changed()
        self._changed()
        self._auto_arm_check(dt_util.utcnow())

    # ------------------------------------------------------------------ night door alarm

    async def async_set_night_door(self, enabled: bool, announce_off: bool = False) -> None:
        self._set_night_door(enabled, announce_off)

    def _set_night_door(self, enabled: bool, announce_off: bool = False) -> None:
        if enabled == self.night_door:
            return
        self.night_door = enabled
        self.night_changed = dt_util.utcnow()
        if enabled:
            self._log("log_night_on")
            self._notify(
                self.opt_list(CONF_NOTIFY), self.t("title_night_on"), self.t("push_night_on")
            )
        else:
            self._log("log_night_off")
            if announce_off and self.opt_list(CONF_NIGHT_OFF_SPEAK):
                self._task("night_off", self._async_night_off())
        self._changed()

    async def _async_night_off(self) -> None:
        await self._async_volume(
            self.opt_list(CONF_NIGHT_OFF_VOLUME_PLAYERS), float(self.opt(CONF_NIGHT_OFF_VOLUME))
        )
        await self._async_speak(self.opt_list(CONF_NIGHT_OFF_SPEAK), self.t("announce_night_off"))

    @callback
    def _on_tag(self, event: Event) -> None:
        if str(event.data.get("tag_id")) != str(self.opt(CONF_NIGHT_TAG)):
            return
        since = None
        if self.night_changed is not None:
            since = (dt_util.utcnow() - self.night_changed).total_seconds()
        action = tag_action(self.night_door, since)
        if action == "on":
            self._set_night_door(True)
        elif action == "off":
            self._set_night_door(False, announce_off=True)

    def _schedule_night_off(self, now: datetime) -> None:
        if not self.night_door_configured:
            return
        local = dt_util.as_local(now)
        when = next_daily(
            local,
            parse_time(self.opt(CONF_NIGHT_OFF_TIME), "05:00"),
            self.opt_list(CONF_NIGHT_OFF_DAYS),
        )
        self._schedule("night_off", when, self._night_auto_off)

    def _night_auto_off(self, now: datetime) -> None:
        self._set_night_door(False)
        self._schedule_night_off(now)

    @callback
    def _on_night_door_sensor(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        if not self.night_door or new is None or new.state != sm.ON:
            return
        if old is None or old.state != sm.OFF:
            return
        self._log("log_night_alarm")
        self._task(
            "night_siren",
            self._async_siren(
                players=self.opt_list(CONF_NIGHT_VOLUME_PLAYERS),
                volume=float(self.opt(CONF_ALARM_VOLUME)),
                reset_volume=float(self.opt(CONF_RESET_VOLUME)),
                reset_after=float(self.opt(CONF_NIGHT_RESET_AFTER)),
                devices=self.opt_list(CONF_NIGHT_SOUND_DEVICES),
                speak=self.opt_list(CONF_NIGHT_SPEAK),
                message=self.opt(CONF_NIGHT_TEXT) or self.t("announce_night_door"),
                turn_on=self.opt_list(CONF_NIGHT_TURN_ON),
            ),
        )

    # ------------------------------------------------------------------ window hint at the door

    @callback
    def _on_hint_door(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        entity = self.opt(CONF_HINT_ENTITY)
        if not entity or new is None or new.state != sm.ON or old is None or old.state != sm.OFF:
            return
        open_windows = [w for w in self.opt_list(CONF_HINT_WINDOWS) if self._value(w) == sm.ON]
        if not open_windows:
            return
        self._log("log_hint", sensors=join_names((self._name(w) for w in open_windows), ""))
        self._task("hint", self._async_hint(entity))

    async def _async_hint(self, entity: str) -> None:
        await self._async_call("homeassistant", "turn_on", {"entity_id": entity})
        await _sleep(float(self.opt(CONF_HINT_DURATION)))
        await self._async_call("homeassistant", "turn_off", {"entity_id": entity})

    # ------------------------------------------------------------------ camera

    def _camera_task(self, camera: Camera, kind: str, coro: Coroutine[Any, Any, Any]) -> None:
        """One running sequence per camera and kind; a new one replaces the old."""
        attr = f"{kind}_task"
        running: asyncio.Task | None = getattr(camera, attr)
        if running is not None and not running.done():
            running.cancel()
        task = self.config_entry.async_create_background_task(
            self.hass, coro, f"{DOMAIN}_{camera.camera_id}_{kind}"
        )
        setattr(camera, attr, task)

    async def _async_privacy(self, camera: Camera, on: bool) -> None:
        switch = camera.conf.get(CONF_PRIVACY)
        if switch:
            await self._async_call("switch", "turn_on" if on else "turn_off", {"entity_id": switch})

    async def _async_preset(self, camera: Camera, preset: str | None = None) -> None:
        select = camera.conf.get(CONF_PTZ)
        option = preset or camera.conf.get(CONF_PTZ_HOME)
        if select and option:
            await self._async_call(
                "select", "select_option", {"entity_id": select, "option": option}
            )

    def _privacy_off_now(self, camera: Camera) -> bool:
        switch = camera.conf.get(CONF_PRIVACY)
        return not switch or self._value(switch) == sm.OFF

    async def _async_camera_armed(self, camera: Camera) -> None:
        await self._async_privacy(camera, False)
        await _sleep(PAUSE_CAMERA)
        await self._async_preset(camera)

    async def _async_camera_disarmed(self, camera: Camera) -> None:
        if not cam.privacy_wanted(True, self.kids_home, self.live_mode):
            return
        await _sleep(float(camera.conf.get(CONF_PRIVACY_DELAY, 2)) * 60)
        if cam.privacy_wanted(self.state == sm.DISARMED, self.kids_home, self.live_mode):
            await self._async_privacy(camera, True)

    async def _async_camera_kids_on(self, camera: Camera) -> None:
        await self._async_privacy(camera, False)
        await _sleep(PAUSE_CAMERA)
        if self._privacy_off_now(camera):
            await self._async_preset(camera)

    async def _async_camera_kids_off(self, camera: Camera) -> None:
        if cam.privacy_wanted(self.state == sm.DISARMED, False, self.live_mode):
            await self._async_privacy(camera, True)

    async def _async_ptz(self, camera: Camera, preset: str | None) -> None:
        await self._async_privacy(camera, False)
        await _sleep(PAUSE_PTZ)
        await self._async_preset(camera, preset)

    async def async_set_live(self, enabled: bool) -> None:
        if enabled == self.live_mode:
            return
        self.live_mode = enabled
        for camera in self.cameras.values():
            coro = self._async_live_on(camera) if enabled else self._async_live_off(camera)
            self._camera_task(camera, "privacy", coro)
        self._changed()

    async def _async_live_on(self, camera: Camera) -> None:
        if self.state != sm.DISARMED:
            return
        await self._async_frigate(camera, cam.FRIGATE_ALL_OFF)
        await self._async_privacy(camera, False)
        await _sleep(PAUSE_CAMERA)
        if self._privacy_off_now(camera):
            await self._async_preset(camera)

    async def _async_live_off(self, camera: Camera) -> None:
        await self._async_privacy(camera, True)
        await _sleep(1)
        await self._async_frigate(camera, self._frigate_mode())

    def _frigate_mode(self) -> str:
        vacuum = self._state(self.opt(CONF_VACUUM))
        active = cam.vacuum_active(
            vacuum.state if vacuum else None,
            vacuum.attributes.get("is_docked") if vacuum else None,
            self._value(self.opt(CONF_VACUUM_CHARGING)),
        )
        return cam.frigate_mode(self.live_mode, self.state == sm.DISARMED, self.kids_home, active)

    async def _async_frigate(self, camera: Camera, mode: str) -> None:
        on, off = self._frigate_split(camera, mode)
        # switches that are not loaded yet (start of Home Assistant) are skipped
        on = [e for e in on if self._value(e) not in (None, *INVALID)]
        off = [e for e in off if self._value(e) not in (None, *INVALID)]
        if on:
            await self._async_call("switch", "turn_on", {"entity_id": on})
        if off:
            await self._async_call("switch", "turn_off", {"entity_id": off})

    def _apply_frigate(self, camera: Camera) -> None:
        if camera.conf.get(CONF_RECORD_SWITCHES) or camera.conf.get(CONF_DETECT_SWITCHES):
            self._task(
                f"frigate_{camera.camera_id}",
                self._async_frigate(camera, self._frigate_mode()),
                restart=True,
            )

    def _frigate_switches(self, camera: Camera) -> list[str]:
        record = [str(e) for e in camera.conf.get(CONF_RECORD_SWITCHES) or []]
        detect = [str(e) for e in camera.conf.get(CONF_DETECT_SWITCHES) or []]
        return record + detect

    def _frigate_split(self, camera: Camera, mode: str) -> tuple[list[str], list[str]]:
        record = [str(e) for e in camera.conf.get(CONF_RECORD_SWITCHES) or []]
        detect = [str(e) for e in camera.conf.get(CONF_DETECT_SWITCHES) or []]
        return cam.frigate_split(mode, record, detect)

    def _frigate_deviates(self, camera: Camera) -> bool:
        """A loaded switch of the camera is not in the state the rules want."""
        on, off = self._frigate_split(camera, self._frigate_mode())
        return any(self._value(e) == sm.OFF for e in on) or any(
            self._value(e) == sm.ON for e in off
        )

    @callback
    def _on_frigate_switch(self, event: Event[EventStateChangedData]) -> None:
        """Frigate restarted or someone switched: set the switches again (debounced)."""
        new = event.data["new_state"]
        old = event.data["old_state"]
        if new is None or new.state in INVALID:
            return
        came_back = old is None or old.state in INVALID
        for camera in self.cameras.values():
            if new.entity_id not in self._frigate_switches(camera):
                continue
            if came_back or self._frigate_deviates(camera):
                self._schedule(
                    f"frigate_resync_{camera.camera_id}",
                    dt_util.utcnow() + timedelta(seconds=FRIGATE_RESYNC),
                    lambda now, camera=camera: self._frigate_resync(camera, now),
                )

    def _frigate_resync(self, camera: Camera, now: datetime) -> None:
        if not self._frigate_deviates(camera):
            return
        camera.resyncs = [t for t in camera.resyncs if now - t < FRIGATE_RESYNC_WINDOW]
        if len(camera.resyncs) >= FRIGATE_RESYNC_MAX:
            LOGGER.warning(
                "%s: detection switches do not follow, not set again for now", camera.name
            )
            return
        camera.resyncs.append(now)
        LOGGER.info("%s: detection switches differ from the rules, set again", camera.name)
        self._apply_frigate(camera)

    def _camera_rules_changed(self) -> None:
        for camera in self._cameras():
            self._apply_frigate(camera)

    @callback
    def _on_camera_input(self, event: Event[EventStateChangedData]) -> None:
        self._camera_rules_changed()

    @callback
    def _on_person(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        if new is None or new.state != sm.ON or old is None or old.state != sm.OFF:
            return
        if self.state == sm.DISARMED:
            return
        for camera in self.cameras.values():
            if camera.conf.get(CONF_PERSON_SENSOR) != new.entity_id:
                continue
            if not camera.conf.get(CONF_PERSON_PUSH):
                continue
            data = None
            image = self._state(camera.conf.get(CONF_PERSON_IMAGE))
            picture = image.attributes.get("entity_picture") if image else None
            if picture:
                data = {"image": url + str(picture)} if (url := self._base_url()) else None
            if camera not in self._cameras():
                continue
            self._notify(
                self._push(CONF_NOTIFY),
                self._mark(self.t("title_person")),
                self._mark(self.t("push_person", camera=camera.name)),
                data=data,
            )

    def _base_url(self) -> str | None:
        """External URL, else internal URL, else the cloud URL."""
        for kwargs in ({"allow_cloud": False}, {}):
            try:
                return get_url(self.hass, prefer_external=True, **kwargs)
            except NoURLAvailableError:
                continue
        return None

    # ------------------------------------------------------------------ garage

    def _garage_connections(self) -> list[str | None]:
        return [self._value(s) for s in self.wifi_sensors()]

    def _garage_check(self, garage: Garage, now: datetime, startup: bool = False) -> None:
        panel = garage.conf.get(CONF_GARAGE_PANEL)
        networks = garage.conf.get(CONF_GARAGE_NETWORKS) or []
        if not panel or not networks or not self.garage_auto:
            return
        if anyone_connected(self._garage_connections(), networks):
            self._cancel(f"garage_{garage.garage_id}")
            if self._value(panel) != sm.DISARMED:
                self._log("log_garage_disarmed")
                self.hass.async_create_task(
                    self._async_call("alarm_control_panel", "alarm_disarm", {"entity_id": panel})
                )
            return
        delay = timedelta(minutes=float(garage.conf.get(CONF_GARAGE_DELAY, 2)))
        self._schedule(
            f"garage_{garage.garage_id}", now + delay, lambda t: self._garage_arm(garage)
        )

    def _garage_arm(self, garage: Garage) -> None:
        panel = garage.conf.get(CONF_GARAGE_PANEL)
        networks = garage.conf.get(CONF_GARAGE_NETWORKS) or []
        if not self.garage_auto or anyone_connected(self._garage_connections(), networks):
            return
        if self._value(panel) == sm.ARMED_AWAY:
            return
        self._log("log_garage_armed")
        self.hass.async_create_task(
            self._async_call("alarm_control_panel", "alarm_arm_away", {"entity_id": panel})
        )

    @callback
    def _on_garage_wifi(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        now = dt_util.utcnow()
        for garage in self.garages.values():
            networks = {str(n).strip() for n in garage.conf.get(CONF_GARAGE_NETWORKS) or []}
            arrived = new is not None and new.state in networks
            left = old is not None and old.state in networks and not arrived
            if arrived or left:
                self._garage_check(garage, now)

    async def async_set_garage_auto(self, enabled: bool) -> None:
        self.garage_auto = enabled
        if not enabled:
            for garage in self.garages.values():
                self._cancel(f"garage_{garage.garage_id}")
        self._changed()

    @callback
    def _on_garage_motion(self, event: Event[EventStateChangedData]) -> None:
        new = event.data["new_state"]
        old = event.data["old_state"]
        if new is None or new.state != sm.ON or old is None or old.state != sm.OFF:
            return
        for garage in self.garages.values():
            if new.entity_id not in (garage.conf.get(CONF_GARAGE_MOTION) or []):
                continue
            if self._value(garage.conf.get(CONF_GARAGE_PANEL)) != sm.ARMED_AWAY:
                continue
            self.hass.async_create_task(self._async_garage_motion(garage, new.name))

    async def _async_garage_motion(self, garage: Garage, camera: str) -> None:
        await self._async_notify(
            self.opt_list(CONF_NOTIFY), self.t("title_garage"), self.t("push_garage", camera=camera)
        )
        tts = garage.conf.get(CONF_GARAGE_TTS_TEXT) or self.t("tts_garage")
        for service in garage.conf.get(CONF_GARAGE_TTS) or []:
            for _ in range(int(garage.conf.get(CONF_GARAGE_TTS_REPEAT, 2))):
                await self._async_notify(
                    [service],
                    "",
                    "TTS",
                    data={
                        "tts_text": tts,
                        "media_stream": "alarm_stream_max",
                        "tts_language": "de-DE" if self.language == "de" else "en-US",
                    },
                )

    # ------------------------------------------------------------------ diagnostics

    def diagnostics(self) -> dict[str, Any]:
        now = dt_util.utcnow()
        return {
            "state": self.state,
            "bypassed": self.bypassed,
            "test": sorted(self.test) if self.test is not None else None,
            "open": [s.conf.entity_id for s in self.open_sensors()],
            "motion_suppressed": self.motion_suppressed(),
            "last_cause": self.last_cause,
            "last_triggered": _iso(self.last_triggered),
            "kids_home": self.kids_home,
            "night_door": self.night_door,
            "live_mode": self.live_mode,
            "auto_arm": {
                "enabled": self.auto_arm_enabled,
                "configured": self.auto_arm_configured,
                "state": self.auto_arm_state(now).__dict__,
                "prewarn_until": _iso(self.prewarn_until),
            },
            "missing_entities": self.missing,
            "timers": sorted(self._timers),
        }


def _looks_like_entity(value: Any) -> bool:
    if not isinstance(value, str) or "." not in value or " " in value:
        return False
    domain = value.split(".", 1)[0]
    return domain.isidentifier() and domain.islower() and not value.startswith("sip:")


def _as_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _to_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    return dt_util.parse_datetime(str(value))
