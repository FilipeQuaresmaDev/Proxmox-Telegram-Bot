#!/bin/sh
set -e

SSH_DIR="/root/.ssh"
KEY_FILE="$SSH_DIR/id_ed25519"
PUB_KEY_FILE="$SSH_DIR/id_ed25519.pub"
KNOWN_HOSTS="$SSH_DIR/known_hosts"

AUDIT_DIR="/app/logs"
AUDIT_FILE="$AUDIT_DIR/audit.log"

echo "🔐 Verificando ambiente SSH do bot..."

# ==================================================
# Diretório .ssh
# ==================================================
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

# ==================================================
# Chave SSH
# ==================================================
if [ ! -f "$KEY_FILE" ]; then
  echo "🔑 Chave SSH não encontrada. Gerando nova chave..."
  ssh-keygen -t ed25519 -f "$KEY_FILE" -N ""
  KEY_STATUS="CRIADA"
else
  echo "🔑 Chave SSH já existente."
  KEY_STATUS="EXISTENTE"
fi

chmod 600 "$KEY_FILE"
chmod 644 "$PUB_KEY_FILE"

# ==================================================
# known_hosts (verificação no mesmo padrão)
# ==================================================
if [ ! -f "$KNOWN_HOSTS" ]; then
  echo "📄 Arquivo known_hosts não encontrado. Criando..."
  touch "$KNOWN_HOSTS"
  chmod 644 "$KNOWN_HOSTS"
  KH_STATUS="CRIADO"
else
  echo "📄 Arquivo known_hosts já existente."
  KH_STATUS="EXISTENTE"
fi

# ==================================================
# audit.log (NOVO – mesmo comportamento)
# ==================================================
mkdir -p "$AUDIT_DIR"

if [ ! -f "$AUDIT_FILE" ]; then
  echo "🧾 Arquivo audit.log não encontrado. Criando..."
  touch "$AUDIT_FILE"
  chmod 644 "$AUDIT_FILE"
  AUDIT_STATUS="CRIADO"
else
  echo "🧾 Arquivo audit.log já existente."
  AUDIT_STATUS="EXISTENTE"
fi

# ==================================================
# Mensagem final consolidada
# ==================================================
echo ""
echo "=============================================="
echo "🤖 BOT PROXMOX INICIADO"
echo "🔐 STATUS DO AMBIENTE:"
echo "   🔑 Chave SSH: $KEY_STATUS"
echo "   📄 known_hosts: $KH_STATUS"
echo "   🧾 audit.log: $AUDIT_STATUS"
echo ""
echo "🔐 SSH KEY FINGERPRINT:"
ssh-keygen -lf "$KEY_FILE" || true
echo "=============================================="
echo ""

# ==================================================
# Execução do processo principal (CMD do Docker)
# ==================================================
exec "$@"
