import optparse

usage = """

\twhere options are:
\t\t -u => upload mode
\t\t\t -f filename => the file to upload
\t\t -d => download mode
"""

class Executor:
    def __init__(self):
        self.parser = optparse.OptionParser(usage='usage: %prog [options]'+usage)
        self.parser.add_option('-u', '--upload', action='store_true', default=False, help='upload mode')
        self.parser.add_option('-d', '--download', action='store_true', default=False, help='download mode')
        self.parser.add_option('-f', '--file',  dest='filename', help='upload filename')

    def run(self, args):
        (options, arguments) = self.parser.parse_args(args)
        if not options.upload or options.download:
            print('No mode selected!')
            self.parser.print_usage()
            return 0;

        if not options.filename:   # if filename is not given
            self.parser.error('Filename not given')

        print(args)
        print(options)
        print(arguments)
