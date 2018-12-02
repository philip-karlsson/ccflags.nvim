# ============================================================================
# FILE: ccflags.py
# AUTHOR: Philip Karlsson <philipkarlsson at me.com>
# License: MIT license
# ============================================================================

import pynvim
import os
import sys

@pynvim.plugin
class ccflags(object):

    def __init__(self, nvim):
        self.nvim = nvim
        self.logstr = []
        self.logstr.append('== ccflags debug ==')

    def log(self, s):
        self.logstr.append(s)

    def processMakeLine(self, l):
        ret = None
        if not '-c' in l:
            return ret
        ret = l.split()
        return ret

    def processFlags(self, fl):
        ret = []
        cIndex = fl.index("-c")
        # cF is the file
        cF = fl[cIndex+1]
        # Strip " if there and convert to
        # abs path
        cF = cF.replace('"', '')
        cF = os.path.abspath(cF)
        flagsOfInterest = []
        # Get the interesting flags
        for f in fl:
            if '-I' in f:
                flagsOfInterest.append(f)
        self.files[cF] = flagsOfInterest

    def parseVerbMakeOut(self, fname):
        self.files = {}
        with open(fname,'r') as f:
            lines = f.read().splitlines()
        for l in lines:
            fl = self.processMakeLine(l)
            if fl != None:
                self.processFlags(fl)

    @pynvim.command('CCFlagsShowLog', nargs='*', range='')
    def testcommand(self, args, range):
        self.nvim.command('e cc_flags_log')
        self.nvim.command('setlocal buftype=nofile')
        self.nvim.command('setlocal filetype=cc_flags_log')
        self.nvim.current.buffer.append(self.logstr)

    @pynvim.autocmd('BufEnter', pattern='*.cpp,*.h', eval='expand("<afile>")', sync=True)
    def on_bufenter(self, filename):
        self.log('== ccflags is in ' + filename)
        # Stupid to do this every time..
        fname = 'verb_make_out'
        if os.path.isfile(fname):
            self.parseVerbMakeOut(fname)
        self.log('== flags ==')
        if filename in self.files:
            for i in self.files[filename]:
                self.log(i)
