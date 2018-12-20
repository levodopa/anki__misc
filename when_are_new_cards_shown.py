# -*- coding: utf-8 -*-
# License: AGPLv3

# allows to quickly change when new cards are shown.
# Usually you have to go to the Preferences to adjust this
# This add-on offers shortcuts and entries in the "More" 
# menu (lower right corner)
# use this at your own risk

######## USER CONFIG ########################################
shortcutMixed    = "8" # "8"
shortcutNewFirst = ""  # "9"
shortcutNewLast  = ""  # "0"
######## END USER CONFIG ####################################


from aqt import mw
from aqt.utils import tooltip
from aqt.reviewer import Reviewer
from anki.hooks import addHook
from aqt.qt import *


# anki/consts.py
# whether new cards should be mixed with reviews, or shown first or last
#    NEW_CARDS_DISTRIBUTE = 0
#    NEW_CARDS_LAST = 1
#    NEW_CARDS_FIRST = 2


def change_order_of_new_cards(order):
    qc = mw.col.conf
    if order == "mixed":
        qc['newSpread']= 0 # NEW_CARDS_DISTRIBUTE
    elif order == "newFirst":
        qc['newSpread']= 2 # NEW_CARDS_FIRST
    elif order == "newLast":
        qc['newSpread']= 1 # NEW_CARDS_LAST
    #run relevant parts of accept (of preferences change)
    ##relevant part of updateCollection
    mw.col.setMod()
    ##rest of accept
    mw.pm.save()
    mw.reset()
    mw.done = 0 # ??
    if order == "mixed":
        tooltip('new and review cards are mixed')
    elif order == "newFirst":
        tooltip('new cards shown first')
    elif order == "newLast":
        tooltip('new cards shown last')
    else:
        tooltip('error in add-on when_are_new_cards_shown')


from aqt.qt import QMainWindow
from aqt.main import AnkiQt

def _keyPressEvent(self, evt):
    # do we have a delegate?
    if self.keyHandler:
        # did it eat the key?
        if self.keyHandler(evt):
            return
    # run standard handler
    QMainWindow.keyPressEvent(self, evt)
    # check global keys
    key = unicode(evt.text())
    if key == "d":
        self.moveToState("deckBrowser")
    elif key == "s":
        if self.state == "overview":
            self.col.startTimebox()
            self.moveToState("review")
        else:
            self.moveToState("overview")
    elif key == "a":
        self.onAddCard()
    elif key == "b":
        self.onBrowse()
    elif key == "S":
        self.onStats()
    elif key == "y":
        self.onSync()
    elif self.state == "overview" or "review":
        if key == shortcutMixed:
            change_order_of_new_cards("mixed")
        elif key == shortcutNewFirst:
            change_order_of_new_cards("newFirst")
        elif key == shortcutNewLast:
            change_order_of_new_cards("newLast")
AnkiQt.keyPressEvent = _keyPressEvent



def showContextMenu(r, m):
    a=m.addAction("Mix Old and New Cards")
    if shortcutMixed:
        a.setShortcut(QKeySequence(shortcutMixed))
    a.triggered.connect(lambda: change_order_of_new_cards("mixed"))

    a=m.addAction("New Cards first")
    if shortcutNewFirst:
        a.setShortcut(QKeySequence(shortcutNewFirst))
    a.triggered.connect(lambda: change_order_of_new_cards("newFirst"))

    a=m.addAction("New Cards Last")
    if shortcutNewLast:
        a.setShortcut(QKeySequence(shortcutNewLast))
    a.triggered.connect(lambda: change_order_of_new_cards("newLast"))
addHook("Reviewer.contextMenuEvent", showContextMenu)
