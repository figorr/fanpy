# Fanpy

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

Custom integration for Home Assistant to configure ceiling fans for use with the [Fan Custom Card](https://github.com/figorr/fan-custom-card) Lovelace card.

## Purpose

Fanpy is the **backend companion** for the Fan Custom Card. While the card provides the frontend UI, this integration provides the configuration wizard and generates all the necessary entities and scripts.

## Features

- ✅ **Multi-step setup wizard** — area selection, mode choice, light/features toggles, Broadlink configuration
- ✅ **Two modes**: Remote (Broadlink RF scripts) and Direct (native `switch.*` / `light.*` entities)
- ✅ **Automatic entity creation**: `switch.*` (power, light), `select.*` (speed), `binary_sensor.*` (state for card), `button.*` (manual triggers)
- ✅ **YAML generation** — generates `scripts.yaml` with all RF commands ready to copy
- ✅ **Multi-language support**: English, Spanish, Catalan
- ✅ **HACS compatible**

## Installation

### HACS (Recommended)

1. Open HACS.
2. Search for **Fanpy** and install it.
3. Restart Home Assistant.

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

   **All modes:**
   - **Step 1 — Mode**: Choose Remote (Broadlink RF) or Direct (switch.\* / light.\*)
   - **Step 2 — Area**: Select the area where the fan is located and choose the fan number. If you select 1, the prefix will be `ventilador_{area}`; if 2 or higher, the prefix becomes `ventilador_{area}_{N}` so each fan gets unique entity IDs.

   **Direct mode:**
   - **Step 3 — Fan & Speeds**: Select the existing `switch.*` entity and set the number of speeds
   - **Step 4 — Light**: Toggle whether the fan has a light
   - **Step 5 — Light Entity** (if has light): Select the existing `light.*` entity
   - **Step 6 — Light Features** (if has light): Toggle color temperature and brightness controls

   **Remote mode:**
   - **Step 3 — Speeds**: Set the number of speeds (1–10)
   - **Step 4 — Light**: Toggle whether the fan has a light
   - **Step 5 — Light Features** (if has light): Toggle color temperature and brightness controls
   - **Step 6 — Broadlink & Commands**: Select the Broadlink `remote.*` entity, set the remote device name, and configure all RF commands (power, light, temperature, intensity, and each speed level)

4. The integration creates all entities automatically. In Remote mode, RF scripts are saved for manual copy.

### Generated Files

After setup in Remote mode, check `custom_components/fanpy/generated/scripts.yaml` for the complete Broadlink RF scripts. Copy its content into your Home Assistant `scripts.yaml` to activate RF commands.

### Entity Naming

Each entity is created with:
- **Friendly name**: `Fanpy Ventilador {Area} Power` (you can edit the "Fanpy" prefix off later in Settings → Entities)
- **Entity ID**: `switch.fanpy_ventilador_{area}_power` — the `fanpy_` prefix lets the card find related entities automatically

## Configuration Options

After setup, you can modify options via **Settings > Devices & Services > Fanpy > Configure**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `has_light` | boolean | `true` | Show/hide the light section |
| `has_light_temperature` | boolean | `true` (remote) / `false` (direct) | Show/hide color temperature buttons |
| `has_light_intensity` | boolean | `true` (remote) / `false` (direct) | Show/hide brightness buttons |

## Requirements

- Home Assistant 2025.12.5 or newer
- [Fan Custom Card](https://github.com/figorr/fan-custom-card) (for the Lovelace UI)

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
