"""Switches: automatic arming, children alone at home, night door alarm, live view, garage."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .engine import AlarmConfigEntry, AlarmEngine
from .entity import AlarmEntity, remove_entities

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlarmConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    engine = entry.runtime_data
    # switches of functions that are set up (key, configured, getter, setter)
    optional = [
        (
            "auto_arm",
            engine.auto_arm_configured,
            lambda e: e.auto_arm_enabled,
            engine.async_set_auto_arm,
        ),
        (
            "night_door",
            engine.night_door_configured,
            lambda e: e.night_door,
            engine.async_set_night_door,
        ),
        ("live_mode", bool(engine.cameras), lambda e: e.live_mode, engine.async_set_live),
        (
            "garage_auto",
            bool(engine.garages),
            lambda e: e.garage_auto,
            engine.async_set_garage_auto,
        ),
    ]
    entities = [EngineSwitch(engine, "kids_home", lambda e: e.kids_home, engine.async_set_kids)]
    entities += [
        EngineSwitch(engine, key, getter, setter)
        for key, configured, getter, setter in optional
        if configured
    ]
    remove_entities(
        hass, entry.entry_id, "switch", [key for key, configured, *_ in optional if not configured]
    )
    async_add_entities(entities)


class EngineSwitch(AlarmEntity, SwitchEntity):
    """A switch whose state lives in the engine (kept over restarts)."""

    def __init__(
        self,
        engine: AlarmEngine,
        key: str,
        getter: Callable[[AlarmEngine], bool],
        setter: Callable[[bool], Coroutine[Any, Any, None]],
    ) -> None:
        super().__init__(engine, key)
        self._getter = getter
        self._setter = setter

    @property
    def is_on(self) -> bool:
        return self._getter(self.coordinator)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._setter(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._setter(False)
