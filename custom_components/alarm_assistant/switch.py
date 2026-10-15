"""Switches: automatic arming, children alone at home, night door alarm, live view, garage."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .engine import AlarmConfigEntry, AlarmEngine
from .entity import AlarmEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlarmConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    engine = entry.runtime_data
    entities = [
        EngineSwitch(engine, "auto_arm", lambda e: e.auto_arm_enabled, engine.async_set_auto_arm),
        EngineSwitch(engine, "kids_home", lambda e: e.kids_home, engine.async_set_kids),
    ]
    if engine.night_door_configured:
        entities.append(
            EngineSwitch(engine, "night_door", lambda e: e.night_door, engine.async_set_night_door)
        )
    if engine.cameras:
        entities.append(
            EngineSwitch(engine, "live_mode", lambda e: e.live_mode, engine.async_set_live)
        )
    if engine.garages:
        entities.append(
            EngineSwitch(
                engine, "garage_auto", lambda e: e.garage_auto, engine.async_set_garage_auto
            )
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
