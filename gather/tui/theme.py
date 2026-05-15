"""Theme Engine — from DeepSeek-TUI + Hermes-Agent's Skin engine."""
from dataclasses import dataclass
BUILTIN_THEMES = {
    "default": {"name": "default", "colors": {"primary": "#4A90D9", "bg": "#1A1A2E", "text": "#E0E0E0"}},
    "catppuccin": {"name": "catppuccin", "colors": {"primary": "#89B4FA", "bg": "#1E1E2E", "text": "#CDD6F4"}},
    "tokyo_night": {"name": "tokyo_night", "colors": {"primary": "#7AA2F7", "bg": "#1A1B26", "text": "#C0CAF5"}},
    "dracula": {"name": "dracula", "colors": {"primary": "#BD93F9", "bg": "#282A36", "text": "#F8F8F2"}},
    "gruvbox": {"name": "gruvbox", "colors": {"primary": "#83A598", "bg": "#282828", "text": "#EBDBB2"}},
    "slate": {"name": "slate", "colors": {"primary": "#64748B", "bg": "#0F172A", "text": "#E2E8F0"}},
}
class ThemeEngine:
    def __init__(self, theme_name: str = "default"): self._current = theme_name; self._themes = dict(BUILTIN_THEMES)
    @property
    def current(self) -> dict: return self._themes.get(self._current, BUILTIN_THEMES["default"])
    def set_theme(self, name: str):
        if name in self._themes: self._current = name
    def list_themes(self) -> list[str]: return list(self._themes.keys())
