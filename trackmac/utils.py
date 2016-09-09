# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import shutil
import datetime
from subprocess import Popen, PIPE

import trackmac.config


def generate_plist(install_base_dir):
    """
    generate a plist file under current folder
    """
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    plist_file = os.path.join(trackmac.config.TRACK_DIR, trackmac.config.TRACK_PLIST_NAME)
    with open(plist_file, 'w') as f:
        f.write("<?xml version=""1.0"" encoding=""UTF-8""?>\n")
        f.write("<!DOCTYPE plist PUBLIC ""-//Apple//DTD PLIST 1.0//EN"" ""http://www.apple.com/DTDs/PropertyList-1.0.dtd"">\n")
        f.write("<plist version=""1.0"">\n")
        f.write("    <dict>\n")
        f.write("        <key>Label</key>\n")
        f.write("        <string>{}</string>\n".format(trackmac.config.TRACK_PLIST_NAME[:-6]))
        f.write("        <key>ProgramArguments</key>\n")
        f.write("        <array>\n")
        f.write("        <string>{}/{}</string>\n".format(install_base_dir, trackmac.config.TRACK_DAEMON))
        f.write("        </array>\n")
        f.write("        <key>KeepAlive</key>\n")
        f.write("        <true/>\n")
        f.write("        <key>RunAtLoad</key>\n")
        f.write("        <true/>\n")
        f.write("   </dict>\n")
        f.write("</plist>\n")


def load_or_unload_daemon(cmd):
    """
    load or unload daemon by using command :launchctl load ... / launchctl unload ...
    Can also use objc calls
    """
    p = Popen(['launchctl', cmd, trackmac.config.TRACK_PLIST_NAME], cwd=trackmac.config.USER_LAUNCHAGENTS_DIR,
              stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    return err.strip() or 'trackmac daemon {}ed.'.format(cmd)


def has_set_up():
    """
    if  has been set up
    """
    plist_file = os.path.join(trackmac.config.USER_LAUNCHAGENTS_DIR, trackmac.config.TRACK_PLIST_NAME)
    return os.path.exists(trackmac.config.TRACK_DIR) and os.path.exists(plist_file)


def create_dir():
    """
    creating dir to save log and sqlite dbfile.
    """
    if not os.path.exists(trackmac.config.TRACK_DIR):
        os.makedirs(trackmac.config.TRACK_DIR)
        open(trackmac.config.TRACK_LOG_FILE, 'a').close()
        print('writing {}'.format(trackmac.config.TRACK_LOG_FILE))


def remove_all_files():
    """
    remove save log, sqlite dbfile and .plist.
    """
    shutil.rmtree(trackmac.config.TRACK_DIR)
    print('Removing {}'.format(trackmac.config.TRACK_DIR))
    plist_file = os.path.join(trackmac.config.USER_LAUNCHAGENTS_DIR, trackmac.config.TRACK_PLIST_NAME)
    print('Removing {}'.format(plist_file))
    os.remove(plist_file)


def create_database():
    """
    create tables.
    """
    import peewee
    import trackmac.models
    if not os.path.isfile(trackmac.config.TRACK_DB_FILE):
        db = peewee.SqliteDatabase(trackmac.config.TRACK_DB_FILE)
        db.create_tables(
            [trackmac.models.Application, trackmac.models.NormalTrackRecord, trackmac.models.WebTrackRecord,
             trackmac.models.BlockedApplication], safe=True)
        print('Creating database...')


def symlink_and_load_plist():
    """
    symlink plist and load at once.
    """
    src = os.path.join(trackmac.config.TRACK_DIR, trackmac.config.TRACK_PLIST_NAME)
    dest = os.path.join(trackmac.config.USER_LAUNCHAGENTS_DIR, trackmac.config.TRACK_PLIST_NAME)
    try:
        os.symlink(src, dest)
        print('Installing {} to {} via symlink'.format(src, trackmac.config.USER_LAUNCHAGENTS_DIR))
    except Exception as e:
        print('Exception making symlink %s -> %s: %s' % (src, dest, e))
    else:
        load_or_unload_daemon('load')


def get_start_date_for_period(period):
    """
    get start date for different params.
    """
    now = datetime.datetime.now()
    day = now.day
    month = now.month
    year = now.year

    if period == 'day':
        start_time = now.date()
    elif period == 'week':
        start_time = datetime.date(year, month, day) - datetime.timedelta(days=now.weekday())
    elif period == 'month':
        start_time = datetime.date(year, month, 1)
    elif period == 'year':
        start_time = datetime.date(year, 1, 1)
    else:
        raise ValueError('Unsupported period value: {}'.format(period))

    return start_time


def get_progress(iteration, total, prefix='', suffix='', barLength=30):
    """
    get progress bar for showing.
    """
    percents = "{0:.1f}".format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '█' * filledLength
    return '{} {} {}%'.format(prefix, bar, percents)


def format_timedelta(seconds):
    """
    return a string roughly representing a timedelta.
    """
    neg = seconds < 0
    seconds = abs(seconds)
    total = seconds
    stems = []

    if total >= 3600:
        hours = seconds // 3600
        stems.append('{}h'.format(hours))
        seconds -= hours * 3600

    if total >= 60:
        mins = seconds // 60
        stems.append('{:02}m'.format(mins))
        seconds -= mins * 60

    stems.append('{:02}s'.format(seconds))

    return ('-' if neg else '') + ' '.join(stems)


def style(name, element):
    """
    different styles for showing.
    """
    def _style_tags(tags):
        if not tags:
            return ''

        return '[{}]'.format(', '.join(
            style('tag', tag) for tag in tags
        ))

    def _style_short_id(id):
        return style('id', id[:7])

    formats = {
        'project': {'fg': 'magenta'},
        'tags': _style_tags,
        'tag': {'fg': 'blue'},
        'time': {'fg': 'green'},
        'error': {'fg': 'red'},
        'date': {'fg': 'yellow'},
        'short_id': _style_short_id,
        'id': {'fg': 'white'}
    }

    fmt = formats.get(name, {})

    if isinstance(fmt, dict):
        import click
        return click.style(element, **fmt)
    else:
        # The fmt might be a function if we need to do some computation
        return fmt(element)


def is_chinese(uchar):
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def fill_text_to_print_width(text, width):
    """
    for aligning...
    """
    cn_count = 0
    for u in text:
        if is_chinese(u):
            cn_count += 1
    return " " * (width - cn_count - len(text)) + text
