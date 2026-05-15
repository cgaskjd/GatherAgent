"""GatherAgent TUI Widgets — Chat display, input, status bar, tool visualization."""

from __future__ import annotations

import time
from textual.widgets import Static, Input, RichLog
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual import events
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich import box


class StatusBar(Static):
    """Top status bar showing model, mode, cost, and turn count."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model = "gpt-4o"
        self._mode = "agent"
        self._cost = 0.0
        self._turns = 0
        self._provider = "openai"

    def update_status(self, model: str = None, mode: str = None,
                      cost: float = None, turns: int = None, provider: str = None):
        if model: self._model = model
        if mode: self._mode = mode
        if cost is not None: self._cost = cost
        if turns is not None: self._turns = turns
        if provider: self._provider = provider
        self._render()

    def _render(self):
        mode_icons = {"plan": "🔍", "agent": "🤖", "yolo": "⚡", "sandbox": "🔒"}
        icon = mode_icons.get(self._mode, "🤖")
        cost_str = f"${self._cost:.4f}" if self._cost < 1 else f"${self._cost:.2f}"
        text = Text()
        text.append(f" {icon} ", style="bold")
        text.append(f"GatherAgent", style="bold cyan")
        text.append(" │ ", style="dim")
        text.append(f"Model: ", style="dim")
        text.append(f"{self._model}", style="bold white")
        text.append(f" ({self._provider})", style="dim")
        text.append(" │ ", style="dim")
        text.append(f"Mode: ", style="dim")
        text.append(f"{self._mode}", style="bold yellow")
        text.append(" │ ", style="dim")
        text.append(f"Turn: ", style="dim")
        text.append(f"{self._turns}", style="bold green")
        text.append(" │ ", style="dim")
        text.append(f"Cost: ", style="dim")
        text.append(f"{cost_str}", style="bold magenta")
        self.update(text)


class ChatMessage(Static):
    """A single chat message bubble."""

    def __init__(self, role: str, content: str, tool_calls: list | None = None, **kwargs):
        super().__init__(**kwargs)
        self._role = role
        self._content = content
        self._tool_calls = tool_calls or []

    def on_mount(self):
        self._render_message()

    def _render_message(self):
        if self._role == "user":
            text = Text()
            text.append("👤 You\n", style="bold cyan")
            text.append(self._content)
            self.update(Panel(text, border_style="cyan", padding=(0, 1)))

        elif self._role == "assistant":
            text = Text()
            text.append("🤖 GatherAgent\n", style="bold green")
            # Try to render as markdown for better readability
            try:
                md = Markdown(self._content)
                panel_content = md
            except Exception:
                text.append(self._content)
                panel_content = text

            # Show tool calls if any
            if self._tool_calls:
                tool_table = Table(box=box.SIMPLE, show_header=True, padding=0)
                tool_table.add_column("Tool", style="bold yellow")
                tool_table.add_column("Arguments", style="dim")
                for tc in self._tool_calls:
                    fn = tc.get("function", {})
                    name = fn.get("name", "unknown")
                    args = fn.get("arguments", "{}")
                    if len(args) > 80:
                        args = args[:77] + "..."
                    tool_table.add_row(f"📎 {name}", args)

                from rich.console import Group
                if isinstance(panel_content, Text):
                    panel_content = Group(panel_content, Text(), tool_table)
                else:
                    panel_content = Group(panel_content, Text(), tool_table)

            self.update(Panel(panel_content, border_style="green", padding=(0, 1)))

        elif self._role == "system":
            text = Text()
            text.append("⚙️ System\n", style="bold yellow")
            text.append(self._content, style="yellow")
            self.update(Panel(text, border_style="yellow", padding=(0, 1)))

        elif self._role == "tool":
            text = Text()
            text.append("🔧 Tool Result\n", style="bold magenta")
            result = self._content
            if len(result) > 500:
                result = result[:497] + "..."
            text.append(result, style="dim")
            self.update(Panel(text, border_style="magenta", padding=(0, 1)))

        elif self._role == "thinking":
            text = Text()
            text.append("💭 Thinking...\n", style="bold blue")
            text.append(self._content, style="dim italic")
            self.update(Panel(text, border_style="blue", padding=(0, 1)))


class ThinkingIndicator(Static):
    """Animated thinking indicator shown while agent is processing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self._frame = 0
        self._active = False

    def start(self):
        self._active = True
        self._animate()

    def stop(self):
        self._active = False
        self.update("")

    def _animate(self):
        if not self._active:
            return
        frame = self._frames[self._frame % len(self._frames)]
        self.update(Text(f" {frame} Agent is thinking...", style="bold blue"))
        self._frame += 1
        if self._active:
            self.set_timer(0.1, self._animate)


class ChatInput(Horizontal):
    """Chat input area with a text input and send button."""

    class Submitted(Message):
        """Message sent when user submits input."""
        def __init__(self, value: str) -> None:
            self.value = value
            super().__init__()

    DEFAULT_CSS = """
    ChatInput {
        dock: bottom;
        height: 3;
        margin: 0 1;
        padding: 0;
    }
    ChatInput > Input {
        width: 1fr;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._input = Input(placeholder="Type your message... (Enter to send, Ctrl+Q to quit)")

    def compose(self):
        yield self._input

    def on_input_submitted(self, event: Input.Submitted):
        if event.value.strip():
            self.post_message(self.Submitted(event.value.strip()))
            self._input.value = ""

    def focus_input(self):
        self._input.focus()

    def set_placeholder(self, text: str):
        self._input.placeholder = text


class HelpOverlay(Static):
    """Help overlay showing keyboard shortcuts."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_mount(self):
        table = Table(box=box.SIMPLE, show_header=True, title="⌨️ Keyboard Shortcuts")
        table.add_column("Key", style="bold cyan")
        table.add_column("Action", style="white")
        table.add_row("Enter", "Send message")
        table.add_row("Ctrl+Q", "Quit GatherAgent")
        table.add_row("Ctrl+C", "Interrupt agent")
        table.add_row("Ctrl+L", "Clear chat")
        table.add_row("Ctrl+H", "Toggle this help")
        table.add_row("Ctrl+T", "Switch theme")
        table.add_row("Up/Down", "Navigate input history")
        self.update(Panel(table, border_style="cyan"))
