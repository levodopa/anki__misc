# -*- coding: utf-8 -*-
# License: AGPLv3

# for 2.0

######## USER CONFIG ########################################
shortcutMixed = "8"
shortcutNewFirst = "9"
shortcutNewLast = "0"
######## END USER CONFIG ####################################


from aqt import mw
from aqt.utils import tooltip
from aqt.reviewer import Reviewer
from anki.hooks import addHook
from aqt.qt import *


#https://www.juliensobczak.com/write/2016/12/26/anki-scripting.html
#"newSpread": "whether new cards should be mixed with reviews, \
#   or shown first or last: NEW_CARDS_DISTRIBUTE(0), NEW_CARDS_LAST(1),
#   NEW_CARDS_FIRST(2)",

def change_order_of_new_cards(order):
    qc = mw.col.conf
    if order == "mixed":
        qc['newSpread']=0
    elif order == "newFirst":
        qc['newSpread']=2
    else:
        qc['newSpread']=1
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
        tooltip('new cards shown last')
    else:
        tooltip('new cards shown first')


# def newKeyHandler(self, evt):
#     key = unicode(evt.text())
#     if key == shortcut0:
#         change_order_of_new_cards(0)
#     elif key == shortcut1:
#         change_order_of_new_cards(1)
#     elif key == shortcut2:
#         change_order_of_new_cards(2)
#     else:
#         origKeyHandler(self, evt)
# origKeyHandler = Reviewer._keyHandler
# Reviewer._keyHandler = newKeyHandler


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
    a.triggered.connect(lambda: change_order_of_new_cards("mixed"))

    a=m.addAction("New Cards first")
    a.triggered.connect(lambda: change_order_of_new_cards("newFirst"))

    a=m.addAction("New Cards Last")
    a.triggered.connect(lambda: change_order_of_new_cards("newLast"))

addHook("Reviewer.contextMenuEvent", showContextMenu)




"""
SHOW_IN_CONTEXT_MENU = True
def insert_reviewer_more_action(self, m):
    amenu = m.addMenu('Prefs - New Cards')
    action = amenu.addAction('mix')
    action.connect(action, SIGNAL('triggered()'),lambda: change_order_of_new_cards("mixed"))
    action = amenu.addAction('after')
    action.connect(action, SIGNAL('triggered()'),lambda: change_order_of_new_cards("newFirst"))
    action = amenu.addAction('before')
    action.connect(action, SIGNAL('triggered()'),lambda: change_order_of_new_cards("newLast"))
if SHOW_IN_CONTEXT_MENU:
    addHook("AnkiWebView.contextMenuEvent", insert_reviewer_more_action)
"""
