import os, logging, toml

EXAMPLE_CONFIG = """
\"token\"=\"\" # the bot's token
\"prefix\"=\"!\" # prefix used to denote commands

[music]
# Opcoes para comandos de musica
"max_volume"=250 # Max audio volume. Set to -1 for unlimited.
"vote_skip"=true # whether vote-skipping is enabled
"vote_skip_ratio"=0.5 # the minimum ratio of votes needed to skip a song
[tips]
"github_url"="https://github.com/sistematico/cryptkeeper"
"""


def load_config(path="./config.toml"):
    """Carrega a config do `path`"""
    if os.path.exists(path) and os.path.isfile(path):
        config = toml.load(path)
        return config
    else:
        # open("u.item", encoding="utf-8") with open('u.item', encoding = "ISO-8859-1")
        with open(path, "w") as config:
            config.write(EXAMPLE_CONFIG)
            logging.warn(f"Nenhum arquivo de config encontrado. Criando um em {path}")
        return load_config(path=path)
