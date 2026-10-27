import os
import shutil
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def make_executable(path, body):
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def test_local_wrapper_runs_src_translate_py(tmp_path):
    (tmp_path / "build").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(ROOT / "build" / "translate.sh", tmp_path / "build" / "translate.sh")
    (tmp_path / "src" / "translate.py").write_text("")
    venv_bin = tmp_path / "venv" / "bin"
    venv_bin.mkdir(parents=True)
    make_executable(venv_bin / "python3", '#!/bin/sh\necho "ARGS:$*"\n')

    result = subprocess.run(
        ["bash", str(tmp_path / "build" / "translate.sh"), "hola", "-l", "en"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    # Diagnostics go to stderr so stdout carries only the translation.
    assert result.stdout.strip().startswith("ARGS:")
    assert result.stdout.strip().endswith("src/translate.py hola -l en")


def test_wrapper_propagates_exit_status(tmp_path):
    (tmp_path / "build").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(ROOT / "build" / "translate.sh", tmp_path / "build" / "translate.sh")
    (tmp_path / "src" / "translate.py").write_text("")
    venv_bin = tmp_path / "venv" / "bin"
    venv_bin.mkdir(parents=True)
    make_executable(venv_bin / "python3", "#!/bin/sh\nexit 3\n")

    result = subprocess.run(["bash", str(tmp_path / "build" / "translate.sh")], capture_output=True)

    assert result.returncode == 3


def test_system_uninstall_removes_system_venv_not_local(tmp_path):
    (tmp_path / "build").mkdir()
    shutil.copy(ROOT / "build" / "uninstall.sh", tmp_path / "build" / "uninstall.sh")
    local_venv = tmp_path / "venv"
    local_venv.mkdir()
    sys_venv = tmp_path / "sys-venv"
    sys_venv.mkdir()
    src_dir = tmp_path / "share" / "src"
    src_dir.mkdir(parents=True)
    bin_file = tmp_path / "bin" / "translate"
    bin_file.parent.mkdir()
    bin_file.write_text("")
    stub_bin = tmp_path / "stub"
    stub_bin.mkdir()
    make_executable(stub_bin / "sudo", '#!/bin/sh\nexec "$@"\n')

    env = dict(
        os.environ,
        PATH=f"{stub_bin}:{os.environ['PATH']}",
        TRANSLATOR_SYS_VENV_DIR=str(sys_venv),
        TRANSLATOR_SRC_DIR=str(src_dir),
        TRANSLATOR_BIN_FILE=str(bin_file),
    )
    result = subprocess.run(
        ["bash", str(tmp_path / "build" / "uninstall.sh")],
        input="yes\n",
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert not sys_venv.exists()
    assert not src_dir.exists()
    assert not bin_file.exists()
    assert local_venv.exists()
