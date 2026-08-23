# DNS Switcher

A lightweight DNS switcher for Linux using NetworkManager (`nmcli`) and a KDE/Qt system tray interface.

## Features

- KDE system tray application
- Switch DNS providers directly from the tray
- IPv4 and IPv6 support
- Automatic (DHCP) mode
- Cloudflare
- Google
- Quad9
- AdGuard
- Mullvad
- Mullvad AdBlock
- Mullvad Base
- Mullvad Extended
- Control D
- CleanBrowsing Security
- CleanBrowsing Family
- Detects the currently configured DNS provider
- Uses NetworkManager for DNS changes
- KDE autostart support

## Requirements

- Linux
- NetworkManager
- `nmcli`
- Python 3
- PyQt6

### Arch Linux / CachyOS

```bash
sudo pacman -S networkmanager python-pyqt6
```

Check NetworkManager:

```bash
systemctl is-active NetworkManager
```

It should return:

```text
active
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Epockis/KDE_DNS_Switch.git
cd dns-switcher
```

Install:

```bash
./install.sh
```

The installer places:

```text
~/.local/bin/dns-switcher
~/.config/autostart/dns-switcher.desktop
```

Start it immediately:

```bash
dns-switcher
```

After the next KDE login, DNS Switcher will start automatically.

## DNS Providers

| Provider | Description |
|---|---|
| Automatic (DHCP) | Use DNS provided by the network |
| Cloudflare | Fast, general-purpose DNS |
| Google | Fast, general-purpose DNS |
| Quad9 | Blocks known malicious domains |
| AdGuard | Blocks ads and trackers |
| Mullvad | Standard, no filtering |
| Mullvad AdBlock | Blocks ads and trackers |
| Mullvad Base | Blocks ads, trackers and malware |
| Mullvad Extended | Blocks ads, trackers, malware and social media |
| Control D | Unfiltered DNS |
| CleanBrowsing Security | Malware and phishing protection |
| CleanBrowsing Family | Security + adult content blocking |

## Usage

After starting the application, a DNS Switcher icon appears in the KDE system tray.

Select a provider from the menu to apply its IPv4 and IPv6 DNS servers to the active NetworkManager connection.

Selecting **Automatic (DHCP)** restores DNS supplied automatically by the network.

## Project layout

```text
dns-switcher/
├── dns-switcher.py
├── dns-switcher.desktop
├── install.sh
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Development

Run the application directly:

```bash
python dns-switcher.py
```

No virtual environment is required for the intended Arch Linux / CachyOS installation.

## License

This repository currently uses a restrictive all-rights-reserved license.
Change `LICENSE` before publishing if you want to use an open-source license such as MIT or GPL.
