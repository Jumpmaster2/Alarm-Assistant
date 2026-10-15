"""Buttons: acknowledge the alarm call, send a test message."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    async_add_entities([AcknowledgeButton(engine), TestButton(engine)])


class AcknowledgeButton(AlarmEntity, ButtonEntity):
    """Pressed by the phone call (key 1): no further numbers are called."""

    def __init__(self, engine: AlarmEngine) -> None:
        super().__init__(engine, "call_acknowledge")

    async def async_press(self) -> None:
        self.coordinator.acknowledge_call()


class TestButton(AlarmEntity, ButtonEntity):
    """Send a test message with the open sensors (nothing else happens)."""

    def __init__(self, engine: AlarmEngine) -> None:
        super().__init__(engine, "test")

    async def async_press(self) -> None:
        await self.coordinator.async_send_test()
