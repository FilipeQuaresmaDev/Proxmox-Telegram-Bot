# Proxmox-Telegram-Bot
Este projeto tem como objetivo buscar uma alternativa para que você possa estar "monitorando" e "Gerindo" seu servidor Proxmox PVE de maneira remota e com o mínimo de gasto de dados de internet através do Telegram. 


=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
             OBJETIVO
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

Este projeto tem como objetivo buscar uma alternativa para que você possa estar "monitorando" e "Gerindo"
seu servidor Proxmox PVE de maneira remota e com o mínimo de gasto de dados de internet através do Telegram.

O motivo pelas aspas se deve que essa aplicação tem algumas limitações, não lhe dando um real e completo monitoramento e gestão
do servidor, realmente mais para usuários que buscam um controle básico de seu servidor como ligar/desligar
maquinas virtuais/ Containers LXC, verificar uso de recursos, logs e também gerenciar os containers Docker caso exista.



=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
             INSTALAÇÃO
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# 1 - Instalação em Container LXC dentro do proxmox

  1.1 Criar Container LXC
   *Criate CT
   *Template: Debian 12 ou Ubuntu 22.04
   *Hostname: SUA ESCOLHA
   *CPU: 1 core
   *RAM: 512MB
   *Disco: 8GB
   *Network: bridge

 # 1.2 Acessar Container
   * atualizar sistema
 
    - apt update && apt upgrade -y
 
   * Instalar pacotes
 
    - apt install -y \
        curl \
        git \
        openssh-client \
        python3 \
        python3-venv \
        python3-pip \

# 1.3 Criar ssh do BOT
    * comando
 
     - ssh-keygen -t ed25519 -f /root/.ssh/id_25519 -C "USER_BOT"

     assim que aparecer para definir passphrase apenas aperte ENTER

# 1.4 Verificação
 Ainda na maquina do BOT execute o comando:

   - ls /root/.ssh

Deve aparecer:

    id_ed25519
    id_ed25519.pub

após essa confirmação execute

   - cat /root/.ssh/id_ed25519.pub

copie o conteúdo mostrado, essa será a chave pública ssh.
essa chave será utilizada em todas as máquinas.

# 1.5 Configurar proxmox

siga as janelas

  Datacenter -> Permissions -> Users -> Add

  User: USER_BOT@pve
  Realm: pve
  password: qualquer um, não será usado.

Após isso siga

USER@pve -> API Tokens -> Add

  Token: USER_BOT
  marcar quadrado - privilege separation

copie o token gerado.

Após isso siga novamente

  Datacenter -> Permissions -> Add -> User Permission

  Path: /
  User: USER_BOT@pve
  Role:
    PVEAuditor
    PVEAdmin

Feito isso, seu token Api e seu Usuário ja está criado e permissionado. Seguindo para o bot no telegram

# 1.6 - Bot no Telegram

Baixe o telegram no celular e inicie uma conversa com o "@BotFather"

Execute

  /newbot

  Nome: SUA ESCOLHA
  Username: SUA ESCOLHA

Após feito isso, o próprio BotFather irá mandar uma mensagem constando tudo do seu bot juntamente com o
TOKEN de acesso a ele. Copie o TOKEN mostrado.

Após isso vamos pegar o seu ID TELEGRAM. Inicie uma conversa com "@userinfobot"

Assim que iniciado a conversa ele mostrará seu id do telegram, copie ele.

EXPLICAÇÃO: Seu id telegram iremos usar como uma medida de segurança, pois com ele o seu bot irá funcionar somente com
            o seu número do telegram e com mais ninguém.

# 1.7 Cria o usuário do bot em todas as VM'S/Containers LXC

Em cada uma das maquinas você irá repetir exatamente a mesma coisa. Primeiramente execute o comando

   - adduser USER_BOT

Crie a estrutura do ssh

   - mkdir -p /home/USER_BOT/.ssh
     nano /home/USER_BOT/.ssh/authorized_keys

Nesse documento cole a chave ssh gerada e copiada no passo 1.4, salve e fecha.
Depois disso execute os comandos

   - chown -R USER_BOT:USER_BOT /home/USER_BOT
     chmod 755 /home/USER_BOT
     chmod 700 /home/USER_BOT/.ssh
     chmod 600 /home/USER_BOT/.ssh/authorized_keys
     usermod -aG docker USER_BOT

Após realizar esses passos nas VM'S/Containers LXC, volte no console da maquina do bot e tente entrar via ssh nas maquinas onde você realizou esse processo

   - ssh USER_BOT@IP_DA_MAQUINA

Deve entrar sem pedir senha, se entrar quer dizer que funcionou.

# 1.8 Instalar e configurar o bot

Volte no console da maquina do bot e execute os comandos:

   - mkdir -p /opt/bot
     cd /opt/bot

Nisso você irá para dentro do diretório e dentro dele que iremos trabalhar. Execute

   - git clone

Após isso iremos criar o ambiente virtual python. execute.

   - python3 -m venv venv
     source venv/bin/activate

Nisso entrará no ambiente virtual python.
EXPLICAÇÃO: Por algum motivo quando se estar dentro de um Container LXC ele não permite execução e nem instalação de
            dependências do python para o bot funcionar, então trabalharemos no ambiente virtual SEMPRE.

Após isso execute esse comando para instalar todas as dependências necessárias:

   ```# pip install --upgrade pip
     pip install -r requirements.txt```

Após isso, todas as dependências foram instaladas.

# 1.9 Configurar o bot

Iremos mexer em três arquivos "config.py" , "proxmox/client.py" e "executor.py"

--config.py--

BOT_TOKEN = "TOKEN DO SEU BOT TELGRAM"
AUTHORIZED_USERS = [SEU ID TELEGRAM]

--proxmox/client.py--

PROXMOX_HOST = "IP_SERVIDOR_PROXMOX"
PROXMOX_USER = "USER_BOT@pve"
PROXMOX_TOKEN_NAME = "USER_BOT"
PROXMOX_TOKEN_VALUE = "TOKEN_PROXMOX"

--executor.py--

SSH_USER = "USER_BOT"


Sobre os campos do arquivo "proxmox/client.py" você encontra eles no passo 1.5 e do "config.py" no passo 1.6.

Feito isso façamos um teste executando

   - python3 bot.py

Após executar esse comando aparecerá a mensagem dizendo que o bot está ativado.

Vá no telegram, na conversa com seu bot, e comece mandando "/start". Se ele responder com opções para você escolher
quer dizer que funcionou.

# 1.10 Inicialização automática do bot ao iniciar maquina

Execute o comando

   - nano /etc/systemd/system/NOME_DO_SERVIÇO_DESEJADO.service

cole dentro do arquivo o seguinte comando

   - [Unit]
     Description=DESCRIÇÃO QUE VOCÊ QUISER
     After=network.target

     [Service]
     WorkingDirectory=/opt/bot
     ExecStart=/opt/bot/venv/bin/python bot.py
     Restart=Always
     User=root

     [Install]
     WantedBy=multi-user.target

Salve e feche. para ativar execute:

   - systemctl daemon-reexec
     systemctl daemon-reload
     systemctl enable NOME_DO_SERVIÇO_DESEJADO
     systemctl start NOME_DO_SERVIÇO_DESEJADO

Após isso o bot está instalado, configurado e sempre irá executar ao iniciar a maquina, reiniciar o bot caso dê algum problema e somente
irá parar caso desligue a maquina.

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=

# 2. Instalação do bot em container Docker.

OBS.: O método de bot em container pula os passos 1.1, 1.2, 1.3 e 1.4, pois ao executar o docker-compose ele ja cria tudo para voce somente copiar a "ssh key"
e o ambiente ja é todo preparado. Tenha em mente que o "USER_BOT" é preferível que ja seja definido por você, pois usaremos ele antes de criar os usuários das vm's
e deve ser exatamente igual ao que você declarou nas variáveis de ambiente do docker-compose.

Comece pelos passos 1.5 e 1.6, pois dessa maneira você ja terá os tokens e id's necessários para preencher o docker-compose. Lembrando que o "USER_BOT" já esta definido e
será os usuários que posteriormente será criado nas VM's/Container's LXC.


Crie uma pasta onde será o diretório de trabalho do bot dentro da maquina escolhida onde roda Docker, em seguinda use o comando

   - docker pull

isso irá trazer a imagem para dentro da sua maquina dentro do servidor. Após isso, pegue o docker-compose que consta nessa pagina
do GitHub e monte de acordo com suas variáveis de ambiente preenchendo com os dados que você ja possui.

DICA: Ja deixei alguns nomes sugestivos para que não haja conflito ou problema na hora de executar o bot, como é o caso do
"USER_BOT" que coloquei querendo indicar que é bom usar o mesmo USER tanto para os usuários das maquinas quanto nas permissões.


Após isso continue no passo 1.7 e já estará pronto seu bot.

Caso queira fazer o mesmo teste do final do passo 1.7, use o comando
    - docker exec -it <nome_do_container> /bin/bash

Irá abrir o terminar do container, apenas cole o mesmo comando substituindo as variáveis.
