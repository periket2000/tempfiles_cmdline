import os
from unittest.mock import patch

import pytest

import tempfiles_cmdline.utils as utils

executor = utils.Executor()


def mocked_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.text = json_data
            self.status_code = status_code

    if args[0] == 'https://tempfil.es/fileupload/':
        return MockResponse('[{"download_link": "https://tempfil.es/filedownload/link.zolZ15"}]', 200)
    return MockResponse('{}', 404)


class TestUtils:

    @patch('requests.post', side_effect=mocked_post)
    def test_upload(self, mock_post):
        test_file = os.path.join(os.path.dirname(__file__), '__init__.py')
        r = executor.upload_file(test_file)
        assert r.status_code == 200
        assert 'download_link' in r.text

    def test_upload_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            executor.upload_file('nonexistent_file')
