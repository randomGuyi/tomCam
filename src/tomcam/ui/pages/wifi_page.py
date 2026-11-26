from tomcam.config import theme
from tomcam.services.wifi_manager import WifiManager
from tomcam.ui.components.button import Button
from tomcam.ui.components.header import draw_header
from tomcam.ui.components.touch_keyboard import TouchKeyboard
from tomcam.ui.pages.base_page import BasePage


class WifiPage(BasePage):
    MAX_VISIBLE_NETWORKS = 5

    def __init__(self, app):
        super().__init__(app)
        self.wifi = WifiManager()
        self.keyboard = TouchKeyboard()
        self.networks = []
        self.selected_network = None
        self.wifi_enabled = None
        self.status = "Scan for nearby networks to get started"
        self._controls = []

        try:
            self.wifi_enabled = self.wifi.is_wifi_enabled()
        except Exception as exc:
            self.status = f"Wi-Fi status unavailable: {exc}"

        self._update_controls()

    def _update_controls(self):
        network_buttons = []
        if not self.keyboard.visible:
            for index, network in enumerate(
                self.networks[:self.MAX_VISIBLE_NETWORKS]
            ):
                label = f"{network.ssid[:22]}  {network.signal}%"
                if network.connected:
                    label += "  Connected"
                elif network.security and network.security != "--":
                    label += "  Locked"
                network_buttons.append(
                    Button(
                        f"network:{index}",
                        label,
                        (42, 155 + index * 45, 716, 39),
                    )
                )

        if self.keyboard.visible:
            actions = [
                Button("connect", "Connect", (42, 422, 300, 48)),
                Button("back", "Cancel", (458, 422, 300, 48)),
            ]
        elif self.selected_network is not None:
            actions = [
                Button("scan", "Scan", (42, 422, 150, 48)),
                Button(
                    "toggle",
                    "Wi-Fi Off" if self.wifi_enabled else "Wi-Fi On",
                    (207, 422, 170, 48),
                ),
                Button("connect", "Connect", (392, 422, 170, 48)),
                Button("back", "Back", (577, 422, 181, 48)),
            ]
        else:
            actions = [
                Button("scan", "Scan", (42, 422, 205, 48)),
                Button(
                    "toggle",
                    "Wi-Fi Off" if self.wifi_enabled else "Wi-Fi On",
                    (270, 422, 240, 48),
                ),
                Button("back", "Back", (533, 422, 225, 48)),
            ]
        self._controls = network_buttons + actions
        self.focus_index = min(
            self.focus_index,
            max(0, len(self._controls) - 1),
        )

    @property
    def controls(self):
        return self._controls

    def activate(self, key):
        if key.startswith("network:"):
            index = int(key.split(":", 1)[1])
            self._select_network(self.networks[index])
        elif key == "scan":
            self.scan()
        elif key == "toggle":
            self.toggle_wifi()
        elif key == "connect":
            self.connect()
        elif key == "back":
            if self.keyboard.visible:
                self.keyboard.close()
                self._update_controls()
            else:
                self.app.navigation.show_settings()

    def go_back(self):
        if self.keyboard.visible:
            self.keyboard.close()
            self._update_controls()
        else:
            self.app.navigation.show_settings()

    def handle_touch(self, event):
        if (
            self.keyboard.visible
            and event.type == 1792
            and self.keyboard.handle_touch(
                int(event.tfinger.x * theme.WIDTH),
                int(event.tfinger.y * theme.HEIGHT),
            )
        ):
            return
        super().handle_touch(event)

    def scan(self):
        self.status = "Scanning for Wi-Fi networks..."
        self._update_controls()
        try:
            self.networks = self.wifi.scan()
            self.status = (
                f"Found {len(self.networks)} network(s)"
                if self.networks
                else "No networks found"
            )
        except Exception as exc:
            self.status = f"Wi-Fi scan failed: {exc}"
        self._update_controls()

    def toggle_wifi(self):
        try:
            enabled = self.wifi.is_wifi_enabled()
            self.wifi.set_wifi_enabled(not enabled)
            self.wifi_enabled = not enabled
            self.status = (
                "Wi-Fi enabled" if self.wifi_enabled else "Wi-Fi disabled"
            )
            if not self.wifi_enabled:
                self.networks = []
        except Exception as exc:
            self.status = f"Could not change Wi-Fi state: {exc}"
        self._update_controls()

    def _select_network(self, network):
        self.selected_network = network
        self.keyboard.close()
        protected = bool(
            network.security
            and network.security.strip() not in ("--", "")
        )
        try:
            saved = self.wifi.get_saved_connections()
            if protected and network.ssid not in saved:
                self.keyboard.open()
                self.status = "Enter the Wi-Fi password"
            else:
                self.status = f"Selected {network.ssid}"
        except Exception as exc:
            if protected:
                self.keyboard.open()
                self.status = f"Enter password; saved profiles unavailable: {exc}"
            else:
                self.status = f"Selected {network.ssid}"
        self._update_controls()

    def connect(self):
        if self.selected_network is None:
            self.status = "Select a network first"
            return

        password = self.keyboard.get_value()
        try:
            self.wifi.connect(
                self.selected_network.ssid,
                password=password,
                security=self.selected_network.security,
            )
            self.keyboard.close()
            self.wifi_enabled = True
            self.status = f"Connected to {self.selected_network.ssid}"
        except Exception as exc:
            self.status = f"Could not connect: {exc}"
        self._update_controls()

    def draw(self, app):
        draw_header(app, "Wi-Fi & Networks")
        wifi_status = (
            "Unavailable"
            if self.wifi_enabled is None
            else "On" if self.wifi_enabled else "Off"
        )
        app.render_text(
            f"Wi-Fi: {wifi_status}",
            44,
            109,
            theme.MUTED,
            18,
        )
        app.render_text(self.status[:86], 44, 129, theme.MUTED, 18)

        if self.keyboard.visible:
            selected = self.selected_network.ssid if self.selected_network else ""
            app.render_text(
                f"Network: {selected[:32]}", 44, 163, theme.TEXT, 18
            )
            password = self.keyboard.get_value()
            app.render_text(
                f"Password: {'*' * len(password)}",
                44,
                184,
                theme.TEXT,
                18,
            )
            self.keyboard.draw(app)
        else:
            for index, button in enumerate(self.controls):
                if button.key.startswith("network:"):
                    button.draw(
                        app,
                        selected=index == self.focus_index,
                        compact=True,
                    )

        for index, button in enumerate(self.controls):
            if not button.key.startswith("network:"):
                button.draw(
                    app,
                    selected=index == self.focus_index,
                    compact=True,
                )
