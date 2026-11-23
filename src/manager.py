import calendar
from datetime import date
from src.models import (
    Apartment,
    ApartmentSettlement,
    Bill,
    Parameters,
    Tenant,
    TenantSettlement,
    Transfer,
)


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []

        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(
        self,
        apartment_key: str,
        year: int | None = None,
        month: int | None = None,
    ) -> float | None:
        if apartment_key not in self.apartments:
            return None

        if month is not None and (month < 1 or month > 12):
            raise ValueError(f"Invalid month: {month}. Month must be between 1 and 12.")

        total = 0.0
        for bill in self.bills:
            if bill.apartment != apartment_key:
                continue
            if year is not None and bill.settlement_year != year:
                continue
            if month is not None and bill.settlement_month != month:
                continue
            total += bill.amount_pln

        return total

    def create_apartment_settlement(
        self, apartment_key: str, year: int, month: int
    ) -> ApartmentSettlement | None:
        if month is None or month < 1 or month > 12:
            raise ValueError(f"Invalid month: {month}. Month must be between 1 and 12.")

        total_bills = self.get_apartment_costs(apartment_key, year=year, month=month)
        if total_bills is None:
            return None

        total_rent = 0.0
        total_due = total_rent - total_bills

        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=total_rent,
            total_bills_pln=total_bills,
            total_due_pln=total_due,
        )

    def create_tenant_settlements(
        self, apartment_settlement: ApartmentSettlement
    ) -> list[TenantSettlement]:
        year = apartment_settlement.year
        month = apartment_settlement.month
        month_start = date(year, month, 1)
        month_end = date(year, month, calendar.monthrange(year, month)[1])

        active_tenants = [
            tenant
            for tenant in self.tenants.values()
            if tenant.apartment == apartment_settlement.apartment
            and date.fromisoformat(tenant.date_agreement_from) <= month_end
            and date.fromisoformat(tenant.date_agreement_to) >= month_start
        ]

        if not active_tenants:
            return []

        bills_share = apartment_settlement.total_bills_pln / len(active_tenants)
        settlement_id = f"{apartment_settlement.apartment}-{year}-{month:02d}"

        return [
            TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=settlement_id,
                month=month,
                year=year,
                rent_pln=0.0,
                bills_pln=bills_share,
                total_due_pln=bills_share,
                balance_pln=-bills_share,
            )
            for tenant in active_tenants
        ]
