from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def audit_menu():
    keyboard = [
        [InlineKeyboardButton("📄 Baixar LOG", callback_data="audit:download")],
        [InlineKeyboardButton("📑 Baixar PDF", callback_data="audit:pdf")],
        [InlineKeyboardButton("🔙 Voltar", callback_data="audit:back")],
    ]

    return InlineKeyboardMarkup(keyboard)
