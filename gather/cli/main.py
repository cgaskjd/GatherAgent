"""CLI Entry Point."""
import click, asyncio
from gather.config.profile import apply_profile
@click.group(invoke_without_command=True)
@click.option("--model", "-m", default=None, help="Model override")
@click.option("--provider", default=None, help="Provider override")
@click.option("--profile", "-p", default=None, help="Profile name")
@click.option("--yolo", is_flag=True, help="Auto-approve all tools")
@click.option("--tui", is_flag=True, help="Launch TUI")
@click.argument("prompt", required=False)
@click.pass_context
def main(ctx, model, provider, profile, yolo, tui, prompt):
    """GatherAgent \u2014 The convergence agent."""
    apply_profile(profile)
    if tui:
        click.echo("TUI mode coming soon..."); return
    if prompt:
        from gather.agent.core import GatherAgent, AgentMode
        mode = AgentMode.YOLO if yolo else AgentMode.AGENT
        agent = GatherAgent(mode=mode, model=model, provider=provider, profile=profile)
        result = asyncio.run(agent.run(prompt))
        click.echo(result)
    else:
        click.echo("GatherAgent v0.1.0 \u2014 The convergence agent")
        click.echo('Run: gather "your prompt" or gather --help')
@main.command()
def setup(): click.echo("Setup wizard coming soon...")
@main.command()
def doctor(): click.echo("Doctor check coming soon...")
@main.command()
def models(): click.echo("Model listing coming soon...")
if __name__ == "__main__": main()
