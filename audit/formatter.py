from pathlib import Path

RAW_LOG = Path("/app/logs/audit.log")
PRETTY_LOG = Path("/app/logs/audit_pretty.log")


def _clean_target(target: str) -> str:
    """
    Extrai apenas o NOME do alvo.
    Remove IDs como 'VM 101', 'LXC 106', etc.
    """
    if not target:
        return "-"

    parts = target.split()

  
    if len(parts) >= 3 and parts[1].isdigit():
        return " ".join(parts[2:])


    if len(parts) == 2:
        return parts[1]

    return target


def generate_pretty_log():
    if not RAW_LOG.exists():
        return None

    lines = RAW_LOG.read_text().splitlines()
    output = []

    for line in lines:
        try:

            parts = [p.strip() for p in line.split("|")]

            date = parts[0]
            user_id = parts[1]
            username = parts[2]
            action = parts[3]
            raw_target = parts[4] if len(parts) > 4 else "-"

            target = _clean_target(raw_target)

            block = [
                "════════════════════════════════════",
                f"📅 Data/Hora : {date}",
                f"👤 Usuário   : {username}",
                f"🆔 User ID   : {user_id}",
                f"🎯 Ação      : {action}",
                f"🖥️ Alvo      : {target}",
                "════════════════════════════════════",
                "",
            ]

            output.extend(block)

        except Exception:

            output.append(line)

    PRETTY_LOG.write_text("\n".join(output))
    return PRETTY_LOG
