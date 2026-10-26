import json

import pytest

import translate


class FakeTranslator:
    def __init__(self, max_chars=5000):
        self.max_chars = max_chars
        self.calls = []

    def translate(self, text):
        assert len(text) < self.max_chars, "chunk exceeds provider limit"
        self.calls.append(text)
        return text.upper()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    path = tmp_path / "xdg" / "translator" / "config.json"
    monkeypatch.setattr(translate, "CONFIG_FILE", str(path))
    monkeypatch.setattr(translate, "DEFAULT_CONFIG_FILE", str(tmp_path / "missing.json"))
    return path


def test_provider_config_is_not_written_to_cwd(tmp_path, monkeypatch, isolated_config):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)

    assert translate.main(["--provider", "MyMemory"]) == 0

    assert not (cwd / "config.json").exists()
    assert json.loads(isolated_config.read_text()) == {"provider": "MyMemory"}
    assert translate.load_config() == {"provider": "MyMemory"}


def test_invalid_provider_is_rejected_and_not_saved(isolated_config, capsys):
    assert translate.main(["--provider", "Bogus"]) == 1

    assert not isolated_config.exists()
    assert "not supported" in capsys.readouterr().err


def test_language_name_is_accepted():
    # deep-translator accepts names as well as codes; the old check rejected names.
    translator = translate.get_translator("Google", target_language="spanish")
    assert translator._target == "es"


def test_unsupported_language_gives_short_error():
    with pytest.raises(translate.TranslatorError, match="'xx' is not supported"):
        translate.get_translator("Google", target_language="xx")


def test_translation_failure_exits_nonzero(monkeypatch, capsys):
    class Failing:
        def translate(self, text):
            raise RuntimeError("network down")

    monkeypatch.setattr(translate, "get_translator", lambda *a, **k: Failing())

    assert translate.main(["hello", "-l", "es"]) == 1
    captured = capsys.readouterr()
    assert "network down" in captured.err
    assert "Translation:" not in captured.out


def test_failed_file_translation_writes_no_output(tmp_path, monkeypatch):
    class Failing:
        def translate(self, text):
            raise RuntimeError("network down")

    monkeypatch.setattr(translate, "get_translator", lambda *a, **k: Failing())
    src = tmp_path / "in.txt"
    src.write_text("hello")

    assert translate.main([str(src), "-l", "es"]) == 1
    assert not (tmp_path / "translated-in.txt").exists()


def test_detect_language_reports_unsupported(capsys):
    assert translate.main(["hola", "-d"]) == 1
    assert "not supported" in capsys.readouterr().err


def test_file_translation_is_utf8_regardless_of_locale(tmp_path, monkeypatch):
    import locale

    monkeypatch.setattr(locale, "getpreferredencoding", lambda *a, **k: "ascii")
    src = tmp_path / "in.txt"
    src.write_bytes("héllo wörld".encode("utf-8"))

    out = translate.translate_file(str(src), FakeTranslator())

    assert open(out, encoding="utf-8").read() == "HÉLLO WÖRLD"


def test_large_file_is_chunked_under_provider_limit(tmp_path):
    lines = [f"line {i} " + "x" * 80 for i in range(200)]  # ~17k chars
    src = tmp_path / "big.txt"
    src.write_text("\n".join(lines), encoding="utf-8")
    fake = FakeTranslator(max_chars=5000)

    out = translate.translate_file(str(src), fake, max_chars=5000)

    assert len(fake.calls) > 1
    assert open(out, encoding="utf-8").read() == "\n".join(lines).upper()


@pytest.mark.parametrize("text", ["", "a", "\n\nabc\n", "a\n\n\nb", "x" * 23, "ab\n" * 10])
def test_split_text_round_trips(text):
    chunks = translate.split_text(text, 6)
    assert all(len(c) < 6 for c in chunks)
    if all(len(line) < 6 for line in text.split("\n")):
        assert "\n".join(chunks) == text
