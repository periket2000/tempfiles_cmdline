from tempfiles_conf import Config, log


class TestConfig:

    def test_config_values(self):
        cfg = Config()
        assert cfg.UPLOAD_URL == 'https://tempfil.es/fileupload/'
        assert cfg.FINISH_URL == 'https://tempfil.es/finish/'
        assert cfg.VERSION == '1.1.3'

    def test_log_no_args(self, capsys):
        log('hello world')
        captured = capsys.readouterr()
        assert captured.out.strip() == 'hello world'

    def test_log_with_args(self, capsys):
        log('hello {}', 'world')
        captured = capsys.readouterr()
        assert captured.out.strip() == 'hello world'
