import pandas as pd
import pytest

from src.autoscription.core.report import find_min_moves_for_sorting


class TestFindMinMovesForSorting:
    def test_empty_dataframes(self):
        df = pd.DataFrame(columns=["pharmacist_idika_prescription_full", "current_index", "desired_index"])
        desired_order = []
        current_order = []
        moves_count, moves_df = find_min_moves_for_sorting(df, desired_order, current_order)

        assert moves_count == 0
        assert moves_df.empty

    def test_partially_matching_orders(self):
        df = pd.DataFrame(
            {"pharmacist_idika_prescription_full": [1, 2, 3], "current_index": [0, 1, 2], "desired_index": [1, 0, 2]}
        )
        desired_order = [1, 2, 3]
        current_order = [2, 1, 3]
        moves_count, moves_df = find_min_moves_for_sorting(df, desired_order, current_order)

        assert moves_count == 1
        assert not moves_df.empty
        # check not value

    def test_two_moves_required(self):
        df = pd.DataFrame(
            {
                "pharmacist_idika_prescription_full": [2525252, 2525254, 2525253, 2525251],
                "current_index": [2, 4, 3, 1],
                "desired_index": [1, 2, 3, 4],
            }
        )

        desired_order = [2525251, 2525252, 2525253, 2525254]
        current_order = [2525252, 2525254, 2525253, 2525251]
        moves_count, moves_df = find_min_moves_for_sorting(
            df=df, desired_order=desired_order, current_order=current_order
        )

        assert moves_count == 2

    def test_consecutive_items(self):  # todo: rename and simplify
        df = pd.DataFrame(
            {
                "pharmacist_idika_prescription_full": [
                    2401307505045100,
                    2401294631918100,
                    2401301560749100,
                    2401051871315120,
                    2401294245723100,
                    2312055035174131,
                    2401306612874100,
                    2401307721272100,
                    2401183392590100,
                    2312065011762130,
                    2401303719575100,
                    2401260672151112,
                ],
                "current_index": [0, 1, 3, 4, 5, 6, 9, 10, 8, 7, 11, 2],
                "desired_index": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            }
        )

        current_order = [
            2401307505045100,
            2401294631918100,
            2401301560749100,
            2401051871315120,
            2401294245723100,
            2312055035174131,
            2401306612874100,
            2401307721272100,
            2401183392590100,
            2312065011762130,
            2401303719575100,
            2401260672151112,
        ]
        desired_order = [
            2401307505045100,
            2401294631918100,
            2401260672151112,
            2401301560749100,
            2401051871315120,
            2401294245723100,
            2312055035174131,
            2312065011762130,
            2401183392590100,
            2401306612874100,
            2401307721272100,
            2401303719575100,
        ]

        moves_count, moves_df = find_min_moves_for_sorting(
            df=df, desired_order=desired_order, current_order=current_order
        )

        assert moves_count == 3
        print(moves_df)

    def test_identical_order(self):
        df = pd.DataFrame(
            {"pharmacist_idika_prescription_full": [1, 2, 3], "current_index": [0, 1, 2], "desired_index": [0, 1, 2]}
        )
        desired_order = [1, 2, 3]
        current_order = [1, 2, 3]
        moves_count, moves_df = find_min_moves_for_sorting(df, desired_order, current_order)

        assert moves_count == 0
        assert moves_df.empty

    def test_reverse_orders(self):
        df = pd.DataFrame(
            {"pharmacist_idika_prescription_full": [1, 2, 3], "current_index": [0, 1, 2], "desired_index": [2, 1, 0]}
        )
        desired_order = [3, 2, 1]
        current_order = [1, 2, 3]
        moves_count, moves_df = find_min_moves_for_sorting(df, desired_order, current_order)

        assert moves_count > 0
        assert not moves_df.empty

    def test_elements_not_common_in_orders(self):
        df = pd.DataFrame(
            {"pharmacist_idika_prescription_full": [1, 2, 3], "current_index": [0, 1, 2], "desired_index": [0, 1, 2]}
        )
        desired_order = [4, 5, 6]
        current_order = [1, 2, 3]
        moves_count, moves_df = find_min_moves_for_sorting(df, desired_order, current_order)

        assert moves_count == 0  # TODO: update implementation to through exception, wrong length
        assert moves_df.empty

    def test_large_reverse_order(self):
        large_number = 1000
        df = pd.DataFrame(
            {
                "pharmacist_idika_prescription_full": list(range(large_number)),
                "current_index": list(range(large_number)),
                "desired_index": list(range(large_number))[::-1],
            }
        )
        desired_order = list(range(large_number))[::-1]
        current_order = list(range(large_number))
        moves_count, moves_df = find_min_moves_for_sorting(df, desired_order, current_order)

        assert moves_count == (large_number - 1)
        assert not moves_df.empty

    def test_invalid_input_types(self):
        with pytest.raises(AttributeError):
            find_min_moves_for_sorting("not a dataframe", "not a dataframe", "not a dataframe")
