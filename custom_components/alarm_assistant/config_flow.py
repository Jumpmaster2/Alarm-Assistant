"""Config flow, options flow and the subentry flows for sensors, cameras and garages."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    SOURCE_USER,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    FlowType,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import (
    BooleanSelector,
    DeviceSelector,
    DeviceSelectorConfig,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    TimeSelector,
)

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
    CONF_NAME,
    CONF_NIGHT_DOOR,
    CONF_NIGHT_OFF_DAYS,
    CONF_NIGHT_OFF_SPEAK,
    CONF_NIGHT_OFF_TIME,
    CONF_NIGHT_OFF_VOLUME,
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
    GARAGE_DEFAULTS,
    LANGUAGE_OPTIONS,
    NAME,
    SENSOR_DEFAULTS,
    SUBENTRY_CAMERA,
    SUBENTRY_GARAGE,
    SUBENTRY_SENSOR,
)
from .engine import hash_code
from .logic.auto_arm import PRESENCE_MODES
from .logic.misc import WEEKDAYS
from .logic.state_machine import SENSOR_TYPES, TYPE_WINDOW, type_defaults

CONF_NEW_CODE = "new_code"
CONF_REMOVE_CODE = "remove_code"
SECTION_ANNOUNCE = "announce"
SECTION_SIREN = "siren"
SECTION_ACTIONS = "actions"
SECTION_KIDS = "kids"
SECTION_HINT = "hint"
SECTION_OFF = "switch_off"


def _number(minimum: float, maximum: float, step: float, unit: str | None = None) -> NumberSelector:
    config = NumberSelectorConfig(min=minimum, max=maximum, step=step, mode=NumberSelectorMode.BOX)
    if unit:
        config["unit_of_measurement"] = unit
    return NumberSelector(config)


def _entity(domains: list[str] | None = None, multiple: bool = False) -> EntitySelector:
    config = EntitySelectorConfig(multiple=multiple)
    if domains:
        config["domain"] = domains
    return EntitySelector(config)


def _choice(options: list[str], key: str, multiple: bool = False) -> SelectSelector:
    return SelectSelector(
        SelectSelectorConfig(
            options=options,
            translation_key=key,
            multiple=multiple,
            mode=SelectSelectorMode.LIST if not multiple else SelectSelectorMode.DROPDOWN,
        )
    )


def _free_list() -> SelectSelector:
    """List of free text values (networks, call targets)."""
    return SelectSelector(
        SelectSelectorConfig(
            options=[], multiple=True, custom_value=True, mode=SelectSelectorMode.DROPDOWN
        )
    )


def _services(hass: HomeAssistant) -> SelectSelector:
    options = sorted(f"notify.{name}" for name in hass.services.async_services_for_domain("notify"))
    return SelectSelector(
        SelectSelectorConfig(
            options=options, multiple=True, custom_value=True, mode=SelectSelectorMode.DROPDOWN
        )
    )


def _alexa_devices() -> DeviceSelector:
    return DeviceSelector(DeviceSelectorConfig(integration="alexa_devices", multiple=True))


def _multiline() -> TextSelector:
    return TextSelector(TextSelectorConfig(multiline=True))


def _opt(key: str, values: dict[str, Any]) -> vol.Optional:
    """Optional field that can be cleared again."""
    return vol.Optional(key, description={"suggested_value": values.get(key)})


def _req(key: str, values: dict[str, Any], defaults: dict[str, Any] | None = None) -> vol.Required:
    defaults = defaults if defaults is not None else DEFAULTS
    return vol.Required(key, default=values.get(key, defaults.get(key)))


def _list(key: str, values: dict[str, Any]) -> vol.Optional:
    return vol.Optional(key, default=list(values.get(key) or []))


def _clean(data: dict[str, Any]) -> dict[str, Any]:
    """Drop cleared optional values."""
    return {k: v for k, v in data.items() if v not in (None, "")}


def _flatten(user_input: dict[str, Any], sections: tuple[str, ...]) -> dict[str, Any]:
    flat = {k: v for k, v in user_input.items() if k not in sections}
    for key in sections:
        flat.update(user_input.get(key) or {})
    return flat


def _schema_keys(schema: vol.Schema) -> set[str]:
    keys: set[str] = set()
    for marker, value in schema.schema.items():
        if isinstance(value, section):
            keys |= _schema_keys(value.schema)
        else:
            keys.add(str(marker))
    return keys


# ---------------------------------------------------------------- global schemas


def _general_schema(hass: HomeAssistant, v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            _req(CONF_LANGUAGE, v): _choice(LANGUAGE_OPTIONS, "language"),
            _list(CONF_NOTIFY, v): _services(hass),
            _list(CONF_NOTIFY_ALARM, v): _services(hass),
            _list(CONF_NOTIFY_ADMIN, v): _services(hass),
        }
    )


def _alarm_fields(v: dict[str, Any]) -> dict[Any, Any]:
    return {
        _req(CONF_ENTRY_DELAY, v): _number(0, 600, 1, "s"),
        _req(CONF_EXIT_DELAY, v): _number(0, 600, 1, "s"),
        _req(CONF_TRIGGER_TIME, v): _number(0, 7200, 1, "s"),
        _req(CONF_DISARM_AFTER_TRIGGER, v): BooleanSelector(),
        _req(CONF_CODE_ARM, v): BooleanSelector(),
        _list(CONF_ARM_ON_ENTITIES, v): _entity(None, True),
    }


def _motion_schema(hass: HomeAssistant, v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            _opt(CONF_VACUUM, v): _entity(["vacuum"]),
            _opt(CONF_VACUUM_CHARGING, v): _entity(["binary_sensor"]),
            _req(CONF_DOCK_GRACE, v): _number(0, 1800, 1, "s"),
            _opt(CONF_FAULT_SENSOR, v): _entity(["binary_sensor"]),
            _req(CONF_NOTIFY_SUPPRESSED, v): BooleanSelector(),
        }
    )


def _reactions_schema(hass: HomeAssistant, v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(SECTION_ANNOUNCE): section(
                vol.Schema(
                    {
                        _list(CONF_ANNOUNCE_ENTITIES, v): _entity(["notify"], True),
                        _opt(CONF_TEXT_TRIGGERED, v): _multiline(),
                        _opt(CONF_TEXT_PENDING, v): _multiline(),
                    }
                ),
                {"collapsed": False},
            ),
            vol.Required(SECTION_SIREN): section(
                vol.Schema(
                    {
                        _list(CONF_VOLUME_PLAYERS, v): _entity(["media_player"], True),
                        _req(CONF_ALARM_VOLUME, v): _number(0, 1, 0.01),
                        _req(CONF_RESET_VOLUME, v): _number(0, 1, 0.01),
                        _req(CONF_RESET_AFTER, v): _number(0, 600, 1, "s"),
                        _list(CONF_SOUND_DEVICES, v): _alexa_devices(),
                        _req(CONF_SOUND, v): TextSelector(),
                        _list(CONF_SPEAK_SERVICES, v): _services(hass),
                    }
                ),
                {"collapsed": False},
            ),
            vol.Required(SECTION_ACTIONS): section(
                vol.Schema(
                    {
                        _list(CONF_TURN_ON, v): _entity(None, True),
                        _list(CONF_CLOSE_COVERS, v): _entity(["cover"], True),
                    }
                ),
                {"collapsed": False},
            ),
        }
    )


def _call_schema(v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            _opt(CONF_CALL_ADDON, v): TextSelector(),
            _list(CONF_CALL_TARGETS, v): _free_list(),
            _req(CONF_CALL_ACK, v): BooleanSelector(),
            _req(CONF_CALL_WAIT, v): _number(0, 600, 1, "s"),
            _opt(CONF_CALL_TTS, v): _entity(["tts"]),
            _req(CONF_CALL_LANGUAGE, v): TextSelector(),
            _req(CONF_CALL_COOLDOWN, v): _number(0, 3600, 1, "s"),
        }
    )


def _auto_arm_schema(v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            _req(CONF_PRESENCE_MODE, v): _choice(PRESENCE_MODES, "presence_mode"),
            _list(CONF_WIFI_SENSORS, v): _entity(["sensor"], True),
            _list(CONF_HOME_NETWORKS, v): _free_list(),
            _list(CONF_PERSONS, v): _entity(["person"], True),
            _req(CONF_QUIET, v): _number(0, 240, 1, "min"),
            _req(CONF_PREWARN, v): _number(0, 60, 1, "min"),
            _req(CONF_RETRY, v): _number(0, 120, 1, "min"),
            _req(CONF_PRESENCE_STABLE, v): _number(0, 60, 1, "min"),
        }
    )


def _lock_schema(v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            _opt(CONF_LOCK, v): _entity(["lock"]),
            _opt(CONF_LOCK_DOOR, v): _entity(["binary_sensor"]),
            _req(CONF_DISARM_ON_UNLOCK, v): BooleanSelector(),
            _req(CONF_LOCK_ON_ARM, v): BooleanSelector(),
        }
    )


def _night_schema(hass: HomeAssistant, v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            _opt(CONF_NIGHT_DOOR, v): _entity(["binary_sensor"]),
            _opt(CONF_NIGHT_TAG, v): TextSelector(),
            _list(CONF_NIGHT_TURN_ON, v): _entity(None, True),
            _list(CONF_NIGHT_VOLUME_PLAYERS, v): _entity(["media_player"], True),
            _list(CONF_NIGHT_SOUND_DEVICES, v): _alexa_devices(),
            _list(CONF_NIGHT_SPEAK, v): _services(hass),
            _opt(CONF_NIGHT_TEXT, v): TextSelector(),
            _req(CONF_NIGHT_RESET_AFTER, v): _number(0, 600, 1, "s"),
            vol.Required(SECTION_OFF): section(
                vol.Schema(
                    {
                        _req(CONF_NIGHT_OFF_TIME, v): TimeSelector(),
                        vol.Optional(
                            CONF_NIGHT_OFF_DAYS, default=list(v.get(CONF_NIGHT_OFF_DAYS) or [])
                        ): _choice(WEEKDAYS, "weekday", multiple=True),
                        _list(CONF_NIGHT_OFF_SPEAK, v): _services(hass),
                        _req(CONF_NIGHT_OFF_VOLUME, v): _number(0, 1, 0.01),
                    }
                ),
                {"collapsed": False},
            ),
        }
    )


def _extras_schema(v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(SECTION_KIDS): section(
                vol.Schema(
                    {
                        _req(CONF_KIDS_RESET_AFTER, v): _number(0, 240, 1, "min"),
                        _req(CONF_KIDS_RESET_TIME, v): TimeSelector(),
                    }
                ),
                {"collapsed": False},
            ),
            vol.Required(SECTION_HINT): section(
                vol.Schema(
                    {
                        _opt(CONF_HINT_DOOR, v): _entity(["binary_sensor"]),
                        _list(CONF_HINT_WINDOWS, v): _entity(["binary_sensor"], True),
                        _opt(CONF_HINT_ENTITY, v): _entity(["switch", "light", "input_boolean"]),
                        _req(CONF_HINT_DURATION, v): _number(1, 600, 1, "s"),
                    }
                ),
                {"collapsed": False},
            ),
        }
    )


SECTIONS = (
    SECTION_ANNOUNCE,
    SECTION_SIREN,
    SECTION_ACTIONS,
    SECTION_KIDS,
    SECTION_HINT,
    SECTION_OFF,
)


# ---------------------------------------------------------------- config flow


class AlarmConfigFlow(ConfigFlow, domain=DOMAIN):
    """Initial setup: notifications and alarm times."""

    VERSION = 1

    def __init__(self) -> None:
        self._options: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return AlarmOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        return {
            SUBENTRY_SENSOR: SensorSubentryFlow,
            SUBENTRY_CAMERA: CameraSubentryFlow,
            SUBENTRY_GARAGE: GarageSubentryFlow,
        }

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(_clean(user_input))
            return await self.async_step_alarm()
        return self.async_show_form(
            step_id="user", data_schema=_general_schema(self.hass, {**DEFAULTS})
        )

    async def async_step_alarm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            data = _clean(user_input)
            code = str(data.pop(CONF_CODE, "") or "").strip()
            options = {**DEFAULTS, **self._options, **data}
            if code:
                options[CONF_CODE] = hash_code(code)
            return self.async_create_entry(title=NAME, data={}, options=options)
        schema = vol.Schema(
            {
                **_alarm_fields({}),
                vol.Optional(CONF_CODE): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
            }
        )
        return self.async_show_form(step_id="alarm", data_schema=schema)

    async def async_on_create_entry(self, result: ConfigFlowResult) -> ConfigFlowResult:
        """Directly continue with the first sensor."""
        entry = result.get("result")
        if entry is None:
            return result
        sub = await self.hass.config_entries.subentries.async_init(
            (entry.entry_id, SUBENTRY_SENSOR), context={"source": SOURCE_USER}
        )
        result["next_flow"] = (FlowType.CONFIG_SUBENTRIES_FLOW, sub["flow_id"])
        return result


# ---------------------------------------------------------------- options flow


class AlarmOptionsFlow(OptionsFlow):
    """All global settings, grouped in a menu."""

    @property
    def _values(self) -> dict[str, Any]:
        return {**DEFAULTS, **self.config_entry.options}

    def _save(self, schema: vol.Schema, user_input: dict[str, Any]) -> ConfigFlowResult:
        """Replace all values of this form (cleared optional fields are removed)."""
        options = {**self.config_entry.options}
        for key in _schema_keys(schema):
            options.pop(key, None)
        options.update(_clean(_flatten(user_input, SECTIONS)))
        return self.async_create_entry(data=options)

    async def _form(
        self, step_id: str, schema: vol.Schema, user_input: dict[str, Any] | None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self._save(schema, user_input)
        return self.async_show_form(step_id=step_id, data_schema=schema)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "general",
                "alarm",
                "motion",
                "reactions",
                "call",
                "auto_arm",
                "lock",
                "night_door",
                "extras",
            ],
        )

    async def async_step_general(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._form("general", _general_schema(self.hass, self._values), user_input)

    async def async_step_alarm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        fields = _alarm_fields(self._values)
        schema = vol.Schema(
            {
                **fields,
                vol.Optional(CONF_NEW_CODE): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.PASSWORD)
                ),
                vol.Optional(CONF_REMOVE_CODE, default=False): BooleanSelector(),
            }
        )
        if user_input is not None:
            data = dict(user_input)
            new_code = str(data.pop(CONF_NEW_CODE, "") or "").strip()
            remove = bool(data.pop(CONF_REMOVE_CODE, False))
            options = {**self.config_entry.options}
            for key in _schema_keys(vol.Schema(fields)):
                options.pop(key, None)
            options.update(_clean(data))
            if remove:
                options.pop(CONF_CODE, None)
            elif new_code:
                options[CONF_CODE] = hash_code(new_code)
            return self.async_create_entry(data=options)
        return self.async_show_form(
            step_id="alarm",
            data_schema=schema,
            description_placeholders={"code": "✔" if self._values.get(CONF_CODE) else "–"},
        )

    async def async_step_motion(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._form("motion", _motion_schema(self.hass, self._values), user_input)

    async def async_step_reactions(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._form("reactions", _reactions_schema(self.hass, self._values), user_input)

    async def async_step_call(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._form("call", _call_schema(self._values), user_input)

    async def async_step_auto_arm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._form("auto_arm", _auto_arm_schema(self._values), user_input)

    async def async_step_lock(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._form("lock", _lock_schema(self._values), user_input)

    async def async_step_night_door(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._form("night_door", _night_schema(self.hass, self._values), user_input)

    async def async_step_extras(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return await self._form("extras", _extras_schema(self._values), user_input)


# ---------------------------------------------------------------- sensor subentry


class SensorSubentryFlow(ConfigSubentryFlow):
    """Add or change an alarm sensor: entity and type, then its behaviour."""

    def __init__(self) -> None:
        self._values: dict[str, Any] = {}
        self._reconfigure = False

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        return await self.async_step_basics(user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        subentry = self._get_reconfigure_subentry()
        self._reconfigure = True
        self._values = {CONF_NAME: subentry.title, **subentry.data}
        return await self.async_step_basics()

    async def async_step_basics(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        if user_input is not None:
            if user_input.get(CONF_TYPE) != self._values.get(CONF_TYPE):
                # new type: start with its defaults
                for key in (CONF_USE_ENTRY, CONF_USE_EXIT, CONF_AUTO_BYPASS, CONF_ALLOW_OPEN):
                    self._values.pop(key, None)
            self._values.update(user_input)
            name = str(user_input.get(CONF_NAME, "") or "").strip()
            if not name:
                state = self.hass.states.get(str(user_input[CONF_ENTITY]))
                name = state.name if state else str(user_input[CONF_ENTITY])
            self._values[CONF_NAME] = name
            return await self.async_step_behavior()
        schema = vol.Schema(
            {
                _opt(CONF_NAME, self._values): TextSelector(),
                vol.Required(CONF_ENTITY, default=self._values.get(CONF_ENTITY)): _entity(
                    ["binary_sensor", "input_boolean"]
                ),
                vol.Required(CONF_TYPE, default=self._values.get(CONF_TYPE, TYPE_WINDOW)): _choice(
                    SENSOR_TYPES, "sensor_type"
                ),
            }
        )
        return self.async_show_form(step_id="basics", data_schema=schema)

    async def async_step_behavior(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        if user_input is not None:
            for key in (CONF_ONLY_UNAVAILABLE, CONF_ARM_COVER, CONF_CAMERA_PRESET):
                self._values.pop(key, None)
            self._values.update(_clean(user_input))
            data = {k: v for k, v in self._values.items() if k != CONF_NAME}
            title = str(self._values[CONF_NAME])
            if self._reconfigure:
                return self.async_update_and_abort(
                    self._get_entry(), self._get_reconfigure_subentry(), title=title, data=data
                )
            return self.async_create_entry(title=title, data=data)
        v = {
            **SENSOR_DEFAULTS,
            **type_defaults(str(self._values.get(CONF_TYPE, TYPE_WINDOW))),
            **self._values,
        }
        mapping = {
            CONF_USE_ENTRY: "entry_delay",
            CONF_USE_EXIT: "exit_delay",
            CONF_AUTO_BYPASS: "auto_bypass",
            CONF_ALLOW_OPEN: "allow_open",
        }
        fields: dict[Any, Any] = {
            vol.Required(key, default=v.get(key, v.get(default_key))): BooleanSelector()
            for key, default_key in mapping.items()
        }
        fields.update(
            {
                _opt(CONF_ONLY_UNAVAILABLE, v): _entity(),
                _opt(CONF_ARM_COVER, v): _entity(["cover"]),
                _req(CONF_ARM_COVER_POSITION, v, SENSOR_DEFAULTS): _number(0, 100, 1, "%"),
                _opt(CONF_CAMERA_PRESET, v): TextSelector(),
            }
        )
        return self.async_show_form(
            step_id="behavior",
            data_schema=vol.Schema(fields),
            description_placeholders={"name": str(self._values.get(CONF_NAME, ""))},
        )


# ---------------------------------------------------------------- camera subentry


def _camera_schema(v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=v.get(CONF_NAME, "")): TextSelector(),
            _opt(CONF_PRIVACY, v): _entity(["switch"]),
            _opt(CONF_PTZ, v): _entity(["select"]),
            _opt(CONF_PTZ_HOME, v): TextSelector(),
            _req(CONF_PRIVACY_DELAY, v, CAMERA_DEFAULTS): _number(0, 60, 1, "min"),
            _list(CONF_RECORD_SWITCHES, v): _entity(["switch"], True),
            _list(CONF_DETECT_SWITCHES, v): _entity(["switch"], True),
            _opt(CONF_PERSON_SENSOR, v): _entity(["binary_sensor"]),
            _opt(CONF_PERSON_COUNT, v): _entity(["sensor"]),
            _opt(CONF_PERSON_IMAGE, v): _entity(["image", "camera"]),
            _req(CONF_PERSON_PUSH, v, CAMERA_DEFAULTS): BooleanSelector(),
        }
    )


def _garage_schema(hass: HomeAssistant, v: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=v.get(CONF_NAME, "")): TextSelector(),
            vol.Required(CONF_GARAGE_PANEL, default=v.get(CONF_GARAGE_PANEL)): _entity(
                ["alarm_control_panel"]
            ),
            _list(CONF_GARAGE_NETWORKS, v): _free_list(),
            _req(CONF_GARAGE_DELAY, v, GARAGE_DEFAULTS): _number(0, 60, 1, "min"),
            _list(CONF_GARAGE_MOTION, v): _entity(["binary_sensor"], True),
            _list(CONF_GARAGE_TTS, v): _services(hass),
            _opt(CONF_GARAGE_TTS_TEXT, v): TextSelector(),
            _req(CONF_GARAGE_TTS_REPEAT, v, GARAGE_DEFAULTS): _number(0, 10, 1),
        }
    )


class _SimpleSubentryFlow(ConfigSubentryFlow):
    """Subentry with one form for adding and changing."""

    def _schema(self, values: dict[str, Any]) -> vol.Schema:
        raise NotImplementedError

    def _result(self, user_input: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        data = _clean(user_input)
        title = str(data.pop(CONF_NAME, "")).strip()
        return title, data

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            title, data = self._result(user_input)
            if title:
                return self.async_create_entry(title=title, data=data)
            errors[CONF_NAME] = "name_required"
        return self.async_show_form(
            step_id="user", data_schema=self._schema(user_input or {}), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        subentry = self._get_reconfigure_subentry()
        errors: dict[str, str] = {}
        values = {CONF_NAME: subentry.title, **subentry.data}
        if user_input is not None:
            title, data = self._result(user_input)
            if title:
                return self.async_update_and_abort(
                    self._get_entry(), subentry, title=title, data=data
                )
            errors[CONF_NAME] = "name_required"
            values = user_input
        return self.async_show_form(
            step_id="reconfigure", data_schema=self._schema(values), errors=errors
        )


class CameraSubentryFlow(_SimpleSubentryFlow):
    """Camera with privacy mode, preset and detection switches."""

    def _schema(self, values: dict[str, Any]) -> vol.Schema:
        return _camera_schema(values)


class GarageSubentryFlow(_SimpleSubentryFlow):
    """Garage cameras armed by the garage network."""

    def _schema(self, values: dict[str, Any]) -> vol.Schema:
        return _garage_schema(self.hass, values)
