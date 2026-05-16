"""GatherAgent TUI — Interactive terminal chat interface.

Built with Textual framework, featuring:
- Real-time chat with streaming agent responses
- Tool call visualization
- 6 built-in themes (Catppuccin, Tokyo Night, Dracula, etc.)
- 4-language i18n (en/zh-Hans/ja/pt-BR)
- Input history with Up/Down navigation
- Keyboard shortcuts (Ctrl+Q quit, Ctrl+C interrupt, etc.)
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll, Vertical
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive
from textual import work

from gather.tui.widgets import StatusBar, ChatMessage, ChatInput, ThinkingIndicator, HelpOverlay
from gather.tui.theme import ThemeEngine, BUILTIN_THEMES
from gather.tui.i18n import I18n

logger = logging.getLogger(__name__)


# ── Theme CSS Generation ──────────────────────────────────

def _generate_theme_css(theme_name: str) -> str:
    """Generate Textual-compatible CSS from a theme definition."""
    theme = BUILTIN_THEMES.get(theme_name, BUILTIN_THEMES["default"])
    colors = theme.get("colors", {})
    bg = colors.get("bg", "#1A1A2E")
    text = colors.get("text", "#E0E0E0")
    primary = colors.get("primary", "#4A90D9")
    return f"""
Screen {{
    background: {bg};
    color: {text};
}}
StatusBar {{
    background: {bg};
    color: {text};
}}
ChatInput {{
    background: {bg};
}}
Input {{
    background: {bg} 90%;
    border: tall {primary} 50%;
    color: {text};
}}
Input:focus {{
    border: tall {primary};
}}
Input.-placeholder {{
    color: {text} 40%;
}}
VerticalScroll {{
    scrollbar-background: {bg};
    scrollbar-color: {primary} 50%;
}}
Footer {{
    background: {bg} 80%;
    color: {text};
}}
HelpOverlay {{
    background: {bg} 95%;
    color: {text};
    border: tall {primary};
}}
"""


class GatherTUI(App):
    """GatherAgent interactive terminal chat interface."""

    CSS = """
Screen {
    layout: vertical;
}

#main-container {
    layout: vertical;
    height: 1fr;
}

#chat-area {
    height: 1fr;
    margin: 0 1;
    scrollbar-size: 1 1;
}

#thinking-indicator {
    dock: top;
    height: 1;
    margin: 0 1;
}

#help-overlay {
    dock: top;
    height: auto;
    max-height: 50%;
    margin: 1 2;
    display: none;
}
"""

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "interrupt_agent", "Interrupt"),
        Binding("ctrl+l", "clear_chat", "Clear"),
        Binding("ctrl+h", "toggle_help", "Help"),
        Binding("ctrl+t", "next_theme", "Theme"),
        Binding("ctrl+m", "switch_model", "Model"),
    ]

    TITLE = "GatherAgent"
    SUB_TITLE = "The convergence agent"

    # Reactive state
    theme_index: reactive[int] = reactive(0)
    show_help: reactive[bool] = reactive(False)
    input_history: reactive[list] = reactive(lambda: [])
    history_pos: reactive[int] = reactive(-1)

    # Model presets: (label, model_id, provider)
    MODEL_PRESETS = [
        ("GPT-4o",               "gpt-4o",                          "openai"),
        ("GPT-4o Mini",          "gpt-4o-mini",                     "openai"),
        ("o3-mini",              "o3-mini",                          "openai"),
        ("Claude Sonnet 4",      "claude-sonnet-4-20250514",         "anthropic"),
        ("Claude Opus 4",        "claude-opus-4-20250514",           "anthropic"),
        ("Gemini 2.0 Flash",     "google/gemini-2.0-flash",          "openrouter"),
        ("DeepSeek V3",          "deepseek/deepseek-chat",           "openrouter"),
        ("Llama 3.3 70B",       "meta-llama/llama-3.3-70b-instruct", "openrouter"),
        ("Qwen 2.5 72B",        "qwen/qwen-2.5-72b-instruct",       "openrouter"),
    ]

    def __init__(
        self,
        model: str | None = None,
        provider: str | None = None,
        profile: str | None = None,
        mode: str = "agent",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._model_override = model
        self._provider_override = provider
        self._model_index = 0
        self._profile = profile
        self._mode = mode
        self._agent = None
        self._running_task = None
        self._theme_engine = ThemeEngine()
        self._i18n = I18n()
        self._theme_names = list(BUILTIN_THEMES.keys())
        self._total_cost = 0.0
        self._turn_count = 0.0

        # Set initial model index to match override
        if model:
            for i, (_, m, p) in enumerate(self.MODEL_PRESETS):
                if m == model and (not provider or p == provider):
                    self._model_index = i
                    break

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield StatusBar(id="status-bar")
        with Vertical(id="main-container"):
            yield HelpOverlay(id="help-overlay")
            yield ThinkingIndicator(id="thinking-indicator")
            with VerticalScroll(id="chat-area"):
                pass  # Messages will be added dynamically
        yield ChatInput(id="chat-input")
        yield Footer()

    def on_mount(self):
        # Apply initial theme
        self._apply_theme(self._theme_names[self.theme_index])
        # Focus input
        self.query_one("#chat-input", ChatInput).focus_input()
        # Show welcome message
        self._add_system_message(self._i18n.t("welcome"))
        model_label, _, _ = self.MODEL_PRESETS[self._model_index]
        self._add_system_message(
            f"Model: {model_label} | Ctrl+M to switch, Ctrl+H for help, Ctrl+Q to quit."
        )
        # Initialize status bar
        self._update_status()

    # ── Theme Management ───────────────────────────────────

    def _apply_theme(self, theme_name: str):
        self._theme_engine.set_theme(theme_name)
        css = _generate_theme_css(theme_name)
        # Remove old theme styles, apply new
        try:
            self.remove_stylesheet("dynamic-theme")
        except Exception:
            pass
        self.install_css(css, name="dynamic-theme")

    def action_next_theme(self):
        self.theme_index = (self.theme_index + 1) % len(self._theme_names)
        name = self._theme_names[self.theme_index]
        self._apply_theme(name)
        self._add_system_message(f"Theme: {name}")

    # ── Model Switching ──────────────────────────────────

    def action_switch_model(self):
        """Cycle through model presets with Ctrl+M."""
        self._model_index = (self._model_index + 1) % len(self.MODEL_PRESETS)
        label, model_id, provider = self.MODEL_PRESETS[self._model_index]
        self._model_override = model_id
        self._provider_override = provider

        # Reset agent so next call uses new model
        self._agent = None

        self._add_system_message(f"Switched to: {label} ({provider})")
        self._update_status()

    # ── Help Toggle ──────────────────────────────────────

    def action_toggle_help(self):
        self.show_help = not self.show_help
        overlay = self.query_one("#help-overlay", HelpOverlay)
        overlay.display = self.show_help

    # ── Chat Input Handling ────────────────────────────────

    def on_chat_input_submitted(self, event: ChatInput.Submitted):
        user_message = event.value
        if not user_message.strip():
            return

        # Save to input history
        history = list(self.input_history)
        history.append(user_message)
        self.input_history = history
        self.history_pos = -1

        # Show user message
        self._add_user_message(user_message)

        # Run agent
        self._run_agent(user_message)

    # ── Input History Navigation ───────────────────────────

    def on_key(self, event):
        if event.key == "up":
            if self.input_history and self.history_pos < len(self.input_history) - 1:
                self.history_pos += 1
                idx = len(self.input_history) - 1 - self.history_pos
                chat_input = self.query_one("#chat-input", ChatInput)
                chat_input._input.value = self.input_history[idx]
            event.prevent_default()
        elif event.key == "down":
            if self.history_pos > 0:
                self.history_pos -= 1
                idx = len(self.input_history) - 1 - self.history_pos
                chat_input = self.query_one("#chat-input", ChatInput)
                chat_input._input.value = self.input_history[idx]
            elif self.history_pos == 0:
                self.history_pos = -1
                chat_input = self.query_one("#chat-input", ChatInput)
                chat_input._input.value = ""
            event.prevent_default()

    # ── Agent Execution ────────────────────────────────────

    @work(exclusive=True)
    async def _run_agent(self, user_message: str):
        """Run the agent in a background worker."""
        thinking = self.query_one("#thinking-indicator", ThinkingIndicator)
        chat_input = self.query_one("#chat-input", ChatInput)

        # Show thinking indicator
        thinking.start()
        chat_input.set_placeholder("Agent is working... (Ctrl+C to interrupt)")

        try:
            # Lazy init agent
            if self._agent is None:
                from gather.agent.core import GatherAgent, AgentMode
                mode_map = {
                    "plan": AgentMode.PLAN,
                    "agent": AgentMode.AGENT,
                    "yolo": AgentMode.YOLO,
                    "sandbox": AgentMode.SANDBOX,
                }
                agent_mode = mode_map.get(self._mode, AgentMode.AGENT)
                self._agent = GatherAgent(
                    mode=agent_mode,
                    model=self._model_override,
                    provider=self._provider_override,
                    profile=self._profile,
                    on_tool_call=self._on_tool_call,
                    on_turn_metrics=self._on_turn_metrics,
                )

            # Run agent
            result = await self._agent.run(user_message)
            self._turn_count = self._agent.turn_count
            self._total_cost = self._agent.total_cost

            # Display result
            self._add_assistant_message(result)

        except asyncio.CancelledError:
            self._add_system_message("⚡ Agent interrupted.")
        except Exception as e:
            logger.error(f"Agent error: {e}")
            self._add_system_message(f"❌ Error: {e}")
        finally:
            thinking.stop()
            chat_input.set_placeholder("Type your message... (Enter to send, Ctrl+Q to quit)")
            chat_input.focus_input()
            self._update_status()

    def _on_tool_call(self, call):
        """Callback when agent makes a tool call — show in chat."""
        self.call_from_thread(self._add_tool_call_message, call.name, str(call.arguments))

    def _on_turn_metrics(self, metrics):
        """Callback when a turn completes — update status."""
        self._turn_count = metrics.turn_number
        self._update_status()

    # ── Interrupt Agent ────────────────────────────────────

    def action_interrupt_agent(self):
        if self._agent:
            self._agent.interrupt()
            self._add_system_message("⚡ Interrupting agent...")

    # ── Clear Chat ─────────────────────────────────────────

    def action_clear_chat(self):
        chat_area = self.query_one("#chat-area", VerticalScroll)
        chat_area.remove_children()
        self._add_system_message("Chat cleared.")

    # ── Message Helpers ────────────────────────────────────

    def _add_user_message(self, content: str):
        chat_area = self.query_one("#chat-area", VerticalScroll)
        msg = ChatMessage(role="user", content=content)
        chat_area.mount(msg)
        chat_area.scroll_end(animate=False)

    def _add_assistant_message(self, content: str, tool_calls: list | None = None):
        chat_area = self.query_one("#chat-area", VerticalScroll)
        msg = ChatMessage(role="assistant", content=content, tool_calls=tool_calls)
        chat_area.mount(msg)
        chat_area.scroll_end(animate=False)

    def _add_system_message(self, content: str):
        chat_area = self.query_one("#chat-area", VerticalScroll)
        msg = ChatMessage(role="system", content=content)
        chat_area.mount(msg)
        chat_area.scroll_end(animate=False)

    def _add_tool_call_message(self, tool_name: str, arguments: str):
        chat_area = self.query_one("#chat-area", VerticalScroll)
        msg = ChatMessage(role="tool", content=f"Tool: {tool_name}\nArgs: {arguments}")
        chat_area.mount(msg)
        chat_area.scroll_end(animate=False)

    def _add_thinking_message(self, content: str):
        chat_area = self.query_one("#chat-area", VerticalScroll)
        msg = ChatMessage(role="thinking", content=content)
        chat_area.mount(msg)
        chat_area.scroll_end(animate=False)

    # ── Status Bar Update ──────────────────────────────────

    def _update_status(self):
        try:
            status = self.query_one("#status-bar", StatusBar)
            status.update_status(
                model=self._model_override or "gpt-4o",
                provider=self._provider_override or "openai",
                mode=self._mode,
                cost=self._total_cost,
                turns=int(self._turn_count),
            )
        except Exception:
            pass  # Widget may not be mounted yet
