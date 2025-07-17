from typing import Dict, Iterable

import items

class Inventory:
    """Manage quantities of items and compute derived stats."""

    def __init__(self, mapping: Dict[str, int] | None = None) -> None:
        self._items: Dict[str, int] = {name: 0 for name in items.ITEMS_BY_NAME}
        if mapping:
            for name, qty in mapping.items():
                if name in self._items:
                    self._items[name] = int(qty)

    # Basic operations -------------------------------------------------
    def add(self, item: str, quantity: int = 1) -> None:
        self._items[item] = self._items.get(item, 0) + quantity

    def remove(self, item: str, quantity: int = 1) -> None:
        if item not in self._items:
            return
        self._items[item] = max(0, self._items[item] - quantity)

    def has(self, item: str, quantity: int = 1) -> bool:
        return self._items.get(item, 0) >= quantity

    def count(self, item: str) -> int:
        return self._items.get(item, 0)

    def clear(self) -> None:
        for name in self._items:
            self._items[name] = 0

    def update(self, other: Dict[str, int]) -> None:
        for name, qty in other.items():
            if name in self._items:
                self._items[name] = int(qty)

    # Dictionary-style helpers ---------------------------------------
    def get(self, item: str, default: int = 0) -> int:
        return self._items.get(item, default)

    def items(self) -> Iterable[tuple[str, int]]:
        return self._items.items()

    def values(self) -> Iterable[int]:
        return self._items.values()

    def to_dict(self) -> Dict[str, int]:
        return dict(self._items)

    def total_weight(self) -> float:
        weight = 0.0
        for name, qty in self._items.items():
            if qty:
                item = items.ITEMS_BY_NAME.get(name)
                if item:
                    weight += item.peso * qty
        return weight

    def __contains__(self, item: str) -> bool:
        return item in self._items

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, item: str) -> int:
        return self._items.get(item, 0)
