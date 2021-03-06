import os
import sys
import math
from cudatext import *
import cudatext as ct
from os.path import getctime
from datetime import datetime as dt

PATH = os.path.join(app_path(APP_DIR_DATA), 'scratches') + os.sep

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
    items_ = ''
    for item in items:
        preview = ''
        with open(item, 'r') as f:
            preview = f.readline()
            for i in range(4):
                preview = preview + ' ' + f.readline()
        preview = preview.replace("\n", '', 5)
        items_ = items_ + os.path.basename(item) + ' | ' + dt.fromtimestamp(getctime(item)).strftime('%Y-%m-%d %H:%M:%S') + ' | ' + convert_size(os.path.getsize(item)) + "\t" + preview + "\n"

    return items, items_

class Command:
    def __init__(self):
        if (not os.path.exists(PATH)):
            try:
                os.mkdir(PATH)
            except OSError as err:
                msg_box("Cannot create dir 'data/scratches', OS error: {0}".format(err), MB_OK+MB_ICONERROR)
                raise

    def get_w_h(self):
        w_ = 600
        h_ = 600
        screen_sizes = app_proc(PROC_COORD_MONITOR, 0)
        if screen_sizes:
            w_ = round(screen_sizes[2] / 2)
            h_ = round(screen_sizes[3] / 3)

        return w_, h_

    def new(self):
        items = ct.lexer_proc(ct.LEXER_GET_LEXERS, False)
        items.insert(0, 'PLAIN TEXT')
        res = dlg_menu(DMENU_LIST, items, 0, 'New scratch')
        if (res == None):
            return

        prop = ct.lexer_proc(ct.LEXER_GET_PROP, items[res])
        if (res == 0):
            ext = 'txt'
        else:
            ext = prop.get('typ')[0]

        def getFname(i):
            return PATH + 'scratch_' + str(i) + '.' + ext

        i = 1
        fname = getFname(i)
        while (os.path.exists(fname)):
            i = i + 1
            fname = getFname(i)

        try:
            ff = open(fname, 'w')
            file_open(fname)
        except OSError as err:
            msg_box("OS error: {0}".format(err), MB_OK)
            raise

    def list(self):
        items, items_ = get_files_list(self)
        if (len(items) > 0):
            res = dlg_menu(DMENU_LIST_ALT, items_, 0, 'List of scratches', CLIP_RIGHT, self.get_w_h()[0], self.get_w_h()[1])
            if (res != None):
                file_open(items[res])
        else:
            msg_status('No scratches found')

    def remove(self):
        items, items_ = get_files_list(self)
        if (len(items) > 0):
            res = dlg_menu(DMENU_LIST_ALT, items_, 0, 'Remove scratch', CLIP_RIGHT, self.get_w_h()[0], self.get_w_h()[1])
            if (res != None):
                res_ = msg_box('Do you really want to remove scratch?', MB_YESNO+MB_ICONQUESTION)
                if res_ == ID_YES:
                    try:
                        os.remove(items[res])
                        msg_box('Removed scratch: ' + os.path.basename(items[res]), MB_OK)
                    except:
                        msg_status('Cannot delete: ' + os.path.basename(items[res]))
        else:
            msg_status('No scratches found')
