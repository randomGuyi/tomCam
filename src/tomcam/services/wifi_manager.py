from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile
import os


@dataclass
class WifiNetwork:
    ssid: str
    signal: int
    security: str
    connected: bool = False


class WifiManager:
    def __init__(self, interface="wlan0"):
        self.interface = interface

    def _run(self, command, timeout=30):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                result.stderr.strip() or "NetworkManager command failed"
            )

        return result.stdout.strip()

    @staticmethod
    def _parse_nmcli_line(line):
        """Split nmcli's escaped, colon-separated output."""
        fields = []
        current = []
        escaped = False

        for char in line:
            if escaped:
                current.append(char)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == ":":
                fields.append("".join(current))
                current = []
            else:
                current.append(char)

        if escaped:
            current.append("\\")

        fields.append("".join(current))
        return fields

    def is_wifi_enabled(self):
        result = self._run(["nmcli", "radio", "wifi"])
        return result.lower() == "enabled"

    def set_wifi_enabled(self, enabled):
        self._run([
            "nmcli",
            "radio",
            "wifi",
            "on" if enabled else "off",
        ])

    def scan(self):
        self.set_wifi_enabled(True)

        output = self._run([
            "nmcli",
            "--terse",
            "--escape", "yes",
            "--fields", "SSID,SIGNAL,SECURITY,IN-USE",
            "device", "wifi", "list",
            "--rescan", "yes",
            "ifname", self.interface,
        ], timeout=40)

        networks = {}

        for line in output.splitlines():
            fields = self._parse_nmcli_line(line)

            if len(fields) != 4:
                continue

            ssid, signal, security, in_use = fields

            # Hidden networks have no readable SSID.
            if not ssid:
                continue

            try:
                signal = int(signal)
            except ValueError:
                signal = 0

            network = WifiNetwork(
                ssid=ssid,
                signal=signal,
                security=security,
                connected=in_use == "*",
            )

            # Avoid showing duplicate access points for one SSID.
            previous = networks.get(ssid)
            if previous is None or signal > previous.signal:
                networks[ssid] = network

        return sorted(
            networks.values(),
            key=lambda network: (
                network.connected,
                network.signal,
            ),
            reverse=True,
        )

    def get_saved_connections(self):
        output = self._run([
            "nmcli",
            "--terse",
            "--escape", "yes",
            "--fields", "NAME,TYPE",
            "connection",
            "show",
        ])

        saved = {}

        for line in output.splitlines():
            fields = self._parse_nmcli_line(line)

            if len(fields) != 2 or fields[1] != "802-11-wireless":
                continue

            connection_name = fields[0]

            try:
                ssid = self._run([
                    "nmcli",
                    "--get-values",
                    "802-11-wireless.ssid",
                    "connection",
                    "show",
                    connection_name,
                ])
            except RuntimeError:
                continue

            if ssid:
                saved[ssid] = connection_name

        return saved

    def connect(self, ssid, password=None, security=""):
        if not ssid:
            raise ValueError("SSID cannot be empty")

        saved = self.get_saved_connections()

        # A saved connection does not need a password again.
        if ssid in saved:
            self._run([
                "nmcli",
                "connection",
                "up",
                "id",
                saved[ssid],
            ], timeout=60)
            return

        protected = bool(security and security.strip() not in ("--", ""))

        if protected and not password:
            raise ValueError("A Wi-Fi password is required")

        if protected and ("\n" in password or "\r" in password):
            raise ValueError("Invalid password")

        connection_name = f"TomCam - {ssid}"

        command = [
            "nmcli",
            "connection",
            "add",
            "type", "wifi",
            "ifname", self.interface,
            "con-name", connection_name,
            "ssid", ssid,
            "connection.autoconnect", "yes",
        ]

        if protected:
            # WPA/WPA2 Personal. Enterprise networks need
            # additional 802.1X configuration.
            command.extend([
                "wifi-sec.key-mgmt", "wpa-psk",
                "wifi-sec.psk-flags", "0",
            ])

        self._run(command)

        try:
            if not protected:
                self._run([
                    "nmcli",
                    "connection",
                    "up",
                    "id",
                    connection_name,
                ], timeout=60)
                return

            # Supply the password through a temporary,
            # permission-restricted file instead of putting
            # it directly into the process command arguments.
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix="tomcam-wifi-",
                delete=False,
            ) as secret_file:
                secret_path = Path(secret_file.name)
                os.chmod(secret_path, 0o600)

                secret_file.write(
                    "802-11-wireless-security.psk:"
                    + password
                    + "\n"
                )

            try:
                self._run([
                    "nmcli",
                    "connection",
                    "up",
                    "id",
                    connection_name,
                    "passwd-file",
                    str(secret_path),
                ], timeout=60)
            finally:
                secret_path.unlink(missing_ok=True)

        except Exception:
            # Remove an unsuccessful new profile.
            try:
                self._run([
                    "nmcli",
                    "connection",
                    "delete",
                    "id",
                    connection_name,
                ])
            except RuntimeError:
                pass
            raise

    def get_status(self):
        output = self._run([
            "nmcli",
            "--terse",
            "--escape", "yes",
            "--fields", "TYPE,STATE,CONNECTION",
            "device", "status",
        ])

        for line in output.splitlines():
            fields = self._parse_nmcli_line(line)

            if len(fields) == 3 and fields[0] == "wifi":
                return {
                    "state": fields[1],
                    "connection": fields[2],
                }

        return {
            "state": "unavailable",
            "connection": None,
        }

