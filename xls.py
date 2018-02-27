# -*- coding: UTF-8 -*-

from calendar import monthrange
from sq import Obiectiv, Agent
import sq
from datetime import datetime, date
from jsdb import Disp as DSP
from context import env

class D(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)


class Xls(object):
    obv = {}
    agenti = {}
    month = False
    year = False

    def write_obv_data(self):
        dis = ['Ana', 'Georgiana', 'Cosmin', 'Valentina']
        lsort = sorted([x for x in self.posturi])
        end = monthrange(self.year, self.month)[1] + 1
        for i in lsort:
            if i == 'nr':
                continue

            for o in self.posturi[i]:
                o.stat = o.dest
                zi = '0123456'
                orarz, orarn = [], []
                for x in zi:
                    d1 = o.orar[x][0]
                    if d1 is None:
                        d1 = 0
                    d1 = str(d1)
                    orarz.append(d1)
                    d1 = o.orar[x][1]
                    if d1 is None:
                        d1 = 0
                    d1 = str(d1)
                    orarn.append(d1)

                obv = D()
                obv.obv = o.obv
                obv.nume = o.nume
                obv.adr = o.adr
                obv.tel = o.tel
                obv.stat = o.stat
                obv.orars = ','.join(orarz)
                obv.orare = ','.join(orarn)
                sqobv = Obiectiv(obv)
                obv.id = sqobv.ins()

                stq = set()
                hyst = o.month_hyst_at(self.month, self.year)
                for zzz in o.agenti:
                    stq.add((zzz.nume, zzz.id))
                for day in hyst:
                    for aid in hyst[day]:
                        for isd in hyst[day][aid]:
                            stq.add((hyst[day][aid][isd]['a'], hyst[day][aid][isd]['aid']))
                lagt = {}

                for agtx in sorted(stq):
                    agt = D()
                    agt.nume = agtx[0]
                    agt.obv = obv.id
                    agent = Agent(agt)
                    agt.id = agent.ins()
                    lagt[agtx[1]] = agt

                for day in hyst:
                    for rec in hyst[day]:
                        agent = lagt[rec]
                        for qq in hyst[day][rec]:
                            obj = D()
                            obj.agent = agent.id
                            obj.obv = obv.id
                            data = hyst[day][rec][qq]
                            obj.bifa = data['b']
                            cifa = data['c']
                            obj.mark_at = str(date.fromordinal(data['d']))
                            # dt_r = datetime.datetime.strptime(data['t'], '%Y-%m-%d %H:%M:%S')
                            obj._time = data['t']
                            user = 4
                            obj.dispecer = user
                            if 'u' in data:
                                user = data['u']
                                obj.dispecer = dis.index(user)
                            # timp = '{}:{}'.format(env.zero(dt_r.hour), env.zero(dt_r.minute))
                            # v = '0%s' % data['h']
                            # hh = '%s:%s' % (v[-4:-2], v[-2:])
                            obj.hour = hh = int(data['h'])
                            
                            obj.isday = 0 if 600 < hh < 1200 else 1
                            obj.obs = data['o']
                            sq.mark_object(obj)

    def __init__(self, year, month):
        self.month, self.year = month, year


class Win:
    btlist = {}
    last_ord = 0
    timp = datetime.now()

    def __init__(self, ):
        self.disp = DSP()

    def on_raport_excel(self, date):
        self.disp.raport_excel(date)

    def update_time(self):
        self.timp = env.timp = self.disp.timp = datetime.now()
        self.disp.azi = self.timp.date()
        env.update()


def main():
    sq.init()
    w = Win()
    for x in range(1, 13):
        w.on_raport_excel(datetime(2017, x, 1))
    #w.on_raport_excel(datetime(2017, 8, 1))
    w.on_raport_excel(datetime(2018, 1, 1))
    w.on_raport_excel(datetime(2018, 2, 1))
    import time
    print('################################################')
    time.sleep(5)
    sq.close()

def test():
    pass

if __name__ == '__main__':
    main()
