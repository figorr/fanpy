import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    mode = entry.data.get(CONF_MODE, CONF_MODE_REMOTE)
    if mode == CONF_MODE_DIRECT:
        return

    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)

    async_add_entities([
        FanPowerBinarySensor(hass, entry, prefix, name),
        FanLightBinarySensor(hass, entry, prefix, name),
    ])


class FanPowerBinarySensor(BinarySensorEntity):

    _attr_icon = "mdi:fan"
    _attr_device_class = "power"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"Fanpy {name} Power"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_power"

    @property
    def is_on(self) -> bool | None:
        state = self._hass.states.get(f"switch.{CONF_ENTITY_PREFIX}_{self._prefix}_power")
        if state is None:
            return None
        return state.state == STATE_ON


class FanLightBinarySensor(BinarySensorEntity):

    _attr_icon = "mdi:lightbulb"
    _attr_device_class = "light"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, prefix: str, name: str) -> None:
        self._hass = hass
        self._entry = entry
        self._prefix = prefix
        self._attr_name = f"Fanpy {name} Luz"
        self._attr_unique_id = f"{CONF_ENTITY_PREFIX}_{prefix}_luz"

    @property
    def is_on(self) -> bool | None:
        state = self._hass.states.get(f"switch.{CONF_ENTITY_PREFIX}_{self._prefix}_luz")
        if state is None:
            return None
        return state.state == STATE_ON
