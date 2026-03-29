import os
import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic
from rich.console import Console
from rich.panel import Panel

console = Console()

YT_AUTH_FILE = "oauth.json"

def authenticate_services():

    # 1. AUTENTICAÇÃO SPOTIFY (Via Variáveis de Ambiente ou Hardcoded)
    # Dica: No futuro, use um arquivo .env para estas 3 variáveis
    sp_oauth = SpotifyOAuth(
        client_id="SEU_CLIENT_ID_AQUI",
        client_secret="SEU_CLIENT_SECRET_AQUI",
        redirect_uri="http://localhost:8888/callback",
        # Escopo para ler e criar playlists (públicas e privadas)
        scope="playlist-modify-public playlist-modify-private playlist-read-private",
        open_browser=False
    )

    token_info = sp_oauth.validate_token(sp_oauth.cache_handler.get_cached_token())

    if not token_info:
        console.print(Panel("[bold green]Autenticação Spotify[/bold green]\n"
                            "1. Clique no link abaixo e autorize no seu navegador.\n"
                            "2. Após o erro de página, cole a URL completa aqui."))
        auth_url = sp_oauth.get_authorize_url()
        console.print(f"\n[link={auth_url}]Clique aqui ou copie o link:[/link]\n{auth_url}\n")
        response_url = console.input("[bold blue]Cole a URL de redirecionamento: [/bold blue]")
        code = sp_oauth.parse_response_code(response_url)
        sp_oauth.get_access_token(code)
        console.print("[green]✓ Spotify conectado![/green]")

    sp_client = Spotify(auth_manager=sp_oauth)

    # 2. AUTENTICAÇÃO YOUTUBE MUSIC
    # Se o arquivo de autenticação não existir, pedimos os headers
    if not os.path.exists(YT_AUTH_FILE):
        console.print(Panel("[bold red]Autenticação YouTube Music[/bold red]\n"
                            "Não encontramos o login do YT Music.\n"
                            "Siga estes passos:\n"
                            "1. Abra o YT Music no Chrome (PC ou Modo Desktop no celular).\n"
                            "2. F12 -> Network -> procure por '/browse'.\n"
                            "3. Clique com o botão direito -> Copy -> Copy as cURL (bash)."))

        curl_input = console.input("[bold blue]Cole o comando cURL copiado aqui: [/bold blue]")
        try:
            # O ytmusicapi consegue extrair os headers direto do comando cURL
            YTMusic.setup(filepath=YT_AUTH_FILE, headers_raw=curl_input)
            console.print("[green]✓ YouTube Music conectado![/green]")
        except Exception as e:
            console.print(f"[red]Erro ao configurar YT Music: {e}[/red]")
            return None, None

    yt_client = YTMusic(YT_AUTH_FILE)

    return sp_client, yt_client

