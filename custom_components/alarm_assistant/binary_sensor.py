"""Binary sensors: motion (filtered), open contacts, suppressed motion, warning."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .engine import AlarmConfigEntry, AlarmEngine
from .entity import AlarmEntity
from .logic.state_machine import TYPE_MOTION

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AlarmConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    engine = entry.runtime_data
    async_add_entities(
        [
            EngineBinarySensor(
                engine, "motion", BinarySensorDeviceClass.MOTION, lambda e: e.motion_active
            ),
            EngineBinarySensor(
                engine,
                "contacts_open",
                BinarySensorDeviceClass.OPENING,
                lambda e: any(s.conf.type != TYPE_MOTION for s in e.open_sensors()),
                lambda e: {
                    "sensors": [s.conf.name for s in e.open_sensors() if s.conf.type != TYPE_MOTION]
                },
            ),
            EngineBinarySensor(engine, "motion_suppressed", None, lambda e: e.motion_suppressed()),
            EngineBinarySensor(
                engine,
                "auto_arm_warning",
                None,
                lambda e: e.prewarn_until is not None,
                lambda e: {"arms_at": e.prewarn_until.isoformat() if e.prewarn_until else None},
            ),
        ]
    )


class EngineBinarySensor(AlarmEntity, BinarySensorEntity):
    """Binary sensor calculated by the engine."""

    def __init__(
        self,
        engine: AlarmEngine,
        key: str,
        device_class: BinarySensorDeviceClass | None,
        getter: Callable[[AlarmEngine], bool],
        attributes: Callable[[AlarmEngine], dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(engine, key)
        self._attr_device_class = device_class
        self._getter = getter
        self._attributes = attributes

    @property
    def is_on(self) -> bool:
        return self._getter(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return self._attributes(self.coordinator) if self._attributes else None
