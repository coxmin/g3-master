# -*- coding: UTF-8 -*-
from re import sub

from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

im_ico = Gtk.Image.new_from_icon_name


def set_autocomp(entry, func, store):
    completion = Gtk.EntryCompletion()
    entry.set_completion(completion)
    completion.set_model(store)
    completion.set_text_column(0)
    completion.set_inline_completion(True)
    completion.set_inline_selection(True)
    completion.set_match_func(func, 0)
    return entry


def format_tel(tel):
    tel = sub(r'\D', '', tel)
    # if not tel.startswith('0'):tel = '0{}'.format(tel)
    return '{}-{}-{}'.format(tel[:-6], tel[-6:-3], tel[-3:])


def zero(n):
    return '0{}'.format(n) if -1 < n < 10 else n

def mcls(w, c):
    [bt.get_style_context().add_class(cls) for bt, cls in zip(w, c)]


def toggle(bt, isday):
    (switch(bt, 'npt', 'nptcheck') if isday else switch(bt, 'czi', 'czicheck')) if bt.on else (
        switch(bt, 'nptcheck', 'npt') if isday else switch(bt, 'czicheck', 'czi'))


def switch(bt, cls, newcls):
    bt.get_style_context().remove_class(cls)
    bt.get_style_context().add_class(newcls)


def hour_spin():
    m_adj = Gtk.Adjustment(0, 0, 24, 1, 10, 0)
    sp_m = Gtk.SpinButton()
    sp_m.set_adjustment(m_adj)
    sp_m.set_numeric(True)
    sp_m.set_property('width-chars', 1)
    sp_m.set_property('max-width-chars', 2)
    return sp_m


def pentry(l, txt):
    h = Gtk.HBox(False, 2)
    e = Gtk.Entry()
    e.set_placeholder_text(txt)
    h.add(Gtk.Label(l))
    h.add(e)
    return h, e


def lentry(l, txt):
    h = Gtk.HBox(False, 2)
    e = Gtk.Entry()
    e.set_text(txt)
    h.add(Gtk.Label(l))
    h.add(e)
    return h, e


def l90(txt='', cls=''):
    b = Gtk.Button(txt)
    b.get_child().set_angle(90)
    b.get_style_context().add_class(cls)
    b.on = 0
    return b


def fhour(h):
    t = '00{}'.format(h)
    return '{}:{}'.format(t[-4:-2], t[-2:])


def imgbt(txt='', img=False, sz=32, cls='', bind=''):
    b = Gtk.Button()
    b.connect('clicked', bind)
    if img:
        h = Gtk.HBox(False, 0)
        h.add(Gtk.Label(txt))
        h.add(img if type(img) is Gtk.Image else Gtk.Image.new_from_pixbuf(Pixbuf.new_from_file_at_size(img, sz, sz)))
        b.add(h)
    else:
        b.add(Gtk.Label(txt))
    b.get_style_context().add_class(cls)
    return b

