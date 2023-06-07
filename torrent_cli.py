import typer
from typing_extensions import Annotated
from pathlib import Path
import sys
from rich.progress import track
import time
import os
import socket
import json


app = typer.Typer()

root_path = Path(__file__).parent

sys.path.append(root_path)

import client


CONFIG_PATH = './'


"""
    load config file
"""
try:
    with open(CONFIG_PATH + 'psi_torrent.config', 'r') as file:
        config = file.readlines()
        DOWNLOAD_PATH = config[0].rstrip('\n')
        VERBOSE = bool(config[1].rstrip('\n'))
        PIECE_LENGTH = int(config[2].rstrip('\n'))
except FileNotFoundError:
    DOWNLOAD_PATH = '.'
    VERBOSE = False
    PIECE_LENGTH = 65536
    with open(CONFIG_PATH + 'psi_torrent.config', 'w') as file:
        file.write(DOWNLOAD_PATH + '\n')
        file.write(str(VERBOSE) + '\n')
        file.write(str(PIECE_LENGTH) + '\n')

@app.command()
def config(
    download_path: Annotated[str, typer.Option(help="Path for downloaded files")] = DOWNLOAD_PATH,
    verbose: Annotated[bool, typer.Option(help="Verbosity of log output")] = VERBOSE,
    piece_length: Annotated[int, typer.Option(help="Default piece size of uploaded files")] = PIECE_LENGTH,
):
    """
    Default config for psi_torrent downloads
    """
    with open(CONFIG_PATH + "psi_torrent.config", "w") as f:
        f.write(download_path + '\n')
        f.write(str(verbose) + '\n')
        f.write(str(piece_length) + '\n')
    print(f"config! {download_path}, {verbose}, {piece_length}")


@app.command()
def download(target: str):
    """
    Use this command to download a torrent to your pc
    """
    torrent_details, torrent_seeders = parse_torrent_file(target)
    # torrent_details to nazwa ia rozmiar pliku, torrent_data to lista dostępnych seederów - do uzupełnienia na callu

    correct_seeders = []

    for s in torrent_seeders:
        correct_seeders.append(tuple(s.values()))

    client.download_file(correct_seeders, torrent_details['file_size'], torrent_details['piece_size'], DOWNLOAD_PATH + torrent_details['file_name'], torrent_details['hash'], torrent_details['file_id'])

@app.command()
def upload(target: str):
    file_path = target
    file_name = target.split('\\')[-1]
    client.add_file(file_name, file_path, PIECE_LENGTH)


"""
    helpers
"""


def parse_torrent_file(torrent_file_path):
    with open(torrent_file_path) as torrent_file:
        json_data = json.loads(torrent_file.read())

        details = json_data['0']
        seeders = json_data['seeders']
        return details, seeders


if __name__ == "__main__":
    app()