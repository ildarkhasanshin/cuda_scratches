import os
import sys
import math
from cudatext import *
import cudatext as ct
from os.path import getctime
from datetime import datetime as dt

from cudax_lib import get_translation
_ = get_translation(__file__)  # I18N

PATH = os.path.join(app_path(APP_DIR_DATA), 'scratches')

def convert_size(size_bytes):
    size_bytes = int(size_bytes)
    if size_bytes == 0:
        return '0 b'
    size_name = ('b', 'kB', 'mB', 'gB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return str("%s %s" % (s, size_name[i]))

def get_files_list(self):
    items = sorted([os.path.join(PATH, i) for i in os.listdir(PATH)], key = os.path.getmtime, reverse = True)
    items = [i for i in items if os.path.isfile(i)]
    items_ = ''
    for item in items:
        preview = ''
        with open(item, 'r', encoding='utf-8') as f:
            preview = f.readline()
            for i in range(4):
                preview = preview + ' ' + f.readline()
        preview = preview.replace("\n", '', 5)
        items_ = items_ + os.path.basename(item) + ' | ' + dt.fromtimestamp(getctime(item)).strftime('%Y-%m-%d %H:%M:%S') + ' | ' + convert_size(os.path.getsize(item)) + "\t" + preview + "\n"

    return items, items_

class Command:
    def __init__(self):
        if not os.path.isdir(PATH):
            try:
                os.mkdir(PATH)
            except OSError as err:
                msg_box(_("Cannot create folder 'data/scratches', OS error: {0}").format(err), MB_OK+MB_ICONERROR)
                raise

    def get_w_h(self):
        w_ = 600
        h_ = 600
        r = app_proc(PROC_COORD_MONITOR, 0)
        if r:
            w_ = (r[2]-r[0]) // 2
            h_ = (r[3]-r[1]) // 3

        return w_, h_

    def new(self):
        items = ct.lexer_proc(ct.LEXER_GET_LEXERS, False)
        items.insert(0, _('PLAIN TEXT'))
        res = dlg_menu(DMENU_LIST, items, 0, _('New scratch'))
        if res is None:
            return

        prop = ct.lexer_proc(ct.LEXER_GET_PROP, items[res])
        if res == 0:
            ext = 'txt'
        else:
            ext = prop.get('typ')[0]

        def get_f_name(i):
            return os.path.join(PATH, 'scratch_' + str(i) + '.' + ext)

        i = 1
        fname = get_f_name(i)
        while os.path.isfile(fname):
            i += 1
            fname = get_f_name(i)

        try:
            ff = open(fname, 'w', encoding='utf-8')
            file_open(fname)
        except OSError as err:
            msg_box(_("OS error: {0}").format(err), MB_OK)
            raise

    def list(self):
        items, items_ = get_files_list(self)
        if len(items) > 0:
            w, h = self.get_w_h()
            res = dlg_menu(DMENU_LIST_ALT, items_, 0, _('List of scratches'), clip=CLIP_RIGHT, w=w, h=h)
            if res is not None:
                file_open(items[res])
        else:
            msg_status(_('No scratches found'))

    def remove(self):
        items, items_ = get_files_list(self)
        if len(items) > 0:
            w, h = self.get_w_h()
            res = dlg_menu(DMENU_LIST_ALT, items_, 0, _('Remove scratch'), clip=CLIP_RIGHT, w=w, h=h)
            if res is not None:
                res_ = msg_box(_('Do you really want to remove scratch?'), MB_YESNO+MB_ICONQUESTION)
                if res_ == ID_YES:
                    try:
                        os.remove(items[res])
                        msg_box(_('Removed scratch: ') + os.path.basename(items[res]), MB_OK)
                    except:
                        msg_status(_('Cannot delete: ') + os.path.basename(items[res]))
        else:
            msg_status(_('No scratches found'))
