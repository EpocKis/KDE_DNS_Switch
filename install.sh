#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"

mkdir -p "$BIN_DIR"
mkdir -p "$AUTOSTART_DIR"

install -m 755 "$SCRIPT_DIR/dns-switcher.py" "$BIN_DIR/dns-switcher"
install -m 644 "$SCRIPT_DIR/dns-switcher.desktop" "$AUTOSTART_DIR/dns-switcher.desktop"

printf '%s\n' "DNS Switcher installed."
printf '%s\n' "Application: $BIN_DIR/dns-switcher"
printf '%s\n' "Autostart:   $AUTOSTART_DIR/dns-switcher.desktop"
printf '%s\n' ""
printf '%s\n' "Run it now with:"
printf '%s\n' "  dns-switcher"
