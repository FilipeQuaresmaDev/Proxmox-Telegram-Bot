from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def docker_menu(containers):
    rows = []

    for c in containers:
        rows.append(
            [
                InlineKeyboardButton(
                    f"{c['name']} ({c['status']})",
                    callback_data=f"docker:select:{c['id']}"
                )
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                "⬅️ Voltar",
                callback_data="back:actions"
            )
        ]
    )

    return InlineKeyboardMarkup(rows)


def docker_actions_menu(container_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📄 Logs",
                callback_data=f"docker:logs:{container_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "▶️ Start",
                callback_data=f"docker:start:{container_id}"
            ),
            InlineKeyboardButton(
                "⏹️ Stop",
                callback_data=f"docker:stop:{container_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔄 Restart",
                callback_data=f"docker:restart:{container_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                "⬅️ Voltar",
                callback_data="back:docker"
            )
        ]
    ])
