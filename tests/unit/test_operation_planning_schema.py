from datetime import date

import pytest
from pydantic import ValidationError

from app.modules.operation_planning.schemas import OperationPlanningRequest


@pytest.mark.unit
def test_accepts_period_when_end_date_is_after_start_date():
    payload = OperationPlanningRequest(
        area_ha=10,
        start_date=date(2026, 8, 19),
        end_date=date(2026, 8, 20),
        hours_per_day=8,
    )

    assert payload.end_date == date(2026, 8, 20)


@pytest.mark.unit
@pytest.mark.parametrize("end_date", [date(2026, 8, 18), date(2026, 8, 19)])
def test_rejects_end_date_before_or_equal_to_start_date(end_date):
    with pytest.raises(ValidationError) as exc_info:
        OperationPlanningRequest(
            area_ha=10,
            start_date=date(2026, 8, 19),
            end_date=end_date,
            hours_per_day=8,
        )

    error = exc_info.value.errors()[0]
    assert error["loc"] == ("end_date",)
    assert "posterior à data inicial" in error["msg"]
