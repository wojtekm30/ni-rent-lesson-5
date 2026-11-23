import pytest
from src.manager import Manager
from src.models import Bill, Parameters


def test_get_apartment_costs():
    manager = Manager(Parameters())

    assert manager.get_apartment_costs("apart-polanka", 2025, 1) == 910.0
    assert manager.get_apartment_costs("apart-polanka", 2025, 2) == 0.0
    assert manager.get_apartment_costs("apart-polanka", 2024, 1) == 0.0
    assert manager.get_apartment_costs("nie-istnieje", 2025, 1) is None

    # Walidacja nieprawidłowego miesiąca (np. 13, 0, -1)
    with pytest.raises(ValueError):
        manager.get_apartment_costs("apart-polanka", 2025, 13)

    with pytest.raises(ValueError):
        manager.get_apartment_costs("apart-polanka", 2025, 0)

    with pytest.raises(ValueError):
        manager.get_apartment_costs("apart-polanka", 2025, -1)


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0

    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0


def test_create_apartment_settlement_tdd():
    from src.models import ApartmentSettlement

    manager = Manager(Parameters())

    # 1. Mieszkanie z rachunkami w 01/2025 (przelewy = 0.0, rachunki = 910.0 -> bilans = -910.0)
    settlement_jan = manager.create_apartment_settlement("apart-polanka", 2025, 1)
    assert isinstance(settlement_jan, ApartmentSettlement)
    assert settlement_jan.apartment == "apart-polanka"
    assert settlement_jan.year == 2025
    assert settlement_jan.month == 1
    assert settlement_jan.total_rent_pln == 0.0
    assert settlement_jan.total_bills_pln == 910.0
    assert settlement_jan.total_due_pln == -910.0

    # 2. Mieszkanie bez rachunków w 02/2025 (bilans = 0.0)
    settlement_feb = manager.create_apartment_settlement("apart-polanka", 2025, 2)
    assert isinstance(settlement_feb, ApartmentSettlement)
    assert settlement_feb.apartment == "apart-polanka"
    assert settlement_feb.year == 2025
    assert settlement_feb.month == 2
    assert settlement_feb.total_rent_pln == 0.0
    assert settlement_feb.total_bills_pln == 0.0
    assert settlement_feb.total_due_pln == 0.0

    # 3. Nieistniejące mieszkanie oraz błędny miesiąc
    assert manager.create_apartment_settlement("nie-istnieje", 2025, 1) is None

    with pytest.raises(ValueError):
        manager.create_apartment_settlement("apart-polanka", 2025, 13)
