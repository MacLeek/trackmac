# -*- coding: utf-8 -*-
import os

VERSION = '0.0.6'
TRACK_SCRIPT = 'tm'
TRACK_DAEMON = 'trackmac_service'
TRACK_DIR = os.path.expanduser('~/Library/Application Support/com.github.macleek.trackmac/')
TRACK_DB_FILE = TRACK_DIR + 'track.db'
TRACK_LOG_FILE = TRACK_DIR + 'track.log'
TRACK_PLIST_NAME = 'com.github.macleek.trackmac.plist'
USER_LAUNCHAGENTS_DIR = os.path.expanduser('~/Library/LaunchAgents')
BROWSERS = {
    'Google Chrome': {
        'bundle_id': 'com.google.Chrome',
        'tab': 'activeTab',
        'title': 'title',
        'url': 'URL'
    },
    'Safari': {
        'bundle_id': 'com.apple.Safari',
        'tab': 'currentTab',
        'title': 'name',
        'url': 'URL'
    }
}
