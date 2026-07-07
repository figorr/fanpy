# Fanpy

![Fanpy Banner](images/banner.png)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Python](https://img.shields.io/badge/Language-Python-blue)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![Release](https://github.com/figorr/fanpy/actions/workflows/release.yml/badge.svg)](https://github.com/figorr/fanpy/actions/workflows/release.yml)
![GitHub all releases](https://img.shields.io/github/downloads/figorr/fanpy/total)
![GitHub release](https://img.shields.io/github/downloads/figorr/fanpy/latest/total)
![Latest release](https://img.shields.io/github/v/release/figorr/fanpy?label=latest)

Custom integration for Home Assistant to configure ceiling fans for use with the [Fanpy Card](https://github.com/figorr/fanpy-card) Lovelace card.

## Purpose

Fanpy is the **backend companion** for the Fanpy Card. While the card provides the frontend UI, this integration provides the configuration wizard and generates all the necessary entities and scripts.

## Features

- ✅ **Multi-step setup wizard** — area selection, mode choice, light/features toggles, Broadlink configuration
- ✅ **Two integration modes**: Remote (Broadlink RF scripts) and Direct (native `switch.*` / `light.*` entities)
- ✅ **Automatic entity creation** (Remote): `fan.*` (power + speed), `light.*` (light), `select.*` (speed selector + timer count)
- ✅ **Automatic entity creation** (Direct): `select.*` only (speed selector + timer count) — fan/light entities managed externally
- ✅ **State persistence** — entities restore their last state after HA restart (power, speed, light)
- ✅ **Timer support** — configurable number of timer buttons (0–3), exposed via a `select.fanpy_<prefix>_num_timers` entity that the card reads at runtime. Timer entities are created manually with the native HA timer helper; the fan entity cancels active timers automatically when the fan turns off.
- ✅ **Multi-language support**: English, Spanish, Catalan
- ✅ **HACS compatible**

### Integration Modes vs Card Modes

| Mode | Description | Integration | Card entity selection | Card service calls |
|------|-------------|-------------|----------------------|-------------------|
| **Fanpy Remote** | Fanpy entities (`fan.fanpy_*`, `light.fanpy_*`, `select.fanpy_*`) + Broadlink RF scripts | Creates fan, light, select entities | Auto by prefix (`fanpy_ventilador_{area}_*`) | Calls `fan.turn_on/off`, `fan.set_percentage`, `light.turn_on/off` natively; speed via `fan.set_percentage` |
| **Fanpy Direct** | Fanpy speed select (`select.fanpy_*_velocidad`) + user's own `switch.*` / `light.*` (Shelly) | Creates only `select.fanpy_*_velocidad` | Manual (`entity_fan`, `entity_light`) | Calls `switch.turn_on/off`, `light.turn_on/off` directly; speed via scripts |

The card also supports two manual modes (Helpers and Direct) that don't require the Fanpy integration — see the [card documentation](https://github.com/figorr/fanpy-card) for details.

## Installation

### HACS (Recommended) — Not available yet

1. Open HACS.
2. Search for **Fanpy** and install it.
3. Restart Home Assistant.

### HACS (Repository method)

Install using HACS before the integration is added to the default HACS repository.

1. Open HACS within Home Assistant.
2. Select the 3-dot button (top right) and then **Custom repositories**.
3. In the dialog that appears, enter:
   - **Repository**: Add the URL to the [repository](https://github.com/figorr/fanpy) 
   - **Category**: Integration
4. Click **Add**.
5. Go to the **Search** tab of HACS and search for **Fanpy**.
6. Install it and restart Home Assistant.

### Manual

1. Download the `fanpy.zip` from the latest release.
2. Unzip and copy `custom_components/fanpy/` to your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/fanpy/
   ```
3. Restart Home Assistant.

## Usage

1. After restart, go to **Settings > Devices & Services > Add Integration**.
2. Search for **Fanpy** and select it.
3. Follow the wizard steps:

### Fanpy Remote (Broadlink RF)

- **Step 1 — Mode**: Select **Remote**
- **Step 2 — Area**: Select the area where the fan is located and choose the fan number. If you select 1, the prefix will be `ventilador_{area}`; if 2 or higher, the prefix becomes `ventilador_{area}_{N}` so each fan gets unique entity IDs.
- **Step 3 — Speeds**: Set the number of speeds (1–10)
- **Step 4 — Light**: Toggle whether the fan has a light
- **Step 5 — Light Features** (if has light): Toggle color temperature and brightness controls
- **Step 6 — Timer**: Select the number of timers (0–3). The card will show that many timer buttons and call native `timer.start`/`timer.cancel` on the timer entities you create manually with the HA timer helper.
- **Step 7 — Broadlink & Commands**: Select the Broadlink `remote.*` entity, set the remote device name, and configure all RF commands (power, light, temperature, intensity, speed levels)

This mode creates `fan.fanpy_*`, `light.fanpy_*`, `select.fanpy_*` entities. You provide the RF scripts in your `scripts.yaml` (just the `remote.send_command` action — no entity updates). Use the card in **Fanpy Remote** mode.

### Fanpy Direct (Shelly switch.* / light.*)

- **Step 1 — Mode**: Select **Direct**
- **Step 2 — Area**: Select the area where the fan is located and choose the fan number
- **Step 3 — Fan & Speeds**: Select the existing `switch.*` entity (e.g. your Shelly relay) and set the number of speeds
- **Step 4 — Light**: Toggle whether the fan has a light
- **Step 5 — Light Entity** (if has light): Select the existing `light.*` entity
- **Step 6 — Light Features** (if has light): Toggle color temperature and brightness controls
- **Step 7 — Timer**: Select the number of timers (0–3). The card will show that many timer buttons and call native `timer.start`/`timer.cancel` on the timer entities you create manually with the HA timer helper.

This mode creates only `select.fanpy_*_velocidad`. The card reads your Shelly entities directly. Use the card in **Fanpy Direct** mode.

### Card Configuration

After creating entities with the integration, add the card to your Lovelace dashboard:

```yaml
type: custom:fanpy-card
mode: fanpy_remote        # or fanpy_direct
prefix: ventilador_bodega  # auto-generated by the integration
name: BODEGA               # auto-generated by the integration
has_light: true
```

For **Fanpy Direct**, you must also specify the entity IDs:

```yaml
type: custom:fanpy-card
mode: fanpy_direct
name: BODEGA
entity_fan: switch.shelly_relay_0
entity_light: light.shelly_rgb_1
has_light: true
```

### Required Scripts

The integration **does not** generate scripts automatically. You must create the RF scripts manually in your `scripts.yaml`. Each script only needs the `remote.send_command` action — entity state updates are handled by the integration's Python code.

Make sure your `configuration.yaml` includes your scripts:

```yaml
script: !include scripts.yaml
```

Example `scripts.yaml` for a fan with 6 speeds and light:

```yaml
ventilador_salon_power_on:
  sequence:
  - action: remote.send_command
    data:
      num_repeats: 1
      delay_secs: 0.4
      hold_secs: 0
      device: ventilador_salon
      command: 'on'
    target:
      device_id: YOUR_BROADLINK_DEVICE_ID
  alias: "Ventilador Salón Power ON"
  description: ''

ventilador_salon_power_off:
  sequence:
  - action: remote.send_command
    data:
      num_repeats: 1
      delay_secs: 0.4
      hold_secs: 0
      device: ventilador_salon
      command: 'off'
    target:
      device_id: YOUR_BROADLINK_DEVICE_ID
  alias: "Ventilador Salón Power OFF"
  description: ''

ventilador_salon_luz_on:
  sequence:
  - action: remote.send_command
    data:
      num_repeats: 1
      delay_secs: 0.4
      hold_secs: 0
      device: ventilador_salon
      command: luz
    target:
      device_id: YOUR_BROADLINK_DEVICE_ID
  alias: "Ventilador Salón Luz ON"
  description: ''

ventilador_salon_luz_off:
  sequence:
  - action: remote.send_command
    data:
      num_repeats: 1
      delay_secs: 0.4
      hold_secs: 0
      device: ventilador_salon
      command: luz
    target:
      device_id: YOUR_BROADLINK_DEVICE_ID
  alias: "Ventilador Salón Luz OFF"
  description: ''

ventilador_salon_velocidad_1:
  sequence:
  - action: remote.send_command
    data:
      num_repeats: 1
      delay_secs: 0.4
      hold_secs: 0
      device: ventilador_salon
      command: 'velocidad1'
    target:
      device_id: YOUR_BROADLINK_DEVICE_ID
  alias: "Ventilador Salón Velocidad 1"
  description: ''

ventilador_salon_velocidad_2:
  sequence:
  - action: remote.send_command
    data:
      num_repeats: 1
      delay_secs: 0.4
      hold_secs: 0
      device: ventilador_salon
      command: 'velocidad2'
    target:
      device_id: YOUR_BROADLINK_DEVICE_ID
  alias: "Ventilador Salón Velocidad 2"
  description: ''
```

> Scripts for speeds 3–6 follow the same pattern (`velocidad3` through `velocidad6`). Scripts for light temperature and intensity follow the same pattern with commands `luz_fria`, `luz_calida`, `intensidad_alta`, `intensidad_baja`.

> **Why no entity updates in scripts?** The integration's `fan` and `light` entities update HA state directly in Python. The scripts only send the RF command. This makes scripts simpler and state management more reliable.

### How the flow works

When you press a button in the Fanpy Card:

#### Fanpy Remote mode

```
Card → fan.set_percentage (service)
        → FanpyFanEntity updates HA state (is_on, percentage)
        → Calls script.{prefix}_velocidad_{n} (RF only)
        → Updates select.fanpy_{prefix}_velocidad to match
```

```
Card → fan.turn_off (service)
        → FanpyFanEntity saves last speed, sets is_on=false
        → Cancels active timers (Python)
        → Calls script.{prefix}_power_off (RF only)
```

#### Fanpy Direct mode

```
Card → switch.turn_on/off (service, power)
Card → light.turn_on/off (service, light)
Card → script.{prefix}_velocidad_{n} (speed, RF only)
```

The card calls `switch.*` / `light.*` entities directly. Speed scripts send the RF command — no entity updates are needed in scripts since the integration manages speed state via `select.fanpy_{prefix}_velocidad`.

Make sure the command names match what you learned with `remote.learn_command`. You can test them with `remote.send_command`.

- **Broadlink learn command example:**

  ![Broadlink Remote Learn Command](images/broadlink_remote_learn_command.png)

- **Broadlink send command test example:**

  ![Broadlink Remote Send Command](images/broadlink_remote_send_command.png)

### Entity Naming (Fanpy Remote mode)

Each entity is created with:
- **Friendly names**: `Fanpy {Name}`, `Fanpy {Name} Luz`, `Fanpy {Name} Velocidad`
- **Entity IDs**:
  - `fan.fanpy_{prefix}` — fan power and speed (state: on/off, percentage)
  - `light.fanpy_{prefix}_luz` — light power (state: on/off)
  - `select.fanpy_{prefix}_velocidad` — speed selector (options: 1–N)
  - `select.fanpy_{prefix}_num_timers` — number of timer buttons (set via config flow)

The `fanpy_` prefix lets the card find related entities automatically.

## Reconfiguration

To change settings after initial setup:
1. Go to **Settings > Devices & Services**
2. Find the Fanpy integration entry
3. Remove and re-add it, selecting the new values

## Requirements

- Home Assistant 2025.12.5 or newer
- [Fanpy Card](https://github.com/figorr/fanpy-card) v3.0.0 or newer (for the Lovelace UI)
  - **The card**

    ![Fanpy-Card](images/fanpy-card.png)
  - **The editor**
  
    ![Fanpy-Card Visual Editor](images/fanpy-card-visual-editor.png)

    ![Fanpy-Card Editor](images/fanpy-card-editor.png)

## Development

```bash
git clone https://github.com/figorr/fanpy.git
cd fanpy
```

## Translations

To add a new language:

1. Create `custom_components/fanpy/translations/{lang}.json` with the same keys as `en.json`.
2. Submit a PR.

## License

Apache-2.0. See [LICENSE](LICENSE).
