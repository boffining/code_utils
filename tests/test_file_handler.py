from codehealer.utils.file_handler import FileHandler


def test_write_and_read_file(tmp_path):
    handler = FileHandler()
    target = tmp_path / "sample.txt"
    handler.write_file(target, "hello")
    assert handler.read_file(target) == "hello"


def test_read_file_handles_missing(tmp_path, capsys):
    handler = FileHandler()
    missing = tmp_path / "missing.txt"
    assert handler.read_file(missing) is None
    captured = capsys.readouterr()
    assert "Error reading file" in captured.out
