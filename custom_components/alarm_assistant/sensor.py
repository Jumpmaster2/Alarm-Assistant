"""Sensors: last cause and time of an alarm."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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
    async_add_entities([CauseSensor(engine), LastTriggeredSensor(engine)])


class CauseSensor(AlarmEntity, SensorEntity):
    """Cause of the last alarm."""

    def __init__(self, engine: AlarmEngine) -> None:
        super().__init__(engine, "cause")

    @property
    def native_value(self) -> str | None:
        return self.coordinator.last_cause


class LastTriggeredSensor(AlarmEntity, SensorEntity):
    """Time of the last alarm."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, engine: AlarmEngine) -> None:
        super().__init__(engine, "last_triggered")

    @property
    def native_value(self) -> datetime | None:
        return self.coordinator.last_triggered
