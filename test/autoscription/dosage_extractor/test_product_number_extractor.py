from __future__ import annotations

import pytest

from src.autoscription.dosage_extractor.product_number_extractor import (
    bottle_x_number,
    bt_x_number,
    bt_x_number_blist_x_number,
    bt_x_number_vial_x_number,
    cap_bt_x_number,
    fl_x_number,
    number_disks,
    number_doses,
)


class TestProductNumberExtractor:
    @pytest.mark.parametrize(
        "given_input, expected",
        [
            ("DEXARIS NASPR.SUS 0,2028+0,5MG/ML BT X 1VIAL X 300 DOSES ΓΕΝΌΣΗΜΟ", 300),
            (
                "FOSTER NEXTHALER PD.INH.MD 100+6MC/DOSE BTX1X120 ΔOΣEIΣ ΠΡΩΤΌΤΥΠΟ ΣΕ ΘΕΡΑΠΕΥΤΙΚΉ "
                "ΚΑΤΗΓΟΡΊΑ XΩΡΊΣ ΓΕΝΌΣΗΜΟ",
                120,
            ),
            (
                "RELVAR ELLIPTA INH.PD.DOS 92+22MCG/DOSE BTX1 ΣΥΣΚΕΥΉ ΕΙΣΠΝΟΏΝ X30 ΔOΣEIΣ "
                "ΠΡΩΤΌΤΥΠΟ ΣΕ ΘΕΡΑΠΕΥΤΙΚΉ ΚΑΤΗΓΟΡΊΑ XΩΡΊΣ ΓΕΝΌΣΗΜΟ",
                30,
            ),
        ],
    )
    def test_number_doses(self, given_input: str, expected: int) -> None:
        res = number_doses(given_input)
        assert res == expected

    @pytest.mark.parametrize(
        "given_input, expected", [("CADELIUS OR.DISP.TA 1500MG+1000 IU/TAB BOTTLEX30 TABS ΓΕΝΌΣΗΜΟ", 30)]
    )
    def test_bottle_x_number(self, given_input: str, expected: int) -> None:
        res = bottle_x_number(given_input)
        assert res == expected

    @pytest.mark.parametrize(
        "given_input, expected",
        [("ENIT TAB 10+20MG/TAB ΣΥΣΚΕΥΑΣΙΑ30 ΔIΣKIΩN ΠΡΩΤΌΤΥΠΟ ΣΕ ΘΕΡΑΠΕΥΤΙΚΉ  ΚΑΤΗΓΟΡΊΑ XΩΡΊΣ ΓΕΝΌΣΗΜΟ", 30)],
    )
    def test_number_disks(self, given_input: str, expected: int) -> None:
        res = number_disks(given_input)
        assert res == expected

    @pytest.mark.parametrize("given_input, expected", [("ELCOZEK GR.CAP 40MG/CAP BTX1VIALX 30 CAPS ΓΕΝΌΣΗΜΟ", 30)])
    def test_bt_x_number_vial_x_number(self, given_input: str, expected: int) -> None:
        res = bt_x_number_vial_x_number(given_input)
        assert res == expected

    @pytest.mark.parametrize(
        "given_input, expected",
        [
            ("NEXIUM GR.TAB 40MG/TAB BT X 28 ΠΡΩΤΌΤΥΠΟ ΣΕ ΘΕΡΑΠΕΥΤΙΚΉ " + "ΚΑΤΗΓΟΡΊΑ XΩΡΊΣ  ΓΕΝΌΣΗΜΟ", 28),
            ("INEGY TAB 10+40MG/TAB BTX28 ΠΡΩΤΌΤΥΠΟ ΣΕ ΘΕΡΑΠΕΥΤΙΚΉ ΚΑΤΗΓΟΡΊΑ ΜΕ  ΓΕΝΌΣΗΜΟ", 28),
            ("CRESTOR F.C.TAB 10MG/TAB BTX  14 ΠΡΩΤΌΤΥΠΟ ΣΕ ΘΕΡΑΠΕΥΤΙΚΉ ΚΑΤΗΓΟΡΊΑ ΜΕ  ΓΕΝΌΣΗΜΟ", 14),
        ],
    )
    def test_bt_x_number(self, given_input: str, expected: int) -> None:
        res = bt_x_number(given_input)
        assert res == expected

    @pytest.mark.parametrize(
        "given_input, expected",
        [
            ("CLARIPEN GRA.OR.SUS 250MG/5ML FLX60 ML ΓΕΝΌΣΗΜΟ", 60),
            ("PROCEF PD.ORA.SUS 250MG/5ML FL X 100 ML ΠΡΩΤΌΤΥΠΟ ΣΕ " + "ΘΕΡΑΠΕΥΤΙΚΉ  ΚΑΤΗΓΟΡΊΑ ΜΕ ΓΕΝΌΣΗΜΟ", 100),
            ("CALCIORAL D3 CHW.TAB 1000MG+20ΜG 800 IU/TAB FLX30 HDPE ΓΕΝΌΣΗΜΟ", 30),
        ],
    )
    def test_fl_x_number(self, given_input: str, expected: int) -> None:
        res = fl_x_number(given_input)
        assert res == expected

    @pytest.mark.parametrize(
        "given_input, expected",
        [
            ("SERTRAL CAPS 100MG/CAP BTX2 BLIST X7 ΓΕΝΌΣΗΜΟ", 14),
            ("SERTRAL CAPS 50 MG/CAP BTX2 BLIST X7 ΓΕΝΌΣΗΜΟ", 14),
        ],
    )
    def test_bt_x_number_blist_x_number(self, given_input: str, expected: int) -> None:
        res = bt_x_number_blist_x_number(given_input)
        assert res == expected

    @pytest.mark.parametrize(
        "given_input, expected",
        [
            ("EDUFIL INHPD.CAP 12 MCG/CAP BTX60", 60),
        ],
    )
    def test_cap_bt_x_number(self, given_input: str, expected: int) -> None:
        res = cap_bt_x_number(given_input)
        assert res == expected
