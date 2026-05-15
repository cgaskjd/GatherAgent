"""Internationalization — from DeepSeek-TUI's 4-language support."""
TRANSLATIONS = {
    "en": {"welcome": "Welcome to GatherAgent", "thinking": "Thinking...", "error": "Error", "cost": "Cost"},
    "zh-Hans": {"welcome": "\u6b22\u8fce\u4f7f\u7528 GatherAgent", "thinking": "\u601d\u8003\u4e2d...", "error": "\u9519\u8bef", "cost": "\u8d39\u7528"},
    "ja": {"welcome": "GatherAgent\u3078\u3088\u3046\u3053\u305d", "thinking": "\u601d\u8003\u4e2d...", "error": "\u30a8\u30e9\u30fc", "cost": "\u30b3\u30b9\u30c8"},
    "pt-BR": {"welcome": "Bem-vindo ao GatherAgent", "thinking": "Pensando...", "error": "Erro", "cost": "Custo"},
}
class I18n:
    def __init__(self, locale: str = "auto"): self._locale = locale if locale != "auto" else self._detect_locale()
    def _detect_locale(self) -> str:
        import os; lang = os.environ.get("LANG", "").lower()
        if "zh" in lang: return "zh-Hans"
        if "ja" in lang: return "ja"
        if "pt" in lang: return "pt-BR"
        return "en"
    def t(self, key: str) -> str: return TRANSLATIONS.get(self._locale, TRANSLATIONS["en"]).get(key, key)
