"""Batch runner for factor generation -> signal processing -> evaluation.

Config-only usage:
- Edit PIPELINE_CONFIG in this file.
- Run: python Utility/run_factor_pipeline.py
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
FACTOR_DIR = ROOT_DIR / "Factor"
UTILITY_DIR = ROOT_DIR / "Utility"
SIGNAL_PROCESS_SCRIPT = UTILITY_DIR / "signalProcess.py"
FACTOR_EVAL_SCRIPT = UTILITY_DIR / "factorEvaluation.py"
SYMBOL = "SOLUSDT"

PIPELINE_CONFIG = {
    "factors": [],
    "stop_on_error": False,
}

DEFAULT_BACKTEST_START_DATE = "00000000"


def _load_module(module_path: Path):
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _apply_factor_overrides(module) -> None:
    module.SYMBOL = SYMBOL

    if hasattr(module, "BACKTEST_START_DATE"):
        module.BACKTEST_START_DATE = DEFAULT_BACKTEST_START_DATE

def _run_one_factor(script_path: Path) -> None:
    module = _load_module(script_path)
    _apply_factor_overrides(module)

    if not hasattr(module, "main"):
        raise AttributeError(f"{script_path.name} has no main()")
    module.main()


def _run_python_script(
    script_path: Path,
    script_args: list[str] | None = None,
) -> None:
    cmd = [sys.executable, str(script_path)]
    if script_args:
        cmd.extend(script_args)
    subprocess.run(cmd, cwd=str(ROOT_DIR), check=True)


def main() -> None:
    factors = PIPELINE_CONFIG["factors"]
    stop_on_error = PIPELINE_CONFIG["stop_on_error"]

    if not FACTOR_DIR.exists():
        raise FileNotFoundError(f"Factor directory not found: {FACTOR_DIR}")
    if not SIGNAL_PROCESS_SCRIPT.exists():
        raise FileNotFoundError(f"signalProcess script not found: {SIGNAL_PROCESS_SCRIPT}")
    if not FACTOR_EVAL_SCRIPT.exists():
        raise FileNotFoundError(f"factorEvaluation script not found: {FACTOR_EVAL_SCRIPT}")

    factor_scripts = sorted(path for path in FACTOR_DIR.glob("*.py") if path.is_file())
    requested = {name.strip() for name in factors if name.strip()}

    selected_scripts: list[Path] = []
    if not requested:
        selected_scripts = factor_scripts
    else:
        for script_path in factor_scripts:
            module = _load_module(script_path)
            if script_path.stem in requested or getattr(module, "FACTOR_NAME", "") in requested:
                selected_scripts.append(script_path)

    if not selected_scripts:
        requested_text = ", ".join(factors) if factors else "<none>"
        raise ValueError(f"No factor scripts matched requested names: {requested_text}")

    print(f"Selected factors: {len(selected_scripts)}")
    failed: list[str] = []

    for idx, script_path in enumerate(selected_scripts, start=1):
        print(f"[Factor {idx}/{len(selected_scripts)}] Running {script_path.stem} ...")
        try:
            _run_one_factor(script_path)
        except Exception as exc:
            msg = f"{script_path.name}: {exc}"
            failed.append(msg)
            print(f"Failed: {msg}")
            if stop_on_error:
                raise

    if failed:
        print("Some factor scripts failed:")
        for item in failed:
            print(f"  - {item}")

    print("Running signalProcess ...")
    _run_python_script(SIGNAL_PROCESS_SCRIPT)

    print("Running factorEvaluation ...")
    _run_python_script(FACTOR_EVAL_SCRIPT)

    print("Pipeline finished")


if __name__ == "__main__":
    main()
