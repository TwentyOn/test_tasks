from models import ClickbaitReportRecord


class TestClickbaitReport:
    """
    Тесты генерации и вывода отчета clickbait
    """
    def test_generate(self, fake_clickbait_report, fake_valid_files):
        generate_data = fake_clickbait_report.generate(fake_valid_files)

        assert isinstance(generate_data, list)
        assert isinstance(generate_data[0], ClickbaitReportRecord)
        assert generate_data[0].ctr > generate_data[-1].ctr
        assert min([d.ctr for d in generate_data]) > 15.0
        assert max([d.retention_rate for d in generate_data]) < 40

    def test_render(self, capsys, fake_clickbait_report, fake_valid_files, fake_valid_data):
        generate_data = fake_clickbait_report.generate(fake_valid_files)
        fake_clickbait_report.render(generate_data)

        stream = capsys.readouterr()
        test_title = generate_data[0].title

        assert test_title in stream.out
