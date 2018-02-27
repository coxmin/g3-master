# -*- coding: UTF-8 -*-
from json import load, dump
import os
from datetime import datetime
from context import env


class Agent:
    def __init__(self, nume='', post='', id=False):
        self.id = id or env.aid
        self.nume = unicode(nume)
        self.post = post


class Post:
    def __init__(self, nume='', id=False):
        self.id = id or env.oid
        self.nume = unicode(nume)
        self.agenti = []
        self.aids = {}
        self.hyst = {}
        self.tel = ''
        self.adr = ''
        self.dest = ''
        self.obv = ''
        self.orar = {
            "1": [0, 0],
            "0": [0, 0],
            "3": [0, 0],
            "2": [0, 0],
            "5": [0, 0],
            "4": [0, 0],
            "6": [0, 0]
        }

    def month_hyst(self):
        return {x: self.hyst[x] for x in self.hyst if env.month_start <= x <= env.month_end}

    def month_hyst_at(self, month, y=False):
        y = y or env.timp.year
        st = datetime(y, month, 1).toordinal()
        end = datetime(y, month, env.nr_days(month, y)).toordinal()
        return {x: self.hyst[x] for x in self.hyst if st <= x <= end}


class Disp:
    posturi = []
    pids = {}
    aids = {}
    agenti = []

    def __init__(self):
        self.timp = datetime.now()
        self.azi = self.timp.date()
        self.load()

    def get_post_by_name(self, n):
        r = [x for x in self.posturi if x.nume == n]
        if r:
            return r[0]
        return False

    def check_now(self):
        dor = self.timp.toordinal()
        isday = 1
        if self.timp.hour < 5:
            dor = env.precedent_date().toordinal()
            isday = 2
        elif self.timp.hour >= 12:
            isday = 2
        w = str(self.timp.weekday())

        def check_post(post):
            if dor in post.hyst:
                for xx in post.hyst[dor]:
                    if isday in post.hyst[dor][xx] and post.hyst[dor][xx][isday]['b'] > 0:
                        return True
            # orar
            h = post.orar[w][0]
            if h == '0' or h is None:
                return False
            if int(h) > self.timp.hour:
                return True
            # end orar
            return False

        return [x.nume for x in self.posturi if not check_post(x)]

    def add_post(self, a):
        if type(a) is unicode:
            a = Post(a)
        elif type(a) is str:
            a = Post(unicode(a))
        if not isinstance(a, Post):
            return -1
        if a.nume in [x.nume for x in self.posturi]:
            return [x for x in self.posturi if x.nume == a.nume][0]
        self.posturi.append(a)
        self.pids[a.id] = a
        a.ref = self
        return a

    def modify_post(self, post, old):
        p = '%s/%s.json' % (env.postdir, old)
        if os.path.exists(p):
            os.rename(p, '%s/%s.json' % (env.postdir, post.nume))
        if os.path.exists('%s/%s.json' % (env.basedir, old)):
            os.rename('%s/%s.json' % (env.basedir, old), '%s/%s.json' % (env.basedir, post.nume))
        self.save()

    def del_post(self, post):
        cfis = '%s/%s.json' % (env.postdir, post.nume.encode('utf-8'))
        dfis = '%s/%s.json' % (env.confdir, post.nume.encode('utf-8'))
        efis = '%s/%s.json' % (env.basedir, post.nume.encode('utf-8'))
        if os.path.exists(cfis):
            with open(dfis, 'w')as dest:
                with open(cfis, 'r')as surse:
                    dest.write(surse.read())
            os.remove(cfis)
        if os.path.exists(efis):
            os.remove(efis)
            # import shutil
            # shutil.move(cfis, dfis)

        self.save_date(post)
        self.posturi.pop(self.posturi.index(post))
        self.pids.pop(post.id)
        self.save()

    def add_agent(self, a):
        if not isinstance(a, Agent):
            return -1
        self.agenti.append(a)
        self.aids[a.id] = a

    def add_agent_at(self, A, pid):
        if not pid in self.pids:
            return -1
        if not isinstance(A, Agent):
            a = [x for x in self.agenti if x.nume == A]
            if not a:
                A = Agent(A)
        else:
            a = [x for x in self.agenti if x.nume == A.nume]
        if a:
            agt = a[0]
        else:
            agt = A
            self.add_agent(A)
        post = self.pids[pid]
        if agt.nume in [x.nume for x in post.agenti]:
            return -2
        post.agenti.append(agt)
        post.aids[agt.id] = agt
        return agt.id

    def modify_agent(self, newname, agent, post):
        self.aids[agent.id].nume = newname
        post.aids[agent.id].nume = newname
        for data in post.hyst:
            for aid in post.hyst[data]:
                if aid != agent.id:
                    continue
                for isday in post.hyst[data][aid]:
                    post.hyst[data][aid][isday]['a'] = newname

    def del_agent(self, agent, post):
        self.save_date(post)
        post.agenti.pop(post.agenti.index(agent))
        post.aids.pop(agent.id)
        self.agenti.pop(self.agenti.index(agent))
        self.aids.pop(agent.id)
        self.save_base()

    def load_month1(self, post, m=False):
        m = m or self.azi.month
        f = '%s/%s_%s.json' % (env.postdir, post.nume.encode('utf-8'), m)
        with open('%s/%s_%s.json' % (env.postdir, post.nume.encode('utf-8'), post.month), 'w')as fis:
            dump(
                {'id': post.id, 'hyst': post.hyst, 'agenti': {z.nume: z.id for z in post.agenti}}, fis)
        post.hyst = {}
        post.month = m
        if not os.path.exists(f):
            print('f Not E')
            return
        with open(f, 'r') as fis:
            p = load(fis)
        for x in p['hyst']:
            post.hyst[int(x)] = {}
            for y in p['hyst'][x]:
                post.hyst[int(x)][int(y)] = {}
                for z in p['hyst'][x][y]:
                    post.hyst[int(x)][int(y)][int(z)] = p['hyst'][x][y][z]
        for agt in p['agenti']:
            if agt in [x.nume for x in post.agenti]:
                continue
            A = Agent(agt, post.nume, p['agenti'][agt])
            self.add_agent_at(A, post.id)

    def load(self):
        if not os.path.exists(env.confdir):
            os.mkdir(env.confdir)
        if not os.path.exists(env.basedir):
            os.mkdir(env.basedir)
        if not os.path.exists(env.postdir):
            os.mkdir(env.postdir)
        for f in os.listdir(env.basedir):
            with open('%s/%s' % (env.basedir, f), 'r') as fis:
                p = load(fis)
            post = Post(p['nume'], p['id'])
            post.tel, post.adr, post.obv, post.dest = p['tel'], p['adr'], p['obv'], p['dest']
            if 'orar' in p:
                post.orar = p['orar']
            self.add_post(post)
            for agt in p['agenti']:
                A = Agent(agt, post.nume, p['agenti'][agt])
                self.add_agent_at(A, post.id)

        for f in os.listdir(env.postdir):
            with open('%s/%s' % (env.postdir, f), 'r') as fis:
                p = load(fis)
            post = self.pids[p['id']]
            for x in p['hyst']:
                post.hyst[int(x)] = {}
                for y in p['hyst'][x]:
                    post.hyst[int(x)][int(y)] = {}
                    for z in p['hyst'][x][y]:
                        post.hyst[int(x)][int(y)][int(z)] = p['hyst'][x][y][z]
            for agt in p['agenti']:
                A = Agent(agt, post.nume, p['agenti'][agt])
                self.add_agent_at(A, post.id)
        d = [x.id for x in self.posturi]
        if d:
            env._obvid = max(d) + 1
        d = [x.id for x in self.agenti]
        if d:
            env._agtid = max(d) + 1

    @staticmethod
    def save_post(post):
        with open('%s/%s.json' % (env.postdir, post.nume.encode('utf-8')), 'w') as f:
            dump(
                {'id': post.id, 'hyst': post.hyst, 'agenti': {z.nume: z.id for z in post.agenti}}, f)

    def save_date(self, post, m=False):
        m = m or self.azi.month
        with open('%s/%s_%s.json' % (env.datadir, post.nume.encode('utf-8'), m), 'w') as f:
            dump({'id': post.id, 'hyst': post.hyst, 'agenti': {z.nume: z.id for z in post.agenti}}, f)

    def save(self):
        self.save_base()
        for x in self.posturi:
            with open('%s/%s.json' % (env.postdir, x.nume.encode('utf-8')), 'w') as f:
                dump({'id': x.id, 'hyst': x.hyst, 'agenti': {z.nume: z.id for z in x.agenti}}, f)
        with open('.disp.json', 'w') as fis:
            d = {'agenti': [x.nume for x in self.agenti], 'posturi': [x.nume for x in self.posturi]}
            dump(d, fis)

    def save_base(self):
        for x in self.posturi:
            with open('%s/%s.json' % (env.basedir, x.nume.encode('utf-8')), 'w')as f:
                dump(
                    {'nume': x.nume, 'id': x.id, 'agenti': {z.nume: z.id for z in x.agenti}, 'adr': x.adr, 'tel': x.tel,
                     'dest': x.dest, 'obv': x.obv, 'orar': x.orar}, f)

    @staticmethod
    def log_at(ref, agt, bifa, now, obs='', isday=False):
        data = now.toordinal()
        ora = env.iora(now)
        if not isday:
            isday = 2 if ora > 1200 else 1
        t = str(datetime.now())[:19]
        agent = ref.aids[agt]
        d = {'u': env.get_user(), 'a': agent.nume, 'aid': agent.id, 'c': isday, 'b': bifa, 'd': data, 'h': ora,
             'o': obs, 't': t, 'p': ref.nume}
        if data in ref.hyst:
            if agt in ref.hyst[data]:
                if len(ref.hyst[data][agt]) > 0:
                    if isday in ref.hyst[data][agt] and ref.hyst[data][agt][isday]['o']:
                        if d['o']:
                            d['o'] += '#' + ref.hyst[data][agt][isday]['o']
                        else:
                            d['o'] = ref.hyst[data][agt][isday]['o']
                    ref.hyst[data][agt][isday] = d
                else:
                    ref.hyst[data][agt] = {isday: d}
            else:
                ref.hyst[data][agt] = {isday: d}
        else:
            ref.hyst[data] = {agt: {isday: d}}

    def raport_excel(self, dt):
        from xls import Xls
        xl = Xls(dt.year, dt.month)
        xl.posturi = {}
        k = 0
        for x in self.posturi:
            if x.obv in xl.posturi:
                xl.posturi[x.obv].append(x)
            else:
                xl.posturi[x.obv] = [x]
            k += 1
        xl.posturi['nr'] = k
        xl.write_obv_data()
