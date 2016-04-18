#!/bin/python
# -*- coding: gb2312; 
# mode:python; tab-width:4 -*- ex:set tabstop=4 shiftwidth=4 expandtab: -*-

#-------------------------------------------------------------------------
# Name:         baseframe.py
# Purpose:      base class of frame
#
# Author:       ma xiao
# Created:      2011-1-20
# Copyright:    iscas
#-------------------------------------------------------------------------

"""
Pydoc
…
"""

__version__ = "1.0"

import wx
import logging
import thread


class wxLogText(logging.Handler):
    def __init__(self, textCtl):
        logging.Handler.__init__(self)
        self.textCtl = textCtl
        self.thread_id = thread.get_ident()

    def emit(self, record):
        if thread.get_ident() == self.thread_id:
            #GUI
            self.textCtl.AppendText(self.format(record))
            self.textCtl.AppendText('\n')
        else:
            wx.CallAfter(self.textCtl.AppendText, self.format(record) + "\n")

