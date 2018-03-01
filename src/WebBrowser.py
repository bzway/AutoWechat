#!/usr/bin/env python
# -*- coding: utf-8 -*-
# - wxPython 4.0 on Windows/Mac/Linux
# - wxPython 3.0 on Windows/Mac
# - wxPython 2.8 on Linux
# - CEF Python v55.4+
__author__ = 'adm zhu'
import wx
from cefpython3 import cefpython as cef
import platform
import sys
import itchat
import os
import json
import time
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY,   title='Auto Chat')
        self.browser = None
        # Must ignore X11 errors like 'BadWindow' and others by
        # installing X11 error handlers. This must be done after
        # wx was intialized.
        if LINUX:
            WindowUtils.InstallX11ErrorHandlers()

        self.setup_icon()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Set wx.WANTS_CHARS style for the keyboard to work.
        # This style also needs to be set for all parent controls.
        self.browser_panel = wx.Panel(self, style=wx.WANTS_CHARS)
        self.browser_panel.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.browser_panel.Bind(wx.EVT_SIZE, self.OnSize)

        # On Linux must show before embedding browser, so that handle
        # is available (Issue #347).
        if LINUX:
            self.Show()
            # In wxPython 3.0 and wxPython 4.0 handle is still
            # not yet available, must delay embedding browser
            # (Issue #349).
            if wx.version().startswith("3.") or wx.version().startswith("4."):
                wx.CallLater(20, self.embed_browser)
            else:
                # This works fine in wxPython 2.8
                self.embed_browser()
        else:
            self.embed_browser()
            self.Show()

    def setup_icon(self):
        icon_file = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 "resources", "wxpython.png")
        # wx.IconFromBitmap is not available on Linux in wxPython 3.0/4.0
        if os.path.exists(icon_file) and hasattr(wx, "IconFromBitmap"):
            icon = wx.IconFromBitmap(wx.Bitmap(icon_file, wx.BITMAP_TYPE_PNG))
            self.SetIcon(icon)


    def embed_browser(self):
        window_info = cef.WindowInfo()
        (width, height) = self.browser_panel.GetClientSize().Get()
        window_info.SetAsChild(self.browser_panel.GetHandle(), [0, 0, width, height])
        path = "file:///"+os.getcwd().replace("\\","/")+ "/index.html"
        print(path)
        self.browser = cef.CreateBrowserSync(window_info, url=path)
        self.browser.SetClientHandler(FocusHandler())
        js = cef.JavascriptBindings()
        js.SetFunction("changeTitle", self.changeTitle)
        js.SetObject("host",self)
        js.SetProperty("other", {"a": 1})
        self.browser.SetJavascriptBindings(js)
        self.login()

    def  changeTitle(self,title):
        self.SetTitle(title)
    def OnSetFocus(self, _):
        if not self.browser:
            return
        if WINDOWS:
            WindowUtils.OnSetFocus(self.browser_panel.GetHandle(),
                                   0, 0, 0)
        self.browser.SetFocus(True)

    def OnSize(self, _):
        if not self.browser:
            return
        if WINDOWS:
            WindowUtils.OnSize(self.browser_panel.GetHandle(),
                               0, 0, 0)
        elif LINUX:
            (x, y) = (0, 0)
            (width, height) = self.browser_panel.GetSize().Get()
            self.browser.SetBounds(x, y, width, height)
        self.browser.NotifyMoveOrResizeStarted()

    def OnClose(self, event):
        print("[wxpython.py] OnClose called")
        if not self.browser:
            # May already be closing, may be called multiple times on Mac
            return

        if MAC:
            # On Mac things work differently, other steps are required
            self.browser.CloseBrowser()
            self.clear_browser_references()
            self.Destroy()
            global g_count_windows
            g_count_windows -= 1
            if g_count_windows == 0:
                cef.Shutdown()
                wx.GetApp().ExitMainLoop()
                # Call _exit otherwise app exits with code 255 (Issue #162).
                # noinspection PyProtectedMember
                os._exit(0)
        else:
            # Calling browser.CloseBrowser() and/or self.Destroy()
            # in OnClose may cause app crash on some paltforms in
            # some use cases, details in Issue #107.
            self.browser.ParentWindowWillClose()
            event.Skip()
            self.clear_browser_references()

    def clear_browser_references(self):
        # Clear browser references that you keep anywhere in your
        # code. All references must be cleared for CEF to shutdown cleanly.
        self.browser = None

    def login(self):
        itchat.login()
        #itchat.run()
    def getFriends(self):
        friends = itchat.get_friends(update=True)
        jsstring =json.dumps(friends, ensure_ascii=False)
        print(jsstring)
        self.browser.ExecuteJavascript("var friends = "+ jsstring)
        self.browser.ExecuteJavascript("LoadFriends(friends);");
    def getChatRooms(self):
        rooms = itchat.get_chatrooms(update=True)
        jsstring =json.dumps(rooms, ensure_ascii=False)
        print(jsstring)
        self.browser.ExecuteJavascript("var friends = " + jsstring)
        self.browser.ExecuteJavascript("LoadFriends(friends);");
    def getMPs(self):
        mps = itchat.get_mps(update=True)
        jsstring =json.dumps(mps, ensure_ascii=False)
        print(jsstring)
        self.browser.ExecuteJavascript("var friends = " + jsstring)
        self.browser.ExecuteJavascript("LoadFriends(friends);");
    def sleep(self, seconds):
        time.sleep(seconds)
    def sendMsg(self, msg, toUser):
        print("send " + msg +" to " + toUser);
        itchat.send(msg=msg, toUserName=toUser)


class FocusHandler(object):
    def OnGotFocus(self, browser, **_):
        # Temporary fix for focus issues on Linux (Issue #284).
        if LINUX:
            print("[wxpython.py] FocusHandler.OnGotFocus:"
                  " keyboard focus fix (Issue #284)")
            browser.SetFocus(True)


class CefApp(wx.App):

    def __init__(self, redirect):
        self.timer = None
        self.timer_id = 1
        self.is_initialized = False
        super(CefApp, self).__init__(redirect=redirect)

    def OnPreInit(self):
        super(CefApp, self).OnPreInit()
        # On Mac with wxPython 4.0 the OnInit() event never gets
        # called. Doing wx window creation in OnPreInit() seems to
        # resolve the problem (Issue #350).
        if MAC and wx.version().startswith("4."):
            print("[wxpython.py] OnPreInit: initialize here"
                  " (wxPython 4.0 fix)")
            self.initialize()

    def OnInit(self):
        self.initialize()
        return True

    def initialize(self):
        if self.is_initialized:
            return
        self.is_initialized = True
        self.create_timer()
        frame = MainFrame()
        self.SetTopWindow(frame)
        #frame.Show()
        frame.ShowFullScreen(True, wx.FULLSCREEN_NOMENUBAR)

    def create_timer(self):
        # See also "Making a render loop":
        # http://wiki.wxwidgets.org/Making_a_render_loop
        # Another way would be to use EVT_IDLE in MainFrame.
        self.timer = wx.Timer(self, self.timer_id)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(10)  # 10ms timer

    def on_timer(self, _):
        cef.MessageLoopWork()

    def OnExit(self):
        self.timer.Stop()
        return 0

@itchat.msg_register(itchat.content.TEXT, isFriendChat=True, isGroupChat=True,isMpChat=True)
def text_reply(msg):
    jsstring = json.dumps(msg,  ensure_ascii=False)
    print(jsstring)
    print(msg.text)
    itchat.send(msg=msg.text)
    msg.user.send("%s : %s" % (msg.user.NickName, msg.text))


if __name__ == '__main__':
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    settings = {}
    if WINDOWS:
        # noinspection PyUnresolvedReferences, PyArgumentList
        cef.DpiAware.EnableHighDpiSupport()
    cef.Initialize(settings=settings)
    app = CefApp(False)
    app.MainLoop()
    del app  # Must destroy before calling Shutdown
    if not MAC:
        # On Mac shutdown is called in OnClose
        cef.Shutdown()
