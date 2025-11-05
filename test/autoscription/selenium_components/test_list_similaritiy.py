import pytest

from src.autoscription.selenium_components.utils import list_similarity


class TestListSimilarity:
    def test_list_similarity_with_common_elements(self):
        list1 = [1, 2, 3, 4, 5]
        list2 = [3, 4, 5, 6, 7]
        result = list_similarity(list1, list2)
        assert result.ratio == pytest.approx(0.6)
        assert result.common_elements == {3, 4, 5}

    def test_list_similarity_with_empty_lists(self):
        list1 = []
        list2 = []
        similarity = list_similarity(list1, list2)
        assert 0 == similarity.ratio
        assert set() == similarity.common_elements

    def test_list_similarity_with_first_list_empty(self):
        list1 = []
        list2 = [1, 2, 3]
        similarity = list_similarity(list1, list2)
        assert 0 == similarity.ratio
        assert set() == similarity.common_elements

    def test_list_similarity_with_zero_total_unique_elements(self):
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]
        similarity = list_similarity(list1, list2)
        assert 0 == similarity.ratio
        assert set() == similarity.common_elements
