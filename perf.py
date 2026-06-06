import time
from typing import Dict, List

ENABLED = True
LOG_INTERVAL = 60

_counters: Dict[str, int] = {}
_timers: Dict[str, float] = {}
_frame_data: Dict[str, float] = {}
_frame_count = 0

def reset():
    global _frame_count
    _counters.clear()
    _timers.clear()
    _frame_data.clear()
    _frame_count = 0

def count(label: str, amount: int = 1):
    if not ENABLED:
        return
    _counters[label] = _counters.get(label, 0) + amount

def start(label: str):
    if not ENABLED:
        return
    _timers[label] = time.perf_counter()

def stop(label: str):
    if not ENABLED:
        return
    t = time.perf_counter()
    key = f"time_{label}"
    _frame_data[key] = _frame_data.get(key, 0) + (t - _timers.get(label, t))

def record(label: str, value: float):
    if not ENABLED:
        return
    _frame_data[label] = _frame_data.get(label, 0) + value

def frame_done():
    global _frame_count
    if not ENABLED:
        return
    _frame_count += 1
    if _frame_count % LOG_INTERVAL != 0:
        return

    lines = []
    lines.append(f"=== PERF frame {_frame_count} ===")
    lines.append(f"  objects: {_frame_data.get('obj_count', 0):.0f}")
    lines.append(f"  update_ms: {_frame_data.get('time_update', 0)*1000:.1f}")
    lines.append(f"  render_ms: {_frame_data.get('time_render', 0)*1000:.1f}")
    lines.append(f"  collision_checks: {_counters.get('collision_checks', 0)}")
    lines.append(f"  get_colliders_calls: {_counters.get('get_colliders_calls', 0)}")
    lines.append(f"  collision_ms: {_frame_data.get('time_collision', 0)*1000:.1f}")
    n_bodies = _counters.get('bodies_updated', 0)
    lines.append(f"  bodies_updated: {n_bodies}")

    total = _frame_data.get('time_update', 0) + _frame_data.get('time_render', 0)
    lines.append(f"  total_frame_ms: {total*1000:.1f}")
    print("\n".join(lines))

    _counters.clear()
    _frame_data.clear()
