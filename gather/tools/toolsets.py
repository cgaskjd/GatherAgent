"""Toolset definitions — from Hermes-Agent's grouping pattern."""
from gather.tools.registry import registry
GATHER_CORE_TOOLS = ["read_file", "write_file", "edit_file", "search_files", "list_dir",
    "shell", "git_status", "git_log", "git_diff", "git_commit"]
TOOLSETS = {
    "core": GATHER_CORE_TOOLS,
    "browser": ["browser_navigate", "browser_click", "browser_screenshot"],
    "delegation": ["delegate_task", "agent_open", "agent_eval", "agent_close"],
    "memory": ["memory_store", "memory_recall", "memory_search"],
    "messaging": ["send_message", "read_messages"],
    "cron": ["cron_add", "cron_list", "cron_remove"],
    "kanban": ["kanban_show", "kanban_complete", "kanban_block"],
    "skills": ["load_skill", "skill_manage"],
    "mcp": ["mcp_call"],
}
