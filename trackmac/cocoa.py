#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ctypes
import ctypes.util
import trackmac.config

foundation = ctypes.cdll.LoadLibrary(ctypes.util.find_library('Foundation'))
core_foundation = ctypes.cdll.LoadLibrary(ctypes.util.find_library('CoreFoundation'))
appkit = ctypes.cdll.LoadLibrary(ctypes.util.find_library('AppKit'))
objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('objc'))
scripting_bridge = ctypes.cdll.LoadLibrary(ctypes.util.find_library('ScriptingBridge'))
service_management = ctypes.cdll.LoadLibrary(ctypes.util.find_library('ServiceManagement'))

objc.objc_getClass.argtypes = [ctypes.c_char_p]
objc.objc_getClass.restype = ctypes.c_void_p

objc.objc_msgSend.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
objc.objc_msgSend.restype = ctypes.c_void_p

objc.sel_registerName.argtypes = [ctypes.c_char_p]
objc.sel_registerName.restype = ctypes.c_void_p

objc.object_getClassName.argtypes = [ctypes.c_void_p]
objc.object_getClassName.restype = ctypes.c_char_p

CFStringCreateWithCString = core_foundation.CFStringCreateWithCString
CFStringCreateWithCString.restype = ctypes.c_void_p
CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32]


def memoize(function):
    memo = {}

    def wrapper(*args):
        if args in memo:
            return memo[args]
        else:
            memo[args] = function(*args)
            return memo[args]

    return wrapper


@memoize
def C(name):
    return objc.objc_getClass(name)


@memoize
def S(name):
    return objc.sel_registerName(name)


def send(obj, sel, param=None):
    """
    sends a message with a simple return value to an instance of a class.
    """
    objc.objc_msgSend.argtypes = [ctypes.c_void_p] * 3
    objc.objc_msgSend.restype = ctypes.c_void_p
    return objc.objc_msgSend(obj, sel, param)


def _convert_str_to_nsstring(str_):
    """
    Python string to NSString
    """
    return send(C(b'NSString'), S(b'stringWithUTF8String:'), ctypes.c_char_p(str_))


def _convert_nsstring_to_str(obj):
    """
    NSString to python string with utf8 encoded
    """
    return ctypes.string_at(send(obj, S(b'UTF8String')))


# def _convert_str_to_cfstring(s):
#     """
#     Python string to CFStringRef
#     """
#     kCFAllocatorDefault = ctypes.c_void_p()
#     kCFStringEncodingUTF8 = 0x08000100
#     return CFStringCreateWithCString(kCFAllocatorDefault,
#                                      s.encode('utf8'),
#                                      kCFStringEncodingUTF8)
#

class NSAutoreleasePool(object):
    """
    To prevent memory leakage
    """

    def __init__(self):
        self.pool = None
        self.drained = False

    def alloc(self):
        pool = send(C(b'NSAutoreleasePool'), S(b'alloc'))
        self.pool = send(pool, S(b'init'))

    def drain(self):
        if self.pool and not self.drained:
            send(self.pool, S(b'drain'))
            self.drained = True

    def __enter__(self):
        self.alloc()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.drain()

    def __del__(self):
        self.drain()


def frontmost_application():
    """
    get the front most application(now deprecated by apple)
    """
    ns_workspace = send(C(b'NSWorkspace'), S(b'sharedWorkspace'))
    active_application = send(ns_workspace, S(b'activeApplication'))
    ns_application_name_obj = send(active_application, S(b'valueForKey:'),
                               _convert_str_to_nsstring(b'NSApplicationName'))
    if ns_application_name_obj:
        return _convert_nsstring_to_str(ns_application_name_obj)
    else:
        return None


def current_tab(brower_name):
    """
    get the current active tab
    """
    broswer_specifics = trackmac.config.BROWSERS[brower_name]
    chrome = send(C(b'SBApplication'), S(b'applicationWithBundleIdentifier:'),
                  _convert_str_to_nsstring(broswer_specifics['bundle_id']))
    windows = send(chrome, S(b'windows'))
    count = send(windows, S(b'count'))
    if count > 0:
        front_window = send(windows, S(b'objectAtIndex:'), 0)
        active_tab = send(front_window, S(broswer_specifics['tab']))
        title_obj = send(active_tab, S(broswer_specifics['title']))
        url_obj = send(active_tab, S(broswer_specifics['url']))
        # must check title and url is not none!
        if title_obj and url_obj:
            title = _convert_nsstring_to_str(title_obj)
            url = _convert_nsstring_to_str(url_obj)
            return title, url
    return None, None


def daemon_status(label):
    """
    get current launchd job exit status
    """
    SMJobCopyDictionary = service_management.SMJobCopyDictionary
    SMJobCopyDictionary.restype = ctypes.c_void_p
    SMJobCopyDictionary.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    # toll-free bridged so no need converting
    job_dict = SMJobCopyDictionary(service_management.kSMDomainUserLaunchd, _convert_str_to_nsstring(label))
    return job_dict is None
    # arr = send(des_dict, S('allKeys'))
    # count = send(arr, S('count'))
    # print [_convert_nsstring_to_str(send(arr, S('objectAtIndex:'), i)) for i in range(count)]
    # send(job_dict, S('valueForKey:'), _convert_str_to_nsstring('LastExitStatus')) == 55
