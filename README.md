# Crypt Keeper

![Crypt Keeper](https://raw.githubusercontent.com/sistematico/cryptkeeper/main/assets/img/crypt_keeper.jpg "Crypt Keeper")

Um bot simples, não intrusivo para tocar músicas e fazer algumas outras coisas em servidores de discord.
Este bot utiliza a biblioteca Discord.py, YoutubeDL e ffmpeg. Use `ajuda` para receber uma lista de comandos!

## Começando

O que você precisa fazer para começar rapidamente é:

1. Clonar este repositório usando o site do GitHub ou uma ferramenta CLI do GitHub/git.
2. Instalar o `pipenv`, o gerenciador de dependências do Python, e se necessário, garante que os pacotes `opus` e `ffmpeg` estão instalados no servidor e disponíveis no seu ambiente de desenvolvimento. Ambos são usados para streaming de mídia.
3. Navague até o diretório do projeto e rode `pipenv install` to install dependencies.
4. Activate the Pipenv using `pipenv shell`. Run the bot using `python -m cryptkeeper`.
5. On first startup, a default `config.toml` will be generated without an API token, so the bot will abort complaining that `No token has been provided.` Fill your bot's token into `config.toml`.
6. Use something like the [Discord API Permissions calculator](https://discordapi.com/permissions.html) to generate an invite link and invite your bot to your server, if necessary.
7. Run the bot using `python -m cryptkeeper`.

## Dependências adicionais

Make sure that [pipenv](https://pipenv.pypa.io/en/latest/) is installed. Navigate to the project directory, and run `pipenv install` to install the Python dependencies.

To allow for streaming of media, make sure `opus` and `ffmpeg` are installed and in your environment.

To run the bot, activate the virtual environment with `pipenv shell` and then `python -m cryptkeeper` to start the bot.

## Configurando

When you run the bot for the first time, a default configuration file will be generated called `config.toml`. You can enter that file and add your token, etc. The default file looks like this:

```toml
"token"="" # the bot's token
"prefix"="!" # prefix used to denote commands

[music]
# Options for the music commands
"max_volume"=250 # Max audio volume. Set to -1 for unlimited.
"vote_skip"=true # whether vote-skipping is enabled
"vote_skip_ratio"=0.5 # the minimum ratio of votes needed to skip a song
[tips]
"github_url"="https://github.com/sistematico/cryptkeeper"
```

If you ever wish to restore the bot to default configuration, you can simply delete (or rename) your config file. A new one will be generated upon startup.

## Comandos
From the bot's `help` command:
```
Meta:
  uptime Tells how long the bot has been running.
Musica:
  sair   Leaves the voice channel, if currently in one.
  tocar  Plays audio from <url>.
Dicas:
  dica   Get a random tip about using the bot.
Sem categoria:
  help  Mostra essa mensagem
```

## Contributing
Issues and pull requests are welcomed and appreciated. I can't guarantee that I will respond to all issues in a timely manner, but I will try my best to respond to any issues that arise.

## Contato

- lucas@archlinux.com.br

## Ajude

Se o meu trabalho foi útil de qualquer maneira, considere doar qualquer valor através do das seguintes plataformas:

[![LiberaPay](https://img.shields.io/badge/LiberaPay-gray?logo=liberapay&logoColor=white&style=flat-square)](https://liberapay.com/sistematico/donate) [![PagSeguro](https://img.shields.io/badge/PagSeguro-gray?logo=pagseguro&logoColor=white&style=flat-square)](https://pag.ae/bfxkQW) [![ko-fi](https://img.shields.io/badge/ko--fi-gray?logo=ko-fi&logoColor=white&style=flat-square)](https://ko-fi.com/K3K32RES9) [![Buy Me a Coffee](https://img.shields.io/badge/Buy_Me_a_Coffee-gray?logo=buy-me-a-coffee&logoColor=white&style=flat-square)](https://www.buymeacoffee.com/sistematico) [![Open Collective](https://img.shields.io/badge/Open_Collective-gray?logo=opencollective&logoColor=white&style=flat-square)](https://opencollective.com/sistematico) [![Patreon](https://img.shields.io/badge/Patreon-gray?logo=patreon&logoColor=white&style=flat-square)](https://patreon.com/sistematico)

![GitHub Sponsors](https://img.shields.io/github/sponsors/sistematico?label=Github%20Sponsors)