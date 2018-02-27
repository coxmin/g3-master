# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
from calendar import monthrange
from os.path import exists


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


now = datetime.now()
logfile = 'logs_%s_%s.txt' % (now.month, now.year)
if not exists(logfile):
    with open(logfile, 'w+'):
        pass


class Vars:
    __metaclass__ = Singleton
    timp = datetime.now()
    luna = ['', 'Ian', 'Feb', 'Mar', 'Apr', 'Mai', 'Iun', 'Iul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    lunA = ['', 'Ianuarie', 'Februarie', 'Martie', 'Aprilie', 'Mai', 'Iunie', 'Iulie', 'August', 'Septembrie',
            'Octombrie', 'Noiembrie', 'Decembrie']
    zile = [u'Luni', u'Marți', u'Miercuri', u'Joi', u'Vineri', u'Sâmbătă', u'Duminică']

    month_start = datetime(now.year, now.month, 1).toordinal()
    month_end = datetime(now.year, now.month, monthrange(now.year, now.month)[1]).toordinal()
    BT_FONT = 12000

    _obvid = 0
    _agtid = 0
    _notaid = 0
    confdir = '.conf'
    basedir = '.base'
    postdir = '.post'
    datadir = '.data'

    def update(self):
        self.month_start = datetime(self.timp.year, self.timp.month, 1).toordinal()
        self.month_end = datetime(self.timp.year, self.timp.month,
                                  monthrange(self.timp.year, self.timp.month)[1]).toordinal()

    @property
    def oid(self):
        self._obvid += 1
        return self._obvid

    @property
    def aid(self):
        self._agtid += 1
        return self._agtid

    @property
    def nid(self):
        self._notaid += 1
        return self._notaid

    def nr_days(self, m=False, y=False):
        if not y:
            y = self.timp.year
        if m:
            return monthrange(y, m)[1]
        else:
            return monthrange(y, self.timp.month)[1]

    @staticmethod
    def zero(x):
        return '0%s' % x if x < 10 else '%s' % x

    def next_date(self, data=False, days=1):
        if data:
            return data + timedelta(days=days)
        return self.timp + timedelta(days=days)

    def precedent_day(self, data=False, days=1):
        if data:
            return (data - timedelta(days=days)).day
        return (self.timp - timedelta(days=days)).day

    def precedent_date(self, data=False, days=1):
        if data:
            return data - timedelta(days=days)
        return self.timp - timedelta(days=days)

    @staticmethod
    def iora(d):
        return int('{h}{m}'.format(h=d.hour, m='0%s' % d.minute if d.minute < 10 else '%s' % d.minute))


env = Vars()
