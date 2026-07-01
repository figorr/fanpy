import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    prefix = entry.data.get(CONF_PREFIX, "ventilador")
    name = entry.data.get(CONF_NAME, prefix)
    num_speeds = entry.data.get(CONF_NUM_SPEEDS, 6)
    has_light = entry.data.get(CONF_HAS_LIGHT, True)
    has_temp = entry.data.get(CONF_HAS_LIGHT_TEMPERATURE, True)
    has_intensity = entry.data.get(CONF_HAS_LIGHT_INTENSITY, True)

    entities = [
        FanButton(entry, prefix, name, "power_on", f"{name} Power On", "mdi:power"),
        FanButton(entry, prefix, name, "power_off", f"{name} Power Off", "mdi:power-off"),
    ]

    if has_light:
        entities.append(FanButton(entry, prefix, name, "luz_on", f"{name} Luz On", "mdi:lightbulb-on"))
        entities.append(FanButton(entry, prefix, name, "luz_off", f"{name} Luz Off", "mdi:lightbulb-off"))
        if has_temp:
            entities.append(FanButton(entry, prefix, name, "luz_calida", f"{name} Luz CÃ¡lida", "mdi:thermometer-plus"))
            entities.append(FanButton(entry, prefix, name, "luz_fria", f"{name} Luz FrÃ­a", "mdi:thermometer-minus"))
        if has_intensity:
            entities.append(FanButton(entry, prefix, name, "intensidad_alta", f"{name} Intensidad Alta", "mdi:brightness-7"))
            entities.append(FanButton(entry, prefix, name, "intensidad_baja", f"{name} Intensidad Baja", "mdi:brightness-1"))

    if num_speeds > 1:
        for i in range(1, num_speeds + 1):
            entities.append(FanButton(entry, prefix, name, f"velocidad_{i}", f"{name} Velocidad {i}", "mdi:fan"))

    async_add_entities(entities)


class FanButton(ButtonEntity):

    def __init__(self, entry: ConfigEntry, prefix: str, name: str, action: str, display_name: str, icon: str) -> None:
        self._entry = entry
        self._prefix = prefix
        self._action = action
        self._attr_name = display_name
        self._attr_unique_id = f"{prefix}_{action}"
        self._attr_icon = icon

    async def async_press(self) -> None:
        script_entity = f"script.{self._prefix}_{self._action}"
        await self.hass.services.async_call(
            "script", "turn_on",
            {"entity_id": script_entity},
            blocking=True,
        )
