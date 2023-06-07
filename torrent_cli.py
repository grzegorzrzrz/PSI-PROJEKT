import typer
from typing_extensions import Annotated
from pathlib import Path
import sys
from rich.progress import track
import time
import os
import socket


app = typer.Typer()

root_path = Path(__file__).parent

sys.path.append(root_path)

import client


"""
    load config file
"""
with open('cli/psi_torrent.config', 'r') as file:
    config = file.readlines()
    DOWNLOAD_PATH = config[0].rstrip('\n')
    VERBOSE = bool(config[1].rstrip('\n'))


@app.command()
def config(
    download_path: Annotated[str, typer.Option(help="Path for downloaded files")] = DOWNLOAD_PATH,
    verbose: Annotated[bool, typer.Option(help="Verbosity of log output")] = VERBOSE,
):
    """
    Default config for psi_torrent downloads
    """
    with open("cli/psi_torrent.config", "w") as f:
        f.write(download_path + '\n')
        f.write(str(verbose) + '\n')
    print(f"config! {download_path}, {verbose}")


@app.command()
def download(target: str):
    """
    Use this command to download a torrent to your pc
    """
    torrent_details, torrent_data = parse_torrent_file(target)
    # torrent_details to nazwa ia rozmiar pliku, torrent_data to lista dostępnych seederów - do uzupełnienia na callu

    file_path = 'dowyslania/zdjecie.png'

    hash_list = client.calculate_hash_list(file_path, torrent_details[2])
    client.download_file(torrent_data, torrent_details[1], torrent_details[2], DOWNLOAD_PATH + torrent_details[0], hash_list)
    print(f"download! target: {target}")

@app.command()
def upload():
    total = 0
    for value in track(['x' for _ in range(100)], description="Processing..."):
        # Fake processing time
        time.sleep(0.01)
        total += 1
    print(f"Processed {total} things.")

"""
    helpers
"""


def parse_torrent_file(torrent_file_path):
    with open(torrent_file_path) as torrent_file:
        file_path = 'dowyslania/zdjecie.png'

        host = socket.gethostbyname(socket.gethostname())
        data = [(host, 5050, file_path), (host, 5051, file_path)]
        file_size = os.path.getsize(file_path)
        print(file_size)
        details = ['norbert_gierczak.png', file_size, 65563]
        return details, data


if __name__ == "__main__":

    app()