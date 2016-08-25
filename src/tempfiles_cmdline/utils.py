import optparse
import os.path
import requests
import json
import sys

usage = """

\twhere options are:
\t\t -u file_path => upload mode
\t\t -d download_link [destination_path] => download mode
"""


class Executor:
    def __init__(self):
        self.parser = optparse.OptionParser(usage='usage: %prog [options]'+usage)
        self.parser.add_option('-u', '--upload', action='store_true', default=False, help='upload mode')
        self.parser.add_option('-d', '--download', action='store_true', default=False, help='download mode')
        self.up_url = "https://tempfil.es/fileupload/"

    def run(self, args):
        (options, arguments) = self.parser.parse_args(args)
        if not options.upload and not options.download:
            print('No mode selected!')
            self.parser.print_usage()
            return;

        if options.upload and len(args) < 2:
            print('No file to upload given!')
            self.parser.print_usage()
            return;
        elif options.upload:
            filepath = args[1]
            if os.path.isfile(filepath):
                print('Uploading "{0}" to https://tempfil.es'.format(filepath))
                self.upload_file(filepath)
            else:
                print('File "{0}" not found!'.format(filepath))

        if options.download and len(args) < 2:
            print('No link to download given!')
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
                print('Invalid destination path given!')

    def upload_file(self, filepath):
        files = {"filedata": open(filepath, "rb")}
        try:
            r = requests.post(self.up_url, files=files)
            print(json.loads(r.text))
        except requests.exceptions.ConnectionError:
            print('Server closed the connection, maybe the file is too large or the network speed too slow')

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
                    option = input('File "{0}" exists, overwrite? (y/n): '.format(destination_file))
                if option == 'y':
                    with open(destination_file, 'wb') as handle:
                        for block in response.iter_content(1024):
                            handle.write(block)
                    print('Download of "{0}" complete!'.format(destination_file))
            else:
                print('File not found!')
        except requests.exceptions.MissingSchema:
            print('Bad url provided!')
        except requests.exceptions.ConnectionError:
            print('Failed to establish a connection with the server!')
        except:
            print('Unexpected error:', sys.exc_info()[0])
            raise
