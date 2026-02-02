#!/usr/bin/env python
"""
Textual TUI for AutoSHiFt - A tool to automatically redeem Gearbox SHiFT codes.
This provides a user-friendly terminal interface for configuring and running the application.
"""

from typing import Dict
from rich.panel import Panel
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Label,
    Static,
    Switch,
    Input,
    TextArea
)
from textual.screen import ModalScreen, Screen

from autoshift.manual_code_screen import ManualCodeScreen, redeem_single_code

from autoshift.common import Game, Platform, settings
from autoshift.auto import main as run_main, auto_redeem_codes


class SettingsScreen(ModalScreen[Dict]):
    """Modal screen for configuring application settings."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
    ]

    def __init__(self, current_settings: Dict = None):
        super().__init__()
        self.current_settings = current_settings or {}

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Settings", classes="title"),

            VerticalScroll(
                Label("Email:"),
                Input(
                    placeholder="Email",
                    id="user-input",
                    value=self.current_settings.get('USER', '') or ''
                ),
                Label("Password:"),
                Input(
                    placeholder="Password",
                    id="password-input",
                    password=True,
                    value=self.current_settings.get('PASS', '') or ''
                ),

                Label("Games:", classes="section-title"),
                Checkbox("BL1", id="game-bl1", value=Game.bl1 in self.current_settings.get('_GAMES_PLATFORM_MAP', {}) and bool(self.current_settings['_GAMES_PLATFORM_MAP'].get(Game.bl1, set()))),
                Checkbox("BL2", id="game-bl2", value=Game.bl2 in self.current_settings.get('_GAMES_PLATFORM_MAP', {}) and bool(self.current_settings['_GAMES_PLATFORM_MAP'].get(Game.bl2, set()))),
                Checkbox("BL3", id="game-bl3", value=Game.bl3 in self.current_settings.get('_GAMES_PLATFORM_MAP', {}) and bool(self.current_settings['_GAMES_PLATFORM_MAP'].get(Game.bl3, set()))),
                Checkbox("BL4", id="game-bl4", value=Game.bl4 in self.current_settings.get('_GAMES_PLATFORM_MAP', {}) and bool(self.current_settings['_GAMES_PLATFORM_MAP'].get(Game.bl4, set()))),
                Checkbox("BLPS", id="game-blps", value=Game.blps in self.current_settings.get('_GAMES_PLATFORM_MAP', {}) and bool(self.current_settings['_GAMES_PLATFORM_MAP'].get(Game.blps, set()))),
                Checkbox("TTW", id="game-ttw", value=Game.ttw in self.current_settings.get('_GAMES_PLATFORM_MAP', {}) and bool(self.current_settings['_GAMES_PLATFORM_MAP'].get(Game.ttw, set()))),
                Checkbox("GDFLL", id="game-gdfll", value=Game.gdfll in self.current_settings.get('_GAMES_PLATFORM_MAP', {}) and bool(self.current_settings['_GAMES_PLATFORM_MAP'].get(Game.gdfll, set()))),

                Label("Platforms:", classes="section-title"),
                Checkbox("Steam", id="platform-steam", value=Platform.steam in self.current_settings.get('PLATFORMS', [])),
                Checkbox("Epic", id="platform-epic", value=Platform.epic in self.current_settings.get('PLATFORMS', [])),
                Checkbox("PSN", id="platform-psn", value=Platform.psn in self.current_settings.get('PLATFORMS', [])),
                Checkbox("Xbox", id="platform-xboxlive", value=Platform.xboxlive in self.current_settings.get('PLATFORMS', [])),

                Label("Interval (min):"),
                Input(
                    placeholder="Interval",
                    id="interval-input",
                    value=str(self.current_settings.get('SCHEDULE', 120) or 120)
                ),

                Label("Limit:"),
                Input(
                    placeholder="Limit",
                    id="limit-input",
                    value=str(self.current_settings.get('LIMIT', 255) or 255)
                ),

                Label("Verbose:"),
                Switch(
                    value=self.current_settings.get('VERBOSE', False),
                    id="verbose-switch"
                ),

                Label("Theme:"),
                Input(
                    placeholder="Theme (e.g., textual-default, catppuccin-mocha)",
                    id="theme-input",
                    value=self.current_settings.get('THEME', 'textual-default')
                ),
            ),  # End of VerticalScroll

            Horizontal(
                Button("Save", variant="primary", id="save-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                id="settings-buttons"
            ),
            id="settings-content"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            # Collect settings from the form
            new_settings = {
                'USER': self.query_one("#user-input", Input).value,
                'PASS': self.query_one("#password-input", Input).value,
                'SCHEDULE': int(self.query_one("#interval-input", Input).value) if self.query_one("#interval-input", Input).value.isdigit() else 120,
                'LIMIT': int(self.query_one("#limit-input", Input).value) if self.query_one("#limit-input", Input).value.isdigit() else 255,
                'THEME': self.query_one("#theme-input", Input).value,  # Get theme from input
                'VERBOSE': self.query_one("#verbose-switch", Switch).value,
                '_GAMES_PLATFORM_MAP': {},
                'PLATFORMS': []
            }

            # Collect selected games using the new simplified IDs
            game_checkboxes = {
                'bl1': Game.bl1,
                'bl2': Game.bl2,
                'bl3': Game.bl3,
                'bl4': Game.bl4,
                'blps': Game.blps,
                'ttw': Game.ttw,
                'gdfll': Game.gdfll
            }

            for id_suffix, game in game_checkboxes.items():
                checkbox = self.query_one(f"#game-{id_suffix}", Checkbox)
                if checkbox.value:
                    new_settings['_GAMES_PLATFORM_MAP'][game] = set()

            # Collect selected platforms using the new simplified IDs
            platform_checkboxes = {
                'steam': Platform.steam,
                'epic': Platform.epic,
                'psn': Platform.psn,
                'xboxlive': Platform.xboxlive
            }

            for id_suffix, platform in platform_checkboxes.items():
                checkbox = self.query_one(f"#platform-{id_suffix}", Checkbox)
                if checkbox.value:
                    new_settings['PLATFORMS'].append(platform)

            # Link platforms to selected games
            for game in new_settings['_GAMES_PLATFORM_MAP']:
                new_settings['_GAMES_PLATFORM_MAP'][game] = set(new_settings['PLATFORMS'])

            self.dismiss(new_settings)
        elif event.button.id == "cancel-btn":
            self.dismiss(None)


class MainScreen(Screen):
    """Main application screen."""

    BINDINGS = [
        ("ctrl+n", "new_session", "New Session"),
        ("ctrl+s", "settings", "Settings"),
        ("ctrl+r", "run", "Run Now"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+g", "query_codes", "Query Codes"),
        ("ctrl+m", "manual_run", "Manual Run"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="main-container"):
            # Title
            yield Static(
                Text("AutoSHiFt", style="bold magenta", justify="center"),
                id="title"
            )
            yield Static(
                Text("Automatically redeem Gearbox SHiFT codes", style="italic", justify="center"),
                id="subtitle"
            )

            # Status panel
            with Container(id="status-container"):
                yield Static("Status: Ready", id="status-label")

            # Action buttons - organized in two rows to fit better
            with Horizontal(id="action-buttons-top"):
                yield Button("Configure", variant="primary", id="configure-btn")
                yield Button("Run Now", variant="success", id="run-btn")
                yield Button("Query", variant="primary", id="query-btn")

            with Horizontal(id="action-buttons-bottom"):
                yield Button("Manual", variant="success", id="manual-btn")
                yield Button("Schedule", variant="default", id="schedule-btn")
                yield Button("Quit", variant="error", id="quit-btn")

            # Log output
            with Container(id="log-container"):
                yield TextArea(
                    text="Log output will appear here...\n",
                    id="log-output",
                    read_only=True
                )

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app starts."""
        # Initialize database
        from autoshift.storage import database
        from autoshift.migrations import run_migrations

        if database.is_closed():
            database.connect()
            run_migrations(database)

        self.update_status("Ready to configure SHiFT code redemption")

    def update_status(self, message: str) -> None:
        """Update the status message."""
        status_label = self.query_one("#status-label", Static)
        status_label.update(f"Status: {message}")

    def append_log(self, message: str) -> None:
        """Append a message to the log output."""
        log_output = self.query_one("#log-output", TextArea)
        current_text = log_output.text
        new_text = current_text + f"{message}\n"
        # Limit log size to prevent memory issues
        lines = new_text.split('\n')
        if len(lines) > 1000:  # Keep only last 1000 lines
            new_text = '\n'.join(lines[-1000:])
        log_output.text = new_text
        # Scroll to bottom
        log_output.move_cursor((len(new_text.split('\n')) - 1, len(new_text.split('\n')[-1]) if new_text.split('\n')[-1] else 0))

    @on(Button.Pressed, "#configure-btn")
    def on_configure_pressed(self) -> None:
        """Handle Configure button press."""
        self.action_settings()

    @on(Button.Pressed, "#run-btn")
    def on_run_pressed(self) -> None:
        """Handle Run Now button press."""
        self.action_run()

    @on(Button.Pressed, "#query-btn")
    def on_query_pressed(self) -> None:
        """Handle Query Codes button press."""
        self.action_query_codes()

    @on(Button.Pressed, "#manual-btn")
    def on_manual_pressed(self) -> None:
        """Handle Manual Run button press."""
        # Open the manual code entry screen
        def handle_manual_code(result: str | None) -> None:
            if result:
                try:
                    platform, code = result.split(":", 1)
                    self._redeem_single_code(code, platform)
                except ValueError:
                    # If split fails, just run the regular manual process
                    self.action_manual_run()
            else:
                # If cancelled, just run the regular manual process
                self.action_manual_run()

        self.app.push_screen(ManualCodeScreen(), handle_manual_code)

    @on(Button.Pressed, "#schedule-btn")
    def on_schedule_pressed(self) -> None:
        """Handle Schedule button press."""
        self.run_scheduled()

    @on(Button.Pressed, "#quit-btn")
    def on_quit_pressed(self) -> None:
        """Handle Quit button press."""
        self.app.exit()

    def action_settings(self) -> None:
        """Open settings modal."""
        def handle_settings(settings_dict: Dict) -> None:
            if settings_dict is not None:
                # Apply settings to global settings object
                if settings_dict.get('USER'):
                    settings.USER = settings_dict['USER']
                if settings_dict.get('PASS'):
                    from pydantic import SecretStr
                    settings.PASS = SecretStr(settings_dict['PASS'])
                if settings_dict.get('SCHEDULE'):
                    settings.SCHEDULE = settings_dict['SCHEDULE']
                if settings_dict.get('LIMIT'):
                    settings.LIMIT = settings_dict['LIMIT']

                # Update verbose logging
                import logging
                if settings_dict.get('VERBOSE'):
                    settings.LOG_LEVEL = "DEBUG"
                    logging.getLogger("autoshift").setLevel(logging.DEBUG)
                else:
                    settings.LOG_LEVEL = "WARNING"
                    logging.getLogger("autoshift").setLevel(logging.WARNING)

                # Update theme
                if settings_dict.get('THEME'):
                    settings.THEME = settings_dict['THEME']
                    # Try to apply theme to the running app if possible
                    try:
                        self.app.theme = settings_dict['THEME']
                    except Exception:
                        # If theme is invalid, skip applying it
                        pass

                # Update games and platforms
                if settings_dict.get('_GAMES_PLATFORM_MAP'):
                    settings._GAMES_PLATFORM_MAP = settings_dict['_GAMES_PLATFORM_MAP']
                if settings_dict.get('PLATFORMS'):
                    settings.PLATFORMS = settings_dict['PLATFORMS']

                # Save settings to file for persistence
                save_settings_to_file()

                self.update_status("Settings updated successfully")
                self.append_log("Settings updated")

        current_pass = ''
        if settings.PASS:
            current_pass = settings.PASS.get_secret_value()

        # Prepare the game selection state based on current settings
        games_platform_map = {}
        for game in Game:
            if game != Game.UNKNOWN:
                # Check if this game has any platforms selected in the current settings
                if game in settings._GAMES_PLATFORM_MAP and settings._GAMES_PLATFORM_MAP[game]:
                    games_platform_map[game] = settings._GAMES_PLATFORM_MAP[game]
                else:
                    games_platform_map[game] = set()

        # Prepare platform list
        current_platforms = list(settings.PLATFORMS) if settings.PLATFORMS else []

        self.app.push_screen(SettingsScreen({
            'USER': settings.USER or '',
            'PASS': current_pass,
            'SCHEDULE': settings.SCHEDULE,
            'LIMIT': settings.LIMIT,
            'VERBOSE': settings.LOG_LEVEL == "DEBUG",
            'THEME': getattr(settings, 'THEME', 'textual-default'),
            '_GAMES_PLATFORM_MAP': games_platform_map,
            'PLATFORMS': current_platforms,
        }), handle_settings)

    def action_run(self) -> None:
        """Run the redemption process once."""
        self.update_status("Running redemption process...")
        self.append_log("Starting redemption process...")

        # Run the redemption process in a background thread to prevent UI freezing
        import threading
        thread = threading.Thread(target=self._run_redemption_once, daemon=True)
        thread.start()

    def action_query_codes(self) -> None:
        """Query new codes."""
        self.update_status("Querying for new codes...")
        self.append_log("Starting code query process...")

        # Run the query process in a background thread to prevent UI freezing
        import threading
        thread = threading.Thread(target=self._run_query_codes, daemon=True)
        thread.start()

    def action_manual_run(self) -> None:
        """Run a single redemption manually."""
        # For now, just run the same process as regular redemption
        self.update_status("Running manual redemption...")
        self.append_log("Starting manual redemption process...")

        # Run the manual redemption in a background thread to prevent UI freezing
        import threading
        thread = threading.Thread(target=self._run_manual_redemption, daemon=True)
        thread.start()

    def _redeem_single_code(self, code: str, platform: str) -> None:
        """Redeem a single code in a background thread."""
        self.update_status(f"Redeeming code {code} for {platform}...")
        self.append_log(f"Starting redemption for code: {code}")

        import threading
        def run_single_redemption():
            try:
                result = redeem_single_code(code, platform)
                self.app.call_from_thread(self.update_status, f"Code {code} redemption completed")
                self.app.call_from_thread(self.append_log, f"Result: {result}")
            except Exception as e:
                self.app.call_from_thread(self.update_status, f"Error redeeming code: {str(e)}")
                self.app.call_from_thread(self.append_log, f"Error: {str(e)}")

        thread = threading.Thread(target=run_single_redemption, daemon=True)
        thread.start()

    def run_scheduled(self) -> None:
        """Run the scheduled redemption process."""
        self.update_status("Starting scheduled redemption...")
        self.append_log("Starting scheduled redemption process...")

        # Run the scheduled redemption process in a background thread to prevent UI freezing
        import threading
        thread = threading.Thread(target=self._run_redemption_scheduled, daemon=True)
        thread.start()

    def _run_redemption_once(self) -> None:
        """Run the redemption process once in a background thread."""
        import sys
        import io
        import logging
        from contextlib import redirect_stdout, redirect_stderr

        try:
            # Update status before starting
            self.app.call_from_thread(self.update_status, "Running redemption process...")
            self.app.call_from_thread(self.append_log, "Starting redemption process...")

            # Temporarily disable scheduling to run once
            original_schedule = settings.SCHEDULE
            settings.SCHEDULE = None

            # Get the autoshift logger and temporarily remove RichHandler during background execution
            logger = logging.getLogger("autoshift")
            original_handlers = logger.handlers[:]  # Make a copy of current handlers

            # Clear all handlers temporarily
            logger.handlers.clear()

            # Create a custom handler to capture log messages
            log_capture_string = io.StringIO()
            string_handler = logging.StreamHandler(log_capture_string)
            string_handler.setLevel(logging.INFO)  # Capture INFO and above
            logger.addHandler(string_handler)

            # Also capture stdout/stderr for any print statements
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Run the main redemption process
                from autoshift.auto import main
                main()

            # Restore original handlers
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)

            # Close our temporary handler and get captured logs
            string_handler.close()
            log_output = log_capture_string.getvalue()

            # Get captured stdout/stderr as well
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            # Send captured log output to the UI log
            if log_output:
                for line in log_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Log: {line.strip()}")

            # Also send any stdout/stderr output
            if stdout_output:
                for line in stdout_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Output: {line.strip()}")
            if stderr_output:
                for line in stderr_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Error: {line.strip()}")

            settings.SCHEDULE = original_schedule
            self.app.call_from_thread(self.update_status, "Redemption process completed")
        except Exception as e:
            # Make sure to restore logger handlers even if there's an error
            logger = logging.getLogger("autoshift")
            from autoshift.common import settings  # Import settings again in case of exception
            original_handlers = getattr(logging.getLogger("autoshift"), 'handlers', [])[:]
            if original_handlers:
                logger.handlers.clear()
                logger.handlers.extend(original_handlers)
            self.app.call_from_thread(self.update_status, f"Error during redemption: {str(e)}")
            self.app.call_from_thread(self.append_log, f"Error: {str(e)}")

    def _run_redemption_scheduled(self) -> None:
        """Run the scheduled redemption process in a background thread."""
        import io
        import logging
        from contextlib import redirect_stdout, redirect_stderr

        try:
            # Update status before starting
            self.app.call_from_thread(self.update_status, "Starting scheduled redemption...")
            self.app.call_from_thread(self.append_log, "Starting scheduled redemption process...")

            # Get the autoshift logger and temporarily remove RichHandler during background execution
            logger = logging.getLogger("autoshift")
            original_handlers = logger.handlers[:]  # Make a copy of current handlers

            # Clear all handlers temporarily
            logger.handlers.clear()

            # Create a custom handler to capture log messages
            log_capture_string = io.StringIO()
            string_handler = logging.StreamHandler(log_capture_string)
            string_handler.setLevel(logging.INFO)  # Capture INFO and above
            logger.addHandler(string_handler)

            # Also capture stdout/stderr for any print statements
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Run scheduled redemption
                from autoshift.auto import auto_redeem_codes
                auto_redeem_codes(interval=settings.SCHEDULE, limit=settings.LIMIT)

            # Restore original handlers
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)

            # Close our temporary handler and get captured logs
            string_handler.close()
            log_output = log_capture_string.getvalue()

            # Get captured stdout/stderr as well
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            # Send captured log output to the UI log
            if log_output:
                for line in log_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Log: {line.strip()}")

            # Also send any stdout/stderr output
            if stdout_output:
                for line in stdout_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Output: {line.strip()}")
            if stderr_output:
                for line in stderr_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Error: {line.strip()}")

            self.app.call_from_thread(self.update_status, "Scheduled redemption completed")
        except Exception as e:
            # Make sure to restore logger handlers even if there's an error
            logger = logging.getLogger("autoshift")
            original_handlers = getattr(logging.getLogger("autoshift"), 'handlers', [])[:]
            if original_handlers:
                logger.handlers.clear()
                logger.handlers.extend(original_handlers)
            self.app.call_from_thread(self.update_status, f"Error in scheduled redemption: {str(e)}")
            self.app.call_from_thread(self.append_log, f"Error: {str(e)}")

    def _run_query_codes(self) -> None:
        """Run the code query process in a background thread."""
        import io
        import logging
        from contextlib import redirect_stdout, redirect_stderr

        try:
            # Update status before starting
            self.app.call_from_thread(self.update_status, "Querying for new codes...")
            self.app.call_from_thread(self.append_log, "Starting code query process...")

            # Get the autoshift logger and temporarily remove RichHandler during background execution
            logger = logging.getLogger("autoshift")
            original_handlers = logger.handlers[:]  # Make a copy of current handlers

            # Clear all handlers temporarily
            logger.handlers.clear()

            # Create a custom handler to capture log messages
            log_capture_string = io.StringIO()
            string_handler = logging.StreamHandler(log_capture_string)
            string_handler.setLevel(logging.INFO)  # Capture INFO and above
            logger.addHandler(string_handler)

            # Also capture stdout/stderr for any print statements
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Run code query
                from autoshift.auto import query
                query()

            # Restore original handlers
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)

            # Close our temporary handler and get captured logs
            string_handler.close()
            log_output = log_capture_string.getvalue()

            # Get captured stdout/stderr as well
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            # Send captured log output to the UI log
            if log_output:
                for line in log_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Log: {line.strip()}")

            # Also send any stdout/stderr output
            if stdout_output:
                for line in stdout_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Output: {line.strip()}")
            if stderr_output:
                for line in stderr_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Error: {line.strip()}")

            self.app.call_from_thread(self.update_status, "Code query completed")
        except Exception as e:
            # Make sure to restore logger handlers even if there's an error
            logger = logging.getLogger("autoshift")
            original_handlers = getattr(logging.getLogger("autoshift"), 'handlers', [])[:]
            if original_handlers:
                logger.handlers.clear()
                logger.handlers.extend(original_handlers)
            self.app.call_from_thread(self.update_status, f"Error in code query: {str(e)}")
            self.app.call_from_thread(self.append_log, f"Error: {str(e)}")

    def _run_manual_redemption(self) -> None:
        """Run a single manual redemption in a background thread."""
        import io
        import logging
        from contextlib import redirect_stdout, redirect_stderr

        try:
            # Update status before starting
            self.app.call_from_thread(self.update_status, "Running manual redemption...")
            self.app.call_from_thread(self.append_log, "Starting manual redemption process...")

            # Get the autoshift logger and temporarily remove RichHandler during background execution
            logger = logging.getLogger("autoshift")
            original_handlers = logger.handlers[:]  # Make a copy of current handlers

            # Clear all handlers temporarily
            logger.handlers.clear()

            # Create a custom handler to capture log messages
            log_capture_string = io.StringIO()
            string_handler = logging.StreamHandler(log_capture_string)
            string_handler.setLevel(logging.INFO)  # Capture INFO and above
            logger.addHandler(string_handler)

            # Also capture stdout/stderr for any print statements
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Run the main redemption process
                from autoshift.auto import main
                main()

            # Restore original handlers
            logger.handlers.clear()
            logger.handlers.extend(original_handlers)

            # Close our temporary handler and get captured logs
            string_handler.close()
            log_output = log_capture_string.getvalue()

            # Get captured stdout/stderr as well
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            # Send captured log output to the UI log
            if log_output:
                for line in log_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Log: {line.strip()}")

            # Also send any stdout/stderr output
            if stdout_output:
                for line in stdout_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Output: {line.strip()}")
            if stderr_output:
                for line in stderr_output.split('\n'):
                    if line.strip():
                        self.app.call_from_thread(self.append_log, f"Error: {line.strip()}")

            self.app.call_from_thread(self.update_status, "Manual redemption completed")
        except Exception as e:
            # Make sure to restore logger handlers even if there's an error
            logger = logging.getLogger("autoshift")
            original_handlers = getattr(logging.getLogger("autoshift"), 'handlers', [])[:]
            if original_handlers:
                logger.handlers.clear()
                logger.handlers.extend(original_handlers)
            self.app.call_from_thread(self.update_status, f"Error in manual redemption: {str(e)}")
            self.app.call_from_thread(self.append_log, f"Error: {str(e)}")


def save_settings_to_file():
    """Save current settings to a config file for persistence."""
    import json
    from pathlib import Path

    # Use the project root directory (one level up from this file)
    config_file = Path(__file__).parent.parent / 'config.json'

    # Prepare settings to save
    settings_to_save = {
        'USER': settings.USER,
        'SCHEDULE': settings.SCHEDULE,
        'LIMIT': settings.LIMIT,
        'LOG_LEVEL': settings.LOG_LEVEL,
        'GAMES': [game.value for game in settings.GAMES] if settings.GAMES else [],
        'PLATFORMS': [platform.value for platform in settings.PLATFORMS] if settings.PLATFORMS else [],
        'THEME': getattr(settings, 'THEME', 'textual-default'),  # Save theme setting
    }

    # Add games-platform mapping
    games_platform_map = {}
    for game, platforms in settings._GAMES_PLATFORM_MAP.items():
        if platforms:  # Only save if there are platforms selected
            games_platform_map[game.value] = [platform.value for platform in platforms]
    settings_to_save['_GAMES_PLATFORM_MAP'] = games_platform_map

    try:
        with open(config_file, 'w') as f:
            json.dump(settings_to_save, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")


def load_settings_from_file():
    """Load settings from config file if it exists."""
    import json
    from pathlib import Path

    # Use the project root directory (one level up from this file)
    config_file = Path(__file__).parent.parent / 'config.json'

    if not config_file.exists():
        return  # No saved settings to load

    try:
        with open(config_file, 'r') as f:
            saved_settings = json.load(f)

        # Apply saved settings
        if 'USER' in saved_settings and saved_settings['USER']:
            settings.USER = saved_settings['USER']
        if 'SCHEDULE' in saved_settings and saved_settings['SCHEDULE']:
            settings.SCHEDULE = saved_settings['SCHEDULE']
        if 'LIMIT' in saved_settings and saved_settings['LIMIT']:
            settings.LIMIT = saved_settings['LIMIT']
        if 'LOG_LEVEL' in saved_settings and saved_settings['LOG_LEVEL']:
            settings.LOG_LEVEL = saved_settings['LOG_LEVEL']
        if 'THEME' in saved_settings and saved_settings['THEME']:
            settings.THEME = saved_settings['THEME']  # Load theme setting

        # Apply games and platforms
        if 'GAMES' in saved_settings and saved_settings['GAMES']:
            from autoshift.common import Game
            settings.GAMES = [Game(game_val) for game_val in saved_settings['GAMES']]

        if 'PLATFORMS' in saved_settings and saved_settings['PLATFORMS']:
            from autoshift.common import Platform
            settings.PLATFORMS = [Platform(platform_val) for platform_val in saved_settings['PLATFORMS']]

        # Apply games-platform mapping
        if 'GAMES' in saved_settings and 'PLATFORMS' in saved_settings:
            # If we have both games and platforms from the saved settings, rebuild the mapping
            settings._GAMES_PLATFORM_MAP.clear()
            if saved_settings.get('_GAMES_PLATFORM_MAP'):
                from autoshift.common import Game, Platform
                for game_val, platform_vals in saved_settings['_GAMES_PLATFORM_MAP'].items():
                    game = Game(game_val)
                    platforms = {Platform(platform_val) for platform_val in platform_vals}
                    settings._GAMES_PLATFORM_MAP[game] = platforms
            else:
                # If no specific mapping was saved, create default mappings
                from autoshift.common import Game, Platform
                for game_val in saved_settings['GAMES']:
                    game = Game(game_val)
                    platforms = {Platform(platform_val) for platform_val in saved_settings['PLATFORMS']}
                    settings._GAMES_PLATFORM_MAP[game] = platforms

    except Exception as e:
        print(f"Error loading settings: {e}")


class AutoSHiFtTUI(App):
    """AutoSHiFt Terminal User Interface Application."""

    TITLE = "AutoSHiFt - SHiFT Code Redemption Tool"
    SUB_TITLE = "Automatically redeem Gearbox SHiFT codes"
    CSS_PATH = None

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        # Load saved settings on startup
        load_settings_from_file()

        # Apply theme if available
        if hasattr(settings, 'THEME') and settings.THEME:
            try:
                self.theme = settings.THEME
            except Exception:
                # If theme is invalid, don't set a theme (use default)
                pass
        # If no theme is set, Textual will use its default theme

        self.push_screen(MainScreen())

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Static("Loading...")


def run_tui():
    """Run the TUI application."""
    app = AutoSHiFtTUI()
    app.run()


if __name__ == "__main__":
    run_tui()