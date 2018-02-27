# -*- coding: UTF-8 -*-
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.GObject import timeout_add, source_remove
import sq
import uz
from calendar import monthrange
from datetime import datetime, date, timedelta
from re import sub


class REC(dict):
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)


def get_last_user():
    with open('.conf/usr', 'r') as f: W._var.USER = f.read()
    return W._var.USER


def set_last_user(u):
    W._var.USER = u
    with open('.conf/usr', 'w') as f: f.write(W._var.USER)


class W:
    aaa = 0
    _ui = REC({'mesaj': Gtk.Label('status OK'), 'selected_date': Gtk.Label(), 'post': Gtk.Label(), 'date': Gtk.Label(),
               'time': Gtk.Label(), 'post_grid': Gtk.Grid(), 'ctx_menu': Gtk.Menu(), 'grid': Gtk.Grid(),
               'LOCK': Gtk.Image()})
    _var = REC({'col_hi': 0, 'row_hi': 0,
                'dispecer': ['Ana-Maria', 'Georgiana', 'Cosmin', 'Valentina'],
                'zile': ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică'],
                'months': ['', 'Ian', 'Feb', 'Mar', 'Apr', 'Mai', 'Iun', 'Iul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                'USER': ''})
    _seldt = date.today()
    _time = datetime.now()
    _obiective = []
    _crt_post_id = 0
    __LOCKED = True
    _ui.LOCK.set_from_pixbuf(Pixbuf.new_from_file_at_size('img/lock.png', 24, 24))
    _mark_bt = {}
    _check_bt = {}
    _agenti = []
    _agent_store = Gtk.ListStore(str)
    _obv_store = Gtk.ListStore(str)
    temp_timer = 0

    @staticmethod
    def _test(*arg):
        print(arg)

    def dialog(self, box, txt1='', txt2=''):
        dialog = Gtk.MessageDialog(self.win,
                                   Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT | Gtk.DialogFlags.USE_HEADER_BAR,
                                   Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL, None)
        dialog.set_alternative_button_order_from_array([Gtk.ResponseType.CANCEL, Gtk.ResponseType.OK])
        dialog.set_default_response(2)
        if txt1:
            dialog.set_markup(txt1)
        if txt2:
            dialog.format_secondary_markup(txt2)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        dialog.vbox.pack_end(box, True, True, 0)
        dialog.show_all()
        return dialog

    def do_w_post(self, p):
        b = uz.imgbt(txt=p.nume, cls='obvbutton', bind=self.on_post_select)
        b._id = p.id
        self._ui.post_grid.attach(b, self._obiective.index(p) % 3, int(self._obiective.index(p) / 3), 1, 1)

    def _make_post_box(self):
        self._obiective = sorted([x for x in sq.posturi()], key=lambda k: k.nume.encode('utf-8'))
        [self._ui.post_grid.remove(x) for x in self._ui.post_grid.get_children()]
        map(self.do_w_post, self._obiective)
        self._ui.post_grid.show_all()
        self._ui.post_grid.get_child_at(0, 0).emit('clicked')

    def _make_layout(self):
        vb = Gtk.VBox
        h, hh, hstat = Gtk.HBox(False, 2), Gtk.HBox(False, 5), Gtk.HBox(False, 5)
        vr, sw, v, pan = vb(False, 5), Gtk.ScrolledWindow(hexpand=True, vexpand=True), vb(False, 0), vb(False, 3)
        e = Gtk.EventBox()
        self._make_post_box()
        h.pack_start(self._ui.post_grid, True, True, 0)
        bt = uz.imgbt(get_last_user(), 'img/dispecer.png', sz=24, cls='dispecer', bind=self.on_switch_user)
        vr.pack_start(Gtk.Image.new_from_pixbuf(Pixbuf.new_from_file_at_size('img/info.png', 44, 44)), False, True, 0)
        vr.pack_start(self.detView, True, True, 0)
        vr.pack_end(bt, False, True, 0)
        h.pack_end(vr, False, False, 0)
        sw.set_shadow_type(Gtk.ShadowType.OUT)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.EXTERNAL)
        sw.set_size_request(-1, 250)
        self._ui.grid.set_row_homogeneous(False)
        self._ui.grid.set_column_homogeneous(False)
        self._ui.grid.set_column_spacing(2)
        self._ui.grid.set_row_spacing(5)
        sw.add(self._ui.grid)
        hh.pack_start(self.meniu, False, True, 0)
        backbt = uz.imgbt(img=uz.im_ico('media-seek-backward', Gtk.IconSize.LARGE_TOOLBAR), bind=self.date_prev)
        hh.pack_start(backbt, False, True, 0)
        uz.mcls((backbt, self._ui.selected_date, self._ui.post), ('navbt', 'navlab', 'navlabb'))
        hh.pack_start(self._ui.selected_date, False, True, 0)
        backbt = uz.imgbt(img=uz.im_ico('media-seek-forward', Gtk.IconSize.LARGE_TOOLBAR), cls='navbt',
                       bind=self.date_next)
        hh.pack_start(backbt, False, True, 0)
        backbt = uz.imgbt(img=uz.im_ico('media-playback-stop', Gtk.IconSize.LARGE_TOOLBAR), cls='navbt',
                       bind=self.date_today)
        hh.pack_start(backbt, False, True, 0)
        hh.pack_end(self._ui.post, False, True, 10)
        v.pack_start(hh, False, False, 0)
        v.pack_end(sw, True, True, 0)
        pan.add(v)
        pan.add(h)
        lbt = uz.imgbt(img=self._ui.LOCK, cls='lock', bind=self.lock)
        hstat.pack_start(self._ui.mesaj, True, True, 0)
        hstat.pack_end(self._ui.time, False, True, 0)
        hstat.pack_end(self._ui.date, False, True, 0)
        hstat.pack_end(lbt, False, True, 0)
        e.add(hstat)
        e.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('#aaa'))
        pan.pack_end(e, False, True, 0)
        return pan

    def _update_tree_head(self):
        def do_w(x):
            dd = (d1 + x - 1) % 7
            l, ll, e, h = Gtk.Label(str(x)), Gtk.Label('LMMJVSD'[dd]), Gtk.EventBox(), Gtk.VBox(False, 0)
            h.add(l)
            h.add(ll)
            e.add(h)
            e.connect('button-press-event', self.on_day_highlight, x)
            e.get_style_context().add_class('hday')
            self._ui.grid.attach(e, x, 0, 1, 1)
            uz.mcls((l, ll), ('azi', 'aziday')) if x == today else uz.mcls((l, ll), cls[dd])

        self._ui.grid.remove_row(0)
        self._ui.grid.insert_row(0)
        h = Gtk.HBox(False, 0)
        b = uz.imgbt(img=Gtk.Image.new_from_pixbuf(Pixbuf.new_from_file_at_size('img/agent.png', 32, 32)), cls='htree',
                  bind=self.set_get_method)
        l = Gtk.Label('Agent')
        l.get_style_context().add_class('htree')
        h.pack_start(b, False, True, 0)
        h.add(l)
        self._ui.grid.attach(h, 0, 0, 1, 1)
        yy, mm = self._seldt.year, self._seldt.month
        d1, today = date(yy, mm, 1).weekday(), self._time.day
        cls = [('day', 'dayday'), ('day', 'dayday'), ('day', 'dayday'), ('day', 'dayday'), ('day', 'dayday'),
               ('samb', 'sambday'), ('dumi', 'dumiday')]
        map(do_w, xrange(1, monthrange(self._seldt.year, self._seldt.month)[1] + 1))

    def _update_tree(self):
        def vbt(m, n):
            h = Gtk.HBox(True, 0)
            bt = self._mark_bt[self._agenti[n - 1]][0][m - 1] = uz.l90('00:00', 'czi')
            bt.connect('button-press-event', self.on_context, m, self._agenti[n - 1], 0)
            h.pack_start(bt, False, True, 0)
            bt = self._mark_bt[self._agenti[n - 1]][1][m - 1] = uz.l90(cls='npt')
            bt.connect('button-press-event', self.on_context, m, self._agenti[n - 1], 1)
            h.pack_end(bt, False, True, 0)
            h.set_tooltip_markup('\t<b>{} - {}</b>\n{}'.format(m, self._var.months[seldt.month], self._agenti[n - 1]))
            return h

        def days(x):
            vv = Gtk.VBox(True, 2)
            [vv.add(vbt(x, y)) for y in xrange(1, nr_agenti + 1)]
            self._ui.grid.attach(vv, x, 1, 1, nr_agenti)

        self._mark_bt, self._check_bt, seldt = {}, {}, self._seldt
        [self._ui.grid.remove_row(1) for _ in xrange(1, len(self._agenti) + 1)]
        self._agenti = self._get_agent(self._crt_post_id, seldt)
        nr_agenti = len(self._agenti)
        if nr_agenti == 0: return
        data = sq.month_hyst(self._crt_post_id, seldt)
        end_month = monthrange(seldt.year, seldt.month)[1]
        hh = self._time.hour
        c_isday = 1 if hh < 6 else 0 if 6 <= hh < 12 else 0
        check_dt = seldt - timedelta(days=1) if hh < 6 else seldt
        check = False
        if self._time.year == seldt.year and self._time.month == seldt.month:
            check = True
        for x in xrange(nr_agenti):
            bt = self._check_bt[self._agenti[x]] = Gtk.CheckButton(self._agenti[x])
            bt.set_size_request(200, -1)
            bt.get_style_context().add_class('cbox')
            self._ui.grid.attach(bt, 0, x + 1, 1, 1)
            self._mark_bt[self._agenti[x]] = {0: [0] * end_month, 1: [0] * end_month}

        map(days, xrange(1, end_month + 1))
        self._ui.grid.get_child_at(seldt.day, 1).get_style_context().add_class('selday')
        for x in data:
            for rec in data[x]:
                isday = 1 if rec.hour < 600 else 0 if 600 <= rec.hour < 1200 else 1
                bt = self._mark_bt[x][isday][rec.mark_at.day - 1]
                if rec.bifa == 0:
                    uz.switch(bt, 'nptcheck', 'npt') if isday else uz.switch(bt, 'czicheck', 'czi')
                    continue
                bt.get_child().set_text(uz.fhour(rec.hour))
                bt.on = 1
                uz.switch(bt, 'npt', 'nptcheck') if isday else uz.switch(bt, 'czi', 'czicheck')
                if check and rec.mark_at == check_dt and rec.isday == c_isday:
                    self._check_bt[x].set_active(True)
        if check:
            map(lambda x: self._check_bt[self._agenti[x]].connect('toggled', self.on_agent_toggled, x),
                xrange(nr_agenti))
        self._ui.grid.show_all()

    def highlight_row(self, agt):
        if self._var.row_hi:
            [x.get_style_context().remove_class('hilightrow') for x in self._mark_bt[self._var.row_hi][0]]
            [x.get_style_context().remove_class('hilightrow') for x in self._mark_bt[self._var.row_hi][1]]
        self._var.row_hi = agt
        [x.get_style_context().add_class('hilightrow') for x in self._mark_bt[agt][0]]
        [x.get_style_context().add_class('hilightrow') for x in self._mark_bt[agt][1]]

    def update_time(self):
        self._time = datetime.now()
        self._ui.date.set_text('{}, {}-{}-{}'.format(self._var.zile[self._time.weekday()], self._time.day,
                                                     self._var.months[self._time.month], self._time.year))
        self._ui.time.set_text('{}:{}'.format(uz.zero(self._time.hour), uz.zero(self._time.minute)))
        return self.timer

    def update_post_info(self):
        o = sq.get_obv_by_id(self._crt_post_id)
        self.headbar.props.title = o.obv
        l, t = [], ''
        tx = [unicode(x) for x in (
            u'Post:\t', o.nume, u'\n\nObiectiv:\t', o.obv, u'\n\nAdresă:\t', o.adr, u'\n\nStatus:\t', o.stat,
            u'\n\nTelefon:\t', o.tel)]
        for x in tx:
            l.append(len(x) + len(t))
            t += x
        self.detBuffer.set_text(t)
        for x in xrange(0, 8, 2):
            self.detBuffer.apply_tag(self.tag_bold, self.detBuffer.get_iter_at_offset(l[x]),
                                     self.detBuffer.get_iter_at_offset(l[x + 1]))
        self.detBuffer.apply_tag(self.tag_boldm, self.detBuffer.get_iter_at_offset(l[8]),
                                 self.detBuffer.get_iter_at_offset(l[9]))

    def set_get_method(self, _):
        if self._get_agent == sq.get_agenti_at_obv:
            self._get_agent = sq.get_agenti_at_date
        else:
            self._get_agent = sq.get_agenti_at_obv
        self._update_tree()

    def on_post_select(self, bt):
        self._ui.post.set_text(bt.get_child().get_text().decode('utf-8'))
        self._crt_post_id = bt._id
        self._var.row_hi = 0
        self.update_post_info()
        self.reprint_selcted()

    def on_unignore(self, _):
        def _match(_, key, itr, col):
            txt = store.get_value(itr, col)
            if txt:
                if key.lower() in txt.lower():
                    return True
            return False

        store = Gtk.ListStore(str)
        [store.append([item.nume]) for item in sq.ignored()]
        e = Gtk.Entry()
        uz.set_autocomp(e, _match, store)
        dialog = self.dialog(e, 'Șterge obiectiv din lista',
                             'celor cu orar ignorat\n( <b>{} obiective</b>)'.format(sq.cite_ignorate()))
        resp = dialog.run()
        nume = e.get_text().decode('utf-8')
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            ob = sq.Obiectiv(nume=nume).g()
            if sq.del_from_ignore_list(ob):
                self._ui.mesaj.set_text('Obv. {} eliminat din ignorate'.format(nume.encode('utf-8')))
                self.check_unmark()

    def on_ignore(self, _):
        def _match(_, key, itr, col):
            txt = self._obv_store.get_value(itr, col)
            if txt:
                if key.lower() in txt.lower():
                    return True
            return False

        e = Gtk.Entry()
        uz.set_autocomp(e, _match, self._obv_store)
        dialog = self.dialog(e, 'Adaugă obiectiv la lista', 'celor cu orar ignorat')
        resp = dialog.run()
        nume = e.get_text().decode('utf-8')
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            ob = sq.Obiectiv(nume=nume).g()
            if sq.add_to_ignore_list(ob):
                self._ui.mesaj.set_text('Obv. {} „ignorat”'.format(nume.encode('utf-8')))
                self.check_unmark()

    def on_key_press(self, _, evt):
        if evt.keyval == 65307: self._exit(0)

    def on_obv_add(self, _):
        v = Gtk.VBox(False, 3)
        h, nume = uz.pentry('Nume:', 'numele obiectivului')
        v.add(h)
        h, adr = uz.pentry('Adresă:', 'adresa obiectivului')
        v.add(h)
        h, tel = uz.pentry('Telefon:', 'număr de telefon')
        v.add(h)
        h, dest = uz.pentry('Destinație:', 'utilitatea')
        v.add(h)
        h, ob = uz.pentry('Obiectiv:', 'obiectivul principal')
        v.add(h)
        h, obs = uz.pentry('Obs.:', 'observații')
        v.add(h)
        g, k, ors, ore, l = Gtk.Grid(), 1, [], [], Gtk.Label()
        l.set_markup('<span color="#080" size="18000"><b>🔓</b></span>')
        g.attach(l, 3, 0, 1, 1)
        l = Gtk.Label()
        l.set_markup('<span color="#800" size="18000"><b>🔒</b></span>')
        g.attach(l, 4, 0, 1, 1)
        for zi in self._var.zile:
            g.attach(Gtk.Label(zi), 0, k, 2, 1)
            g.attach(Gtk.Label('  '), 2, k, 1, 1)
            os, oe = uz.hour_spin(), uz.hour_spin()
            ors.append(os)
            ore.append(oe)
            g.attach(os, 3, k, 1, 1)
            g.attach(oe, 4, k, 1, 1)
            k += 1
        v.add(g)
        dlg = self.dialog(v, '<b>Adaugă</b> obiectiv nou')
        dlg.set_border_width(5)
        resp = dlg.run()
        nume, adr, tel, dest, ob, obs = nume.get_text().decode('utf-8').title(), adr.get_text().decode(
            'utf-8'), uz.format_tel(
            tel.get_text()), dest.get_text().decode('utf-8'), ob.get_text().decode('utf-8'), obs.get_text().decode(
            'utf-8')
        ors = ','.join([str(x.get_value_as_int()) for x in ors])
        ore = ','.join([str(x.get_value_as_int()) for x in ore])
        dlg.destroy()
        if resp == Gtk.ResponseType.OK:
            sq.Obiectiv(nume=nume, adr=adr, stat=dest, tel=tel, obv=ob, orars=ors, orare=ore).ins()
            self._make_post_box()
            try:
                ix = self._obiective.index([x for x in self._obiective if x.nume == nume][0])
                self._ui.post_grid.get_child_at(ix % 3, int(ix) / 3).emit('clicked')
            except:
                pass

    def on_obv_edit(self, _):
        ob = sq.get_obv_by_id(self._crt_post_id)
        (h, nume), v = uz.pentry('Nume:', 'numele obiectivului'), Gtk.VBox(False, 3)
        nume.set_text(ob.nume)
        v.add(h)
        h, adr = uz.pentry('Adresă:', 'adresa obiectivului')
        adr.set_text(ob.adr)
        v.add(h)
        h, tel = uz.pentry('Telefon:', 'număr de telefon')
        tel.set_text(ob.tel)
        v.add(h)
        h, dest = uz.pentry('Destinație:', 'utilitatea')
        dest.set_text(ob.stat)
        v.add(h)
        h, obv = uz.pentry('Obiectiv:', 'obiectivul principal')
        obv.set_text(ob.obv)
        v.add(h)
        h, obs = uz.pentry('Obs.:', 'observații')
        obs.set_text(ob.obs or '')
        v.add(h)
        g, l, k, ors, ore = Gtk.Grid(), Gtk.Label(), 1, [], []
        oras, orae = [int(x) for x in ob.orars.split(',')], [int(x) for x in ob.orare.split(',')]
        l.set_markup('<span color="#080" size="18000"><b>🔓</b></span>')
        g.attach(l, 3, 0, 1, 1)
        l = Gtk.Label()
        l.set_markup('<span color="#800" size="18000"><b>🔒</b></span>')
        g.attach(l, 4, 0, 1, 1)
        for zi in self._var.zile:
            g.attach(Gtk.Label(zi), 0, k, 2, 1)
            g.attach(Gtk.Label('  '), 2, k, 1, 1)
            os, oe = uz.hour_spin(), uz.hour_spin()
            os.set_value(oras[k - 1])
            oe.set_value(orae[k - 1])
            ors.append(os)
            ore.append(oe)
            g.attach(os, 3, k, 1, 1)
            g.attach(oe, 4, k, 1, 1)
            k += 1
        v.add(g)
        dlg = self.dialog(v, 'Modifică obiectivul', '<b>{}</b>'.format(ob.nume.encode('utf-8')))
        dlg.set_border_width(5)
        resp = dlg.run()
        nume, adr, tel, dest, obv, obs = nume.get_text().decode('utf-8').title(), adr.get_text().decode('utf-8'), sub(
            r'\D', '', tel.get_text()), dest.get_text().decode('utf-8'), obv.get_text().decode(
            'utf-8'), obs.get_text().decode('utf-8')
        ors = ','.join([str(x.get_value_as_int()) for x in ors])
        ore = ','.join([str(x.get_value_as_int()) for x in ore])
        dlg.destroy()
        if resp == Gtk.ResponseType.OK:
            o = sq.Obiectiv(nume=nume, adr=adr, stat=dest, tel=tel, obv=obv, obs=obs, orars=ors, orare=ore)
            mod = REC()
            for x in ob.keys():
                if x in ['_time', 'id']: continue
                if ob[x] != o[x]:
                    mod[x] = o[x]
            if len(mod) < 1: return
            sq.edit_post(ob, mod)
            self._make_post_box()

    def on_obv_del(self, _):
        ob = sq.get_obv_by_id(self._crt_post_id)
        dialog = self.dialog(Gtk.Label(), 'Sigur ștergeți obiectivul', '<b>{}</b>?'.format(ob.nume.encode('utf-8')))
        resp = dialog.run()
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            sq.del_post(ob)
            self._ui.mesaj.set_text('Obiectiv „{}” șters!'.format(ob.nume.encode('utf-8')))
            self._make_post_box()

    def on_agent_add(self, bt):
        def _match(_, key, itr, col):
            txt = self._agent_store.get_value(itr, col)
            if txt:
                if key.lower() in txt.lower():
                    return True
            return False

        box = Gtk.VBox(False, 5)
        h, nume = uz.pentry('Nume', 'numele agentului')
        uz.set_autocomp(nume, _match, self._agent_store)
        box.add(h)
        h, tel = uz.pentry('Tel.:', 'telefon')
        box.add(h)
        dialog = self.dialog(box, 'Adaugă agent la obiectiv', '<b>{}</b>'.format(sq.re_obv(self._crt_post_id)))
        resp = dialog.run()
        nume = nume.get_text().decode('utf-8').title()
        tel = tel.get_text()
        if tel: tel = uz.format_tel(tel)
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            if not nume: return
            agent = sq.Agent(nume=nume, tel=tel)
            a = agent.g()
            if a is None:
                agent.id = agent.ins()
                a = agent
            sq.add_at_obv(a.id, self._crt_post_id)
            self._update_tree()

    def on_agent_mod(self, bt):
        if not self._var.row_hi:
            return self.err_mesaj('<b>Selectați un agent!</b>')
        agent = sq.Agent(nume=self._var.row_hi.decode('utf-8')).g()
        box = Gtk.VBox(False, 5)
        h, nume = uz.lentry('Nume', agent.nume)
        box.add(h)
        h, tel = uz.lentry('Tel.:', agent.tel or '')
        box.add(h)
        box.add(Gtk.Label('Adăugat la: {}'.format(agent._time)))
        dialog = self.dialog(box, 'Modifică agent <b>{}</b> (id:{}):'.format(self._var.row_hi, agent.id),
                             '(Obiectiv: <b>{}</b>)'.format(sq.re_obv(self._crt_post_id)))
        resp = dialog.run()
        nume = nume.get_text().decode('utf-8')
        tel = tel.get_text()
        if tel: tel = uz.format_tel(tel)
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            if not nume: return
            if sq.mody_agent(agent, nume.title(), tel) == -1:
                self.err_mesaj('Numele <b>{}</b> deja există!'.format(nume.title().encode('utf-8')),
                               'Introduceti unul nou')
            self.date_today('')

    def on_agent_del(self, _):
        if not self._var.row_hi:
            return self.err_mesaj('<b>Selectați un agent!</b>')
        agent = sq.Agent(nume=self._var.row_hi.decode('utf-8')).g()
        dialog = self.dialog(Gtk.Label(), 'Sigur ștergeți <b>{}</b>'.format(agent.nume.encode('utf-8')),
                             'de la obiectiv <b>{}</b>'.format(sq.re_obv(self._crt_post_id)))
        resp = dialog.run()
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            sq.del_agent(agent, self._crt_post_id)
            self._var.row_hi = 0
            self._update_tree()

    def on_switch_user(self, bt):
        store = Gtk.ListStore(int, str)
        entry = Gtk.ComboBox.new_with_model_and_entry(store)
        entry.set_entry_text_column(1)
        map(lambda n: store.append([self._var.dispecer.index(n), n]), self._var.dispecer)
        dialog = self.dialog(entry, 'Dispecer:')
        resp = dialog.run()
        text = unicode(entry.get_children()[0].get_text())
        dialog.destroy()
        if resp == Gtk.ResponseType.OK:
            if not text: return
            set_last_user(text)
            bt.get_child().get_children()[0].set_text(self._var.USER)

    def on_context(self, bt, evt, dt, agt, isday):
        if evt.button == 3:
            self._ui.ctx_menu.popup(None, None, None, None, evt.button, evt.time)
        elif evt.button == 1:
            if self.__LOCKED:
                self._ui.mesaj.set_text('{} {}-{} ({}) - {}'.format(agt, dt, self._var.months[self._seldt.month],
                                                                    'noapte' if isday else 'zi',
                                                                    self._mark_bt[agt][isday][
                                                                        dt - 1].get_child().get_text()))
            else:
                bt.on = not bt.on
                hh = 1900 if isday else 700
                bifa = isday + 2 if bt.on else 0
                self.mark(agt, date(self._seldt.year, self._seldt.month, dt), hh, isday, bifa)
        self.highlight_row(agt)

    def on_day_highlight(self, wgt, evt, x):
        [self._mark_bt[self._agenti[a]][0][self._var.col_hi].get_style_context().remove_class('hilight') for a in
         xrange(len(self._agenti))]
        [self._mark_bt[self._agenti[a]][1][self._var.col_hi].get_style_context().remove_class('hilightr') for a in
         xrange(len(self._agenti))]
        [self._mark_bt[self._agenti[a]][0][x - 1].get_style_context().add_class('hilight') for a in
         xrange(len(self._agenti))]
        [self._mark_bt[self._agenti[a]][1][x - 1].get_style_context().add_class('hilightr') for a in
         xrange(len(self._agenti))]
        self._var.col_hi = x - 1

    def mark(self, agt, dt, hh, isday, bifa):
        o = REC({'agent': sq.Agent(nume=agt.decode('utf-8')).g().id, 'obv': self._crt_post_id,
                 'dispecer': self._var.dispecer.index(self._var.USER), 'bifa': bifa, 'hour': hh, 'mark_at': str(dt),
                 'isday': isday})
        uz.toggle(self._mark_bt[agt][isday][dt.day - 1], isday)
        self._mark_bt[agt][isday][dt.day - 1].get_child().set_text(uz.fhour(hh))
        sq.mark_object(o)

    def on_agent_toggled(self, bt, xx):
        hh = self._time.hour * 100 + self._time.minute
        dt = date.today() - timedelta(days=1) if hh < 600 else date.today()
        isday = 1 if hh < 600 else 0 if 600 <= hh < 1200 else 1
        bifa = isday + 1 if bt.get_active() else 0
        self._mark_bt[self._agenti[xx]][isday][dt.day - 1].on = bifa
        self.mark(self._agenti[xx], dt, hh, isday, bifa)
        self.highlight_row(self._agenti[xx])
        self.check_unmark()

    def _exit(self, *_):
        source_remove(self.timer)
        source_remove(self.check_timer)
        if self.temp_timer:
            source_remove(self.temp_timer)
        self.timer = self.temp_timer = self.check_timer = 0
        sq.close()
        Gtk.main_quit()

    def check_unmark(self):
        hh = self._time.hour
        c_isday = 1 if hh < 6 else 0 if 6 <= hh < 12 else 1
        check_dt = (self._time - timedelta(days=1)).date() if hh < 6 else self._time.date()
        hyst = sq.day_hyst(check_dt)
        unch = [x.id for x in self._obiective if x.id not in hyst]
        for o in hyst:
            bif = False
            for rec in hyst[o]:
                if rec.isday == c_isday and rec.bifa > 0:
                    bif = True
                    break
            if not bif:
                unch.append(o)
        lst = sorted([sq.re_obv(x) for x in unch])
        [x.get_style_context().add_class('destructive-action') for x in self._ui.post_grid.get_children() if
         x.get_child().get_text() in lst]
        [x.get_style_context().remove_class('destructive-action') for x in self._ui.post_grid.get_children() if
         x.get_child().get_text() not in lst]
        return self.check_timer

    @staticmethod
    def mk_meniu(ttl, lst):
        menu = Gtk.Menu()
        fm = Gtk.MenuItem.new_with_label(ttl)
        fm.set_submenu(menu)
        for nume, bind, ico in lst:
            if ico:
                sub = Gtk.MenuItem()
                box = Gtk.HBox(False, 0)
                box.pack_start(uz.im_ico(ico, Gtk.IconSize.MENU), False, False, 0)
                box.pack_end(Gtk.Label(nume), False, False, 0)
                sub.add(box)
            else:
                sub = Gtk.MenuItem.new_with_label(nume)
            sub.connect('activate', bind)
            menu.append(sub)
        return fm

    def __init__(self):
        self.win = Gtk.Window()
        self.win.set_double_buffered(True)
        self.win.connect('destroy', self._exit)
        self.win.connect('key-press-event', self.on_key_press)
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.set_icon_from_file('img/dispa.png')

        self.headbar = Gtk.HeaderBar()
        self.headbar.set_show_close_button(True)
        self.headbar.props.title = 'Dispecerat'
        self.headbar.props.subtitle = 'Dispecerat'
        self.headbar.set_has_subtitle(True)
        self.headbar.set_decoration_layout('close,minimize:icon')
        self.win.set_titlebar(self.headbar)

        self.detView = Gtk.TextView()
        self.detBuffer = self.detView.get_buffer()

        self.meniu = Gtk.MenuBar()
        self.meniu.append(self.mk_meniu('Meniu', [('Salvează', self.do_save, 'document-save'),
                                                  ('Închide', self._exit, "window-close")]))
        self.meniu.append(self.mk_meniu('Obiective', [('Adaugă', self.on_obv_add, 'list-add'),
                                                      ('Modifică', self.on_obv_edit, 'document-open'),
                                                      ('Șterge', self.on_obv_del, 'list-remove'),
                                                      ('Ignoră', self.on_ignore, 'edit-delete'),
                                                      ('Nu ignora', self.on_unignore, 'edit-clear')]))
        self.meniu.append(self.mk_meniu('Agenți', [('Adaugă', self.on_agent_add, 'face-smile'),
                                                   ('Modifică', self.on_agent_mod, 'face-surprise'),
                                                   ('Șterge', self.on_agent_del, 'face-uncertain')]))
        self.meniu.append(
            self.mk_meniu('Rapoarte',
                          [('Adaugă', self._test, 0), ('Modifică', self._test, 0), ('Șterge', self._test, 0)]))
        self.meniu.append(
            self.mk_meniu('Utile', [('Telefoane', self._test, 0), ('Ture', self._test, 0), ('Auto', self._test, 0)]))
        self.meniu.show_all()

        m = Gtk.MenuItem('Detalii')
        m.show_all()
        m.connect('activate', self._test)
        self._ui.ctx_menu.append(m)
        m = Gtk.MenuItem('Modifică')
        m.connect('activate', self._test)
        self._ui.ctx_menu.append(m)
        m.show_all()

        uz.mcls((self._ui.time, self._ui.date, self._ui.mesaj, self.detView),
                    ('timp', 'date', 'statbar', 'txtinfo'))
        self.detView.set_size_request(250, -1)
        self.detView.set_left_margin(5)
        self.detView.set_right_margin(5)
        self.detView.set_editable(False)
        self.detView.set_sensitive(False)
        self.tag_redm = self.detBuffer.create_tag(foreground='red')
        self.tag_bold = self.detBuffer.create_tag("bold", foreground='#000', font='Sans bold 10')
        self.tag_boldm = self.detBuffer.create_tag(foreground='#083', font='Serif bold 12', justification=1)
        self.detView.set_justification(Gtk.Justification.FILL)
        self.detView.set_wrap_mode(Gtk.WrapMode.WORD)
        self._ui.post_grid.set_row_spacing(3)
        self._ui.post_grid.set_column_spacing(3)
        self._get_agent = sq.get_agenti_at_date
        self._update_tree_head()
        self.win.add(self._make_layout())
        self.win.show_all()
        self.timer = timeout_add(10000, self.update_time)
        self.check_timer = timeout_add(60000, self.check_unmark)
        self.update_time()
        self.check_unmark()
        map(lambda x: self._agent_store.append([x.nume]), sq.agenti())
        map(lambda x: self._obv_store.append([x.nume]), sq.posturi())

    def do_save(self, *arg):
        print(arg)

    def lock(self, _):
        self.__LOCKED = not self.__LOCKED
        self._ui.LOCK.set_from_pixbuf(
            Pixbuf.new_from_file_at_size('img/lock.png', 24, 24)) if self.__LOCKED else self._ui.LOCK.set_from_pixbuf(
            Pixbuf.new_from_file_at_size('img/unlock.png', 24, 24))

    def reprint_selcted(self):
        self._ui.selected_date.set_text('{}, {}'.format(self._var.months[self._seldt.month], self._seldt.year))
        self._var.row_hi = 0
        self._update_tree()

    def date_next(self, _):
        self._seldt = self._seldt + timedelta(days=monthrange(self._seldt.year, self._seldt.month)[1])
        self._update_tree_head()
        self.reprint_selcted()

    def date_prev(self, _):
        self._seldt = self._seldt - timedelta(days=monthrange(self._seldt.year, self._seldt.month)[1])
        self._update_tree_head()
        self.reprint_selcted()

    def date_today(self, _):
        self._seldt = date.today()
        self._update_tree_head()
        self.reprint_selcted()
        self.check_unmark()

    def err_mesaj(self, txt, txt2=''):
        dialog = self.dialog(Gtk.Label(), txt, txt2)
        dialog.run()
        dialog.destroy()


with open('main_css.css', 'r')as f:
    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(f.read())
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, 600)
sq.init()
W()
Gtk.main()
