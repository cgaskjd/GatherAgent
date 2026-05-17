"""CLI Entry Point."""
import click, asyncio, sys
from gather.config.profile import apply_profile


@click.group(invoke_without_command=True)
@click.option("--model", "-m", default=None, help="Model name (any model ID, e.g. gpt-5.5, claude-opus-4-7, deepseek/deepseek-v4-pro)")
@click.option("--provider", default=None, help="Provider (openai/anthropic/openrouter/ollama/custom)")
@click.option("--base-url", default=None, help="Custom API base URL (e.g. https://api.my-proxy.com/v1)")
@click.option("--api-key", default=None, help="Custom API key (prefer env vars or config)")
@click.option("--profile", "-p", default=None, help="Profile name")
@click.option("--yolo", is_flag=True, help="Auto-approve all tools")
@click.option("--tui", is_flag=True, help="Launch TUI (default if no prompt)")
@click.argument("prompt", required=False)
@click.pass_context
def main(ctx, model, provider, base_url, api_key, profile, yolo, tui, prompt):
    """GatherAgent -- The convergence agent."""
    apply_profile(profile)
    mode = "yolo" if yolo else "agent"

    # Set custom base_url/api_key as env overrides if provided
    if api_key:
        import os
        # Route key to correct env var based on provider
        key_env_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }
        env_var = key_env_map.get(provider, "OPENAI_API_KEY")
        os.environ[env_var] = api_key

    if prompt:
        from gather.agent.core import GatherAgent, AgentMode
        agent_mode = AgentMode.YOLO if yolo else AgentMode.AGENT
        agent = GatherAgent(mode=agent_mode, model=model, provider=provider, profile=profile)
        if base_url:
            agent.set_base_url(base_url)
        result = asyncio.run(agent.run(prompt))
        click.echo(result)
    else:
        _launch_tui(model=model, provider=provider, profile=profile, mode=mode, base_url=base_url, api_key=api_key)


def _launch_tui(model=None, provider=None, profile=None, mode="agent", base_url=None, api_key=None):
    """Launch the Textual TUI interactive chat interface."""
    try:
        from gather.tui.app import GatherTUI
    except ImportError:
        click.echo("Error: TUI requires 'textual' package. Install with: pip install textual")
        click.echo("Falling back to simple interactive mode...")
        _simple_repl(model, provider, profile, mode)
        return

    app = GatherTUI(model=model, provider=provider, profile=profile, mode=mode)
    if base_url:
        app._custom_base_url = base_url
    if api_key:
        app._custom_api_key = api_key
    app.run()


def _simple_repl(model=None, provider=None, profile=None, mode="agent"):
    """Simple REPL fallback when Textual is not available."""
    from gather.agent.core import GatherAgent, AgentMode
    from gather.config.loader import load_config

    config = load_config(profile)
    agent_mode = AgentMode.YOLO if mode == "yolo" else AgentMode.AGENT
    agent = GatherAgent(mode=agent_mode, model=model, provider=provider, profile=profile)

    click.echo("GatherAgent v0.1.0 — The convergence agent")
    click.echo("Type your message and press Enter. Ctrl+C to exit.")
    click.echo("=" * 50)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("/quit", "/exit", "/q"):
                click.echo("Goodbye!")
                break
            if user_input.lower() == "/help":
                click.echo("Commands: /quit, /help, /clear, /cost, /mode <plan|agent|yolo|sandbox>")
                continue
            if user_input.lower() == "/clear":
                click.clear()
                continue
            if user_input.lower() == "/cost":
                click.echo(f"💰 Cost: ${agent.total_cost:.4f} | Turns: {agent.turn_count}")
                continue
            if user_input.lower().startswith("/mode "):
                new_mode = user_input.split(" ", 1)[1].strip()
                mode_map = {"plan": AgentMode.PLAN, "agent": AgentMode.AGENT,
                            "yolo": AgentMode.YOLO, "sandbox": AgentMode.SANDBOX}
                if new_mode in mode_map:
                    agent.mode = mode_map[new_mode]
                    click.echo(f"Mode changed to: {new_mode}")
                else:
                    click.echo(f"Unknown mode: {new_mode}")
                continue

            result = asyncio.run(agent.run(user_input))
            click.echo(f"\n🤖 GatherAgent:\n{result}")
            click.echo(f"\n💰 Cost: ${agent.total_cost:.4f} | Turns: {agent.turn_count}")

        except KeyboardInterrupt:
            click.echo("\nGoodbye!")
            break
        except EOFError:
            click.echo("\nGoodbye!")
            break


@main.command()
def setup():
    """Interactive setup wizard."""
    click.echo("GatherAgent Setup Wizard")
    click.echo("=" * 30)

    api_key = click.prompt("OpenAI API Key", default="", show_default=False)
    if api_key:
        click.echo("✓ OpenAI API Key saved to .env")

    model = click.prompt("Default model", default="gpt-5.5")
    provider = click.prompt("Default provider", default="openai",
                           type=click.Choice(["openai", "anthropic", "openrouter", "ollama", "custom"]))
    mode = click.prompt("Default mode", default="agent",
                       type=click.Choice(["plan", "agent", "yolo", "sandbox"]))

    click.echo(f"\n✓ Configuration saved:")
    click.echo(f"  Model: {model}")
    click.echo(f"  Provider: {provider}")
    click.echo(f"  Mode: {mode}")


@main.command()
def doctor():
    """Check environment and dependencies."""
    import importlib
    click.echo("GatherAgent Doctor Check")
    click.echo("=" * 30)

    checks = [
        ("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
         sys.version_info >= (3, 11)),
        ("openai", _check_pkg("openai"), None),
        ("anthropic", _check_pkg("anthropic"), None),
        ("textual (TUI)", _check_pkg("textual"), None),
        ("rich", _check_pkg("rich"), None),
        ("click", _check_pkg("click"), None),
        ("pyyaml", _check_pkg("yaml"), None),
        ("aiohttp", _check_pkg("aiohttp"), None),
    ]

    for name, info, required in checks:
        if required is True:
            status = "✓" if info else "✗ REQUIRED"
        elif required is False:
            status = "✗"
        else:
            status = "✓" if info else "— (optional)"
        click.echo(f"  {status} {name}: {info or 'not installed'}")

    # Check API keys
    import os
    from pathlib import Path
    env_path = Path(".env")
    click.echo(f"\n  {'✓' if env_path.exists() else '✗'} .env file: {'found' if env_path.exists() else 'not found'}")

    api_keys = {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY"),
    }
    for key, val in api_keys.items():
        status = "✓" if val else "—"
        masked = f"{val[:8]}..." if val else "not set"
        click.echo(f"  {status} {key}: {masked}")


def _check_pkg(name: str) -> str | None:
    """Check if a package is installed and return its version."""
    try:
        mod = importlib.import_module(name)
        return getattr(mod, "__version__", "installed")
    except ImportError:
        return None


@main.command()
def models():
    """List available model providers."""
    click.echo("Available Model Providers:")
    click.echo("  • openai      — OpenAI (GPT-5.5, GPT-5, GPT-4o, o3-mini)")
    click.echo("  • anthropic   — Anthropic (Claude Opus 4.7, Sonnet 4.6, Haiku 4.5)")
    click.echo("  • openrouter  — OpenRouter (Gemini, DeepSeek, Llama, Qwen, Mistral, etc.)")
    click.echo("  • ollama      — Ollama (local models, e.g. qwen3:8b)")
    click.echo("  • custom      — Custom base_url (set in config.yaml)")
    click.echo("\nUsage:")
    click.echo("  gather -m gpt-5.5 \"hello\"                        # OpenAI")
    click.echo("  gather --provider anthropic -m claude-opus-4-7 \"hi\"  # Anthropic")
    click.echo("  gather --provider openrouter -m deepseek/deepseek-v4-pro \"hi\"  # OpenRouter")
    click.echo("  gather --provider ollama -m qwen3:8b \"hi\"        # Ollama local")
    click.echo("\nOr use Ctrl+Shift+M in TUI to set any model interactively.")


@main.command()
@click.option("--dev", is_flag=True, help="Launch in development mode")
@click.option("--port", default=18790, help="Backend port (default: 18790)")
def desktop(dev, port):
    """Launch GatherAgent Desktop (Electron + React)."""
    try:
        from gather.desktop.launcher import launch_desktop
        launch_desktop(port=port, dev=dev)
    except ImportError as e:
        click.echo(f"Error: Desktop dependencies not installed: {e}")
        click.echo("Install with: pip install gather-agent[desktop]")
        click.echo("Then: cd desktop && npm install")


if __name__ == "__main__":
    main()
