import os
import codecs
import re


class ConfigurationService:
    def __init__(self, filepath=None):
        if filepath:
            self.meta_info = filepath
        else:
            self.meta_info = os.path.join(os.path.abspath(os.path.dirname(__file__)), "__init__.py")
        self.meta_file = self.read()

    def get(self, key):
        return self.find_meta(key)

    def log(self, key, substitutions=None):
        if substitutions:
            print(self.get(key).format(*substitutions))
        else:
            print(self.get(key))

    def read(self):
        """
        Build an absolute path from *parts* and and return the contents of the
        resulting file.  Assume UTF-8 encoding.
        """
        with codecs.open(self.meta_info, "rb", "utf-8") as f:
            return f.read()

    def find_meta(self, key):
        """
        Extract __*meta*__ from META_FILE.
        """
        meta_match = re.search(
            r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=key),
            self.meta_file, re.M
        )
        if meta_match:
            return meta_match.group(1)
        raise RuntimeError("Unable to find __{meta}__ string.".format(meta=key))