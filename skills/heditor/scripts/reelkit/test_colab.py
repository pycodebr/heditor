"""colabkit without network: parsing, machine order, and the 'unavailable' contract (exit 75, nothing runs)."""
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import colabkit as ck  # noqa: E402

KIT = Path(__file__).parent


def test_parse_usage():
    text = "Current balance: 444.16 compute units\nUsage rate: 1.94/hr\nActive assignments: 1\n"
    assert ck.parse_usage(text) == {"balance": 444.16, "rate": 1.94, "active": 1}
    assert ck.parse_usage("Current balance: 1,204.50 compute units")["balance"] == 1204.5
    assert ck.parse_usage("error")["balance"] is None


def test_parse_sessions():
    text = ("[heditor-render-1120-010203-0042] m-s-use4b1-x | Hardware: GPU L4 | Shape: Standard\n"
            "[kratos-test] m-s-euw4 | Hardware: CPU | Shape: Standard | Variant: DEFAULT\n")
    assert ck.parse_sessions(text) == ["heditor-render-1120-010203-0042", "kratos-test"]
    assert ck.parse_sessions("[colab] No active sessions found on server.") == []


def test_parse_shapes():
    assert ck.parse_shapes("L4, cpu-hm,cpu ,t4-hm") == [
        ("L4", ["--gpu", "L4"]), ("cpu-hm", ["--high-mem"]), ("cpu", []), ("t4-hm", ["--gpu", "T4", "--high-mem"])]
    assert ck.parse_shapes("") == []


def test_enabled(monkeypatch):
    monkeypatch.delenv("HEDITOR_COMPUTE", raising=False)
    assert not ck.enabled()
    monkeypatch.setenv("HEDITOR_COMPUTE", "Colab")
    assert ck.enabled()


def _fake_cli(tmp_path, balance):
    cli = tmp_path / "colab"
    cli.write_text("#!/usr/bin/env bash\n"
                   "for a in \"$@\"; do case \"$a\" in\n"
                   f"  usage) echo 'Current balance: {balance} compute units'; echo 'Usage rate: 0.00/hr'; exit 0 ;;\n"
                   "  sessions) echo '[colab] No active sessions found on server.'; exit 0 ;;\n"
                   "  new) echo 'Service Unavailable' >&2; exit 1 ;;\n"
                   "esac; done\nexit 0\n")
    cli.chmod(cli.stat().st_mode | stat.S_IEXEC)
    key = tmp_path / "id_ed25519.pub"
    key.write_text("ssh-ed25519 AAAA test\n")
    return cli, key


def test_missing_cli_is_unavailable(monkeypatch, tmp_path):
    monkeypatch.setenv("HEDITOR_COLAB", str(tmp_path / "nope"))
    with pytest.raises(ck.Unavailable, match="CLI not found"):
        ck.usage()


@pytest.mark.skipif(not (os.path.exists("/usr/bin/ssh") and os.path.exists("/usr/bin/rsync")), reason="needs ssh and rsync")
def test_low_balance_and_no_machine(monkeypatch, tmp_path):
    cli, key = _fake_cli(tmp_path, "2.00")
    monkeypatch.setenv("HEDITOR_COLAB", str(cli))
    monkeypatch.setenv("HEDITOR_COLAB_KEY", str(key))
    monkeypatch.setenv("HEDITOR_HOME", str(tmp_path / "home"))
    with pytest.raises(ck.Unavailable, match="below the minimum"):
        ck.check()
    cli, key = _fake_cli(tmp_path, "100.00")
    with pytest.raises(ck.Unavailable, match="no Colab machine available"):
        with ck.Runtime("render", ck.parse_shapes("L4,cpu-hm"), quiet=True):
            pass


@pytest.mark.skipif(not (os.path.exists("/usr/bin/ssh") and os.path.exists("/usr/bin/rsync")), reason="needs ssh and rsync")
def test_cli_exit_75_runs_nothing(tmp_path):
    cli, key = _fake_cli(tmp_path, "2.00")
    env = dict(os.environ, HEDITOR_COLAB=str(cli), HEDITOR_COLAB_KEY=str(key), HEDITOR_HOME=str(tmp_path / "home"))
    out = tmp_path / "out.json"
    res = subprocess.run([sys.executable, str(KIT / "colabkit.py"), "transcribe", str(tmp_path / "x.wav"), str(out), "--dur", "1"],
                         env=env, capture_output=True, text=True)
    assert res.returncode == ck.UNAVAILABLE
    assert "re-run with --local" in res.stderr
    assert not out.exists()


def test_render_script_has_the_render_contract():
    assert "RESULT $out rc=$rc" in ck.RENDER_SH
    assert ck.CHROME_LIBS in ck.RENDER_SH
    assert "Acquire::ForceIPv4=true" in ck.RENDER_SH
    assert f"{ck.REMOTE}/jobs.tsv" in ck.RENDER_SH


def test_hyperframes_command_for_the_runtime(monkeypatch):
    monkeypatch.setenv("HEDITOR_HYPERFRAMES", "npx --yes hyperframes@9.9.9")
    assert ck._hf() == "npx --yes hyperframes@9.9.9"
    monkeypatch.setenv("HEDITOR_HYPERFRAMES", "/opt/hf/bin/hyperframes")
    assert ck._hf() == ck.HF_DEFAULT


def test_last_line_prefers_the_error():
    res = subprocess.CompletedProcess([], 1, stdout="[colab] Creating session 'x'...\n",
                                      stderr="ColabRequestError: Failed to issue request POST\nhttps://x/assign?shape=hm: Service Unavailable\n")
    assert ck._last(res).endswith("Service Unavailable")
    assert ck._last(subprocess.CompletedProcess([], 2, stdout="", stderr="")) == "exit 2"
