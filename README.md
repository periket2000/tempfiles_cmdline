# Tempfil.es command line tool [![CI](https://github.com/periket2000/tempfiles_cmdline/actions/workflows/ci.yml/badge.svg)](https://github.com/periket2000/tempfiles_cmdline/actions/workflows/ci.yml)

This tool is intended to provide command line access to the ephemeral/anonymous file sharing service [Tempfil.es].

## Installation

```bash
pip install tempfiles_cmdline
```

Or install from source:

```bash
pip install -e .
```

## Usage

```
tempfiles -u file_path       upload mode
tempfiles -d URL [DEST]      download mode
tempfiles -v                 show version
```

### Examples

Upload a file:
```bash
$ tempfiles -u ~/myfile.zip
Uploading myfile.zip to https://tempfil.es
[{'download_link': 'https://tempfil.es/filedownload/link.cZIByw'}]
```

Download a file:
```bash
$ tempfiles -d https://tempfil.es/filedownload/link.cZIByw
Download of "myfile.zip" complete!
```

[Tempfil.es]: https://tempfil.es
