import tkinter

from pytest_mock import MockerFixture

from src.autoscription import core
from src.autoscription.core.logging import TestMonitoring
from src.autoscription.gui.Application import Application


class TestApplicationRemoveTempScans:
    def test_remove_temp_scans_confirmation_true(self, mocker: MockerFixture):
        mocker.patch("tkinter.messagebox.askyesno", return_value=True)
        mock_themed_tk = mocker.patch("ttkthemes.ThemedTk")
        mocker.patch.object(Application, "__init__", return_value=None)
        mocker.patch("src.autoscription.core.core.remove_last_scan_dir")
        mocker.patch("tkinter.messagebox.showinfo")

        instance = Application(master=mock_themed_tk, application_configuration={}, monitoring=TestMonitoring())
        instance.application_configuration = {"last_scan_dir": "/tmp/test"}
        instance.monitoring = TestMonitoring()

        instance.remove_last_scans()

        tkinter.messagebox.askyesno.assert_called_once_with(
            "Καθαρισμός προσωρινών σαρώσεων",
            "Πρόκειται να διαγράψετε τις σαρωμένες συνταγές που υπάρχουν στην προσωρινή "
            "μνήμη.\n"
            "Θα χρειαστεί να σαρώσετε πάλι τις συνταγές της ημέρας προς έλεγχο.\n"
            "Είστε σίγουροι ;",
        )
        core.core.remove_last_scan_dir.assert_called_once()
        tkinter.messagebox.showinfo.assert_called_once_with(
            "Επιτυχής καθαρισμός",
            "Οι σαρωμένες συντάγες που υπάρχουν στην προσωρινή μνήμη διεγράφησαν.\n"
            "Παρακαλώ σαρώστε πάλι τις συνταγές της ημέρας προς έλεγχο.",
        )

    def test_remove_temp_scans_confirmation_false(self, mocker: MockerFixture):
        mocker.patch("tkinter.messagebox.askyesno", return_value=False)
        mock_themed_tk = mocker.patch("ttkthemes.ThemedTk")
        mocker.patch.object(Application, "__init__", return_value=None)
        mocker.patch("src.autoscription.core.core.remove_last_scan_dir")
        mocker.patch("tkinter.messagebox.showinfo")

        instance = Application(master=mock_themed_tk, application_configuration={}, monitoring=TestMonitoring())
        instance.application_configuration = {"last_scan_dir": "/tmp/test"}
        instance.monitoring = TestMonitoring()

        instance.remove_last_scans()

        tkinter.messagebox.askyesno.assert_called_once_with(
            "Καθαρισμός προσωρινών σαρώσεων",
            "Πρόκειται να διαγράψετε τις σαρωμένες συνταγές που υπάρχουν στην προσωρινή "
            "μνήμη.\n"
            "Θα χρειαστεί να σαρώσετε πάλι τις συνταγές της ημέρας προς έλεγχο.\n"
            "Είστε σίγουροι ;",
        )
        core.core.remove_last_scan_dir.assert_not_called()
        tkinter.messagebox.showinfo.assert_not_called()
