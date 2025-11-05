import pandas as pd
import pytest

from src.autoscription.core.report import contains_eu_citizen


class TestEuCityzenship:
    # Pytest fixture for the DataFrame
    @pytest.fixture
    def sample_dataframe(self):
        data = {"Κατηγορία": ["Ευρωπαίων Ασφαλισμένων**", "Other", "Another"]}
        return pd.DataFrame(data)

    # Test function when the DataFrame contains an EU citizen
    def test_contains_eu_citizen_true(self, sample_dataframe):
        assert contains_eu_citizen(sample_dataframe) is True

    # Test function when the DataFrame does not contain an EU citizen
    def test_contains_eu_citizen_false(self):
        df = pd.DataFrame({"Κατηγορία": ["Other", "Another"]})
        assert contains_eu_citizen(df) is False

    # Test function with an empty DataFrame
    def test_contains_eu_citizen_empty_df(self):
        df = pd.DataFrame({"Κατηγορία": []})
        assert contains_eu_citizen(df) is False
