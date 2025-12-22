from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, AUTHORIZED_USERS
from menus.main import main_menu
from menus.instances import instances_menu
from menus.actions import actions_menu
from menus.docker import docker_menu, docker_actions_menu
from menus.audit import audit_menu

from proxmox.client import get_proxmox
from proxmox.list import list_all_instances
from proxmox.network import (
    get_vm_ip_via_agent,
    get_lxc_ip_via_api
)
from proxmox.actions import (
    start_instance,
    stop_instance,
    reboot_instance
)
from proxmox.status import (
    get_instance_status,
    human_bytes,
    human_uptime
)

from docker.manager import (
    has_docker,
    list_containers,
    docker_action,
    docker_logs
)

from ssh.executor import run_command
from audit.logger import log_action
from audit.formatter import generate_pretty_log
from audit.pdf_exporter import generate_audit_pdf


# =========================================================
# STATUS
# =========================================================

async def render_status(query, context):
    inst = context.user_data.get("current_instance")
    if not inst:
        await query.edit_message_text("❌ Contexto perdido.")
        return

    proxmox = get_proxmox()
    status = get_instance_status(
        proxmox,
        inst["inst_type"],
        inst["node"],
        inst["vmid"]
    )

    if status["type"] == "vm":
        disk_line = f"💾 *Disco:* {human_bytes(status['disk_total'])} (total)"
    else:
        disk_line = (
            f"💾 *Disco:* {human_bytes(status['disk_used'])} / "
            f"{human_bytes(status['disk_total'])}"
        )

    text = (
        f"🖥️ *{inst['name']}*\n"
        f"🆔 *ID:* {inst['vmid']}\n\n"
        "📊 *Status da Instância*\n\n"
        f"🔢 CPU: {status['cpu']}%\n"
        f"🧠 Memória: {human_bytes(status['mem_used'])} / {human_bytes(status['mem_total'])}\n"
        f"{disk_line}\n"
        f"🌐 Rede IN: {human_bytes(status['net_in'])}\n"
        f"🌐 Rede OUT: {human_bytes(status['net_out'])}\n"
        f"⏱️ Uptime: {human_uptime(status['uptime'])}"
    )

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=actions_menu(
            inst["inst_type"],
            inst["node"],
            inst["vmid"],
            inst["has_docker"]
        )
    )


# =========================================================
# /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("⛔ Acesso negado.")
        return

    await update.message.reply_text(
        "🤖 Bot Proxmox\n\nSelecione uma opção:",
        reply_markup=main_menu()
    )


# =========================================================
# CALLBACKS
# =========================================================

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    user = query.from_user
    user_id = user.id
    username = user.username or user.first_name

    # -------------------------
    # SAIR
    # -------------------------
    if data == "exit":
        context.user_data.clear()
        log_action(user_id, username, "exit", "session")  # AUDIT
        await query.edit_message_text("👋 Sessão encerrada.\n\nAté a próxima!")
        return

    # -------------------------
    # MENU AUDITORIA
    # -------------------------
    if data == "audit:menu":
        await query.edit_message_text(
            "📄 Auditoria\n\nSelecione o formato:",
            reply_markup=audit_menu()
        )
        return

    if data == "audit:back":
        await query.edit_message_text(
            "🤖 Bot Proxmox\n\nSelecione uma opção:",
            reply_markup=main_menu()
        )
        return

    if data == "audit:download":
        log_action(user_id, username, "audit_download", "log")  # AUDIT
        log_file = generate_pretty_log()
        if not log_file:
            await query.edit_message_text("❌ Auditoria não encontrada.")
            return

        await query.message.reply_document(
            document=log_file.open("rb"),
            filename="audit.log",
            caption="📄 Auditoria em LOG"
        )
        return

    if data == "audit:pdf":
        log_action(user_id, username, "audit_download", "pdf")  # AUDIT
        pdf = generate_audit_pdf()
        if not pdf:
            await query.edit_message_text("❌ Auditoria não encontrada.")
            return

        await query.message.reply_document(
            document=pdf.open("rb"),
            filename="audit.pdf",
            caption="📑 Auditoria em PDF"
        )
        return

    # -------------------------
    # PROXMOX
    # -------------------------
    if data == "proxmox" or data == "back:instances":
        await query.edit_message_text(
            "🖥️ Selecione uma VM ou Container LXC:",
            reply_markup=instances_menu()
        )
        return

    # -------------------------
    # STATUS
    # -------------------------
    if data.startswith("status:") or data == "refresh:status":
        await render_status(query, context)
        return

    # -------------------------
    # VOLTAR AÇÕES
    # -------------------------
    if data == "back:actions":
        inst = context.user_data["current_instance"]
        await query.edit_message_text(
            inst["text"],
            reply_markup=actions_menu(
                inst["inst_type"],
                inst["node"],
                inst["vmid"],
                inst["has_docker"]
            )
        )
        return

    # -------------------------
    # DOCKER
    # -------------------------
    if data == "back:docker":
        containers = list_containers(context.user_data["ssh_host"])
        await query.edit_message_text(
            "🐳 Containers Docker:",
            reply_markup=docker_menu(containers)
        )
        return

    if data == "docker:list":
        containers = list_containers(context.user_data["ssh_host"])
        await query.edit_message_text(
            "🐳 Containers Docker:",
            reply_markup=docker_menu(containers)
        )
        return

    if data.startswith("docker:select:"):
        cid = data.split(":")[2]
        await query.edit_message_text(
            f"🐳 Container selecionado:\n{cid}",
            reply_markup=docker_actions_menu(cid)
        )
        return

    if data.startswith("docker:logs:"):
        cid = data.split(":")[2]
        logs = docker_logs(context.user_data["ssh_host"], cid) or "(sem logs)"
        if len(logs) > 3500:
            logs = logs[-3500:]

        log_action(user_id, username, "docker_logs", cid)  # AUDIT

        await query.edit_message_text(
            f"📄 *Logs do container*\n\n```\n{logs}\n```",
            parse_mode="Markdown",
            reply_markup=docker_actions_menu(cid)
        )
        return

    if data.startswith("docker:"):
        _, action, cid = data.split(":")
        log_action(user_id, username, f"docker_{action}", cid)  # AUDIT
        docker_action(context.user_data["ssh_host"], action, cid)
        await query.edit_message_text(
            f"🐳 Docker `{action}` executado com sucesso.",
            reply_markup=docker_actions_menu(cid)
        )
        return

    # -------------------------
    # AÇÕES VM / LXC
    # -------------------------
    if data.startswith("action:"):
        _, action, inst_type, node, vmid = data.split(":")
        vmid = int(vmid)
        proxmox = get_proxmox()

        target = f"{inst_type.upper()} {vmid}"

        if action == "cmd":
            context.user_data["awaiting_cmd"] = True
            await query.edit_message_text("💻 Envie o comando:")
            return

        log_action(user_id, username, action, target)  # AUDIT

        if action == "start":
            start_instance(proxmox, inst_type, node, vmid)
            msg = "▶️ *Comando de INÍCIO enviado*"
        elif action == "stop":
            stop_instance(proxmox, inst_type, node, vmid)
            msg = "⏹️ *Comando de PARADA enviado*"
        elif action == "reboot":
            reboot_instance(proxmox, inst_type, node, vmid)
            msg = "🔁 *Comando de REINÍCIO enviado*"

        await query.edit_message_text(msg, parse_mode="Markdown")
        return

    # -------------------------
    # SELEÇÃO VM / LXC
    # -------------------------
    if data.startswith("instance:"):
        _, inst_type, node, vmid = data.split(":")
        vmid = int(vmid)

        inst = next(
            i for i in list_all_instances()
            if i["id"] == vmid and i["type"] == inst_type
        )

        name = inst["name"]
        status = inst["status"]

        if inst_type == "vm":
            ip = get_vm_ip_via_agent(get_proxmox(), node, vmid)
            ssh_host = ip
            label = "🖥️ VM"
        else:
            ip = get_lxc_ip_via_api(get_proxmox(), node, vmid) 
            ssh_host = ip 

            context.user_data["ssh_host"] = ssh_host
            label = "📦 LXC"

        docker_ok = has_docker(ssh_host)

        text = (
            f"{label}\n"
            f"📛 Nome: {name}\n"
            f"🆔 ID: {vmid}\n"
            f"⚙️ Status: {status}\n"
            f"🌐 IP: {ip}"
        )

        context.user_data["ssh_host"] = ssh_host
        context.user_data["current_instance"] = {
            "inst_type": inst_type,
            "node": node,
            "vmid": vmid,
            "name": name,
            "has_docker": docker_ok,
            "text": text,
        }

        await query.edit_message_text(
            text,
            reply_markup=actions_menu(inst_type, node, vmid, docker_ok)
        )


# =========================================================
# COMANDO MANUAL (SSH)
# =========================================================

async def receive_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_cmd"):
        return

    context.user_data["awaiting_cmd"] = False
    cmd = update.message.text
    host = context.user_data["ssh_host"]

    log_action(
        update.effective_user.id,
        update.effective_user.username or update.effective_user.first_name,
        "ssh_command",
        host,
        details=cmd
    )  # AUDIT

    output = run_command(host, cmd) or "(sem saída)"
    if len(output) > 3500:
        output = output[:3500] + "\n...\n(saída truncada)"

    await update.message.reply_text(
        "✅ *Comando executado*\n\n"
        f"💻 *Comando:*\n```\n{cmd}\n```\n\n"
        "📤 *Saída:*\n"
        f"```\n{output}\n```",
        parse_mode="Markdown"
    )


# =========================================================
# MAIN
# =========================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_command)
    )

    print("🤖 Bot Proxmox iniciado")
    app.run_polling()


if __name__ == "__main__":
    main()
