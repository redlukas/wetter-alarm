# Wetter-Alarm

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]
[![Validate with Hassfest][hassfest-badge]][hassfest]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

**This component will set up the following platforms.**

| Platform | Description                      |
| -------- | -------------------------------- |
| `sensor` | Show info from Wetter-Alarm API. |

## Overview

Wetter-Alarm is an app that alerts you of severe weather events in Switzerland.
This Integration will poll the [Wetter-Alarm](https://wetteralarm.ch/) API and expose the available Alerts to Home Assistant.

## Installation

### Automated (suggested):

Just click here: [![Open in HACS.][my-hacs-badge]][open-in-hacs]

### Manual:

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `wetter_alarm`.
4. Download _all_ the files from the `custom_components/wetter_alarm/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/wetter_alarm/__init__.py
custom_components/wetter_alarm/api.py
custom_components/wetter_alarm/config_flow.py
custom_components/wetter_alarm/const.py
custom_components/wetter_alarm/coordinator.py
custom_components/wetter_alarm/data.py
custom_components/wetter_alarm/entity.py
custom_components/wetter_alarm/manifest.json
custom_components/wetter_alarm/sensor.py
custom_components/wetter_alarm/translations/en.json
```

## Configuration

No matter which way you installed the Integration, you need to restart Home Assistant before configuring the integration.

Go to the `Settings -> Devices & Services -> Integrations` tab of your Home Assistant instance.
Click `ADD INTEGRATION` and search for "Wetter-Alarm".
The Configuration flow will start when you click install.

## How to find the ID of your location

### Method 1

Go to  [https://redlukas.github.io/poi-presenter/],
select the desired canton and find the location on the map.

### Method 2

Look at [the POIs folder]( POIs) in this repo.
In there you'll find a JSON with all the POIs
as well as a site for each Canton where the POIs are listed by kind.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/redlukas/wetter-alarm.svg
[commits]: https://github.com/redlukas/wetter-alarm/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Default-green.svg
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=flat&logo=discord
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/redlukas/wetter-alarm.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40redlukas-blue.svg
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen
[releases-shield]: https://img.shields.io/github/release/redlukas/wetter-alarm.svg
[releases]: https://github.com/redlukas/wetter-alarm/releases
[user_profile]: https://github.com/redlukas
[hassfest-badge]: https://github.com/redlukas/wetter-alarm/actions/workflows/hassfest.yml/badge.svg
[hassfest]: https://developers.home-assistant.io/blog/2020/04/16/hassfest/
[open-in-hacs]: https://my.home-assistant.io/redirect/hacs_repository/?owner=redlukas&repository=wetter-alarm&category=integration
[my-hacs-badge]: https://my.home-assistant.io/badges/hacs_repository.svg
[overviewimg]: ./images/overview.png
[metersimg]: ./images/meters.png
