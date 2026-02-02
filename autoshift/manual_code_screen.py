from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from autoshift.shift import ShiftClient, Status
from autoshift.models import Key


class ManualCodeScreen(ModalScreen[str]):
    """Screen for entering and redeeming a manual SHiFT code."""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
    ]

    def __init__(self, current_code: str = ""):
        super().__init__()
        self.current_code = current_code
        
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Enter SHiFT Code to Redeem Manually", classes="title"),
            
            Label("Code:"),
            Input(
                placeholder="Enter SHiFT code (e.g., XXXXX-XXXXX-XXXXX-XXXXX)",
                id="code-input",
                value=self.current_code
            ),
            
            Label("Platform:"),
            Input(
                placeholder="Enter platform (steam, epic, psn, xboxlive)",
                id="platform-input",
                value="steam"  # Default to steam
            ),
            
            Horizontal(
                Button("Redeem Code", variant="primary", id="redeem-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                id="buttons"
            ),
            id="manual-code-container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "redeem-btn":
            code_input = self.query_one("#code-input", Input)
            platform_input = self.query_one("#platform-input", Input)
            
            code = code_input.value.strip().upper()
            platform = platform_input.value.strip().lower()
            
            if not code:
                self.app.bell()  # Alert user
                return
            
            if not platform:
                platform = "steam"  # Default
            
            # Validate platform
            valid_platforms = {"steam", "epic", "psn", "xboxlive"}
            if platform not in valid_platforms:
                platform = "steam"  # Default to steam if invalid
            
            self.dismiss(f"{platform}:{code}")
        elif event.button.id == "cancel-btn":
            self.dismiss(None)


def redeem_single_code(code: str, platform: str) -> str:
    """Redeem a single code directly."""
    from autoshift.common import settings
    from autoshift.shift import ShiftClient

    client = ShiftClient()
    # Login first
    client.login(settings.USER, settings.PASS.get_secret_value() if settings.PASS else None)

    # Create a temporary key object
    temp_key = Key(
        code=code,
        platform=platform,
        game="UNKNOWN",
    )

    # Redeem the code
    status = client.redeem(temp_key)

    return str(status.msg)  # Return the status message