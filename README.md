# [Tempfil.es] command line tool [![Build Status](https://travis-ci.org/periket2000/tempfiles_cmdline.svg?branch=master)](https://travis-ci.org/periket2000/tempfiles_cmdline)

This tool is intended to provide command line access to the ephemeral/anonymous file sharing service [Tempfil.es].

### Installing the package locally
```python
python setup.py install
```

### Installing the package with Pypi
```python
pip install tempfiles_cmdline
```

### Executable inteface

After install the command line tool, you'll get a "tempfiles" comman line tool ready to run.

> usage

```bash
$ tempfiles
No mode selected!
Usage: tempfiles [options]

	where options are:
		 -u file_path => upload mode
		 -d download_link [destination_path] => download mode
```

> uploading a file

```bash
$ tempfiles -u ~/myfile.zip
Uploading "~/myfile.zip" to https://tempfil.es
[{'download_link': 'https://tempfil.es/filedownload/link.cZIByw'}]
```

> download a file

```bash
$ tempfiles -d https://tempfil.es/filedownload/link.cZIByw
Download of "myfile.zip" complete!
```

[Tempfil.es]: <https://tempfil.es>
