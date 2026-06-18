import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

import click
import tempfiles_conf as config


def main() -> None:
    executor = Executor()
    executor.run(sys.argv[1:])

BLOCKSIZE = 512 * 1024


class Executor:
    def __init__(self) -> None:
        self.cfg = config.Config()
        self.up_url = os.environ.get("TEMPFILES_UPLOAD_URL", self.cfg.UPLOAD_URL)
        self.finish_url = os.environ.get("TEMPFILES_FINISH_URL", self.cfg.FINISH_URL)
        self.prev_read: int = 0
        self.block_size: int = 8192

    def run(self, args: list[str]) -> None:
        parser = argparse.ArgumentParser(
            prog='tempfiles',
            description='Upload/download files to/from tempfil.es',
        )
        parser.add_argument('-v', '--version', action='store_true', help='show version')
        parser.add_argument('-u', '--upload', metavar='FILE', help='upload a file')
        parser.add_argument('-d', '--download', metavar='URL', nargs='?', help='download URL')
        parser.add_argument('destination', nargs='?', help='destination path for download')

        parsed = parser.parse_args(args)

        if parsed.version:
            config.log(self.cfg.VERSION)
            return

        if parsed.upload:
            filepath = parsed.upload
            if os.path.isfile(filepath):
                config.log(self.cfg.UPLOADING, filepath)
                self.upload_file(filepath)
            else:
                config.log(self.cfg.FILE_NOT_FOUND, filepath)
            return

        if parsed.download:
            link = parsed.download
            dest = parsed.destination
            if dest and os.path.isdir(dest):
                self.download_file(link, dest, is_directory=True)
            elif dest:
                self.download_file(link, dest)
            else:
                self.download_file(link)
            return

        config.log(self.cfg.NO_MODE)
        parser.print_help()

    def upload_file(self, filepath: str) -> requests.Response:
        try:
            raw = os.environ.get("TEMPFILES_RAW_BACKEND")
            if raw:
                encoder = MultipartEncoder({
                    'file': (os.path.basename(filepath), open(filepath, 'rb'), 'text/plain')
                })
            else:
                encoder = open(filepath, 'rb')
                encoder.len = os.path.getsize(filepath)

            callback = self._create_callback(encoder)
            monitor = MultipartEncoderMonitor(encoder, callback)

            file_id = str(uuid.uuid4())
            times = (encoder.len // BLOCKSIZE) + 1
            range_total = encoder.len
            range_start = 0
            range_chunk = BLOCKSIZE
            download_link = None

            while times:
                response = requests.post(
                    self.up_url,
                    verify=False,
                    data=monitor.read(BLOCKSIZE),
                    headers={
                        'Content-Type': 'application/octet-stream',
                        'X-NAME': os.path.basename(filepath),
                        'X-ID': file_id,
                        'Content-Range': f'bytes {range_start}-{range_start + range_chunk}/{range_total}',
                    },
                )
                times -= 1
                range_start = range_chunk + 1
                if times == 0:
                    r = json.loads(response.text)
                    download_link = r[0]['download_link']

            requests.post(
                self.finish_url,
                verify=False,
                data=json.dumps({"finish": "true"}).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'X-NAME': os.path.basename(filepath),
                    'X-ID': file_id,
                },
            )

        except requests.exceptions.ConnectionError:
            config.log(self.cfg.CONNECTION_CLOSED)
            raise

        print()
        print(download_link)
        return response

    def download_file(
        self,
        link: str,
        destination: Optional[str] = None,
        is_directory: bool = False,
    ) -> None:
        try:
            response = requests.get(link, verify=False, stream=True)
        except requests.exceptions.MissingSchema:
            config.log(self.cfg.BAD_URL)
            return
        except requests.exceptions.ConnectionError:
            config.log(self.cfg.SERVER_KO)
            raise

        if 'content-disposition' not in response.headers:
            config.log(self.cfg.NOT_FOUND)
            return

        filename = response.headers['content-disposition'].split("=", 1)[1].replace('"', "")

        if destination and is_directory:
            destination_file = str(Path(destination) / filename)
        elif destination:
            destination_file = destination
        else:
            destination_file = filename

        if os.path.isfile(destination_file):
            option = input(self.cfg.OVERWRITE.format(destination_file))
            if option.strip().lower() != 'y':
                return

        total_length = int(response.headers.get('content-length', 0))
        with click.progressbar(length=total_length, label=f'Downloading {filename}') as bar:
            with open(destination_file, 'wb') as handle:
                for block in response.iter_content(self.block_size):
                    handle.write(block)
                    bar.update(len(block))

        print()
        config.log(self.cfg.COMPLETE, destination_file)

    def _create_callback(self, encoder):
        bar = click.progressbar(length=encoder.len, label='Uploading')

        def callback(monitor):
            bar.update(monitor.bytes_read - self.prev_read)
            self.prev_read = monitor.bytes_read

        return callback
