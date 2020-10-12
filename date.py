import datetime
import time
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

# replace this if possible
import QuantLib as ql
CALENDARS_MAP = {
    'BOND': ql.UnitedStates(ql.UnitedStates.GovernmentBond),
    'STOCK': ql.UnitedStates(ql.UnitedStates.NYSE)
}

__all__ = ['Date']


class Date(datetime.date):
    """
    Date can be initialized by the following form:
        20201001
        '20201001', '2020-10-01', '2020.10.01'
        datetime.datetime(2020,10,1)
        datetime.date(2020,10,1)
        Date
        QuantLib date
        2020, 10, 1 - original datetime.date input
    
    Given different calendar package, rewrite is_bizday() accordingly.
    """
    default_format = "%Y%m%d"

    def __new__(cls, *args):
        if len(args) == 1:
            date = cls.__to_str(args[0])
            year  = int(date[:4])
            month = int(date[4:6])
            day   = int(date[6:])
            return datetime.date.__new__(cls, year, month, day)
        elif len(args) == 3:
            return datetime.date.__new__(cls, *args)
        else:
            raise Exception('Input has to be either 1 or 3')

    @classmethod
    def __to_str(cls, date):
        type_d = type(date)
        if type_d is str:
            date = date.replace('-', '') if '-' in date else date
            date = date.replace('.', '') if '.' in date else date
            return date
        elif type_d is int:
            return str(date)
        elif type_d is datetime.datetime:
            return date.strftime(cls.default_format)
        elif type_d is datetime.date:
            return date.strftime(cls.default_format)
        elif type_d is Date:
            return date.as_str()
        elif type_d is ql.QuantLib.Date:
            # it has st, nd, rd, th in the str
            return parse(str(date)).strftime(cls.default_format)
        else:
            raise Exception("Date: wrong date input type")

    def edate(self, months):
        """Excel EDATE function"""
        return self.add(months=months)

    def add(self, years=0, months=0, days=0):
        return self + relativedelta(years=years, months=months, days=days)

    def _neighbour_bizday(self, calendar, n):
        d = self
        while True:
            d = d.add(days=n)
            if d.is_bizday(calendar):
                return d

    def next_bizday(self, calendar='Bond'):
        return self._neighbour_bizday(calendar, 1)

    def prev_bizday(self, calendar='Bond'):
        return self._neighbour_bizday(calendar, -1)

    def is_bizday(self, calendar='Bond'):
        calendar_used = CALENDARS_MAP[calendar.upper()]
        return calendar_used.isBusinessDay(self.as_ql())

    @classmethod
    def range(cls, start, end, include_last=False, show_holiday=False, calendar='Bond'):
        # include_last default to False to be consistent with range(.)
        if not include_last:
            end = end.add(days=-1)
        dates = []
        d = start
        while d <= end:
            if show_holiday or d.is_bizday(calendar):
                dates.append(d)
            d = d.add(days=1)
        return dates

    def as_str(self, format=None):
        format = self.default_format if format is None else format
        return self.strftime(format)

    def as_int(self):
        return int(self.as_str())

    def as_js(self):
        return time.mktime(self.timetuple()) * 1000

    def as_q(self):
        return self.as_str('%Y.%m.%d')

    def as_ql(self):
        return ql.Date(self.as_str(), self.default_format)
