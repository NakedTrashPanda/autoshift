#!/usr/bin/env python
"""
Textual TUI for AutoSHiFt - A tool to automatically redeem Gearbox SHiFT codes.
This provides a user-friendly terminal interface for configuring and running the application.
"""

from typing import Dict, List
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


# ... (keeping all the existing code until the problematic method)

    def _run_manual_redemption(self) -> None:
        """Run a single manual redemption in a background thread."""
        import io
        import logging
        from contextlib import redirect_stdout, redirect_stderr

        try:
            # Update status before starting
            self.app.call_from_thread(self.update_status, "Running manual redemption...")
            self.app.call_from_thread(self.append_log, "Starting manual redemption process...")

            # Get the autoshift logger and capture its current handlers
            logger = logging.getLogger("autoshift")
            original_handlers = logger.handlers[:]
            
            # Store the original level
            original_level = logger.level
            
            # Create a custom handler to capture log messages
            log_capture_string = io.StringIO()
            string_handler = logging.StreamHandler(log_capture_string)
            string_handler.setLevel(logging.INFO)  # Capture INFO and above
            
            # Temporarily replace handlers with our capture handler only
            logger.handlers = [string_handler]

            # Also capture stdout/stderr for any print statements
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Run the main redemption process
                from autoshift.auto import main
                main()

            # Restore original handlers and level
            logger.handlers = original_handlers
            logger.setLevel(original_level)

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
            self.app.call_from_thread(self.update_status, f"Error in manual redemption: {str(e)}")
            self.app.call_from_thread(self.append_log, f"Error: {str(e)}")


class AutoSHiFtTUI(App):
    """AutoSHiFt Terminal User Interface Application."""

    TITLE = "AutoSHiFt - SHiFT Code Redemption Tool"
    SUB_TITLE = "Automatically redeem Gearbox SHiFT codes"
    CSS_PATH = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Static("Loading...")


def run_tui():
    """Run the TUI application."""
    app = AutoSHiFtTUI()
    app.run()