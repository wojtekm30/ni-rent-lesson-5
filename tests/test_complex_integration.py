import pytest
from src.manager import Manager
from src.models import Parameters


def test_get_apartment_costs():
    manager = Manager(Parameters())

    assert manager.get_apartment_costs("apart-polanka", 2025, 1) == 910.0
    assert manager.get_apartment_costs("apart-polanka", 2025, 2) == 0.0
    assert manager.get_apartment_costs("apart-polanka", 2024, 1) == 0.0

    with pytest.raises(ValueError):
        manager.get_apartment_costs("nie-istnieje", 2025, 1)
