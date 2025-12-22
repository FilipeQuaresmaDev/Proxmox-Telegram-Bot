from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def actions_menu(inst_type, node, vmid, has_docker):
    rows = [
        [
            InlineKeyboardButton(
                "📊 Status",
                callback_data=f"status:{inst_type}:{node}:{vmid}"
            ),
            InlineKeyboardButton(
                "🔄 Atualizar",
                callback_data="refresh:status"
            ),
        ],
        [
            InlineKeyboardButton(
                "▶️ Start",
                callback_data=f"action:start:{inst_type}:{node}:{vmid}"
            ),
            InlineKeyboardButton(
                "⏹️ Stop",
                callback_data=f"action:stop:{inst_type}:{node}:{vmid}"
            ),
            InlineKeyboardButton(
                "🔁 Reboot",
                callback_data=f"action:reboot:{inst_type}:{node}:{vmid}"
            ),
        ],
        [
            InlineKeyboardButton(
                "💻 Executar comando",
                callback_data=f"action:cmd:{inst_type}:{node}:{vmid}"
            )
        ],
    ]

    if has_docker:
        rows.append(
            [
                InlineKeyboardButton(
                    "🐳Containers Docker",
                    callback_data="docker:list"
                )
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                "⬅️ Voltar",
                callback_data="back:instances"
            )
        ]
    )

    return InlineKeyboardMarkup(rows)
