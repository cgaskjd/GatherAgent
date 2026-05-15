"""Internationalization — from DeepSeek-TUI's 4-language support."""
TRANSLATIONS = {
    "en": {
        "welcome": "Welcome to GatherAgent",
        "thinking": "Thinking...",
        "error": "Error",
        "cost": "Cost",
        "mode": "Mode",
        "model": "Model",
        "turn": "Turn",
        "provider": "Provider",
        "input_placeholder": "Type your message... (Enter to send, Ctrl+Q to quit)",
        "input_busy": "Agent is working... (Ctrl+C to interrupt)",
        "interrupted": "Agent interrupted.",
        "cleared": "Chat cleared.",
        "goodbye": "Goodbye!",
        "help_title": "Keyboard Shortcuts",
        "theme_changed": "Theme changed to:",
        "no_prompt": "Type your message and press Enter. Ctrl+H for help.",
        "tool_call": "Tool Call",
        "tool_result": "Tool Result",
        "system": "System",
    },
    "zh-Hans": {
        "welcome": "\u6b22\u8fce\u4f7f\u7528 GatherAgent",
        "thinking": "\u601d\u8003\u4e2d...",
        "error": "\u9519\u8bef",
        "cost": "\u8d39\u7528",
        "mode": "\u6a21\u5f0f",
        "model": "\u6a21\u578b",
        "turn": "\u8f6e\u6b21",
        "provider": "\u63d0\u4f9b\u5546",
        "input_placeholder": "\u8f93\u5165\u6d88\u606f... (\u56de\u8f66\u53d1\u9001, Ctrl+Q \u9000\u51fa)",
        "input_busy": "Agent \u5de5\u4f5c\u4e2d... (Ctrl+C \u4e2d\u65ad)",
        "interrupted": "Agent \u5df2\u4e2d\u65ad\u3002",
        "cleared": "\u804a\u5929\u5df2\u6e05\u9664\u3002",
        "goodbye": "\u518d\u89c1\uff01",
        "help_title": "\u952e\u76d8\u5feb\u6377\u952e",
        "theme_changed": "\u4e3b\u9898\u5df2\u5207\u6362\u4e3a\uff1a",
        "no_prompt": "\u8f93\u5165\u6d88\u606f\u5e76\u6309\u56de\u8f66\u3002Ctrl+H \u67e5\u770b\u5e2e\u52a9\u3002",
        "tool_call": "\u5de5\u5177\u8c03\u7528",
        "tool_result": "\u5de5\u5177\u7ed3\u679c",
        "system": "\u7cfb\u7edf",
    },
    "ja": {
        "welcome": "GatherAgent\u3078\u3088\u3046\u3053\u305d",
        "thinking": "\u601d\u8003\u4e2d...",
        "error": "\u30a8\u30e9\u30fc",
        "cost": "\u30b3\u30b9\u30c8",
        "mode": "\u30e2\u30fc\u30c9",
        "model": "\u30e2\u30c7\u30eb",
        "turn": "\u30bf\u30fc\u30f3",
        "provider": "\u30d7\u30ed\u30d0\u30a4\u30c0",
        "input_placeholder": "\u30e1\u30c3\u30bb\u30fc\u30b8\u3092\u5165\u529b... (Enter\u3067\u9001\u4fe1, Ctrl+Q\u3067\u7d42\u4e86)",
        "input_busy": "Agent\u304c\u51e6\u7406\u4e2d... (Ctrl+C\u3067\u4e2d\u65ad)",
        "interrupted": "Agent\u3092\u4e2d\u65ad\u3057\u307e\u3057\u305f\u3002",
        "cleared": "\u30c1\u30e3\u30c3\u30c8\u3092\u30af\u30ea\u30a2\u3057\u307e\u3057\u305f\u3002",
        "goodbye": "\u3055\u3088\u3046\u306a\u3089\uff01",
        "help_title": "\u30ad\u30fc\u30dc\u30fc\u30c9\u30b7\u30e7\u30fc\u30c8\u30ab\u30c3\u30c8",
        "theme_changed": "\u30c6\u30fc\u30de\u5909\u66f4:",
        "no_prompt": "\u30e1\u30c3\u30bb\u30fc\u30b8\u3092\u5165\u529b\u3057\u3066Enter\u3002Ctrl+H\u3067\u30d8\u30eb\u30d7\u3002",
        "tool_call": "\u30c4\u30fc\u30eb\u547c\u3073\u51fa\u3057",
        "tool_result": "\u30c4\u30fc\u30eb\u7d50\u679c",
        "system": "\u30b7\u30b9\u30c6\u30e0",
    },
    "pt-BR": {
        "welcome": "Bem-vindo ao GatherAgent",
        "thinking": "Pensando...",
        "error": "Erro",
        "cost": "Custo",
        "mode": "Modo",
        "model": "Modelo",
        "turn": "Turno",
        "provider": "Provedor",
        "input_placeholder": "Digite sua mensagem... (Enter para enviar, Ctrl+Q para sair)",
        "input_busy": "Agent trabalhando... (Ctrl+C para interromper)",
        "interrupted": "Agent interrompido.",
        "cleared": "Chat limpo.",
        "goodbye": "Tchau!",
        "help_title": "Atalhos de Teclado",
        "theme_changed": "Tema alterado para:",
        "no_prompt": "Digite sua mensagem e pressione Enter. Ctrl+H para ajuda.",
        "tool_call": "Chamada de Ferramenta",
        "tool_result": "Resultado da Ferramenta",
        "system": "Sistema",
    },
}


class I18n:
    def __init__(self, locale: str = "auto"):
        self._locale = locale if locale != "auto" else self._detect_locale()

    def _detect_locale(self) -> str:
        import os
        lang = os.environ.get("LANG", "").lower()
        if "zh" in lang: return "zh-Hans"
        if "ja" in lang: return "ja"
        if "pt" in lang: return "pt-BR"
        return "en"

    def t(self, key: str) -> str:
        return TRANSLATIONS.get(self._locale, TRANSLATIONS["en"]).get(key, key)

    @property
    def locale(self) -> str:
        return self._locale
