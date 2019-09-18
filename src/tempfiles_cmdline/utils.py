import uuid
import optparse
import os.path
import requests
import json
import sys
import os
import tempfiles_conf.configuration as configuration
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import click

# Support vars
BLOCKSIZE = 512*1024
ENDL = "\n"
usage = """
\twhere options are:
\t\t -v => show the tool's version
\t\t -u file_path => upload mode
\t\t -d download_link [destination_file_path] => download mode
"""
class ExtendedMonitor(MultipartEncoderMonitor):
    def __init__(self, encoder, callback=None, block_size=BLOCKSIZE):
        super().__init__(encoder, callback)

    def to_string(self):
        return self.read(block_size)


class Executor:
    """ Class for execute uploads/downloads to/from tempfil.es service. """
    def __init__(self):
        self.parser = optparse.OptionParser(usage='usage: %prog [options]'+usage)
        self.parser.add_option('-u', '--upload', action='store_true', default=False, help='upload mode')
        self.parser.add_option('-d', '--download', action='store_true', default=False, help='download mode')
        self.parser.add_option('-v', '--version', action='store_true', default=False, help='version number')
        self.configuration_service = configuration.ConfigurationService()
        self.up_url = os.environ.get("TEMPFILES_UPLOAD_URL", self.configuration_service.get('UPLOAD_URL'))
        self.finish_url = os.environ.get("TEMPFILES_FINISH_URL", self.configuration_service.get('FINISH_URL'))
        self.prev_read = 0
        self.block_size = 8192
        self.file_type = 'text/plain'

    def run(self, args):
        (options, arguments) = self.parser.parse_args(args)

        if options.version:
            filepath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "__init__.py")
            conf = configuration.ConfigurationService(filepath=filepath)
            print(conf.get('version'))
            sys.exit(0)

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
            raw = os.environ.get("TEMPFILES_RAW_BACKEND", None)
            if raw:
                encoder = self.create_upload(filepath)
            else:
                # bypass multipart encoder / don't works with nginx direct upload.
                encoder = open(filepath, 'rb')
                try:
                    encoder.len = os.path.getsize(filepath)
                except AttributeError:
                    # supporting python 2.7 trick for adding len to file stream
                    class Wrapped(object):
                        def __init__(self, enc, path):
                            self._enc = enc
                            self.len = os.path.getsize(path)

                        def __getattr__(self, attr):
                            return getattr(self._enc, attr)
                    encoder = Wrapped(encoder, filepath)
            callback = self.create_callback(encoder)
            monitor = ExtendedMonitor(encoder, callback)
            print("Uploading to: " + self.up_url)
            id = str(uuid.uuid4())
            try:
                times = (encoder.len // BLOCKSIZE)+1
                range_total = encoder.len
                range_start = 0
                range_chunk = BLOCKSIZE
                download_link = None
                while times:
                    response = requests.post(self.up_url,
                                             verify=False,
                                             data=monitor.read(BLOCKSIZE),
                                             headers={
                                                 'Content-Type': 'application/octet-stream',
                                                 'X-NAME': os.path.basename(filepath),
                                                 'X-ID': id,
                                                 'Content-Range': 'bytes {}-{}/{}'.format(range_start, range_start+range_chunk, range_total)
                                             })
                    times-=1
                    range_start = range_chunk + 1
                    if times == 0:
                        r = json.loads(response.text)
                        download_link = r[0]['download_link']
                # finish upload
                requests.post(self.finish_url,
                              verify=False,
                              data=json.dumps({"finish": "true"}).encode('utf-8'),
                              headers={
                                  'Content-Type': 'application/json',
                                  'X-NAME': os.path.basename(filepath),
                                  'X-ID': id
                              })


            except Exception as e:
                print(e)
            print(ENDL)
            print(download_link)
            return download_link
        except requests.exceptions.ConnectionError:
            self.configuration_service.log('CONNECTION_CLOSED')

    def download_file(self, link, destination=None, is_directory=False):
        try:
            response = requests.get(link, verify=False, stream=True)
            if 'content-disposition' in response.headers:
                filename = response.headers['content-disposition'].split("=", 1)[1].replace("\"","")

                if destination and is_directory:
                    destination_file = destination + '/' + filename
                elif destination:
                    destination_file = destination
                else:
                    destination_file = filename

                option = 'y'
                if os.path.isfile(destination_file):
                    try:
                        option = raw_input(self.configuration_service.get('OVERWRITE').format(destination_file))
                    except NameError:
                        option = input(self.configuration_service.get('OVERWRITE').format(destination_file))
                if str(option) == 'y':
                    #total_length = int(response.headers.get('content-length'))
                    total_length = 0
                    with click.progressbar(length=total_length) as bar:
                        with open(destination_file, 'wb') as handle:
                            for block in response.iter_content(self.block_size):
                                handle.write(block)
                                bar.update(len(block))
                    print(ENDL)
                    self.configuration_service.log('COMPLETE', (destination_file,))
            else:
                self.configuration_service.log('NOT_FOUND')
        except requests.exceptions.MissingSchema:
            self.configuration_service.log('BAD_URL')
        except requests.exceptions.ConnectionError:
            self.configuration_service.log('SERVER_KO')
            raise
        except:
            print(self.configuration_service.get('ALIEN'), sys.exc_info()[0])
            raise

    def create_callback(self, encoder):
        bar = click.progressbar(length=encoder.len)

        def callback(monitor):
            bar.update(monitor.bytes_read - self.prev_read)
            self.prev_read = monitor.bytes_read

        return callback

    def create_upload(self, filepath):
        return MultipartEncoder({
            'file': (os.path.basename(filepath), open(filepath, 'rb'), self.file_type)
            })
