# -*- coding: UTF-8 -*-
from calendar import monthrange
from datetime import datetime, date, timedelta

import apsw

_db = 'test.db'
_conn = apsw.Connection(_db)
dis = ['Ana', 'Georgiana', 'Cosmin', 'Valentina']


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def init():
    crs = _conn.cursor()
    crs.execute("PRAGMA synchronous = OFF")
    crs.execute("PRAGMA cache_size = 100000")
    crs.execute("PRAGMA temp_store = MEMORY")
    # crs.execute("PRAGMA journal_mode = MEMORY#OFF")
    sq_obv = 'CREATE TABLE IF NOT EXISTS obiectiv(id INTEGER PRIMARY KEY, nume TEXT UNIQUE NOT NULL, adr TEXT, stat TEXT, tel TEXT, obv TEXT, _time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,obs TEXT, orars TEXT DEFAULT "0,0,0,0,0,0,0", orare TEXT default "0,0,0,0,0,0,0")'
    sq_obv_bk = 'CREATE TABLE IF NOT EXISTS obiectiv_bk(id INTEGER PRIMARY KEY, nume TEXT UNIQUE NOT NULL, adr TEXT, stat TEXT, tel TEXT, obv TEXT, _time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,obs TEXT, orars TEXT DEFAULT "0,0,0,0,0,0,0", orare TEXT default "0,0,0,0,0,0,0")'
    sq_agent = 'CREATE TABLE IF NOT EXISTS agent(id INTEGER PRIMARY KEY, nume TEXT UNIQUE NOT NULL, tel TEXT, obs TEXT, _time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, obv INTEGER, FOREIGN KEY(obv) REFERENCES obv(id))'
    sq_agent_obv = 'CREATE TABLE IF NOT EXISTS agentobv(id INTEGER PRIMARY KEY, agent INTEGER NOT NULL, nume INTEGER, _time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(agent) REFERENCES agent(id), FOREIGN KEY(nume) REFERENCES obiectiv(id))'
    sq_jur = 'CREATE TABLE IF NOT EXISTS jurnal(id INTEGER PRIMARY KEY, agent INTEGER NOT NULL, obv INTEGER NOT NULL, dispecer INTEGER, isday INTEGER DEFAULT 0, bifa INTEGER DEFAULT 1, hour INTEGER, mark_at TIMESTAMP DEFAULT CURRENT_DATE, obs TEXT, _time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(agent) REFERENCES agent(id), FOREIGN KEY(obv) REFERENCES obv(id))'
    sq_ignore = 'CREATE TABLE IF NOT EXISTS ignore(id INTEGER PRIMARY KEY, nume TEXT UNIQUE, obv INTEGER UNIQUE NOT NULL, _time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(obv) REFERENCES obv(id))'
    crs.execute(sq_obv)
    crs.execute(sq_agent)
    crs.execute(sq_agent_obv)
    crs.execute(sq_jur)
    crs.execute(sq_ignore)

    crs.execute(sq_obv_bk)


class DL(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        if key in self:
            self[key].append(value)
        else:
            dict.__setitem__(self, key, [value])


class REC(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)


class Base(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def ins(self):
        s = 'INSERT INTO {} ({}) VALUES ({})'.format(self._name, ','.join(self.keys()),
                                                     ','.join(['?'] * len(self.keys())))
        c = _conn.cursor()
        try:
            c.execute(s, self.values())
        except apsw.ConstraintError:
            return self.exist()
        return _conn.last_insert_rowid()

    def exist(self, nume=False):
        if not nume:
            nume = self.nume
        c = _conn.cursor()
        for x in c.execute('SELECT id FROM {} WHERE nume=?'.format(self._name), (nume,)):
            return x[0]
        return False

    def g(self):
        c = _conn.cursor()
        for x in c.execute('SELECT * FROM {} WHERE nume=? LIMIT 1'.format(self._name), (self.nume,)):
            return self.__class__(zip([i[0] for i in c.getdescription()], x))


class Obiectiv(Base):
    _name = 'obiectiv'


class Agent(Base):
    _name = 'agent'


class Jurnal(Base):
    _name = 'jurnal'


class AgObv(Base):
    _name = 'agentobv'


class Ignore(Base):
    _name = 'ignore'


def get_lista_obiective():
    return sorted([unicode(x[0]) for x in _conn.cursor().execute("SELECT nume FROM obiectiv").fetchall()])


def add_at_obv(agent, obv):
    nr = _conn.cursor().execute('SELECT COUNT(*) FROM agentobv WHERE agent=? AND nume=?', (agent, obv)).fetchone()[
        0]
    if nr < 1:
        _conn.cursor().execute('INSERT INTO agentobv (agent, nume) VALUES (?,?)', (agent, obv))


def mark_object(o):
    Jurnal(o).ins()
    nr = _conn.cursor().execute('SELECT COUNT(*) FROM agentobv WHERE agent=? AND nume=?', (o.agent, o.obv)).fetchone()[
        0]
    if nr < 1:
        _conn.cursor().execute('INSERT INTO agentobv (agent, nume) VALUES (?,?)', (o.agent, o.obv))
        print(re_agent(o.agent))


def re_agent(i):
    return _conn.cursor().execute('SELECT nume FROM agent WHERE id=? LIMIT 1', (i,)).fetchone()[0].encode('utf-8')


def re_obv(i):
    return _conn.cursor().execute('SELECT nume FROM obiectiv WHERE id=? LIMIT 1', (i,)).fetchone()[0].encode('utf-8')


def get_obv_by_id(i):
    c = _conn.cursor()
    c.execute('SELECT * FROM obiectiv WHERE id=? LIMIT 1', (i,))
    return REC(zip([i[0] for i in c.getdescription()], c.fetchone()))


def posturi():
    c = _conn.cursor()
    for x in c.execute('SELECT * FROM obiectiv'):
        yield REC(zip([i[0] for i in c.getdescription()], x))


def agenti():
    c = _conn.cursor()
    for x in c.execute('SELECT id, nume, tel, obv FROM agent'):
        yield REC(zip([i[0] for i in c.getdescription()], x))


def mody_agent(old, nume, tel):
    try:
        _conn.cursor().execute('UPDATE agent SET nume=?,tel=? WHERE id=?', (nume, tel, old.id))
        return 0
    except apsw.ConstraintError:
        return -1


def del_agent(a, obv):
    _conn.cursor().execute('DELETE FROM agentobv WHERE agent=? AND nume=?', (a.id, obv))


def get_agenti_at_obv(obvid, d=0):
    return sorted([re_agent(x[0]) for x in
                   _conn.cursor().execute('SELECT agent FROM agentobv WHERE nume=?', (obvid,)).fetchall()])


def get_agenti_at_date(obvid, d=date.today()):
    sd = str(date(d.year, d.month, 1))
    ed = str(date(d.year, d.month, monthrange(d.year, d.month)[1]))
    l = set()
    for x in _conn.cursor().execute('SELECT agent FROM jurnal WHERE obv=? AND mark_at BETWEEN ? AND ?',
                                    (obvid, sd, ed,)):
        l.add(x[0])
    return [re_agent(x) for x in l]


def get_hyst_date(self, d=date.today()):
    nd = d + timedelta(days=1)
    c = _conn.cursor()
    for x in c.execute('SELECT * FROM jurnal WHERE mark_at BETWEEN ? AND ?', (str(d), str(nd))):
        r = REC(zip([i[0] for i in c.getdescription()], x))
        r.nume = self.re_agent(r.agent)
        r.post = self.re_obv(r.obv)
        yield r


def day_hyst(d=date.today()):
    c = _conn.cursor()
    sq = 'SELECT agent, obv, bifa, isday FROM jurnal WHERE mark_at=?'
    l = DL()
    for x in c.execute(sq,(str(d),)):
        rec = REC(zip([i[0] for i in c.getdescription()], x))
        l[rec.obv] = rec
    return l

def month_hyst(obv, d=date.today()):
    sd = str(date(d.year, d.month, 1))
    ed = str(date(d.year, d.month, monthrange(d.year, d.month)[1]))
    c = _conn.cursor()
    sq = 'SELECT agent, bifa, isday, hour, mark_at, obs, dispecer, _time FROM jurnal WHERE obv=? AND mark_at BETWEEN ? AND ?'
    l = DL()
    obvid = obv if type(obv) is int else obv.id
    for x in c.execute(sq, (obvid, sd, ed,)):
        rec = REC(zip([i[0] for i in c.getdescription()], x))
        rec.agent = re_agent(rec.agent)
        rec.mark_at = datetime.strptime(rec.mark_at, '%Y-%m-%d').date()
        l[rec.agent] = rec
    return l


def ignored():
    c = _conn.cursor()
    for x in c.execute('SELECT * FROM ignore'):
        yield REC(zip([i[0] for i in c.getdescription()], x))


def get_unmarked():
    c = _conn.cursor()
    dt = date.today()
    hh = datetime.now().hour
    ignore = [x.obv for x in ignored()]
    if hh < 6:
        sd = str(dt - timedelta(days=1))
        q = 'SELECT obv FROM jurnal WHERE mark_at=? AND hour > 1200 OR hour < 600 AND bifa > 0'
        lst = [x[0] for x in c.execute(q, (sd,)).fetchall()]
        q = 'SELECT obv FROM jurnal WHERE mark_at=? AND hour < 600 AND bifa > 0'
        lst.extend([x[0] for x in c.execute(q, (str(dt),)).fetchall()])
    elif 6 <= hh < 12:
        q = 'SELECT obv FROM jurnal WHERE mark_at=? AND hour BETWEEN 600 AND 1200 AND bifa > 0'
        lst = [x[0] for x in c.execute(q, (str(dt),)).fetchall()]
    else:
        q = 'SELECT obv FROM jurnal WHERE mark_at=? AND hour > 1200 AND bifa > 0'
        lst = [x[0] for x in c.execute(q, (str(dt),)).fetchall()]
    lst.extend(ignore)
    lst = [re_obv(x) for x in lst]
    return [x for x in get_lista_obiective() if x.encode('utf-8') not in lst]


def edit_post(o, mod):
    s = 'UPDATE obiectiv SET {} WHERE id={}'.format(','.join(['{}=?'.format(x) for x in mod.keys()]), o.id)
    _conn.cursor().execute(s, mod.values())


def del_post(o):
    s = 'INSERT INTO obiectiv_bk ({}) VALUES ({})'.format(','.join(o.keys()), ','.join(['?'] * len(o.keys())))
    _conn.cursor().execute(s, o.values())
    return _conn.cursor().execute('DELETE FROM obiectiv WHERE id=?', (o.id,))


def del_from_ignore_list(o):
    return _conn.cursor().execute('DELETE FROM ignore WHERE obv=?', (o.id,))


def add_to_ignore_list(o):
    return Ignore(obv=o.id, nume=o.nume).ins()


def cite_ignorate():
    return _conn.cursor().execute('SELECT count(*) FROM ignore').fetchone()[0]


def close():
    _conn.close()
