# -*- coding: UTF-8 -*-

import gtk
from pango import FontDescription
from gobject import timeout_add, source_remove
from datetime import datetime
from jsdb import Disp
from treecal import TreeCal
from context import env
from agenda import Uz4us
import context
import sys

# ăâîșțĂÂÎȘȚ

sys.stderr = open('.stderr', 'a')
sys.stdout = open('.stdout', 'a')


def resp_to_dialog(_, dlg, resp):
    dlg.response(resp)


def label_mod(l, col, font=False):
    l.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse(col))
    if font:
        l.modify_font(FontDescription(font))


def set_autocomp(entry, func, store):
    completion = gtk.EntryCompletion()
    entry.set_completion(completion)
    completion.set_model(store)
    completion.set_text_column(0)
    completion.set_inline_completion(True)
    completion.set_inline_selection(True)
    completion.set_match_func(func, 0)
    return entry


class Win:
    btlist = {}
    last_ord = 0
    timp = datetime.now()
    lock_status = gtk.Image()
    nb = gtk.Notebook()
    USER = None

    def exit(self, *arg):
        self.disp.save()
        source_remove(self.timer)
        source_remove(self.timer1)
        self.timer = self.timer1 = 0
        gtk.main_quit()

    def __init__(self, ):
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.connect('delete_event', self.exit)
        self.win.connect('key-press-event', self.on_key)
        self.win.set_default_size(1000, 680)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_title('Dispecerat')
        self.win.set_icon(gtk.gdk.pixbuf_new_from_file('agt.png'))
        self.win.set_border_width(0)

        self.disp = Disp()
        self.cal = TreeCal(self)
        self.agenda = Uz4us(self)
        self.mesaj = gtk.TextView()
        self.text_buff = self.mesaj.get_buffer()
        self.tag_redm = self.text_buff.create_tag(foreground='red')
        self.tag_bold = self.text_buff.create_tag("bold", weight=700, foreground='#038')
        self.tag_boldm = self.text_buff.create_tag(foreground='#038', font='Serif bold 12')

        self.tlabel = gtk.Label()
        self.hlabel = gtk.Label()
        context.USER = env.last_user
        self.userbt = gtk.Button(context.USER)
        self.userbt.connect('clicked', self.log_user)
        self.agtora = gtk.Label()
        label_mod(self.agtora, '#a04', 'Sans bold 16')
        label_mod(self.userbt.child, '#480', 'Serif bold 16')
        label_mod(self.tlabel, '#260', 'Serif bold 12')
        label_mod(self.hlabel, '#505a64', 'Serif bold 16')
        self.status = self.cal.status

        self.nb.connect('switch-page', self.on_nb_switch)
        self.agent_store = gtk.ListStore(str)
        # self.make_agent_store()
        self.meniu = gtk.MenuBar()
        self.make_menu()

        self.bt_tab = gtk.Table()
        self.bt_tab.set_homogeneous(True)
        self.bt_frame = gtk.ScrolledWindow()
        self.bt_frame.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.bt_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        self.win.add(self.lay())

        self.win.show_all()
        self.make_agent_store()
        self.timer = timeout_add(10000, self.update_time)
        self.timer1 = timeout_add(60000, self.check_unmark)
        self.check_unmark()
        self.update_time()

    def on_key(self, _, evt):
        if evt.keyval == 65307:
            self.exit()
        if evt.keyval == 104:
            self.disp.raport_html(10)
            self.set_status('Raport HTML generat!')
        return False

    def log_user(self, bt):
        dialog = gtk.MessageDialog(
            None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Dispecer:')
        store = gtk.ListStore(str)
        for n in self.agenda.dis:
            store.append([n])
        entry = gtk.combo_box_entry_new_with_model(store, 0)
        entry.child.set_text(env.last_user)
        entry.show_all()
        dialog.vbox.pack_end(entry, True, True, 0)
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.show_all()
        resp = dialog.run()
        text = unicode(entry.get_active_text())
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            if not text:
                return
            ou = context.USER
            context.USER = text
            env.last_user = text
            self.userbt.child.set_text(text)
            env.log('dispecer', 'old', ou, 'new', text)

    def set_obv_detail(self, o):
        self.agtora.set_text('')

        def retag():
            for x in xrange(0, 8, 2):
                buff.apply_tag(self.tag_bold, buff.get_iter_at_offset(l[x]), buff.get_iter_at_offset(l[x + 1]))

        def ln(tx):
            tx = unicode(tx)
            l.append(len(t) + len(tx))
            return tx

        l = []
        buff = self.text_buff
        t = ''
        t += ln(u'Post:\t')
        t += ln(o.nume)
        t += ln(u'\nObiectiv: ')
        t += ln(o.obv)
        t += ln(u'\nAdresă:\t')
        t += ln(o.adr)
        t += ln(u'\nOb. activitate:\t')
        t += ln(o.dest)
        t += ln(u'\nTelefon:\t\t')
        t += ln(o.tel)

        buff.set_text(t)
        retag()
        buff.apply_tag(self.tag_boldm, buff.get_iter_at_offset(l[8]), buff.get_iter_at_offset(l[9]))

    def toggled(self, bt, _):
        self.last_ord = bt.get_data('ord')
        self.cal.redraw(self.disp.pids[self.last_ord])
        self.set_obv_detail(self.disp.pids[self.last_ord])

    def make_btobv(self):
        hh = 0
        ww = 0
        for y in self.disp.posturi:
            bt = gtk.Button('')
            bt.connect('clicked', self.toggled, y.id)
            bt.child.set_text(y.nume)
            label_mod(bt.child, '#000', 'Segoe UI Semibold %s' % int(env.BT_FONT / 1000))
            self.bt_tab.attach(bt, hh, hh + 1, ww, ww + 1)
            bt.set_data('ord', y.id)
            hh += 1
            if hh % 3 == 0:
                hh = 0
                ww += 1
            self.btlist[y.nume] = bt
        self.bt_frame.add_with_viewport(self.bt_tab)
        self.bt_tab.set_data('hh', hh)
        self.bt_tab.set_data('ww', ww)
        self.btlist['Alison Hayes - Post 1'].emit('clicked')
        return self.bt_frame

    def on_nb_switch(self, _, g, pnum):
        if pnum == 0:
            self.cal.redraw(self.cal.current)
        elif pnum == 1:
            self.agenda.nb.set_current_page(-1)
        return

    def on_raport_html(self, _):
        dialog = gtk.MessageDialog(
            None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Raport HTML pentru luna:')
        v = gtk.VBox(False, 5)
        m_adj = gtk.Adjustment(0, 0, 12, 1, 10, 0)
        sp_m = gtk.SpinButton(m_adj, 1, 0)
        sp_m.set_numeric(True)
        sp_m.set_size_request(60, 27)
        h = gtk.HBox(False, 5)
        h.add(gtk.Label('Luna:'))
        h.pack_end(sp_m, False, True)
        v.add(h)
        dialog.format_secondary_markup("(<b>0</b> pentru luna <b>curentă</b>)")
        dialog.vbox.pack_end(v, True, True, 0)
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.show_all()
        resp = dialog.run()
        month = sp_m.get_value_as_int()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            self.disp.raport_html(month)
            self.set_status('Raport HTML generat!')

    def on_raport_excel(self, _):
        self.disp.raport_excel(True, self.cal.selected_date)
        self.set_status('Raport pentru luna %s generat!' % (env.lunA[self.timp.month]))

    def on_raport_excel_email(self, _):
        r = self.disp.raport_excel_email()
        self.set_status(r, '#b00') if r else self.set_status('Raport livrat la tehnic!')

    def on_raport_at_month(self, _):
        dialog = gtk.MessageDialog(
            None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Alegeți data')
        c = gtk.Calendar()
        dialog.vbox.pack_end(c)
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.show_all()
        resp = dialog.run()
        d = c.get_date()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            dt = datetime(d[0], d[1] + 1, d[2])
            self.disp.raport_excel(True, dt)
            self.set_status('Raport pentru luna %s generat!' % (env.lunA[d[1] + 1]))
            del dialog

    def on_edit_agt(self, _):
        if not self.cal.agent_selected or self.cal.agent_selected == -1:
            self.set_status('Selectați unul din agenții din obiective!', '#c00')
            return
        agt = self.disp.aids[self.cal.agent_selected]
        oa = agt.nume[:]
        dialog = gtk.MessageDialog(
            None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Modificați numele <b>agentului</b>:')
        dialog.set_position(gtk.WIN_POS_CENTER)
        eid = gtk.Entry()
        eid.set_text(str(agt.id))
        eid.set_size_request(80, -1)
        entry = gtk.Entry()
        entry.set_text(agt.nume)
        entry.connect("activate", resp_to_dialog, dialog, gtk.RESPONSE_OK)
        v = gtk.VBox(False, 5)
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(gtk.Label("Nume:"), False, True)
        hbox.pack_end(entry)
        v.add(hbox)
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(gtk.Label("ID:"), False, True)
        hbox.pack_end(eid, False, True)
        v.add(hbox)
        dialog.format_secondary_markup("<i>agent:</i> \n<b>%s</b>" % agt.nume)
        dialog.vbox.pack_end(v, True, True, 0)
        dialog.show_all()
        resp = dialog.run()
        text = entry.get_text()
        eid = eid.get_text()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            ret = self.disp.modify_agent(text, agt, self.cal.current)
            if ret == -2:
                self.set_status('Nume identic!')
                return
            elif ret == -3:
                self.set_status('S-a produs o eroare!')
                return
            self.cal.agent_selected = text
            self.toggled(self.btlist[self.cal.current.nume], self.last_ord)
            self.make_agent_store()
            env.log('mod_agent', oa, text, self.cal.current.nume)

    def on_del_obv(self, _):
        obv = self.cal.current
        dialog = gtk.MessageDialog(
            None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('<span color="#900"><u>Ștergeți</u></span> obiectiv <b>\n%s</b>?' % obv.nume)
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.show_all()
        resp = dialog.run()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            env.log('del_obiectiv', obv.nume)
            self.disp.del_post(obv)
            self.cal.redraw(self.disp.posturi[0])
            bt = self.btlist.pop(obv.nume)
            self.bt_tab.remove(bt)
            del obv

    def on_edit_obv(self, _):
        o = self.cal.current

        def lentry(txt, etxt=''):
            h = gtk.HBox(False, 5)
            l = gtk.Label(txt)
            e = gtk.Entry()
            if etxt:
                e.set_text(etxt)
            h.pack_start(l, False, True)
            h.pack_end(e, True, True)
            return h, e, l

        def hour_adj():
            m_adj = gtk.Adjustment(0, 0, 24, 1, 10, 0)
            sp_m = gtk.SpinButton(m_adj, 1, 0)
            sp_m.set_numeric(True)
            sp_m.set_size_request(40, 27)
            return sp_m

        def make_orar_tab():
            tab = gtk.Table()
            l = gtk.Label()
            l.set_markup('<b>Orar:</b>')
            tab.attach(l, 0, 1, 0, 1)
            l = gtk.Label()
            l.modify_font(FontDescription('Segoe UI Symbol 14'))
            l.set_markup('<span color="#080"><b>🔓</b></span>')
            tab.attach(l, 1, 2, 0, 1)
            l = gtk.Label()
            l.modify_font(FontDescription('Segoe UI Symbol 14'))
            l.set_markup('<span color="#800"><b>🔒</b></span>')
            tab.attach(l, 2, 3, 0, 1)
            k = 1
            ore = []
            for z in ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică']:
                l = gtk.Label(z)
                l.set_size_request(100, -1)
                tab.attach(l, 0, 1, k, k + 1)
                os, oe = hour_adj(), hour_adj()
                olds, olde = o.orar[str(k - 1)]
                if olds is None:
                    olds = 0
                if olde is None:
                    olde = 0
                os.set_value(olds)
                oe.set_value(olde)
                ore.append((os, oe))
                tab.attach(os, 1, 2, k, k + 1)
                tab.attach(oe, 2, 3, k, k + 1)
                k += 1
            return tab, ore

        v = gtk.VBox(False, 5)
        h, enume, _ = lentry('Nume:', o.nume)
        v.add(h)
        h, eadr, _ = lentry('Adresă:', o.adr)
        v.add(h)
        h, etel, _ = lentry('Telefon:', o.tel)
        v.add(h)
        h, edest, _ = lentry('Destinație:', o.dest)
        v.add(h)
        h, eobv, _ = lentry('Obiectiv:', o.obv)
        v.add(h)
        t, ore = make_orar_tab()
        v.add(t)

        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Editați <i>atributele</i> obiectivului')
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.format_secondary_markup('<b>%s</b>' % o.nume)
        dialog.vbox.pack_end(v, True, True, 0)
        dialog.show_all()
        oldtel = o.tel
        oldadr = o.adr
        olddest = o.dest
        oldlore = dict(enumerate(ore))
        oldobv = o.obv
        resp = dialog.run()
        tenume = unicode(enume.get_text())
        teadr = unicode(eadr.get_text())
        tetel = unicode(etel.get_text())
        tedest = unicode(edest.get_text())
        teobv = unicode(eobv.get_text())
        lore = {}
        for x in ore:
            lore[str(ore.index(x))] = (x[0].get_value_as_int(), x[1].get_value_as_int())
        old = o.nume
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:

            o = self.disp.pids[o.id]
            o.nume = tenume
            o.obv = teobv or False
            o.tel = tetel or False
            o.dest = tedest or False
            o.adr = teadr or False
            o.orar = lore
            l = []

            def app(lst):
                for x in lst:
                    l.append(str(x))

            app([old, o.nume])
            if oldtel != o.tel:
                app(['TEL', oldtel, o.tel])
            if oldadr != o.adr:
                app(['ADR', oldadr, o.adr])
            if olddest != o.dest:
                app(['DEST', olddest, o.dest])
            if oldlore != o.orar:
                app(['ORAR'])
            if oldobv != o.obv:
                app(['OBV', oldobv, o.obv])
            self.disp.modify_post(o, old)
            self.btlist[old].child.set_text(o.nume)
            self.btlist[o.nume] = self.btlist[old]
            del self.btlist[old]
            env.log('mod_obiectiv', *l)

    def on_add_obv(self, _):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Introduceți numele <i>noului</i> <b>obiectiv</b>:')
        dialog.set_position(gtk.WIN_POS_CENTER)
        entry = gtk.Entry()
        entry.connect("activate", resp_to_dialog, dialog, gtk.RESPONSE_OK)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Nume:"), False, 5, 5)
        hbox.pack_end(entry)
        # dialog.format_secondary_markup("Adăugți un <i>obiectiv</i> nou")
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        resp = dialog.run()
        text = entry.get_text().title()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            post = self.disp.add_post(text)
            self.cal.redraw(post)
            hh, ww = self.bt_tab.get_data('hh'), self.bt_tab.get_data('ww')
            if hh % 3 == 0:
                hh = 0
                ww += 1
            bt = gtk.Button('')
            bt.connect('clicked', self.toggled, post.id)
            bt.child.set_markup('<span size="%s">%s</span>' % (env.BT_FONT, post.nume))
            bt.child.modify_font(FontDescription('Calibri %s' % int(env.BT_FONT / 1000)))
            self.bt_tab.attach(bt, hh, hh + 1, ww, ww + 1)
            bt.set_data('ord', post.id)
            bt.show_all()
            self.bt_tab.show_all()
            self.bt_frame.show_all()
            self.bt_frame.set_size_request(-1, -1)
            self.btlist[post.nume] = bt
            env.log('add_obiectiv', text.title(), text)
            self.check_unmark()

    def on_add_agt(self, _):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Introduceți numele <b>agentului</b>:')
        dialog.set_position(gtk.WIN_POS_CENTER)
        entry = gtk.Entry()
        set_autocomp(entry, self.match, self.agent_store)
        entry.connect("activate", resp_to_dialog, dialog, gtk.RESPONSE_OK)
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("Nume:"), False, 5, 5)
        hbox.pack_end(entry)
        dialog.format_secondary_markup("Adăugți un <i>agent</i> la obiectivul\n<b>%s</b>" % self.cal.current.nume)
        dialog.vbox.pack_end(hbox, True, True, 0)
        dialog.show_all()
        resp = dialog.run()
        text = unicode(entry.get_text()).title()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            self.disp.add_agent_at(text, self.cal.current.id)
            if self.is_in_store(text):
                self.agent_store.append([text])
            self.toggled(self.btlist[self.cal.current.nume], self.last_ord)
            env.log('add agent', text, self.cal.current.nume)

    def on_del_agt(self, _):
        if not self.cal.agent_selected or self.cal.agent_selected == -1:
            self.set_status('Selectați unul din agenții din obiectiv!', '#c00')
            return
        agt = self.disp.aids[self.cal.agent_selected]
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_WARNING,
            gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Ștergeți agent <b>%s</b>?' % agt.nume)
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.show_all()
        resp = dialog.run()
        dialog.destroy()
        if resp == gtk.RESPONSE_OK:
            self.do_del_agent(agt)

    def on_raport_obiectiv(self, _):
        obv = self.cal.current
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Raport obiectiv:')
        dialog.set_position(gtk.WIN_POS_CENTER)
        v = gtk.VBox(False, 5)
        m_adj = gtk.Adjustment(0, 0, 12, 1, 10, 0)
        sp_m = gtk.SpinButton(m_adj, 1, 0)
        sp_m.set_numeric(True)
        sp_m.set_size_request(60, 27)
        h = gtk.HBox(False, 5)
        h.add(gtk.Label('Luna:'))
        h.pack_end(sp_m, False, True)
        v.add(h)

        h = gtk.HBox(False, 5)
        _adj = gtk.Adjustment(2017, 2017, 2030, 1, 10, 0)
        sp_y = gtk.SpinButton(_adj, 1, 0)
        sp_y.set_numeric(True)
        sp_y.set_size_request(60, 27)
        h.add(gtk.Label('Anul:'))
        h.pack_end(sp_y, False, True)
        v.add(h)

        v.add(gtk.Label('(0 pentru întreaga perioadă)'))
        dialog.format_secondary_markup("<b>{}</b>".format(obv.nume))
        dialog.vbox.pack_end(v, True, True, 0)
        dialog.show_all()
        resp = dialog.run()
        month = sp_m.get_value_as_int()
        year = sp_y.get_value_as_int()
        dialog.destroy()

        if resp == gtk.RESPONSE_OK:
            r = self.disp.raport_obiectiv(obv, year, month)
            if r == 0:
                self.set_status('Raport generat!')
            else:
                self.set_status('Err {}'.format(r), '#c00')
                raise ValueError('Err on_raport_obiectiv', r, obv.nume)

    def on_raport_agent(self, _):
        dialog = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK_CANCEL, None)
        dialog.set_alternative_button_order([gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK])
        dialog.set_default_response(2)
        dialog.set_markup('Raport <b>agent</b>:')
        dialog.set_position(gtk.WIN_POS_CENTER)
        entry = gtk.combo_box_entry_new_with_model(self.agent_store, 0)  # self.autocomp()  # gtk.Entry()
        # entry.set_model(self.agent_store)
        # entry.connect("activate", resp_to_dialog, dialog, gtk.RESPONSE_OK)
        set_autocomp(entry.child, self.match, self.agent_store)
        entry.show_all()
        v = gtk.VBox(False, 5)
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(gtk.Label("Nume:"), False, 5, 5)
        hbox.pack_end(entry)
        v.add(hbox)

        y_adj = gtk.Adjustment(2018, 2000, 2024, 1, 10, 0)
        sp_y = gtk.SpinButton(y_adj, 1, 0)
        sp_y.set_numeric(True)
        sp_y.set_size_request(60, 27)
        h = gtk.HBox(False, 5)
        h.pack_start(gtk.Label('An:'), False, True)
        h.pack_start(sp_y, False, True)

        m_adj = gtk.Adjustment(0, 0, 12, 1, 10, 0)
        sp_m = gtk.SpinButton(m_adj, 1, 0)
        sp_m.set_numeric(True)
        sp_m.set_size_request(60, 27)
        h.add(gtk.Label('Luna:'))
        h.pack_end(sp_m, False, True)
        v.add(h)
        v.add(gtk.Label('(0 pentru întreaga perioadă)'))
        # dialog.format_secondary_markup("Adăugți un <i>agent</i>")
        dialog.vbox.pack_end(v, True, True, 0)
        dialog.show_all()
        resp = dialog.run()
        # text = unicode(entry.get_text())
        text = unicode(entry.get_active_text())
        month = sp_m.get_value_as_int()
        year = sp_y.get_value_as_int()
        dialog.destroy()

        if resp == gtk.RESPONSE_OK:
            r = self.disp.raport_agent(unicode(text), month, year)
            if r == 0:
                self.set_status('Raport generat!')
            else:
                self.set_status('Err {}'.format(r), '#c00')
                raise ValueError('Err on_raport_agent', r, text)

    def make_msg_tab(self):
        def pack(txt, i):
            hb = gtk.HBox(False, 2)
            l = gtk.Label()
            l.set_markup('<span size="10000"><b>{}</b></span>'.format(txt))
            hb.add(i)
            hb.add(l)
            return hb

        v = gtk.VBox(False, 1)
        v.pack_start(self.agtora, False, True, 5)
        vv = gtk.HBox(True, 5)
        tooltips = gtk.Tooltips()

        pixbuf = env.IconTheme.load_icon("kuser", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
        img = gtk.Image()
        img.set_from_pixbuf(pixbuf)
        bt = gtk.Button()
        bt.connect('clicked', self.on_add_agt)
        bt.add(pack('Adaugă', img))
        tooltips.set_tip(bt, 'Adaugă un nou agent!')
        vv.add(bt)

        img = gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU)
        bt = gtk.Button()
        bt.connect('clicked', self.on_del_agt)
        tooltips.set_tip(bt, 'Șterge agentul selectat!')
        bt.add(pack('Șterge', img))
        vv.add(bt)

        pixbuf = env.IconTheme.load_icon("gnome-settings-theme", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
        img = gtk.Image()
        img.set_from_pixbuf(pixbuf)
        bt = gtk.Button()
        bt.connect('clicked', self.on_edit_agt)
        tooltips.set_tip(bt, 'Modifică numele\nagentului selectat!')
        bt.add(pack('Modifică', img))
        vv.add(bt)
        v.pack_start(vv, False, True)
        v.add(gtk.image_new_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size('agt.png', 64, 64)))

        self.mesaj.set_editable(False)
        self.mesaj.modify_font(FontDescription('Segoe UI 9'))
        self.mesaj.set_wrap_mode(gtk.WRAP_WORD)
        # self.mesaj.set_justification(gtk.JUSTIFY_CENTER)
        self.mesaj.set_cursor_visible(False)
        self.mesaj.set_left_margin(2)
        self.mesaj.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('#ddd'))
        self.mesaj.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#000'))
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.mesaj)
        self.mesaj.set_size_request(-1, 80)
        v.add(sw)
        v.pack_end(self.userbt, False, True)
        return v

    def clear_status(self):
        self.status.set_text('')
        self.status.modify_fg(gtk.STATE_ACTIVE, gtk.gdk.color_parse('#fff'))
        return False

    def set_status(self, msg, col='#fff', timeout=10000):
        self.status.set_text(msg)
        self.status.modify_fg(gtk.STATE_ACTIVE, gtk.gdk.color_parse(col))
        timeout_add(timeout, self.clear_status)

    def make_status(self):
        h = gtk.HBox(False, 2)
        btl = gtk.Button()
        btl.connect('clicked', self.lock)
        self.lock_status.set_from_pixbuf(env.lockRed)
        btl.add(self.lock_status)
        h.pack_end(btl, False, False)
        h.pack_end(self.hlabel, False, False)
        h.pack_end(self.tlabel, False, False)
        h.show_all()
        return h

    def update_time(self):
        self.timp = env.timp = self.cal.timp = self.disp.timp = datetime.now()
        self.disp.azi = self.timp.date()
        env.update()
        d = env.zero(self.timp.day)
        m = self.timp.month
        y = self.timp.year
        self.tlabel.set_text('%s, %s %s %s  ' % (env.zile[self.timp.weekday()], d, env.luna[m], y))
        h, m = env.zero(self.timp.hour), env.zero(self.timp.minute)
        self.hlabel.set_text('{}:{}'.format(h, m))

        return True

    def match(self, _, key, itr, col):
        txt = self.agent_store.get_value(itr, col)
        if txt:
            if key.lower() in txt.lower():
                return True
        return False

    def is_in_store(self, n):
        item = self.agent_store.get_iter_first()
        while item is not None:
            if self.agent_store.get_value(item, 0) == n:
                return True
            item = self.agent_store.iter_next(item)
        return False

    def do_del_agent(self, agt):
        self.disp.del_agent(agt, self.cal.current)
        env.log('del_agt', agt.nume, self.cal.current.nume)
        self.cal.redraw(self.cal.current)
        self.make_agent_store()
        self.check_unmark()
        del agt

    def make_agent_store(self):
        self.agent_store.clear()
        for item in self.disp.agenti:
            self.agent_store.append([item.nume])

    def lay(self):
        self.nb.set_tab_pos(gtk.POS_TOP)
        self.nb.popup_enable()
        self.nb.set_group_name('tab')
        self.nb.set_show_border(False)

        self.meniu.show_all()
        hhw = gtk.HBox(False, 5)
        hhw.add(self.meniu)
        hhw.add(gtk.Label(' Obiective'))
        hhw.show_all()

        sp = gtk.VPaned()
        v = gtk.VBox(False, 0)
        sp.add1(self.cal.frame)
        h = gtk.HBox(False, 1)
        h.pack_start(self.make_btobv(), True, True)
        h.pack_end(self.make_msg_tab(), False, True)
        v.add(h)
        sp.add2(v)
        sp.set_position(290)
        sp.set_name('Obiective')
        self.nb.append_page(sp, hhw)
        self.nb.set_menu_label_text(sp, 'Obiective')

        # self.nb.append_page(self.detal.frame, gtk.Label('Detalii'))
        self.nb.append_page(self.agenda.nb, self.make_status())
        self.nb.set_menu_label_text(self.agenda.nb, 'Diverse')

        return self.nb

    def do_save(self, _):
        self.disp.save()
        self.set_status('Date salvate!')

    def make_menu(self):
        def mk_filemenu():
            menu = gtk.Menu()
            fm = gtk.ImageMenuItem('File')
            fm.set_submenu(menu)
            img = gtk.image_new_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)
            fm.set_image(img)
            save = gtk.ImageMenuItem('Salvați')
            save.connect('activate', self.do_save)
            img = gtk.image_new_from_stock(gtk.STOCK_SAVE, gtk.ICON_SIZE_MENU)
            save.set_image(img)
            mexit = gtk.ImageMenuItem('Închide')
            mexit.connect('activate', self.exit)
            img = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
            mexit.set_image(img)
            menu.append(save)
            menu.append(mexit)
            return fm

        def mk_addmenu():
            menu = gtk.Menu()
            ad = gtk.ImageMenuItem('Post')
            ad.set_submenu(menu)
            img = gtk.image_new_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
            ad.set_image(img)

            ada = gtk.ImageMenuItem('Adaugă Agent')
            ada.connect('activate', self.on_add_agt)
            pixbuf = env.IconTheme.load_icon("kuser", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            # img = gtk.image_new_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_MENU)
            ada.set_image(img)

            adm = gtk.ImageMenuItem('Modifică Agent')
            adm.connect('activate', self.on_edit_agt)
            pixbuf = env.IconTheme.load_icon("gnome-settings-theme", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            # img = gtk.image_new_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_MENU)
            adm.set_image(img)

            add = gtk.ImageMenuItem('Șterge Agent')
            add.connect('activate', self.on_del_agt)
            img = gtk.image_new_from_stock(gtk.STOCK_CLEAR, gtk.ICON_SIZE_MENU)
            add.set_image(img)

            ado = gtk.ImageMenuItem('Adaugă Obiectiv')
            ado.connect('activate', self.on_add_obv)
            img = gtk.image_new_from_stock(gtk.STOCK_HOME, gtk.ICON_SIZE_MENU)
            # ado.set_sensitive(False)
            ado.set_image(img)

            admo = gtk.ImageMenuItem('Modifică Obiectiv')
            admo.connect('activate', self.on_edit_obv)
            pixbuf = env.IconTheme.load_icon("accessories-text-editor", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            # img = gtk.image_new_from_stock(gtk.STOCK_HOME, gtk.ICON_SIZE_MENU)
            # admo.set_sensitive(False)
            admo.set_image(img)

            addl = gtk.ImageMenuItem('Șterge Obiectiv')
            addl.connect('activate', self.on_del_obv)
            img = gtk.image_new_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_MENU)
            addl.set_image(img)
            # addl.set_sensitive(False)

            menu.append(ada)
            menu.append(adm)
            menu.append(add)
            menu.append(gtk.SeparatorMenuItem())
            menu.append(ado)
            menu.append(admo)
            menu.append(addl)
            return ad

        def mk_rapmenu():
            menu = gtk.Menu()
            rap = gtk.ImageMenuItem('Rapoarte')
            rap.set_submenu(menu)
            img = gtk.image_new_from_stock(gtk.STOCK_CONVERT, gtk.ICON_SIZE_MENU)
            rap.set_image(img)

            rxl = gtk.ImageMenuItem('Exportă raport Excel')
            rxl.connect('activate', self.on_raport_excel)
            img = gtk.image_new_from_stock(gtk.STOCK_JUSTIFY_RIGHT, gtk.ICON_SIZE_MENU)
            rxl.set_image(img)
            menu.append(rxl)

            rxl = gtk.ImageMenuItem('Raport Excel ⇨ tehnic')
            rxl.connect('activate', self.on_raport_excel_email)
            pixbuf = env.IconTheme.load_icon("gnome-stock-mail-fwd", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            rxl.set_image(img)
            menu.append(rxl)

            rxl = gtk.ImageMenuItem('Raport HTML')
            rxl.connect('activate', self.on_raport_html)
            pixbuf = env.IconTheme.load_icon("gnome-mime-text-html", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            rxl.set_image(img)
            menu.append(rxl)
            # todo: raport HTML
            rxl = gtk.ImageMenuItem('Raport pe luna...')
            rxl.connect('activate', self.on_raport_at_month)
            pixbuf = env.IconTheme.load_icon("x-office-document-template", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            rxl.set_image(img)
            # rxl.set_sensitive(False)
            menu.append(rxl)

            rxl = gtk.ImageMenuItem('Raport agent')
            rxl.connect('activate', self.on_raport_agent)
            pixbuf = env.IconTheme.load_icon("start-here", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            rxl.set_image(img)
            # rxl.set_sensitive(False)
            menu.append(rxl)

            rxl = gtk.ImageMenuItem('Raport Obiectiv')
            rxl.connect('activate', self.on_raport_obiectiv)
            pixbuf = env.IconTheme.load_icon("go-home", 24, gtk.ICON_LOOKUP_GENERIC_FALLBACK)
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            rxl.set_image(img)
            menu.append(rxl)

            return rap

        self.meniu.append(mk_filemenu())
        self.meniu.append(mk_addmenu())
        self.meniu.append(mk_rapmenu())

    def check_unmark(self):
        todaydata = self.disp.check_now()
        for x in self.btlist:
            if x in env.ignore:
                if x in todaydata:
                    todaydata.pop(todaydata.index(x))
                continue
            if x in todaydata:
                self.btlist[x].child.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#a04'))
                self.btlist[x].child.modify_fg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse('#f40'))
            else:
                self.btlist[x].child.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#000'))
                self.btlist[x].child.modify_fg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse('#360'))
        self.disp.save()
        self.cal.re_today(0)
        self.cal.redraw(self.cal.current)
        #print(gc.collect())
        return True

    def lock(self, _):
        self.cal.LOCKED = not self.cal.LOCKED
        if self.cal.LOCKED:
            self.lock_status.set_from_pixbuf(env.lockRed)
        else:
            self.lock_status.set_from_pixbuf(env.lockBlue)


w = Win()
gtk.main()
