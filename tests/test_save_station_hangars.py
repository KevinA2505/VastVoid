import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from station import SpaceStation
from ship import Ship, SHIP_MODELS
from savegame import save_station_hangars, load_station_hangars


def test_station_hangar_persistence(tmp_path):
    savegame_SAVE_DIR = tmp_path
    import savegame
    savegame.SAVE_DIR = str(savegame_SAVE_DIR)

    st = SpaceStation(0, 0, num_hangars=1)
    st.name = "TestStation"
    ship = Ship(0, 0, SHIP_MODELS[0])
    st.dock_ship(ship)

    save_station_hangars([st])

    new_station = SpaceStation(0, 0, num_hangars=1)
    new_station.name = "TestStation"
    load_station_hangars([new_station])
    assert new_station.hangars[0].occupied_by is not None
    assert new_station.hangars[0].occupied_by.model.name == SHIP_MODELS[0].name
