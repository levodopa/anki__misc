# -*- coding: utf-8 -*-

# License AGPLv3
# some code reused from dae/anki/aqt/addcards.py Copyright: Damien Elmes <anki@ichi2.net>

# skip learning steps for this new card and reschedule as review
# might be useful if:
# - you add several cards that ask about the same topic in different ways
#   and you don't want to see them at the same time
# - cards that you know are easy
# If you want all cards to be shown only after n days wait until
# https://github.com/lovac42/3ft_Under is published.



import aqt
import aqt.addcards

from aqt.qt import QPushButton, QShortcut, QKeySequence, QAction
from aqt.utils import tooltip, getText, askUser
from anki.sound import clearAudioQueue

from PyQt4 import QtGui, QtCore


class AddCards(aqt.addcards.AddCards):
    
    def __init__(self,mw):
        global second_part
        super(aqt.addcards.AddCards, self).__init__(mw)
        ### for contextmenu on Add button to reschedule
        self.counter = 1
        self.mysetupButtons()

    ######### for contextmenu on Add button to reschedule
    # only useful for notes that generate one card
    def mysetupButtons(self):
        self.addButton.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.addButton.customContextMenuRequested.connect(self.on_add_context_menu)

        self.contextmenu = QtGui.QMenu(self)

        a = self.contextmenu.addAction('clear counter')
        a.connect(a, QtCore.SIGNAL("triggered()"), self.clearcounter)

        a = self.contextmenu.addAction('add+reschedule - counter %d ' % self.counter)
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule_with_counter(self.counter))

        self.contextmenu.addSeparator()

        a = self.contextmenu.addAction('add+reschedule - tomorrow')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(1))

        a = self.contextmenu.addAction('add+reschedule - 2 days')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(2))

        a = self.contextmenu.addAction('add+reschedule - 3 days')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(3))

        a = self.contextmenu.addAction('add+reschedule - 5 days')
        a.setShortcut(QKeySequence("Alt+Shift+Return"))   #just to add it to the gui
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(5))
        #workaround
        a = QShortcut(QKeySequence("Alt+Shift+Return"), self)
        a.activated.connect(lambda s=self: self.add_and_reschedule(5))

        self.contextmenu.addSeparator()

        a = self.contextmenu.addAction('add+reschedule - 7 days')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(7))

        self.contextmenu.addSeparator()

        a = self.contextmenu.addAction('add+reschedule - 1 months')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(30))

        a = self.contextmenu.addAction('add+reschedule - 1 year')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(365))

        self.contextmenu.addSeparator()

        #a = self.contextmenu.addAction('add as first new card')
        #a.connect(a, QtCore.SIGNAL("triggered()"), self.add_as_first_new)

        a = self.contextmenu.addAction('add+reschedule - ask ')
        a.setShortcut(QKeySequence("Ctrl+Return"))   #just to add it to the gui
        a.connect(a, QtCore.SIGNAL("triggered()"), self.ask_to_reschedule)
        a = QShortcut(QKeySequence("Alt+Return"), self)
        a.activated.connect(self.ask_to_reschedule)

    def on_add_context_menu(self, point):
        self.contextmenu.exec_(self.addButton.mapToGlobal(point))

    def ask_to_reschedule(self):
        nd = getText("Reschedule with intervals of __ days: ")
        try:
            ndi = int(nd[0])
        except:
            tooltip('input is not an integer. Aborting')
        else:
            self.add_and_reschedule(ndi)

    def clearcounter(self):
        self.counter = 1
        self.mysetupButtons()
    
    def add_and_reschedule_with_counter(self, days):
        self.add_and_reschedule(days)
        self.counter += 1
        self.mysetupButtons()

    def add_and_reschedule(self, days):
        self.editor.saveNow()
        self.editor.saveAddModeVars()
        note = self.editor.note
        note = self.addNote(note)
        if not note:
            return
        tooltip(_("Added and rescheduled for %d" % days), period=500)
        # stop anything playing
        clearAudioQueue()
        self.onReset(keep=True)
        self.mw.col.autosave()

        nid, txt = self.history[0]
        note = aqt.mw.col.getNote(nid)
        cids = [int(c.id) for c in note.cards()]
        aqt.mw.col.sched.reschedCards( cids, days, days )

    def add_as_first_new(self):
        self.editor.saveNow()
        self.editor.saveAddModeVars()
        note = self.editor.note
        note = self.addNote(note)
        if not note:
            return
        tooltip(_("Added as first new"), period=500)
        # stop anything playing
        clearAudioQueue()
        self.onReset(keep=True)
        self.mw.col.autosave()

        nid, txt = self.history[0]
        note = aqt.mw.col.getNote(nid)
        cids = [int(c.id) for c in note.cards()]
        
        #browser.py -  reposition
        #self.mw.checkpoint(_("Reposition"))
        aqt.mw.col.sched.sortCards(
            cids, start=0, step=1,
            shuffle=True, shift=True)
        aqt.mw.requireReset()



aqt.addcards.AddCards= AddCards
aqt.dialogs._dialogs["AddCards"]=[AddCards,None]
