from datetime import datetime


LOG_FILE = "/app/logs/audit.log"


def log_action(
    user_id,
    username,
    action,
    target,
    result="OK",
    details=""
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = (
        f"[{timestamp}] "
        f"user_id={user_id} "
        f"user={username} "
        f"action={action} "
        f"target={target} "
        f"result={result} "
        f"details=\"{details}\"\n"
    )

    with open(LOG_FILE, "a") as f:
        f.write(line)
