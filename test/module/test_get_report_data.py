import datetime
from test.module.utils import (
    default_dosages_dict,
    default_full_prescription_summaries,
    default_pages_dict,
    default_partial_prescription_summaries,
    report_data_schema,
)

import pandas as pd

from src.autoscription.core.logging import TestMonitoring
from src.autoscription.core.report import get_report_data


class TestGetReportData:
    def test_get_report_data_schema(self):
        pages = pd.DataFrame.from_dict(default_pages_dict)
        dosages = pd.DataFrame.from_dict(default_dosages_dict)
        partial_prescription_summaries = pd.DataFrame.from_dict(default_partial_prescription_summaries)
        full_prescription_summaries = pd.DataFrame.from_dict(default_full_prescription_summaries)

        result = get_report_data(
            pages=pages,
            dosages=dosages,
            partial_prescription_summaries=partial_prescription_summaries,
            full_prescription_summaries=full_prescription_summaries,
            run_date=datetime.date(2023, 11, 3),
            report_config={"execution_time_ordering": False, "show_overview": True, "category_breakdown": False},
            business_rules_config={"fyk_limit": 3000.0},
            monitoring=TestMonitoring(),
        )

        report_data_schema.validate(result)
