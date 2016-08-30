import codecs
import os
import re

from setuptools import setup, find_packages


###################################################################

NAME = "tempfiles_cmdline"
PACKAGES = find_packages(where="src")
META_PATH = os.path.join("src", "tempfiles_cmdline", "__init__.py")
KEYWORDS = ["ephemeral file sharing", "anonymous file sharing", "devops", "sysadmin"]
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: Implementation :: PyPy"
]
INSTALL_REQUIRES = [
    'requests>=2.11.1',
    'requests-toolbelt>=0.7.0',
    'click>=6.6'
]
TEST_REQUIRE = [
    'pytest>=3.0.1',
    'mock>=2.0.0'

]
###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("uri"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        keywords=KEYWORDS,
        long_description=read("README.rst"),
        packages=PACKAGES,
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        tests_require=TEST_REQUIRE,
        scripts=['bin/tempfiles'],
    )
