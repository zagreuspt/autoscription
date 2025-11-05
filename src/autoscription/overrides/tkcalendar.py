def _btns_date_range(self) -> None:  # type: ignore[no-untyped-def]
    """Disable/enable buttons depending on allowed date range."""
    maxdate = self["maxdate"]
    mindate = self["mindate"]

    if maxdate is not None:
        max_year, max_month = maxdate.year, maxdate.month
        if self._date > maxdate:
            self._date = self._date.replace(year=max_year, month=max_month)
            self._display_calendar()

        dy = max_year - self._date.year
        # if dy == 0:
        #     self._r_year.state(['disabled'])
        #     if self._date.month == max_month:
        #         self._r_month.state(['disabled'])
        #     else:
        #         self._r_month.state(['!disabled'])
        # elif dy == 1:
        #     if self._date.month > max_month:
        #         self._r_year.state(['disabled'])
        #     else:
        #         self._r_year.state(['!disabled'])
        #         self._r_month.state(['!disabled'])
        # else:  # dy > 1
        #     self._r_year.state(['!disabled'])
        #     self._r_month.state(['!disabled'])
        if dy >= 0:
            self._r_year.state(["!disabled"] if dy > 0 else ["disabled"])
            if dy == 0 and self._date.month >= max_month:
                self._r_month.state(["disabled"])
            else:
                self._r_month.state(["!disabled"])

    if mindate is not None:
        min_year, min_month = mindate.year, mindate.month
        if self._date < mindate:
            self._date = self._date.replace(year=min_year, month=min_month)
            self._display_calendar()

        dy = self._date.year - min_year
        if dy == 0:
            self._l_year.state(["disabled"])
            if self._date.month == min_month:
                self._l_month.state(["disabled"])
            else:
                self._l_month.state(["!disabled"])
        elif dy == 1:
            if self._date.month >= min_month:
                self._l_year.state(["!disabled"])
                self._l_month.state(["!disabled"])
            else:
                self._l_year.state(["disabled"])
        else:  # dy > 1
            self._l_year.state(["!disabled"])
            self._l_month.state(["!disabled"])
