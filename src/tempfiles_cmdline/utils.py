import optparse
import os.path
import requests
import json

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

    def run(self, args):
        (options, arguments) = self.parser.parse_args(args)
        if not options.upload or options.download:
            print('No mode selected!')
            self.parser.print_usage()
            return 0;

        if options.upload and len(args) < 2:
            print('No file to upload given!')
            self.parser.print_usage()
            return 0;
        else:
            filepath = args[1]
            if os.path.isfile(filepath):
                print('Uploading "{0}" to https://tempfil.es'.format(filepath))
                self.upload_file(filepath)
            else:
                print('File "{0}" not found!'.format(filepath))
            return 0;

    def upload_file(self, filepath):
        url = "https://tempfil.es/fileupload/"
        files = {"filedata": open(filepath, "rb")}
        try:
            r = requests.post(url, files=files)
            print(json.loads(r.text))
        except requests.exceptions.ConnectionError as e:
            print('Server closed the connection, maybe the file is too large or the network speed too slow')
