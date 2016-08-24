# [Tempfil.es] command line tool

This tool is intended to provide command line access to the ephemeral/anonymous file sharing service [Tempfil.es].

### Building the package locally
```python
python setup.py build
```

### Installing the package locally
```python
python setup.py install
```

### Uploading your package

1. Register in https://pypi.python.org

2. Create the file ~/.pypirc with the following content
```python
[distutils]
index-servers=
    pypi
    test

[test]
repository = https://testpypi.python.org/pypi
username = <your test user name goes here>
password = <your test password goes here>

[pypi]
repository = https://pypi.python.org/pypi
username = <your production user name goes here>
password = <your production password goes here>
```

3. Go to you package directory and type

- python setup.py register
- python setup.py sdist upload

> Be careful, once you upload a version of your package, you can't upload the same
> version again, should update your version number and upload the new package.

> Note that if you specify a concrete version of python in your setup.py CLASSIFIERS,
> some versions of pip couldn't find your package.

[Tempfil.es]: <https://tempfil.es>
