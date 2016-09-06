from peewee import *
import datetime

import trackmac.config

db = SqliteDatabase(trackmac.config.TRACK_DB_FILE)


class BaseModel(Model):
    class Meta:
        database = db


class Application(BaseModel):
    app_name = CharField()
    tag_name = CharField(null=True)


class NormalTrackRecord(BaseModel):
    """
    Application records except for web browsers
    """
    app = ForeignKeyField(Application, related_name='normal_records')
    start_datetime = DateTimeField(default=datetime.datetime.now)
    end_datetime = DateTimeField(default=datetime.datetime.now)
    duration = IntegerField(default=1)
    is_current = BooleanField(default=True)


class WebTrackRecord(BaseModel):
    """
    Web browsers records
    """
    app = ForeignKeyField(Application, related_name='web_records')
    start_datetime = DateTimeField(default=datetime.datetime.now)
    end_datetime = DateTimeField(default=datetime.datetime.now)
    duration = IntegerField(default=1)
    title = CharField(null=True)  # can be null when web page not fully loaded
    url = CharField()
    is_current = BooleanField(default=True)


class BlockedApplication(BaseModel):
    """
    App not track
    """
    name = CharField()
