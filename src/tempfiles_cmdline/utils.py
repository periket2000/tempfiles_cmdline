import optparse
import os.path
import requests
import json
import sys
import tempfiles_conf.configuration as configuration
from clint.textui.progress import Bar as ProgressBar
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

usage = """
\twhere options are:
\t\t -u file_path => upload mode
\t\t -d download_link [destination_file_path] => download mode
"""


class Executor:
    def __init__(self):
        self.parser = optparse.OptionParser(usage='usage: %prog [options]'+usage)
        self.parser.add_option('-u', '--upload', action='store_true', default=False, help='upload mode')
        self.parser.add_option('-d', '--download', action='store_true', default=False, help='download mode')
        self.configuration_service = configuration.ConfigurationService()
        self.up_url = self.configuration_service.get('UPLOAD_URL')

    def run(self, args):
        (options, arguments) = self.parser.parse_args(args)
        if not options.upload and not options.download:
            self.configuration_service.log('NO_MODE')
            self.parser.print_usage()
            return

        if options.upload and len(args) < 2:
            self.configuration_service.log('NO_FILE_GIVEN')
            self.parser.print_usage()
            return
        elif options.upload:
            filepath = args[1]
            if os.path.isfile(filepath):
                self.configuration_service.log('UPLOADING', (filepath,))
                self.upload_file(filepath)
            else:
                self.configuration_service.log('FILE_NOT_FOUND', (filepath,))
            return

        if options.download and len(args) < 2:
            self.configuration_service.log('NO_DOWNLOAD_LINK')
            self.parser.print_usage()
            return

        if options.download and len(args) < 3:
            download_link = args[1]
            self.download_file(download_link)
            return
        else:
            download_link = args[1]
            destination_path = args[2]

            if os.path.isdir(destination_path):
                self.download_file(download_link, destination_path, is_directory=True)
                return
            elif os.path.isfile(destination_path) or os.access(os.path.dirname(destination_path), os.W_OK):
                self.download_file(download_link, destination_path)
                return
            else:
                self.configuration_service.log('INVALID_DESTINATION')

    def upload_file(self, filepath):
        try:
            encoder = self.create_upload(filepath)
            callback = self.create_callback(encoder)
            monitor = MultipartEncoderMonitor(encoder, callback)
            r = requests.post(self.up_url, data=monitor, headers={'Content-Type': monitor.content_type})
            print()
            print(json.loads(r.text))
        except requests.exceptions.ConnectionError:
            self.configuration_service.log('CONNECTION_CLOSED')

    def download_file(self, link, destination=None, is_directory=False):
        try:
            response = requests.get(link, stream=True)
            if 'content-disposition' in response.headers:
                filename = response.headers['content-disposition'].split("\"")[1]

                if destination and is_directory:
                    destination_file = destination + '/' + filename
                elif destination:
                    destination_file = destination
                else:
                    destination_file = filename

                option = 'y'
                if os.path.isfile(destination_file):
                    option = input(self.configuration_service.get('OVERWRITE').format(destination_file))
                if option == 'y':
                    total_length = int(response.headers.get('content-length'))
                    dl = 0
                    with open(destination_file, 'wb') as handle:
                        for block in response.iter_content(1024):
                            handle.write(block)
                            dl = self._progress(dl, block, total_length)
                    print()
                    self.configuration_service.log('COMPLETE', (destination_file,))
            else:
                self.configuration_service.log('NOT_FOUND')
        except requests.exceptions.MissingSchema:
            self.configuration_service.log('BAD_URL')
        except requests.exceptions.ConnectionError:
            self.configuration_service.log('SERVER_KO')
        except:
            print(self.configuration_service.get('ALIEN'), sys.exc_info()[0])
            raise

    @staticmethod
    def _progress(dl, block, total_length):
        dl += len(block)
        bar = ProgressBar(expected_size=total_length, filled_char='=')
        bar.show(dl)
        return dl

    @staticmethod
    def create_callback(encoder):
        encoder_len = encoder.len
        bar = ProgressBar(expected_size=encoder_len, filled_char='=')

        def callback(monitor):
            bar.show(monitor.bytes_read)

        return callback

    @staticmethod
    def create_upload(filepath):
        return MultipartEncoder({
            'file': (os.path.basename(filepath), open(filepath, 'rb'), 'text/plain')
            })
