"""
進度回報模組
腳本呼叫 update() 即可讓手機監控頁面即時看到進度
"""
import json
import time
from pathlib import Path

_FILE = Path(__file__).parent / "progress.json"

_state = {
    "script": "",
    "task": "",
    "current": 0,
    "total": 0,
    "percent": 0,
    "message": "",
    "log": [],
    "started": "",
    "updated": "",
    "done": False,
    "error": "",
}


def start(script_name: str, total: int, task: str = ""):
    _state.update({
        "script": script_name,
        "task": task,
        "current": 0,
        "total": total,
        "percent": 0,
        "message": "",
        "log": [],
        "started": time.strftime("%H:%M:%S"),
        "updated": time.strftime("%H:%M:%S"),
        "done": False,
        "error": "",
    })
    _write()


def update(current: int, message: str = "", task: str = ""):
    total = _state["total"]
    percent = round(current / total * 100) if total > 0 else 0
    now = time.strftime("%H:%M:%S")

    if task:
        _state["task"] = task
    _state["current"] = current
    _state["percent"] = percent
    _state["message"] = message
    _state["updated"] = now

    if message:
        log = _state["log"]
        log.append(f"[{now}] {message}")
        if len(log) > 50:
            log.pop(0)

    _write()


def done(message: str = "完成！"):
    _state["current"] = _state["total"]
    _state["percent"] = 100
    _state["done"] = True
    _state["message"] = message
    _state["updated"] = time.strftime("%H:%M:%S")
    log = _state["log"]
    log.append(f"[{_state['updated']}] {message}")
    _write()


def error(message: str):
    _state["error"] = message
    _state["updated"] = time.strftime("%H:%M:%S")
    log = _state["log"]
    log.append(f"[{_state['updated']}] ❌ {message}")
    _write()


def _write():
    _FILE.write_text(json.dumps(_state, ensure_ascii=False), encoding="utf-8")
