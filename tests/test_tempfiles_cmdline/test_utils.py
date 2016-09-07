import mock
import pytest
import tempfiles_cmdline.utils as utils
import os

executor = utils.Executor()


def mocked_post(*args, **kwargs):
    """ helper function for mocking post request """
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.text = json_data
            self.status_code = status_code

        def text(self):
            return self.text

    if args[0] == 'https://tempfil.es/fileupload/':
        return MockResponse('[{"download_link": "https://tempfil.es/filedownload/link.zolZ15"}]', 200)
    else:
        return MockResponse('{"key2": "value2"}', 200)

    return MockResponse('{}', 404)


class TestUtils:

    @mock.patch('requests.post', side_effect=mocked_post)
    def test_download(self, mock_post):
        r = executor.upload_file(os.path.abspath(os.path.dirname(__file__))+'/__init__.py')
        assert r.status_code == 200
        assert 'download_link' in r.text

    def test_download_err(self):
        with pytest.raises(IOError):
            executor.upload_file('bababa')

