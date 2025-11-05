import pytest

from src.autoscription.core.errors import MappingIdikaResponseUnexpectedValueException
from src.autoscription.idika_client.mapping.utils import get_boolean_from_id_value


class TestGetBooleanFromIdValue:
    def test_true(self):
        """Test that the function returns True when the input value is '1'."""
        assert get_boolean_from_id_value("1") is True

    def test_false(self):
        """Test that the function returns False when the input value is '0'."""
        assert get_boolean_from_id_value("0") is False

    def test_unexpected_values(self):
        """Test that the function raises an exception for unexpected values."""
        with pytest.raises(MappingIdikaResponseUnexpectedValueException):
            get_boolean_from_id_value("2")
        with pytest.raises(MappingIdikaResponseUnexpectedValueException):
            get_boolean_from_id_value("abc")
        with pytest.raises(MappingIdikaResponseUnexpectedValueException):
            get_boolean_from_id_value("-1")
