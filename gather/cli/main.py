"""CLI Entry Point."""
import click, asyncio, sys
from gather.config.profile import apply_profile


@click.group(invoke_without_command=True)
@click.option("--model", "-m", default=None, help="Model override")
@click.option("--provider", default=None, help="Provider override")
@click.option("--profile", "-p", default=None, help="Profile name")
@click.option("--yolo", is_flag=True, help="Auto-approve all tools")
@click.option("--tui", is_flag=True, help="Launch TUI (default if no prompt)")
@click.argument("prompt", required=False)
@click.pass_context
def main(ctx, model, provider, profile, yolo, tui, prompt):
    """GatherAgent — The convergence agent."""
    apply_profile(profile)
    mode = "yolo" if yolo else "agent"

    if prompt:
        # One-shot mode: run agent directly and print result
        from gather.agent.core import GatherAgent, AgentMode
        agent_mode = AgentMode.YOLO if yolo else AgentMode.AGENT
        agent = GatherAgent(mode=agent_mode, model=model, provider=provider, profile=profile)
        result = asyncio.run(agent.run(prompt))
        click.echo(result)
    else:
        # No prompt: launch TUI interactive chat
        _launch_tui(model=model, provider=provider, profile=profile, mode=mode)


def _launch_tui(model=None, provider=None, profile=None, mode="agent"):
    """Launch the Textual TUI interactive chat interface."""
    try:
        from gather.tui.app import GatherTUI
    except ImportError:
        click.echo("Error: TUI requires 'textual' package. Install with: pip install textual")
        click.echo("Falling back to simple interactive mode...")
        _simple_repl(model, provider, profile, mode)
        return

    app = GatherTUI(model=model, provider=provider, profile=profile, mode=mode)
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

    model = click.prompt("Default model", default="gpt-4o")
    provider = click.prompt("Default provider", default="openai",
                           type=click.Choice(["openai", "anthropic", "openrouter"]))
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
    click.echo("  • openai      — OpenAI (GPT-4o, GPT-4o-mini, etc.)")
    click.echo("  • anthropic   — Anthropic (Claude Sonnet, Opus, etc.)")
    click.echo("  • openrouter  — OpenRouter (multi-provider access)")
    click.echo("\nSet via: gather --provider openai --model gpt-4o")


if __name__ == "__main__":
    main()
