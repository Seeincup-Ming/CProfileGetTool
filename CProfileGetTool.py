#!/bin/python
# -*- coding: gb2312; 
# mode:python; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-


# -------------------------------------------------------------------------
# Name:         monitor.py
# Purpose:      main frame for svn confirm
# Author:       Zhang Xiaoming
# Created:      2014-9-15
# Copyright:    Netease
# -------------------------------------------------------------------------

"""
Pydoc
…
"""

__version__ = "1.3"

import logging
import wx
import wx.animate
import time
import os
import sys
from baseframe import wxLogText


titlestring = "Cprofile Data Getting Tool"


path = os.path.abspath(os.path.dirname(sys.argv[0]))
filedir_per = path + "\\data_pattern\\"
filedir_duration = path + "\\data_duration\\"
filedir_span = path + "\\data_span\\"
filedir_fps = path + "\\data_fps\\"


class MonitorFrame(wx.Frame):
    def __init__(self, parent):
        """
        initialize frame
        """

        wx.Frame.__init__(self, parent, -1, titlestring, size=(301, 600),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.CenterOnScreen()
        self.initData()
        self.initUI()
        self.initLayout()
        self.initLogging()

        #path = os.path.abspath(os.path.dirname(sys.argv[0]))
        #logging.info(path)



    def initData(self):

        self.buttonDefaultSize = (88, 30)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.fpslimit = None
        self.span = None
        self.duration = None
        self.pattern = None
        self.sp1 = None
        self.snifferstartflag = 0

        pass

    def initLogging(self):
        '''
        Add self.msgTxtCtrl to logging system
        '''
        logger = logging.getLogger()
        handler = wxLogText(self.msgTextCtrl)
        formatter = logging.Formatter('%(asctime)s:  %(message)s')
        # #formatter = logging.Formatter('%(levelname)s :%(asctime)s %(filename)s %(lineno)s :  %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        '''
        set the level of the logger
        '''
        logger.setLevel(logging.INFO)
        pass

    def initUI(self):
        """
        initialize book_page, include quest_page, monitor_page, capture_page, date_base_page, test_suite_page, about_page
            quest_page, monitor_page includes grid
            capture_page, date_base_page, test_suite_page includes list_ctrl and tool_panel, list_ctrl display the information,
            tool_panel include the buttons
        """

        self.CreateStatusBar()
        self.SetStatusText("Welcome to Cprofile Data Getting Tool!")

        menuBar = wx.MenuBar()
        # 1st menu from left
        menu = wx.Menu()

        self.menuCloseID = wx.NewId()
        self.menuStartGet = wx.NewId()
        self.menuStopGet = wx.NewId()


        menu.Append(self.menuStartGet,"&Start","Start the inner gettiing interface!")
        menu.Append(self.menuStopGet,"&Stop","Stop the inner gettiing interface!")
        menu.AppendSeparator()
        menu.Append(self.menuCloseID, "&Exit", "Exit.")
        self.Bind(wx.EVT_MENU, self.OnClose, id=self.menuCloseID)
        self.Bind(wx.EVT_MENU, self.OnMenuStartGetting, id=self.menuStartGet)
        self.Bind(wx.EVT_MENU, self.OnMenuStopGetting, id=self.menuStopGet)

        menuBar.Append(menu, "&Admin")
        self.SetMenuBar(menuBar)

        self.mainPanel = wx.Panel(self, -1)

        self.Statictext_pattern = wx.StaticText(self.mainPanel, label='* Select Pattern :')
        self.Statictext_duration = wx.StaticText(self.mainPanel, label='Select Duration (s) :')
        self.Statictext_Fps = wx.StaticText(self.mainPanel, label='Select Fps Limit Value :')
        self.Statictext_span = wx.StaticText(self.mainPanel, label='Select Time Span (s) :')

        patternlist = ["default", "3v3", "5v5", "FightClub"]
        durationlist = ["default", "5", "30", "60", "600", "1800", "2400"]
        fpslimitvaluelist = ["default", "30", "35", "40", "45", "50"]
        spanlist = ["default", "1", "5", "10", "15", "20"]

        self.combbox_pattern = wx.ComboBox(self.mainPanel, -1, "default", wx.DefaultPosition, (100, -1), patternlist,
                                           wx.CB_DROPDOWN)
        self.combbox_duration = wx.ComboBox(self.mainPanel, -1, "default", wx.DefaultPosition, (100, -1), durationlist,
                                            wx.CB_DROPDOWN)
        self.combbox_fpslimit = wx.ComboBox(self.mainPanel, -1, "default", wx.DefaultPosition, (100, -1),
                                            fpslimitvaluelist, wx.CB_DROPDOWN)
        self.combbox_span = wx.ComboBox(self.mainPanel, -1, "default", wx.DefaultPosition, (100, -1), spanlist,
                                        wx.CB_DROPDOWN)


        self.combbox_span.Enable(False)
        self.combbox_fpslimit.Enable(False)
        self.combbox_duration.Enable(False)

        self.combbox_pattern.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.combbox_pattern)
        self.combbox_duration.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.combbox_duration)
        self.combbox_fpslimit.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.combbox_fpslimit)
        self.combbox_span.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.combbox_span)

        self.start_button = wx.Button(self.mainPanel, -1, u"Start", size=(-1, 50))
        self.stop_button = wx.Button(self.mainPanel, -1, u"Stop", size=(-1, 50))
        self.dump_button = wx.Button(self.mainPanel, -1, u"Dump", size=(255, 60))

        self.start_button.Enable(False)
        self.stop_button.Enable(False)
        self.dump_button.Enable(False)

        self.Bind(wx.EVT_BUTTON, self.OnStartButton, self.start_button)

        self.Bind(wx.EVT_BUTTON, self.OnStopButton, self.stop_button)
        self.Bind(wx.EVT_BUTTON, self.OnDumpButton, self.dump_button)

        self.ring = "STOP"
        self.text_ring = wx.StaticText(self.mainPanel, -1, self.ring, (20, 120))
        self.text_ring.SetForegroundColour("red")

        self.msgPanel = wx.Panel(self, -1)
        self.staticbox = wx.StaticBox(self.msgPanel, -1, "Running Log...")
        self.msgTextCtrl = wx.TextCtrl(self.msgPanel, size=(-1, -1), style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)

        self.Bind(wx.EVT_TIMER, self.OnTimeSpan)

        # self.bsizer = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)
        # self.msgTextCtrl = wx.TextCtrl(self.msgPanel, size=(-1, 140), style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE)
        # self.bsizer.Add(self.msgTextCtrl, 0, wx.TOP | wx.LEFT, 10)


        # self.logListPanel = wx.Panel(self, -1)
        # self.loglist = EditListCtrl(self.logListPanel)
        # self.loglist.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnLogItemSelected)
        #
        # self.filediffPanel = wx.Panel(self, -1)
        # self.filediffPanel.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        #
        # self.filedifflist = EditListCtrl(self.filediffPanel)
        # self.filedifflist.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnfilediffItemSelected)
        #
        # self.toolPanel = wx.Panel(self.filediffPanel, -1)
        # self.refresh_button = wx.Button(self.toolPanel, -1, u"Refresh", size=(88, 50))
        # self.refresh_button.Enable(False)
        #
        # self.Bind(wx.EVT_BUTTON, self.OnRefreshButton, self.refresh_button)
        #
        # self.allconfirm_button = wx.Button(self.toolPanel, -1, u"AllConfirm", size=(88, 50))
        # self.Bind(wx.EVT_BUTTON, self.OnAllConfirmButton, self.allconfirm_button)
        # self.allconfirm_button.Enable(False)
        #
        # self.confirm_button = wx.Button(self.toolPanel, -1, u"Confirm", size=(88, 50))
        # self.Bind(wx.EVT_BUTTON, self.OnConfirmButton, self.confirm_button)
        # self.confirm_button.Enable(False)
        #
        # self.vacantPanel = wx.Panel(self.toolPanel, -1)
        #
        # self.ok_button = wx.Button(self.toolPanel, -1, u"Exit")
        # self.Bind(wx.EVT_BUTTON, self.OnOkButton, self.ok_button)


        pass


    def initLayout(self):
        """
        set layout of the picture_ctrl, page panel
        """
        self._icon = _icon = wx.EmptyIcon()
        _icon.LoadFile("./pic/detect.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(_icon)

        mainpageSizer = wx.GridBagSizer()
        # mainpageSizer.Add( wx.StaticText(self.mainPanel, -1, "Use the folowing option to start!"),(0,0), (1,7), wx.ALIGN_CENTER | wx.ALL, 5)


        mainpageSizer.Add(self.Statictext_pattern, pos=(0, 0), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mainpageSizer.Add(self.combbox_pattern, pos=(0, 1), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mainpageSizer.Add(self.Statictext_duration, pos=(1, 0), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mainpageSizer.Add(self.combbox_duration, pos=(1, 1), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mainpageSizer.Add(self.Statictext_Fps, pos=(3, 0), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mainpageSizer.Add(self.combbox_fpslimit, pos=(3, 1), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mainpageSizer.Add(self.Statictext_span, pos=(2, 0), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        mainpageSizer.Add(self.combbox_span, pos=(2, 1), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        mainpageSizer.Add(self.start_button, pos=(4, 0), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=20)
        mainpageSizer.Add(self.stop_button, pos=(4, 1), span=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=20)
        mainpageSizer.Add(self.dump_button, pos=(5, 0), span=(1, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        mainpageSizer.Add(self.text_ring, pos=(6, 0), span=(1, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        self.mainPanel.SetSizer(mainpageSizer)

        bsizer = wx.StaticBoxSizer(self.staticbox, wx.VERTICAL)
        bsizer.Add(self.msgTextCtrl, 1,
                   wx.ALL | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 0)
        self.msgPanel.SetSizer(bsizer)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.mainPanel, 6, wx.ALL | wx.EXPAND, 0)
        mainSizer.Add(self.msgPanel, 4, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(mainSizer)

        pass

    def OnMenuStartGetting(self,event):

        try:
            from utils import monkey_patch
            import x9
            from x9.debug import StuckSniffer
            if self.snifferstartflag == 0:
                StuckSniffer.instance().start()
                self.snifferstartflag = 1
                self.ringstring("start")
                self.showDlg("STARTED..  Files has been saved into \'/game\'..",wx.ICON_INFORMATION)
                self.combbox_pattern.Enable(False)
                #self.start_button.Enable(False)
            else:
                self.showDlg("Already started!!", wx.ICON_ERROR)
                self.ringstring("stop")

        except Exception, err:
            if str(err) == "No module named x9":
                # print "Open X9 and restart this tool!!"
                self.showDlg("Open X9 And RESTART This Tool!!", wx.ICON_ERROR)
            elif str(err) == "stream has been closed":
                # print "X9 has been CLOSED!!"
                self.showDlg("X9 Has Been CLOSED!!Open X9 And RESTART This Tool!!", wx.ICON_ERROR)
            return

        print "menustart"

    def OnMenuStopGetting(self,event):
        try:
            from utils import monkey_patch
            import x9
            from x9.debug import StuckSniffer
            if self.snifferstartflag == 1:
                StuckSniffer.instance().stop()
                self.snifferstartflag = 0
                self.ringstring("stop")
                self.showDlg("STOPPED..",wx.ICON_INFORMATION)
                self.combbox_pattern.Enable(True)
                #self.start_button.Enable(True)
            else:
                self.showDlg("Already stoped!!", wx.ICON_ERROR)
                self.ringstring("start")


            self.snifferstartflag = 0

        except Exception, err:
            if str(err) == "No module named x9":
                # print "Open X9 and restart this tool!!"
                self.showDlg("Open X9 And RESTART This Tool!!", wx.ICON_ERROR)
            elif str(err) == "stream has been closed":
                # print "X9 has been CLOSED!!"
                self.showDlg("X9 Has Been CLOSED!!Open X9 And RESTART This Tool!!", wx.ICON_ERROR)
            return
        print "menustop"


    def EvtComboBox(self, evt):

        cb = evt.GetEventObject()

        print evt.GetString(), "@@@@@"

        if cb == self.combbox_fpslimit:
            if evt.GetString() != "default":
                self.fpslimit_name = evt.GetString()
                self.fpslimit = int(self.fpslimit_name)
                self.combbox_span.Enable(False)
                self.combbox_duration.Enable(False)
            else:
                self.fpslimit_name = None
                self.fpslimit = None
                self.combbox_span.Enable(True)
                if self.span is None:
                    self.combbox_duration.Enable(True)

            print "fps", self.fpslimit, self.fpslimit_name

        elif cb == self.combbox_span:
            if evt.GetString() != "default":
                self.span_name = evt.GetString()
                self.span = int(self.span_name)
                self.combbox_fpslimit.Enable(False)
                self.combbox_duration.Enable(False)
            else:
                self.span_name = None
                self.span = None
                self.combbox_fpslimit.Enable(True)
                if self.fpslimit is None:
                    self.combbox_duration.Enable(True)
            print "span", self.span_name, self.span


        elif cb == self.combbox_duration:
            if evt.GetString() != "default":
                self.duration_name = evt.GetString()
                self.duration = int(self.duration_name)
                self.combbox_span.Enable(True)
                self.combbox_fpslimit.Enable(True)
                self.stop_button.Enable(False)
                self.combbox_pattern.Enable(False)

            else:
                self.duration_name = None
                self.duration = None
                self.combbox_span.Enable(False)
                self.combbox_fpslimit.Enable(False)
                self.combbox_pattern.Enable(True)

            print "duration", self.duration_name, self.duration

        elif cb == self.combbox_pattern:
            if evt.GetString() != "default":
                self.pattern_name = evt.GetString()
                self.pattern = self.pattern_name
                print "pattrn", self.pattern_name, self.pattern
                self.start_button.Enable(True)
                self.combbox_duration.Enable(True)
            else:
                self.pattern_name = None
                self.pattern = None
                self.combbox_duration.Enable(False)
                self.start_button.Enable(False)
                # self.stop_button.Enable(True)
        else:
            print "error3"

        # 向下面的log输出一项log
        print self.pattern, self.duration, self.fpslimit, self.span, "       ", self.combbox_span.GetLabelText()

    def OnTimeSpan(self, event):
        print "timeer"
        if self.sp1 is not None:
            self.ringstring("stop")
            spandir = filedir_span + "span_" + self.pattern_name + "_" + self.duration_name + "_" + self.span_name + "\\"

            isotimeformat = '%Y%m%d%H%M%S'
            currenttime = time.strftime(isotimeformat, time.localtime())
            filename = spandir + currenttime

            self.mkdir(spandir)
            self.sp1.disable()
            self.sp1.dump_stats(filename)
            self.sp1.clear()

            self.sp1.enable()
            self.ringstring("start")

        pass

    def progressstarted(self,duration):
        beilu = 10

        max = duration*beilu

        dlg = wx.ProgressDialog("Wait...",
                               "Please wait...",
                               maximum = max,
                               parent=self,
                               style = 0
                                #| wx.PD_APP_MODAL
                                #| wx.PD_CAN_ABORT
                                #| wx.PD_CAN_SKIP
                                #| wx.PD_ELAPSED_TIME
                                #| wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                | wx.PD_AUTO_HIDE

                                )
        keepGoing = True
        count = 0

        while keepGoing and count < max:
            count += 1
            wx.MilliSleep(1000/beilu)
            wx.Yield()

            if count >= max / 2:
                (keepGoing, skip) = dlg.Update(count, "Half-time!")
            else:
                (keepGoing, skip) = dlg.Update(count)


        dlg.Destroy()



    def OnTimeDuration(self):

        self.ringstring("stop")
        try:

            if self.sp1 is not None and self.span is None and self.fpslimit is None:
                print "only duration selected"
                self.mkdir(filedir_duration)
                isotimeformat = '%Y%m%d%H%M%S'
                currenttime = time.strftime(isotimeformat, time.localtime())
                filename = filedir_duration + "duration_" + self.pattern_name + "_" + self.duration_name + "_" + currenttime
                self.sp1.disable()
                self.sp1.dump_stats(filename)
                self.sp1.clear()

                self.combbox_pattern.Enable(False)
                self.combbox_duration.Enable(True)
                self.combbox_fpslimit.Enable(True)
                self.combbox_span.Enable(True)
                self.ringstring("stop")



            elif self.span is not None and self.duration is not None and self.fpslimit is None:
                print "only span and duration selected 111"
                self.timer1.Stop()
                del self.timer1
                spandir = filedir_span + "span_" + self.pattern_name + "_" + self.duration_name + "_" + self.span_name + "\\"
                isotimeformat = '%Y%m%d%H%M%S'
                currenttime = time.strftime(isotimeformat, time.localtime())
                filename = spandir + currenttime
                self.mkdir(spandir)
                self.sp1.disable()
                self.sp1.dump_stats(filename)
                self.sp1.clear()

                self.combbox_pattern.Enable(False)
                self.combbox_duration.Enable(False)
                self.combbox_fpslimit.Enable(False)
                self.combbox_span.Enable(True)

                self.ringstring("start")

            elif self.span is None and self.duration is not None and self.fpslimit is not None:
                print "duration and fps selected"

                # 有时间添加fps显示的控件，或者增加log

                self.t2.Stop()
                del self.t2


                if self.start_flag == 1:
                    self.sp1.disable()
                    self.start_flag = 0
                    fpsdir = filedir_fps + "fps_" + self.pattern_name + "_" + self.duration_name + "_" + self.fpslimit_name + "\\"
                    isotimeformat = '%Y%m%d%H%M%S'
                    currenttime = time.strftime(isotimeformat, time.localtime())
                    filename = fpsdir + currenttime
                    self.mkdir(fpsdir)

                    self.sp1.dump_stats(filename)
                    self.sp1.clear()

                self.combbox_pattern.Enable(False)
                self.combbox_duration.Enable(False)
                self.combbox_fpslimit.Enable(True)
                self.combbox_span.Enable(False)

                self.ringstring("start")

                print "storage"


            else:
                print "error4"
                # 学习回调机制，应用。


        except Exception, err:
            print str(err)

        self.start_button.Enable(True)
        logging.info("Stop!")
        # self.dump_button.Enable(False)


    def OnStartButton(self, event):


        # do someting according to the selected ....start
        try:
            from utils import monkey_patch
            import x9
            from x9.debug import hack
            from x9 import BigWorld as BW
            from x9.debug.profile import cProfile

            self.BigWorld = BW

            self.per_time1 = time.time()

            self.sp1 = cProfile.Profile()
            self.sp1.enable()

            if self.duration is not None and self.span is None and self.fpslimit is None:

                self.ringstring("start")
                logging.info(self.pattern_name +"  "+self.duration_name + "  Started!")
                wx.CallLater(int(self.duration) * 1000, self.OnTimeDuration)
                wx.CallLater(0,self.progressstarted,int(self.duration))

            elif self.duration is not None and self.span is not None and self.fpslimit is None:
                if int(self.span) < int(self.duration):
                    self.ringstring("start")
                    logging.info(self.pattern_name +"  "+self.duration_name+" "+self.span_name +"  Started!")
                    self.timer1 = wx.Timer(self)
                    self.timer1.Start(int(self.span) * 1000)
                    wx.CallLater(int(self.duration) * 1000, self.OnTimeDuration)
                    wx.CallLater(0,self.progressstarted,int(self.duration))
                else:
                    print "duration need more than span"
                    return
            elif self.duration is not None and self.span is None and self.fpslimit is not None:
                print "fps start testing..."
                self.ringstring("start")
                logging.info(self.pattern_name +"  "+self.duration_name+" "+self.fpslimit_name +"  Started!")
                self.start_flag = 0
                self.t2 = wx.CallLater(0,self.fpstest)
                wx.CallLater(int(self.duration) * 1000, self.OnTimeDuration)  # to stop
                wx.CallLater(0,self.progressstarted,int(self.duration))

            elif self.duration is None and self.span is None and self.fpslimit is None:
                print "only pattern has been selected"
                self.ringstring("start")
                logging.info(self.pattern_name + " Started!")
            else:
                print "error5"


        except Exception, err:
            if str(err) == "No module named x9":
                # print "Open X9 and restart this tool!!"
                self.showDlg("Open X9 And RESTART This Tool!!", wx.ICON_ERROR)
            elif str(err) == "stream has been closed":
                # print "X9 has been CLOSED!!"
                self.showDlg("X9 Has Been CLOSED!!Open X9 And RESTART This Tool!!", wx.ICON_ERROR)
            return

        self.combbox_pattern.Enable(False)
        self.combbox_duration.Enable(False)
        self.combbox_fpslimit.Enable(False)
        self.combbox_span.Enable(False)

        self.start_button.Enable(False)
        if self.duration is None:
            self.stop_button.Enable(True)
        self.dump_button.Enable(False)
        if self.stop_button.Enabled is True:
            self.stop_button.Enable(True)

    def fpstest(self):

        #print self.BigWorld.getFps()
        if self.BigWorld.getFps() <= self.fpslimit and self.start_flag == 0:
            self.sp1.enable()
            self.start_flag = 1
            #print "start getting fps"
        elif self.BigWorld.getFps() > self.fpslimit and self.start_flag == 1:
            self.sp1.disable()
            self.start_flag = 0
            fpsdir = filedir_fps + "fps_" + self.pattern_name + "_" + self.duration_name + "_" + self.fpslimit_name + "\\"

            isotimeformat = '%Y%m%d%H%M%S'
            currenttime = time.strftime(isotimeformat, time.localtime())

            filename = fpsdir + currenttime
            self.mkdir(fpsdir)

            self.sp1.dump_stats(filename)
            self.sp1.clear()
        else:
            pass
        self.t2.Restart(0)


    def OnStopButton(self, event):
        self.ringstring("stop")
        logging.info("Stop!")
        self.per_time2 = time.time()
        try:

            if self.sp1 is not None:
                self.sp1.disable()


            if self.span is not None:
                self.timer1.Stop()
                del self.timer1

        except Exception, err:
            print str(err)

        self.stop_button.Enable(False)
        self.dump_button.Enable(True)


    def OnDumpButton(self, event):
        #print "dump"
        logging.info("Dump the file!")
        try:

            if self.sp1 is not None:
                #print "here"
                self.mkdir(filedir_per)
                isotimeformat = '%Y%m%d%H%M%S'
                currenttime = time.strftime(isotimeformat, time.localtime())
                self.pertime = int(self.per_time2 - self.per_time1)
                filename = filedir_per + "pattern_" + self.pattern_name + "_" + str(self.pertime) + "_" + currenttime
                self.sp1.dump_stats(filename)
        except Exception, err:
            print str(err)

        self.combbox_pattern.Enable(True)
        self.combbox_duration.Enable(True)
        self.start_button.Enable(True)
        self.dump_button.Enable(False)


    def mkdir(self, path):
        # 引入模块

        path = path.strip()

        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            return False

    def ringstring(self, flag):
        if flag == "start":
            self.ring = "START"
            self.text_ring.SetLabel(self.ring)
            self.text_ring.SetForegroundColour("blue")
        elif flag == "stop":
            self.ring = "STOP"
            self.text_ring.SetLabel(self.ring)
            self.text_ring.SetForegroundColour("red")
        else:
            print "error1"

    def showDlg(self, content, title):
        """
        show information and error dialog
        """
        dlg = None
        if title == wx.ICON_INFORMATION:
            dlg = wx.MessageDialog(self, content, "Information", wx.OK | wx.ICON_INFORMATION)
        elif title == wx.ICON_ERROR:
            dlg = wx.MessageDialog(self, content, "Error", wx.OK | wx.ICON_ERROR)
        elif title == wx.ICON_NONE:
            dlg = wx.MessageDialog(self, content, "Infomation", wx.OK | wx.ICON_NONE)
        dlg.ShowModal()
        dlg.Destroy()

    def OnClose(self, event):
        """
        call when closing frame
        """
        # if hasattr(self,"netThread"):
        # self.showDlg("Thread is running, please stop first!", wx.ICON_ERROR)
        # return
        dlg = wx.MessageDialog(self, "Are you sure to exit??",
                               titlestring,
                               wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
        )
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()


if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MonitorFrame(None)
    frame.CenterOnScreen()
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()
