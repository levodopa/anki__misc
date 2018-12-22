# -*- coding: utf-8 -*-
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html

# some code reused from anki aqt/addcards.py which is
#     Copyright: Damien Elmes <anki@ichi2.net>
#     License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# mostly my functions add_and_reschedule and add_as_first_new reuse code from
# addCards 

"""
If you want all new cards to be shown only after n days use
https://github.com/lovac42/3ft_Under 

This add-on skips learning steps for this new card and reschedules 
it as a review to a set date.

Maybe useful for: 
- you add several cards that ask about the same topic in different ways
  and you don't want to see them at the same time. You could quickly 
  reschedule them when you see them the first time in the reviewer
  (with ReMemorize/QuickReschedule or MoreButtonsForNewCards) but
  then I don't know how many similar cards were created. This is 
  why I prefer to reschedule when adding multiple cards.
- cards that you know are easy

USE THIS AT YOUR OWN RISK
ALPHA QUALITY - add_as_first_new is untested
"""


######## USER CONFIG ########################################
# You can apply to rescheduled cards the value you have set
# in your deck options under "New Cards - Starting ease". Then 
# set EaseForCards = "DeckSettings".
# You can also set EaseForCards to an integer (e.g. 263)
# that is applied to all cards. Then deck settings are ignored.
EaseForCards = "DeckSettings"
######## END USER CONFIG ####################################



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
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(1,1))

        a = self.contextmenu.addAction('add+reschedule - 2 days')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(2,2))

        a = self.contextmenu.addAction('add+reschedule - 3 days')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(3,3))

        a = self.contextmenu.addAction('add+reschedule - 5 days')
        a.setShortcut(QKeySequence("Alt+Shift+Return"))   #just to add it to the gui
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(5,5))
        #workaround
        a = QShortcut(QKeySequence("Alt+Shift+Return"), self)
        a.activated.connect(lambda s=self: self.add_and_reschedule(5,5))

        self.contextmenu.addSeparator()

        a = self.contextmenu.addAction('add+reschedule - 7 days')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(7,7))

        self.contextmenu.addSeparator()

        a = self.contextmenu.addAction('add+reschedule - 1 months')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(28,32))

        a = self.contextmenu.addAction('add+reschedule - 1 year')
        a.connect(a, QtCore.SIGNAL("triggered()"),lambda s=self: self.add_and_reschedule(335,395))

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
            self.add_and_reschedule(ndi,ndi)

    def clearcounter(self):
        self.counter = 1
        self.mysetupButtons()
    
    def add_and_reschedule_with_counter(self, days):
        self.add_and_reschedule(days,days)
        self.counter += 1
        self.mysetupButtons()


    def add_and_reschedule(self, mindays, maxdays):
        self.editor.saveNow()
        self.editor.saveAddModeVars()
        note = self.editor.note
        note = self.addNote(note)
        if not note:
            return

        # stop anything playing
        clearAudioQueue()
        self.onReset(keep=True)
        self.mw.col.autosave()

        cards = note.cards()
        cids = [int(c.id) for c in cards]
        #if there is a deck override new cards can go to
        #different decks 
        if EaseForCards == "DeckSettings":  
            ce = {}
            for c in cards:
                conf = self.mw.col.decks.confForDid(c.did)
                ease = conf['new']['initialFactor']
                ce[c.id] = ease
                lastvalue = ease
            #writing to the database multiple times should be slow
            #so I check if all cards will have the same ease
            all_equal = all(value == lastvalue for value in ce.values())
            if all_equal:
                self.mw.col.sched.reschedNewCards(cids, lastvalue, mindays, maxdays)
            else:
                for id,factor in ce.items():
                    self.mw.col.sched.reschedNewCards([id], factor, mindays, maxdays)
        elif isinstance(EaseForCards,int):  #user has set custom ease value
            factor = EaseForCards * 10
            self.mw.col.sched.reschedNewCards(cids, factor, mindays, maxdays)
        else:
            tooltip('Invalid settings for EaseForCards in add-on add_and_reschedule')


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



from anki.utils import intTime
import random
from anki.sched import Scheduler
# slight modification of reschedCards from anki/sched.py which is
#    Copyright: Damien Elmes <anki@ichi2.net>
#    License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# I inserted the function parameter "factor",removed remFromDyn,added the tooltip
def reschedNewCards(self, ids, factor, imin, imax):
    "Put cards in review queue with a new interval in days (min, max)."
    d = []
    t = self.today
    mod = intTime()
    for id in ids:
        r = random.randint(imin, imax)
        d.append(dict(id=id, due=r+t, ivl=max(1, r), mod=mod,
                        usn=self.col.usn(), fact=int(factor)))
    #self.remFromDyn(ids)   #Cards just created can't be in a filtered deck
    self.col.db.executemany("""
update cards set type=2,queue=2,ivl=:ivl,due=:due,odue=0,
usn=:usn,mod=:mod,factor=:fact where id=:id""",
                            d)
    self.col.log(ids)

    if len(ids) == 1:
        tooltip(_("Added and rescheduled for %d" % d[0]('ivl')), period=800)
    else:
        ivls = []
        for c in d:
            ivls.append(c['ivl'])
        print(ivls)
        tooltip(_("Added and rescheduled cards for intervals between %d and %d" % (min(ivls),max(ivls))), period=800)
Scheduler.reschedNewCards = reschedNewCards
