"""Format action outputs for appleboy/telegram-action."""

import html
import os
import re
import uuid
from datetime import datetime


def format_notification(env):
    is_html = env["MESSAGE_FORMAT"].lower() == "html"

    def text(value):
        if is_html:
            return html.escape(value, quote=False)
        return re.sub(r"([_*`\[])", r"\\\1", value)

    def bold(value):
        if is_html:
            return f"<b>{text(value)}</b>"
        # Legacy Markdown cannot escape delimiters inside bold entities.
        # The sender also rewrites underscores. Use plain text for these names.
        if "*" in value or "_" in value:
            return text(value)
        return f"*{value}*"

    sha = env["GITHUB_SHA"]
    short_sha = f"<code>{sha[:7]}</code>" if is_html else f"`{sha[:7]}`"
    repo = text(env["GITHUB_REPOSITORY"])
    repo_url = f"https://github.com/{repo}"
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M%p [%A]")
    body = "\n".join([
        f"⏰ {bold(timestamp)}",
        "",
        f"📂 {bold('Branch')}: {text(env['BRANCH'])}",
        f"🔢 {bold('Run')}: #{env['GITHUB_RUN_NUMBER']}",
        f"🔖 {bold('Commit')}: {short_sha}",
        "",
        f"👤 {bold('Triggered by')}: {text(env['GITHUB_ACTOR'])}",
        "",
        f"🧑‍💻 {bold('Commit message')}:",
        text(env["COMMIT_MESSAGE"]),
        "",
        f"🗂 {bold('Changed files')}:",
        text(env["CHANGED_FILES"]),
        "",
        f"🎯 {bold('Repository')}: {repo}",
        "",
        f"🔎 {bold('Run details')}: {repo_url}/actions/runs/{env['GITHUB_RUN_ID']}",
        f"👍 {bold('See changes')}: {repo_url}/commit/{sha}",
    ])
    return {"workflow": bold(env["WORKFLOW_NAME"]), "body": body}


if __name__ == "__main__":
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        for name, value in format_notification(os.environ).items():
            # The sender renders a Handlebars template, then HTML-decodes once.
            # Protect literal braces and preserve the Telegram markup across both.
            value = value.replace("&", "&amp;").replace("{", "&#123;")
            delimiter = uuid.uuid4().hex
            print(f"{name}<<{delimiter}\n{value}\n{delimiter}", file=output)
