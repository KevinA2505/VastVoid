import csv
from pathlib import Path
from typing import Iterable, Tuple


def save_reward_history(history: Iterable[Tuple[float, float]], path: str = "ally_reward_history.csv") -> None:
    """Save accumulated reward over time to a CSV file.

    Parameters
    ----------
    history:
        Iterable of ``(time, reward)`` pairs.
    path:
        Destination CSV path. Created if it does not exist.
    """
    data = list(history)
    if not data:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "reward"])
        writer.writerows(data)

