import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

# ── Path Detection ──────────────────────────────────────────────
# When running as .exe (frozen): use AppData for writable data
# When running as script (dev):  use project root
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = Path(sys.executable).parent          # where .exe is
    DATA_DIR   = Path(os.environ['APPDATA']) / 'AI Employee'
    os.environ['AI_EMPLOYEE_DATA'] = str(DATA_DIR)    # pass to watchers
else:
    BUNDLE_DIR = Path(__file__).parent.parent
    DATA_DIR   = BUNDLE_DIR

BASE_DIR = DATA_DIR

# ── First Run Setup ─────────────────────────────────────────────
# Copy initial files from bundle to AppData on first install
def first_run_setup():
    if not getattr(sys, 'frozen', False):
        return  # dev mode — skip
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Copy vault (with scheduled posts, handbook, etc.)
    src_vault = BUNDLE_DIR / '_internal' / 'vault'
    dst_vault = DATA_DIR / 'vault'
    if src_vault.exists() and not dst_vault.exists():
        shutil.copytree(str(src_vault), str(dst_vault))
    # Copy settings.json
    src_settings = BUNDLE_DIR / '_internal' / 'settings.json'
    dst_settings = DATA_DIR / 'settings.json'
    if src_settings.exists() and not dst_settings.exists():
        shutil.copy2(str(src_settings), str(dst_settings))
    # Create empty .env
    env_file = DATA_DIR / '.env'
    if not env_file.exists():
        env_file.write_text('GMAIL_ADDRESS=\nGMAIL_APP_PASSWORD=\nLINKEDIN_ACCESS_TOKEN=\nANTHROPIC_API_KEY=\n')

first_run_setup()

# ── Flask App ───────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    template_folder = str(BUNDLE_DIR / '_internal' / 'dashboard' / 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

app.secret_key = "ai_employee_secret_2026"

@app.context_processor
def inject_pending_count():
    count = len(list(PENDING_DIR.glob("*.md"))) if PENDING_DIR.exists() else 0
    return {"pending_dir_count": count}

SETTINGS_FILE = BASE_DIR / "settings.json"
VAULT_DIR = BASE_DIR / "vault"
LOGS_DIR = VAULT_DIR / "Logs"
DONE_DIR = VAULT_DIR / "Done"
NEEDS_ACTION_DIR = VAULT_DIR / "Needs_Action"
PENDING_DIR = VAULT_DIR / "Pending_Approval"


DEFAULT_SETTINGS = {
    "client_name": "My Business",
    "agent": {"status": "running"},
    "email": {
        "auto_reply": True,
        "check_interval_minutes": 2,
        "reply_tone": "Professional",
        "sensitive_keywords": ["payment", "password", "bank", "urgent", "lawsuit"],
    },
    "linkedin": {
        "auto_post": True,
        "post_time": "09:00",
        "topics": [],
    },
}


def load_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # Merge with defaults so missing keys never crash templates
            for section, defaults in DEFAULT_SETTINGS.items():
                if section not in data:
                    data[section] = defaults
                elif isinstance(defaults, dict):
                    for key, val in defaults.items():
                        if key not in data[section]:
                            data[section][key] = val
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_stats():
    done_count = len(list(DONE_DIR.glob("*.md"))) if DONE_DIR.exists() else 0
    pending_count = len(list(NEEDS_ACTION_DIR.glob("*.md"))) if NEEDS_ACTION_DIR.exists() else 0
    approval_count = len(list(PENDING_DIR.glob("*.md"))) if PENDING_DIR.exists() else 0
    return done_count, pending_count, approval_count


def get_recent_logs(limit=10):
    logs = []
    if LOGS_DIR.exists():
        log_files = sorted(LOGS_DIR.glob("*.md"), reverse=True)[:3]
        for log_file in log_files:
            try:
                lines = log_file.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    if line.strip().startswith("-"):
                        logs.append(line.strip("- ").strip())
                        if len(logs) >= limit:
                            return logs
            except Exception:
                pass
    return logs


# ─── Routes ───────────────────────────────────────────────

@app.route("/")
def index():
    settings = load_settings()
    done, pending, approval = get_stats()
    logs = get_recent_logs()
    status = settings.get("agent", {}).get("status", "running")
    return render_template("index.html",
                           settings=settings,
                           done=done,
                           pending=pending,
                           approval=approval,
                           logs=logs,
                           status=status)


@app.route("/emails", methods=["GET", "POST"])
def emails():
    settings = load_settings()
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_keyword":
            kw = request.form.get("keyword", "").strip().lower()
            if kw and kw not in settings["email"]["sensitive_keywords"]:
                settings["email"]["sensitive_keywords"].append(kw)
                save_settings(settings)
                flash(f"Keyword '{kw}' added successfully!", "success")

        elif action == "remove_keyword":
            kw = request.form.get("keyword", "")
            if kw in settings["email"]["sensitive_keywords"]:
                settings["email"]["sensitive_keywords"].remove(kw)
                save_settings(settings)
                flash(f"Keyword '{kw}' removed.", "info")

        elif action == "save_settings":
            settings["email"]["reply_tone"] = request.form.get("reply_tone", "Professional")
            settings["email"]["check_interval_minutes"] = int(request.form.get("check_interval", 2))
            settings["email"]["auto_reply"] = request.form.get("auto_reply") == "on"
            save_settings(settings)
            flash("Email settings saved!", "success")

        return redirect(url_for("emails"))

    return render_template("emails.html", settings=settings)


@app.route("/linkedin", methods=["GET", "POST"])
def linkedin():
    settings = load_settings()
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_topic":
            topic = request.form.get("topic", "").strip()
            if topic and topic not in settings["linkedin"]["topics"]:
                settings["linkedin"]["topics"].append(topic)
                save_settings(settings)
                flash(f"Topic added!", "success")

        elif action == "remove_topic":
            topic = request.form.get("topic", "")
            if topic in settings["linkedin"]["topics"]:
                settings["linkedin"]["topics"].remove(topic)
                save_settings(settings)
                flash(f"Topic removed.", "info")

        elif action == "save_settings":
            settings["linkedin"]["post_time"] = request.form.get("post_time", "09:00")
            settings["linkedin"]["auto_post"] = request.form.get("auto_post") == "on"
            save_settings(settings)
            flash("LinkedIn settings saved!", "success")

        elif action == "add_post":
            post_date = request.form.get("post_date", "").strip()
            post_content = request.form.get("post_content", "").strip()
            if post_date and post_content:
                scheduled_file = BASE_DIR / "vault" / "scheduled_posts.json"
                scheduled = {}
                if scheduled_file.exists():
                    with open(scheduled_file, encoding='utf-8') as f:
                        scheduled = json.load(f)
                scheduled[post_date] = post_content
                scheduled_file.parent.mkdir(parents=True, exist_ok=True)
                with open(scheduled_file, 'w', encoding='utf-8') as f:
                    json.dump(scheduled, f, ensure_ascii=False, indent=2)
                flash(f"Post scheduled for {post_date}!", "success")
            else:
                flash("Date aur content dono zaroori hain.", "warning")

        elif action == "delete_post":
            post_date = request.form.get("post_date", "").strip()
            scheduled_file = BASE_DIR / "vault" / "scheduled_posts.json"
            if scheduled_file.exists() and post_date:
                with open(scheduled_file, encoding='utf-8') as f:
                    scheduled = json.load(f)
                scheduled.pop(post_date, None)
                with open(scheduled_file, 'w', encoding='utf-8') as f:
                    json.dump(scheduled, f, ensure_ascii=False, indent=2)
                flash(f"Post deleted for {post_date}.", "info")

        return redirect(url_for("linkedin"))

    # Load scheduled posts
    scheduled_file = BASE_DIR / "vault" / "scheduled_posts.json"
    scheduled_posts = {}
    if scheduled_file.exists():
        with open(scheduled_file, encoding='utf-8') as f:
            scheduled_posts = json.load(f)
    return render_template("linkedin.html", settings=settings, scheduled_posts=scheduled_posts)


def parse_log_file(log_file):
    """Parse a log file — handles both old and new formats."""
    import re
    entries = []
    try:
        lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        date = log_file.stem

        # Detect format
        # New format: lines like "- [09:31:15] LinkedIn | POSTED | ..."
        # Old format: sections like "## 09:52 — Email Processed" with sub-bullets

        current_section = None
        current_time = ""
        current_title = ""
        current_details = []

        for line in lines:
            stripped = line.strip()

            # Old format — section header: ## 09:52 — Email Processed
            if stripped.startswith("##"):
                # Save previous section
                if current_section and current_details:
                    entries.append({
                        "date": date,
                        "time": current_time,
                        "title": current_title,
                        "entry": current_title,
                        "details": current_details[:],
                        "format": "old"
                    })
                # Parse new section
                m = re.match(r'##\s*(\d{1,2}:\d{2})\s*[—-]\s*(.+)', stripped)
                if m:
                    current_time = m.group(1)
                    current_title = m.group(2).strip()
                    current_details = []
                    current_section = True

            # Old format — sub-bullet under a section
            elif stripped.startswith("-") and current_section:
                detail = stripped.lstrip("-").strip()
                # Remove markdown bold **text:**
                detail = re.sub(r'\*\*(.+?)\*\*', r'\1', detail)
                if detail:
                    current_details.append(detail)

            # New format — standalone entry: - [09:31:15] Module | Action
            elif stripped.startswith("-") and not current_section:
                m = re.match(r'-\s*\[(\d{2}:\d{2}:\d{2})\]\s*(.+)', stripped)
                if m:
                    time_str = m.group(1)
                    rest = m.group(2).strip()
                    entries.append({
                        "date": date,
                        "time": time_str,
                        "title": rest,
                        "entry": rest,
                        "details": [],
                        "format": "new"
                    })

        # Save last old-format section
        if current_section and current_details:
            entries.append({
                "date": date,
                "time": current_time,
                "title": current_title,
                "entry": current_title,
                "details": current_details[:],
                "format": "old"
            })

    except Exception as e:
        entries.append({
            "date": log_file.stem, "time": "", "title": f"Error: {e}",
            "entry": f"Error: {e}", "details": [], "format": "new"
        })

    return entries


@app.route("/logs")
def logs():
    all_logs = []
    ralph_logs = []
    SKIP_KEYWORDS = ["RalphWiggum | All tasks complete"]

    if LOGS_DIR.exists():
        log_files = sorted(LOGS_DIR.glob("*.md"), reverse=True)[:14]
        for log_file in log_files:
            entries = parse_log_file(log_file)
            for e in reversed(entries):  # newest first
                if any(kw in e["entry"] for kw in SKIP_KEYWORDS):
                    ralph_logs.append(e)
                else:
                    all_logs.append(e)

    def sort_key(e):
        # Sort by date then time — newest first
        return (e.get("date", ""), e.get("time", ""))

    all_logs.sort(key=sort_key, reverse=True)
    ralph_logs.sort(key=sort_key, reverse=True)

    show_ralph = request.args.get("show_all") == "1"
    if show_ralph:
        all_logs = all_logs + ralph_logs

    return render_template("logs.html", logs=all_logs,
                           settings=load_settings(),
                           ralph_count=len(ralph_logs),
                           show_all=show_ralph)


@app.route("/email_detail/<filename>")
def email_detail(filename):
    """Return email task details from vault/Done/."""
    import re
    safe_name = Path(filename).name
    email_file = DONE_DIR / safe_name
    if not email_file.exists():
        # Search in all Done subfolders
        for f in DONE_DIR.rglob("*.md"):
            if f.name == safe_name:
                email_file = f
                break
    if not email_file.exists():
        return {"found": False}

    try:
        raw = email_file.read_text(encoding="utf-8", errors="replace")
        # Parse frontmatter
        data = {"found": True, "from_": "", "subject": "", "received": "", "body": "", "reply": ""}
        fm_match = re.match(r'^---\s*\n(.*?)\n---', raw, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).splitlines():
                if line.startswith("from:"):
                    data["from_"] = line.split(":", 1)[1].strip()
                elif line.startswith("subject:"):
                    data["subject"] = line.split(":", 1)[1].strip()
                elif line.startswith("received:"):
                    data["received"] = line.split(":", 1)[1].strip()
        # Parse email body
        body_match = re.search(r'## Email Content\s*\n(.*?)(?:\n##|\Z)', raw, re.DOTALL)
        if body_match:
            data["body"] = body_match.group(1).strip() or "(Email body was empty)"
        # Parse reply if saved
        reply_match = re.search(r'## Reply Sent\s*\n(.*?)(?:\n##|\Z)', raw, re.DOTALL)
        if reply_match:
            data["reply"] = reply_match.group(1).strip()
        return data
    except Exception as e:
        return {"found": False, "error": str(e)}


@app.route("/post_content/<filename>")
def post_content(filename):
    """Return LinkedIn post content for modal display."""
    safe_name = Path(filename).name  # prevent path traversal
    post_file = DONE_DIR / "linkedin_posted" / safe_name
    if post_file.exists():
        content = post_file.read_text(encoding="utf-8", errors="replace")
        # Strip frontmatter
        lines = content.strip().splitlines()
        body_lines = []
        in_front = False
        started = False
        for line in lines:
            if line.strip() == "---":
                if not started:
                    in_front = True
                    started = True
                    continue
                elif in_front:
                    in_front = False
                    continue
            if not in_front:
                body_lines.append(line)
        return {"found": True, "content": "\n".join(body_lines).strip()}
    return {"found": False, "content": ""}


@app.route("/approvals")
def approvals():
    pending = []
    if PENDING_DIR.exists():
        for f in sorted(PENDING_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                import re
                raw = f.read_text(encoding="utf-8", errors="replace")
                info = {"filename": f.name, "from_": "", "subject": "", "received": "", "body": "", "raw": raw}
                fm = re.match(r'^---\s*\n(.*?)\n---', raw, re.DOTALL)
                if fm:
                    for line in fm.group(1).splitlines():
                        if line.startswith("from:"):    info["from_"]    = line.split(":",1)[1].strip()
                        elif line.startswith("subject:"): info["subject"] = line.split(":",1)[1].strip()
                        elif line.startswith("received:"): info["received"] = line.split(":",1)[1].strip()
                body_m = re.search(r'## Email Content\s*\n(.*?)(?:\n##|\Z)', raw, re.DOTALL)
                if body_m:
                    info["body"] = body_m.group(1).strip() or "(empty)"
                # Detect why flagged
                keywords = load_settings().get("email", {}).get("sensitive_keywords", [])
                flagged = [kw for kw in keywords if kw.lower() in raw.lower()]
                info["flagged_keywords"] = flagged
                pending.append(info)
            except Exception:
                pass
    return render_template("approvals.html", pending=pending, settings=load_settings())


@app.route("/approve/<filename>", methods=["POST"])
def approve(filename):
    safe = Path(filename).name
    src = PENDING_DIR / safe
    dst = BASE_DIR / "vault" / "Approved" / safe
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        src.rename(dst)
        flash(f"✅ Approved: {safe}", "success")
    return redirect(url_for("approvals"))


@app.route("/reject/<filename>", methods=["POST"])
def reject(filename):
    safe = Path(filename).name
    src = PENDING_DIR / safe
    dst = BASE_DIR / "vault" / "Rejected" / safe
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        src.rename(dst)
        flash(f"❌ Rejected: {safe}", "warning")
    return redirect(url_for("approvals"))


def start_hidden(script_path):
    """Start a Python script as a hidden background process."""
    import subprocess, sys
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    env = os.environ.copy()
    env['AI_EMPLOYEE_DATA'] = str(DATA_DIR)
    if getattr(sys, 'frozen', False):
        # In frozen mode, find python in bundle or system
        python = os.path.join(os.path.dirname(sys.executable), '_internal', 'python.exe')
        if not os.path.exists(python):
            python = 'python'
        # Watcher scripts are in _internal/watchers/
        script_path = Path(sys.executable).parent / '_internal' / 'watchers' / Path(script_path).name
    else:
        python = sys.executable
    subprocess.Popen(
        [python, str(script_path)],
        cwd=str(DATA_DIR),
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        env=env
    )


def restart_gmail_agent():
    """Kill existing watchers and start fresh ones (Gmail + LinkedIn)."""
    import subprocess, sys, os

    python = sys.executable

    # Kill existing watchers
    for script in ['gmail_watcher', 'linkedin_watcher', 'linkedin_content_generator']:
        subprocess.run(
            f'wmic process where "name=\'python.exe\' and commandline like \'%{script}%\'" delete',
            shell=True, capture_output=True
        )

    import time
    time.sleep(1)

    # Start Gmail watcher
    start_hidden(BASE_DIR / "watchers" / "gmail_watcher.py")

    # Start LinkedIn watcher
    start_hidden(BASE_DIR / "watchers" / "linkedin_watcher.py")

    # Start LinkedIn scheduler (checks time and posts daily)
    start_hidden(BASE_DIR / "watchers" / "linkedin_scheduler.py")


@app.route("/restart_agent", methods=["POST"])
def restart_agent():
    restart_gmail_agent()
    flash("Agent restarted with new settings!", "success")
    return redirect(url_for("accounts"))


@app.route("/toggle_agent", methods=["POST"])
def toggle_agent():
    settings = load_settings()
    current = settings.get("agent", {}).get("status", "running")
    settings.setdefault("agent", {})["status"] = "stopped" if current == "running" else "running"
    save_settings(settings)
    new_status = settings["agent"]["status"]
    flash(f"Agent is now {new_status.upper()}.", "success" if new_status == "running" else "warning")
    return redirect(url_for("index"))


@app.route("/linkedin/auth")
def linkedin_auth():
    """Redirect user to LinkedIn OAuth login page."""
    env = {}
    ENV_FILE = BASE_DIR / ".env"
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

    # LinkedIn app credentials — loaded from bundled secrets file
    try:
        from dashboard._app_secrets import LINKEDIN_CLIENT_ID as _LI_ID, LINKEDIN_CLIENT_SECRET as _LI_SECRET
    except ImportError:
        try:
            from _app_secrets import LINKEDIN_CLIENT_ID as _LI_ID, LINKEDIN_CLIENT_SECRET as _LI_SECRET
        except ImportError:
            _LI_ID = env.get("LINKEDIN_CLIENT_ID", "")
            _LI_SECRET = env.get("LINKEDIN_CLIENT_SECRET", "")
    client_id = env.get("LINKEDIN_CLIENT_ID", _LI_ID)

    redirect_uri = "http://localhost:5000/linkedin/callback"
    scope = "openid profile email w_member_social"
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope.replace(' ', '%20')}"
    )
    return redirect(auth_url)


@app.route("/linkedin/callback")
def linkedin_callback():
    """Handle LinkedIn OAuth callback — exchange code for token."""
    import urllib.request, urllib.parse
    code = request.args.get("code", "")
    error = request.args.get("error", "")

    if error:
        flash(f"LinkedIn login failed: {error}", "danger")
        return redirect(url_for("accounts"))

    ENV_FILE = BASE_DIR / ".env"
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()

    try:
        from dashboard._app_secrets import LINKEDIN_CLIENT_ID as _LI_ID2, LINKEDIN_CLIENT_SECRET as _LI_SECRET2
    except ImportError:
        try:
            from _app_secrets import LINKEDIN_CLIENT_ID as _LI_ID2, LINKEDIN_CLIENT_SECRET as _LI_SECRET2
        except ImportError:
            _LI_ID2 = env.get("LINKEDIN_CLIENT_ID", "")
            _LI_SECRET2 = env.get("LINKEDIN_CLIENT_SECRET", "")
    client_id     = env.get("LINKEDIN_CLIENT_ID", _LI_ID2)
    client_secret = env.get("LINKEDIN_CLIENT_SECRET", _LI_SECRET2)
    redirect_uri  = "http://localhost:5000/linkedin/callback"

    try:
        data = urllib.parse.urlencode({
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  redirect_uri,
            "client_id":     client_id,
            "client_secret": client_secret,
        }).encode()
        req = urllib.request.Request(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())

        token = result.get("access_token", "")
        if token:
            env["LINKEDIN_ACCESS_TOKEN"] = token
            lines = [f"{k}={v}" for k, v in env.items()]
            ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
            flash("LinkedIn connected successfully! Token saved automatically.", "success")
        else:
            flash(f"Could not get token: {result}", "danger")
    except Exception as e:
        flash(f"Error connecting LinkedIn: {e}", "danger")

    return redirect(url_for("accounts"))


@app.route("/accounts", methods=["GET", "POST"])
def accounts():
    ENV_FILE = BASE_DIR / ".env"
    TOKEN_FILE = BASE_DIR / "token.json"
    CREDS_FILE = BASE_DIR / "credentials.json"

    def read_env():
        env = {}
        if ENV_FILE.exists():
            for line in ENV_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
        return env

    def write_env(env_dict):
        lines = [f"{k}={v}" for k, v in env_dict.items()]
        ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if request.method == "POST":
        action = request.form.get("action")
        env = read_env()

        if action == "save_linkedin_app":
            cid = request.form.get("linkedin_client_id", "").strip()
            csecret = request.form.get("linkedin_client_secret", "").strip()
            if cid and csecret:
                env["LINKEDIN_CLIENT_ID"] = cid
                env["LINKEDIN_CLIENT_SECRET"] = csecret
                write_env(env)
                flash("LinkedIn App credentials saved! Now click 'Connect LinkedIn'.", "success")
            else:
                flash("Both Client ID and Client Secret are required.", "warning")

        elif action == "save_linkedin":
            token = request.form.get("linkedin_token", "").strip()
            if token:
                env["LINKEDIN_ACCESS_TOKEN"] = token
                write_env(env)
                restart_gmail_agent()
                flash("✅ LinkedIn connected! Agent restarted automatically.", "success")
            else:
                flash("Token cannot be empty.", "warning")

        elif action == "save_anthropic":
            key = request.form.get("anthropic_key", "").strip()
            if key:
                env["ANTHROPIC_API_KEY"] = key
                write_env(env)
                flash("Anthropic API key updated!", "success")
            else:
                flash("API key cannot be empty.", "warning")

        elif action == "save_gmail":
            gmail_addr = request.form.get("gmail_address", "").strip()
            gmail_pass = request.form.get("gmail_app_password", "").strip()
            if gmail_addr and gmail_pass:
                env["GMAIL_ADDRESS"]      = gmail_addr
                env["GMAIL_APP_PASSWORD"] = gmail_pass
                write_env(env)
                # Delete UID watermark so watcher takes fresh inbox snapshot
                # on next start — only NEW emails after this point get replied
                uid_file = BASE_DIR / "last_uid.txt"
                if uid_file.exists():
                    uid_file.unlink()
                processed_file = BASE_DIR / "processed_emails.json"
                processed_file.write_text("[]", encoding="utf-8")
                restart_gmail_agent()
                flash(f"✅ Gmail connected: {gmail_addr} — Agent restarted! Only NEW emails will get auto-reply.", "success")
            else:
                flash("Both email and app password are required.", "warning")

        elif action == "disconnect_gmail":
            # Save credentials as backup before disconnecting
            if env.get("GMAIL_ADDRESS"):
                env["GMAIL_ADDRESS_BACKUP"]      = env.get("GMAIL_ADDRESS", "")
                env["GMAIL_APP_PASSWORD_BACKUP"] = env.get("GMAIL_APP_PASSWORD", "")
            env.pop("GMAIL_ADDRESS", None)
            env.pop("GMAIL_APP_PASSWORD", None)
            write_env(env)
            if TOKEN_FILE.exists():
                TOKEN_FILE.unlink()
            flash("Gmail disconnected. Saved credentials available for reconnect.", "info")

        elif action == "disconnect_linkedin":
            env.pop("LINKEDIN_ACCESS_TOKEN", None)
            write_env(env)
            flash("LinkedIn disconnected successfully.", "info")

        elif action == "upload_credentials":
            file = request.files.get("credentials_file")
            if file and file.filename.endswith(".json"):
                file.save(str(CREDS_FILE))
                flash("Gmail credentials uploaded! Now restart the agent to connect Gmail.", "success")
            else:
                flash("Please upload a valid .json file.", "warning")

        return redirect(url_for("accounts"))

    env = read_env()
    gmail_address        = env.get("GMAIL_ADDRESS", "")
    gmail_backup_email   = env.get("GMAIL_ADDRESS_BACKUP", "")
    gmail_backup_pass    = env.get("GMAIL_APP_PASSWORD_BACKUP", "")
    gmail_connected      = bool(gmail_address) or TOKEN_FILE.exists()
    creds_exist = CREDS_FILE.exists()
    linkedin_token     = env.get("LINKEDIN_ACCESS_TOKEN", "")
    linkedin_client_id = env.get("LINKEDIN_CLIENT_ID", "")
    anthropic_key      = env.get("ANTHROPIC_API_KEY", "")

    # Mask tokens for display
    def mask(val):
        if not val or len(val) < 10:
            return ""
        return val[:6] + "•" * 20 + val[-4:]

    return render_template("accounts.html",
                           settings=load_settings(),
                           gmail_connected=gmail_connected,
                           gmail_address=gmail_address,
                           gmail_backup_email=gmail_backup_email,
                           gmail_backup_pass=gmail_backup_pass,
                           gmail_backup_masked=mask(gmail_backup_pass),
                           creds_exist=creds_exist,
                           linkedin_token=linkedin_token,
                           linkedin_masked=mask(linkedin_token),
                           linkedin_client_id=linkedin_client_id,
                           anthropic_key=anthropic_key,
                           anthropic_masked=mask(anthropic_key))


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    settings = load_settings()
    if request.method == "POST":
        settings["client_name"] = request.form.get("client_name", "My Business")
        save_settings(settings)
        flash("Settings saved!", "success")
        return redirect(url_for("settings_page"))
    return render_template("settings.html", settings=settings)


if __name__ == "__main__":
    print("=" * 50)
    print("  AI Employee Dashboard")
    print("  Open browser: http://localhost:5000")
    print("=" * 50)
    # Auto-start all agents
    restart_gmail_agent()
    print("  All Agents started automatically")
    print("=" * 50)
    # Auto-open browser
    import threading, webbrowser, time
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(debug=False, port=5000)
