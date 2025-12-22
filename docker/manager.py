from ssh.executor import run_command


def has_docker(host):
    """
    Retorna True SOMENTE se Docker estiver realmente em execução.
    Verificação baseada no socket oficial do Docker.
    """
    try:
        cmd = "[ -S /var/run/docker.sock ] && echo OK || echo NO"
        result = run_command(host, cmd).strip()
        return result == "OK"
    except Exception:
        return False


def list_containers(host):
    """
    Lista TODOS os containers Docker (rodando e parados)
    """
    output = run_command(
        host,
        "docker ps -a --format '{{.ID}}|{{.Names}}|{{.Status}}'"
    )

    containers = []
    for line in output.splitlines():
        cid, name, status = line.split("|")
        containers.append({
            "id": cid,
            "name": name,
            "status": status
        })

    return containers


def docker_action(host, action, container_id):
    if action not in ["start", "stop", "restart"]:
        raise ValueError("Ação Docker inválida")

    run_command(host, f"docker {action} {container_id}")


def docker_logs(host, container_id, tail=100):
    return run_command(
        host,
        f"docker logs --tail {tail} {container_id}"
    )
