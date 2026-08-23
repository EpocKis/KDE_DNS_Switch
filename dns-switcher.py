#!/usr/bin/env python3

import sys
import subprocess

from PyQt6.QtCore import QByteArray, QTimer, QRectF, Qt
from PyQt6.QtGui import QAction, QIcon, QPainter, QPixmap, QCursor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


# ============================================================
# DNS PROVIDERS
# ============================================================

DNS_PROVIDERS = {
    "automatic": {
        "name": "Automatic (DHCP)",
        "description": "Use DNS provided by your network",
        "ipv4": "",
        "ipv6": "",
    },

    "cloudflare": {
        "name": "Cloudflare",
        "description": "Fast, general-purpose DNS",
        "ipv4": "1.1.1.1 1.0.0.1",
        "ipv6": "2606:4700:4700::1111 2606:4700:4700::1001",
    },

    "google": {
        "name": "Google",
        "description": "Fast, general-purpose DNS",
        "ipv4": "8.8.8.8 8.8.4.4",
        "ipv6": "2001:4860:4860::8888 2001:4860:4860::8844",
    },

    "quad9": {
        "name": "Quad9",
        "description": "Blocks known malicious domains",
        "ipv4": "9.9.9.9 149.112.112.112",
        "ipv6": "2620:fe::fe 2620:fe::9",
    },

    "adguard": {
        "name": "AdGuard",
        "description": "Blocks ads and trackers",
        "ipv4": "94.140.14.14 94.140.15.15",
        "ipv6": "2a10:50c0::ad1:ff 2a10:50c0::ad2:ff",
    },

    "mullvad": {
        "name": "Mullvad",
        "description": "Standard, no filtering",
        "ipv4": "194.242.2.2",
        "ipv6": "2a07:e340::2",
    },

    "mullvad_adblock": {
        "name": "Mullvad AdBlock",
        "description": "Blocks ads and trackers",
        "ipv4": "194.242.2.3",
        "ipv6": "2a07:e340::3",
    },

    "mullvad_base": {
        "name": "Mullvad Base",
        "description": "Blocks ads, trackers and malware",
        "ipv4": "194.242.2.4",
        "ipv6": "2a07:e340::4",
    },

    "mullvad_extended": {
        "name": "Mullvad Extended",
        "description": "Blocks ads, trackers, malware and social media",
        "ipv4": "194.242.2.5",
        "ipv6": "2a07:e340::5",
    },

    "controld": {
        "name": "Control D",
        "description": "Unfiltered DNS",
        "ipv4": "76.76.2.0 76.76.10.0",
        "ipv6": "2606:1a40:: 2606:1a40:1::",
    },

    "cleanbrowsing_security": {
        "name": "CleanBrowsing Security",
        "description": "Malware and phishing protection",
        "ipv4": "185.228.168.9 185.228.169.9",
        "ipv6": "2a0d:2a00:1::2 2a0d:2a00:2::2",
    },

    "cleanbrowsing_family": {
        "name": "CleanBrowsing Family",
        "description": "Security + adult content blocking",
        "ipv4": "185.228.168.168 185.228.169.168",
        "ipv6": "2a0d:2a00:1:: 2a0d:2a00:2::",
    },
}


# ============================================================
# TRAY ICON
# ============================================================

DNS_ICON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg"
     width="64"
     height="64"
     viewBox="0 0 64 64">

    <!-- Main DNS/server stack -->

    <rect x="10" y="11"
          width="44" height="12"
          rx="4"
          fill="#3daee9"/>

    <circle cx="19" cy="17"
            r="2.5"
            fill="#ffffff"/>

    <circle cx="27" cy="17"
            r="2.5"
            fill="#ffffff"/>

    <rect x="10" y="26"
          width="44" height="12"
          rx="4"
          fill="#d8dee9"/>

    <circle cx="19" cy="32"
            r="2.5"
            fill="#30343b"/>

    <circle cx="27" cy="32"
            r="2.5"
            fill="#30343b"/>

    <rect x="10" y="41"
          width="44" height="12"
          rx="4"
          fill="#d8dee9"/>

    <circle cx="19" cy="47"
            r="2.5"
            fill="#30343b"/>

    <circle cx="27" cy="47"
            r="2.5"
            fill="#30343b"/>

    <!-- Small DNS/status indicator -->

    <circle cx="48"
            cy="47"
            r="7"
            fill="#3daee9"
            stroke="#202328"
            stroke-width="2"/>

    <path d="M44.5 47
             l2.2 2.2
             l4.5 -5"
          fill="none"
          stroke="#ffffff"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"/>
</svg>
"""


def create_tray_icon():
    renderer = QSvgRenderer(
        QByteArray(
            DNS_ICON_SVG.encode("utf-8")
        )
    )

    pixmap = QPixmap(64, 64)

    pixmap.fill(
        Qt.GlobalColor.transparent
    )

    painter = QPainter(pixmap)

    painter.setRenderHint(
        QPainter.RenderHint.Antialiasing
    )

    renderer.render(
        painter,
        QRectF(0, 0, 64, 64)
    )

    painter.end()

    return QIcon(pixmap)


# ============================================================
# COMMAND HELPERS
# ============================================================

def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        return (
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )

    except Exception:
        return 1, "", ""


# ============================================================
# NETWORKMANAGER
# ============================================================

def get_active_connection():
    code, output, _ = run_command([
        "nmcli",
        "-t",
        "-f",
        "NAME,TYPE",
        "connection",
        "show",
        "--active",
    ])

    if code != 0:
        return None

    for line in output.splitlines():

        parts = line.rsplit(":", 1)

        if len(parts) != 2:
            continue

        name, connection_type = parts

        if connection_type in (
            "802-3-ethernet",
            "wifi",
        ):
            return name

    return None


def get_active_dns():
    code, output, _ = run_command([
        "nmcli",
        "dev",
        "show",
    ])

    if code != 0:
        return set()

    dns = set()

    for line in output.splitlines():

        if "DNS" not in line:
            continue

        if ":" not in line:
            continue

        value = line.split(
            ":",
            1
        )[1].strip()

        if value:
            dns.add(value)

    return dns


def get_current_provider():
    active_dns = get_active_dns()

    if not active_dns:
        return "automatic"

    for key, provider in DNS_PROVIDERS.items():

        if key == "automatic":
            continue

        configured = set(
            provider["ipv4"].split()
            + provider["ipv6"].split()
        )

        if configured and configured.issubset(
            active_dns
        ):
            return key

    return "automatic"


# ============================================================
# DNS SWITCHING
# ============================================================

def apply_dns(provider_key):

    connection = get_active_connection()

    if not connection:
        return False

    provider = DNS_PROVIDERS[
        provider_key
    ]

    if provider_key == "automatic":

        command = [
            "nmcli",
            "connection",
            "modify",
            connection,

            "ipv4.dns",
            "",

            "ipv4.ignore-auto-dns",
            "no",

            "ipv6.dns",
            "",

            "ipv6.ignore-auto-dns",
            "no",
        ]

    else:

        command = [
            "nmcli",
            "connection",
            "modify",
            connection,

            "ipv4.dns",
            provider["ipv4"],

            "ipv4.ignore-auto-dns",
            "yes",

            "ipv6.dns",
            provider["ipv6"],

            "ipv6.ignore-auto-dns",
            "yes",
        ]

    code, _, _ = run_command(
        command
    )

    if code != 0:
        return False

    code, _, _ = run_command([
        "nmcli",
        "connection",
        "up",
        connection,
    ])

    return code == 0


# ============================================================
# TRAY APPLICATION
# ============================================================

class DnsTray:

    def __init__(self, app):

        self.app = app

        self.tray = QSystemTrayIcon()

        self.tray.setIcon(
            create_tray_icon()
        )

        self.tray.setToolTip(
            "DNS Switcher"
        )

        # ----------------------------------------------------
        # IMPORTANT
        #
        # Let QSystemTrayIcon handle the native right-click
        # menu. This makes KDE handle right-click correctly.
        # Left-click is handled separately below.
        # ----------------------------------------------------

        self.menu = QMenu()

        self.tray.setContextMenu(
            self.menu
        )

        self.build_menu()

        self.tray.activated.connect(
            self.tray_activated
        )

        self.tray.show()

        # Refresh every 3 seconds.
        self.refresh_timer = QTimer()

        self.refresh_timer.timeout.connect(
            self.refresh
        )

        self.refresh_timer.start(3000)

    # ========================================================
    # MENU
    # ========================================================

    def build_menu(self):

        self.menu.clear()

        connection = get_active_connection()

        current_provider = get_current_provider()

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = QAction(
            "DNS Switcher",
            self.menu
        )

        header.setEnabled(False)

        font = header.font()
        font.setBold(True)

        header.setFont(font)

        self.menu.addAction(
            header
        )

        # ----------------------------------------------------
        # Connection
        # ----------------------------------------------------

        if connection:

            connection_action = QAction(
                f"Connection: {connection}",
                self.menu
            )

        else:

            connection_action = QAction(
                "No active connection",
                self.menu
            )

        connection_action.setEnabled(
            False
        )

        self.menu.addAction(
            connection_action
        )

        self.menu.addSeparator()

        # ----------------------------------------------------
        # DNS providers
        # ----------------------------------------------------

        for key, provider in DNS_PROVIDERS.items():

            action = QAction(
                f"{provider['name']} — "
                f"{provider['description']}",
                self.menu
            )

            action.setCheckable(
                True
            )

            action.setChecked(
                key == current_provider
            )

            action.triggered.connect(
                lambda checked=False,
                provider_key=key:
                self.change_dns(
                    provider_key
                )
            )

            self.menu.addAction(
                action
            )

        self.menu.addSeparator()

        # ----------------------------------------------------
        # Refresh
        # ----------------------------------------------------

        refresh_action = QAction(
            "Refresh",
            self.menu
        )

        refresh_action.triggered.connect(
            self.refresh
        )

        self.menu.addAction(
            refresh_action
        )

        self.menu.addSeparator()

        # ----------------------------------------------------
        # Quit
        # ----------------------------------------------------

        quit_action = QAction(
            "Quit",
            self.menu
        )

        quit_action.triggered.connect(
            self.app.quit
        )

        self.menu.addAction(
            quit_action
        )

    # ========================================================
    # LEFT CLICK
    # ========================================================

    def tray_activated(
        self,
        reason
    ):

        if reason == (
            QSystemTrayIcon
            .ActivationReason
            .Trigger
        ):

            self.show_menu()

    # ========================================================
    # SHOW MENU
    # ========================================================

    def show_menu(self):

        self.build_menu()

        # Position the menu above the tray icon.
        position = QCursor.pos()

        self.menu.popup(
            position
        )

    # ========================================================
    # CHANGE DNS
    # ========================================================

    def change_dns(
        self,
        provider_key
    ):

        provider = DNS_PROVIDERS[
            provider_key
        ]

        success = apply_dns(
            provider_key
        )

        if success:

            self.tray.showMessage(
                "DNS Switcher",
                f"DNS changed to "
                f"{provider['name']}",
                QSystemTrayIcon
                .MessageIcon
                .Information,
                2000
            )

        else:

            self.tray.showMessage(
                "DNS Switcher",
                "Failed to change DNS.",
                QSystemTrayIcon
                .MessageIcon
                .Critical,
                3000
            )

        self.build_menu()

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(self):

        if self.menu.isVisible():
            return

        self.build_menu()


# ============================================================
# MAIN
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "DNS Switcher"
    )

    app.setQuitOnLastWindowClosed(
        False
    )

    if not QSystemTrayIcon.isSystemTrayAvailable():

        print(
            "System tray is not available."
        )

        sys.exit(1)

    DnsTray(app)

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
