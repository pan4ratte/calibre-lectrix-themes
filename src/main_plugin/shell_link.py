# Reads and changes the icon of a Windows shortcut (.lnk) in place, through the shell's
# IShellLinkW and IPersistFile, with ctypes. calibre's own shortcut helper makes shortcuts
# afresh, which would drop what a pinned shortcut keeps to group calibre's windows under it.
# Windows only.

import ctypes
from ctypes import HRESULT, POINTER, byref, c_int, c_uint, c_ulong, c_void_p, wintypes

ole32 = ctypes.windll.ole32
shell32 = ctypes.windll.shell32


class GUID(ctypes.Structure):
    _fields_ = [('Data1', wintypes.DWORD), ('Data2', wintypes.WORD), ('Data3', wintypes.WORD), ('Data4', ctypes.c_ubyte * 8)]


def guid(text):
    g = GUID()
    ole32.CLSIDFromString(text, byref(g))
    return g


CLSID_SHELL_LINK = guid('{00021401-0000-0000-C000-000000000046}')
IID_SHELL_LINK_W = guid('{000214F9-0000-0000-C000-000000000046}')
IID_PERSIST_FILE = guid('{0000010B-0000-0000-C000-000000000046}')
CLSCTX_INPROC_SERVER = 1
STGM_READWRITE = 2
MAX_PATH = 1024

# Places in the interfaces' tables of methods.
QUERY_INTERFACE, RELEASE = 0, 2
LINK_GET_PATH, LINK_GET_ICON_LOCATION, LINK_SET_ICON_LOCATION = 3, 16, 17
FILE_LOAD, FILE_SAVE = 5, 6


def method(obj, index, restype, *argtypes):
    "A COM method of an interface pointer, by its place in the table."
    table = ctypes.cast(obj, POINTER(POINTER(c_void_p)))[0]
    fn = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)(table[index])
    return lambda *args: fn(obj, *args)


class ShellLink:
    "A shortcut file, open for reading and changing. Use with `with`."

    def __init__(self, path):
        self.path = path
        self.link = c_void_p()
        self.file = c_void_p()
        # Qt has COM set up in calibre's main thread already; this only counts a use of it.
        self.com = ole32.CoInitialize(None) in (0, 1)
        try:
            ctypes.oledll.ole32.CoCreateInstance(byref(CLSID_SHELL_LINK), None, CLSCTX_INPROC_SERVER, byref(IID_SHELL_LINK_W), byref(self.link))
            method(self.link, QUERY_INTERFACE, HRESULT, c_void_p, c_void_p)(byref(IID_PERSIST_FILE), byref(self.file))
            method(self.file, FILE_LOAD, HRESULT, wintypes.LPCWSTR, wintypes.DWORD)(path, STGM_READWRITE)
        except Exception:
            self.close()
            raise

    def target(self):
        buf = ctypes.create_unicode_buffer(MAX_PATH)
        method(self.link, LINK_GET_PATH, HRESULT, wintypes.LPWSTR, c_int, c_void_p, wintypes.DWORD)(buf, MAX_PATH, None, 0)
        return buf.value

    def icon_location(self):
        "(icon file, index). An empty file means the target's own icon."
        buf = ctypes.create_unicode_buffer(MAX_PATH)
        index = c_int()
        method(self.link, LINK_GET_ICON_LOCATION, HRESULT, wintypes.LPWSTR, c_int, POINTER(c_int))(buf, MAX_PATH, byref(index))
        return buf.value, index.value

    def set_icon_location(self, path, index):
        method(self.link, LINK_SET_ICON_LOCATION, HRESULT, wintypes.LPCWSTR, c_int)(path, index)

    def save(self):
        method(self.file, FILE_SAVE, HRESULT, wintypes.LPCWSTR, wintypes.BOOL)(self.path, True)

    def close(self):
        for name in ('file', 'link'):
            obj = getattr(self, name)
            if obj:
                method(obj, RELEASE, c_ulong)()
                setattr(self, name, c_void_p())
        if self.com:
            ole32.CoUninitialize()
            self.com = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


SHCNE_UPDATEITEM = 0x00002000
SHCNE_ASSOCCHANGED = 0x08000000
SHCNF_PATHW = 0x0005
SHCNF_IDLIST = 0x0000


def notify_changed(paths):
    "Tell Explorer, and so the taskbar, that these shortcuts' icons changed."
    shell32.SHChangeNotify.argtypes = [wintypes.LONG, c_uint, c_void_p, c_void_p]
    for path in paths:
        shell32.SHChangeNotify(SHCNE_UPDATEITEM, SHCNF_PATHW, ctypes.c_wchar_p(path), None)
    shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
