# AutoSHiFt: Automatically redeem Gearbox SHiFT Codes

- **Compatibility:** 3.12+.
- **Platform:** Crossplatform (with enhanced Termux support).
- **Version:** 2.1.4
- **Repo:** https://github.com/Fabbi/autoshift

# Overview

Data provided by [ugoogalizer's autoshift-scraper](https://github.com/ugoogalizer/autoshift-scraper).

*This tool doesn't save your login data anywhere on your machine!*
After your first login your login-cookie (a string of seemingly random characters) is saved to the `data` folder and reused every time you use `autoshift` after that.

`autoshift` tries to prevent being blocked when it redeems too many keys at once.

You can choose to only redeem mods/skins etc, only golden keys or both. There is also a limit parameter so you don't waste your keys (there is a limit on how many bl2 keys your account can hold for example).

## Features

- **CLI Interface**: Traditional command-line interface for advanced users
- **TUI Interface**: Modern terminal user interface with interactive configuration
- **Termux Compatibility**: Enhanced support for Termux on Android devices
- **Automatic Redemption**: Schedule automatic redemption of SHiFT codes
- **Multi-Game Support**: Supports Borderlands 1, 2, 3, 4, The Pre-Sequel, Tiny Tina's Wonderlands, and Godfall
- **Multi-Platform Support**: Works with Steam, Epic Games, PlayStation Network, and Xbox Live

## Installation

### Standard Installation

You'll need to install [uv](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repo:

```sh
git clone git@github.com:Fabbi/autoshift.git
cd autoshift
```

### Termux Installation

For Termux on Android, the project includes special compatibility features:

```sh
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/Fabbi/autoshift.git
cd autoshift
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then you can run the Termux-optimized version:
```sh
python termux_runner.py
```

## Usage

### CLI Usage

- For help
```sh
uv run autoshift --help
```

- Redeem codes for Borderlands 4 on Steam (and keep redeeming every 2 hours)
```sh
uv run autoshift schedule --bl4=steam
```

- Redeem codes for Borderlands 4 on Steam using Username and Password (Use quotes for User and Password)
```sh
uv run autoshift schedule --bl4=steam --user "my@user.edu" --pass "p4ssw0rd!123"
```

- Redeem a single code
```sh
uv run autoshift redeem steam <code>
```

### TUI Usage

Start the interactive terminal user interface:

```sh
uv run autoshift-tui
```

Or using the Python module:
```sh
python -m autoshift.tui
```

The TUI provides:
- Interactive configuration of games and platforms
- Real-time status updates
- Log output display
- Scheduled redemption controls
- Credential management

### Termux Usage

On Termux, you can use the dedicated runner:

```sh
python termux_runner.py
```

Or use the executable script:
```sh
./autoshift-termux
```

### Configuration

You can configure the tool using a `.env` file. See [env.default](env.default) for all possible options.
All those options can also be set via ENV-vars and mixed how you like

Config precedence (from high to low):
- passed command-line arguments
- Environment variables
- `.env`-file entries


# Docker

Available as a docker image based on `python3.12-alpine`

## Usage

All command-line arguments can be used just like running the script directly

```
  docker run --name autoshift \
  --restart=always \
  -v autoshift:/autoshift/data \
  fabianschweinfurth/autoshift:latest schedule --user="<username>" --pass="<password>" --bl4=steam
```

Or with docker-compose:

```
services:
  autoshift:
    container_name: autoshift
    restart: always
    volumes:
      - ./autoshift:/autoshift/data
    image: fabianschweinfurth/autoshift:latest
    command: schedule --user="<username>" --pass="<password>" --bl4=steam
volumes:
  autoshift:
    external: true
    name: autoshift
networks: {}
```

# Termux-Specific Features

The application includes special enhancements for Termux on Android:

- **Optimized Data Storage**: Uses appropriate directories in Termux environment
- **Enhanced TUI**: Full-featured terminal user interface accessible on mobile
- **Environment Handling**: Automatic detection and configuration of Termux environment
- **Mobile-Friendly**: Designed to work efficiently on mobile devices with limited resources
