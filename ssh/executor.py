import os
import paramiko
from pathlib import Path

SSH_USER = os.getenv("SSH_USER")
SSH_KEY = Path("/root/.ssh/id_ed25519")

def run_command(ip: str, command: str, timeout: int = 10) -> str:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    key = paramiko.Ed25519Key.from_private_key_file(str(SSH_KEY))

    ssh.connect(
        hostname=ip,
        username=SSH_USER,
        pkey=key,
        look_for_keys=False,
        allow_agent=False,
        timeout=timeout
    )

    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    output = stdout.read().decode()
    error = stderr.read().decode()

    ssh.close()

    return output if output else error
