import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import config
from station import SpaceStation
from items import ITEMS_BY_NAME


def test_price_updates_clamped_and_infrequent():
    station = SpaceStation(0, 0)
    station.market = {"hierro": {"stock": 5, "price": ITEMS_BY_NAME["hierro"].valor}}

    base = ITEMS_BY_NAME["hierro"].valor
    min_price = int(base * config.STATION_MIN_PRICE_MULT)
    max_price = int(base * config.STATION_MAX_PRICE_MULT)

    # Price should not change before 1 second has elapsed
    station.update(0.5)
    price = station.market["hierro"]["price"]
    station.update(0.4)
    assert station.market["hierro"]["price"] == price

    # After the threshold it should update and stay within bounds
    station.update(0.2)  # total dt now > 1.0
    assert min_price <= station.market["hierro"]["price"] <= max_price

    # Simulate multiple seconds of updates
    for _ in range(20):
        station.update(1.0)
        assert min_price <= station.market["hierro"]["price"] <= max_price

