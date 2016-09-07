#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging
import datetime

from peewee import *

import trackmac.config
import trackmac.cocoa
from trackmac.models import Application, NormalTrackRecord, WebTrackRecord, BlockedApplication


class TimeTracking(object):
    def __init__(self, **kwargs):
        """
        basic config
        """

    def start(self):
        """
        Start tracking active application or active browser tab in while loop
        """
        with trackmac.cocoa.NSAutoreleasePool():
            while True:
                try:
                    app_name = trackmac.cocoa.frontmost_application()
                    if app_name and app_name.decode('utf8') not in self.black_list:
                        cur_app, created = Application.get_or_create(app_name=app_name)
                        if app_name not in trackmac.config.BROWSERS.keys():
                            WebTrackRecord.update(is_current=False).where(WebTrackRecord.is_current == True).execute()
                            record_set = NormalTrackRecord.select().where(NormalTrackRecord.is_current == True)
                            if record_set.exists():
                                old_rec = record_set[0]
                                now = datetime.datetime.now()
                                # time delay or stopped for some time (1.5s is very inaccurate.)
                                if old_rec.app != cur_app or (now - old_rec.end_datetime).total_seconds() > 1.5:
                                    old_rec.is_current = False
                                    NormalTrackRecord(app=cur_app).save()
                                else:
                                    old_rec.end_datetime = now
                                    old_rec.duration = (old_rec.end_datetime - old_rec.start_datetime).total_seconds()
                                old_rec.save()
                            else:
                                NormalTrackRecord(app=cur_app).save()
                        else:
                            NormalTrackRecord.update(is_current=False).where(NormalTrackRecord.is_current == True).execute()
                            title, url = trackmac.cocoa.current_tab(app_name)
                            # title can be null
                            if url:
                                record_set = WebTrackRecord.select().where(WebTrackRecord.is_current == True)
                                if record_set.exists():
                                    old_rec = record_set[0]
                                    old_rec.end_datetime = datetime.datetime.now()
                                    old_rec.duration = (old_rec.end_datetime - old_rec.start_datetime).total_seconds()
                                    if old_rec.url != url:
                                        old_rec.is_current = False
                                        WebTrackRecord(app=cur_app, url=url, title=title).save()
                                    else:
                                        # sometime web pages not loaded at start due to network lag
                                        old_rec.title = title
                                    old_rec.save()
                                else:
                                    WebTrackRecord(app=cur_app, url=url, title=title).save()
                        time.sleep(1)
                except Exception as e:
                    logging.exception("Error occurred")
                    # normally exiting while loop
                    break

    def report(self, start, end, group_by_field):
        """
        get all application records from start to end group by `app_name` or `tag_name`
        """
        group_by_field = getattr(Application, group_by_field)
        records_n = NormalTrackRecord.select(fn.SUM(NormalTrackRecord.duration).alias('duration'), group_by_field). \
            where((NormalTrackRecord.start_datetime >= start) & (NormalTrackRecord.start_datetime <= end)).join(
            Application).group_by(group_by_field).dicts()
        records_w = WebTrackRecord.select(fn.SUM(WebTrackRecord.duration).alias('duration'), group_by_field). \
            where((WebTrackRecord.start_datetime >= start) & (WebTrackRecord.start_datetime <= end)).join(
            Application).group_by(group_by_field).dicts()
        rec_list = [r for r in records_n] + [r for r in records_w]
        # It's weird
        # map(lambda x:x.update({'duration':int((x['duration']-datetime.datetime.fromtimestamp(0)). \
        # total_seconds())}), rec_list)
        return rec_list

    def web_report(self, start, end):
        """
        get all web browsing records from start to end group by url's domain name
        """
        records = WebTrackRecord.select(fn.SUM(WebTrackRecord.duration).alias('duration'),
                                        fn.Substr(WebTrackRecord.url, 1, fn.Instr(
                                            fn.Substr(WebTrackRecord.url, 9), '/') + 8).alias('domain')). \
            where((WebTrackRecord.start_datetime >= start) & (WebTrackRecord.start_datetime <= end)).join(
            Application).group_by(SQL('domain')).order_by(WebTrackRecord.duration.desc()).dicts()
        return records

    @property
    def black_list(self):
        """
        names of all blocked apps
        """
        black_list = [n[1] for n in BlockedApplication.select().tuples()]
        return black_list

    def block(self, name, flag=True):
        """
        block a application from being tracked and delete all existing track records
        """
        if flag:
            q = Application.select().where(Application.app_name == name)
            num_of_rows = q.count()
            if num_of_rows == 0:
                return False
                # elif num_of_rows > 1:
                #     return num_of_rows, u'Found {}.Please use specify the right one.'.format(",".join([x.app_name for x in q]))
            # delete related records first
            WebTrackRecord.delete().where(WebTrackRecord.app_id == q[0].id).execute()
            NormalTrackRecord.delete().where(NormalTrackRecord.app_id == q[0].id).execute()
            Application.delete().where(Application.app_name % name).execute()
            BlockedApplication.get_or_create(name=q[0].app_name)
            return True
        else:
            return BlockedApplication.delete().where(name == name).execute() > 0

    def add_tag(self, tag_name, app_name):
        """
        add tag for the specified application
        """
        app_set = Application.select().where(Application.app_name == app_name)
        if app_set.exists():
            app = app_set[0]
            app.tag_name = tag_name
            app.save()
            return True
        else:
            return False

    @property
    def tags(self):
        """
        current added tags and related apps
        """
        apps_set = Application.select(fn.Group_concat(Application.app_name).alias("app_names"),
                                      Application.tag_name).where(Application.tag_name.is_null(False)).\
                                      group_by(Application.tag_name).dicts()
        return apps_set

    @property
    def is_not_running(self):
        return trackmac.cocoa.daemon_status(trackmac.config.TRACK_PLIST_NAME[:-6].encode("utf8"))


def main():
    TimeTracking().start()


if __name__ == '__main__':
    main()
