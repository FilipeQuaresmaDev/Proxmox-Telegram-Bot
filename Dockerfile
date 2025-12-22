FROM python:3.12-slim

# ===============================
# Dependências do sistema
# ===============================
RUN apt-get update && apt-get install -y \
    openssh-client \
    gcc \
    libffi-dev \
    libssl-dev \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# Diretório de trabalho
# ===============================
WORKDIR /app

# ===============================
# Copiar requirements
# ===============================
COPY requirements.txt .

# ===============================
# Instalar dependências Python
# ===============================
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ===============================
# Copiar código do projeto
# ===============================
COPY . .

# ===============================
# Permissões do script SSH
# ===============================
RUN chmod +x /app/ssh_keygen.sh

# ===============================
# Timezone (opcional)
# ===============================
ENV TZ=UTC

# ===============================
# Entrypoint
# ===============================
ENTRYPOINT ["/app/ssh_keygen.sh"]
CMD ["python", "bot.py"]
