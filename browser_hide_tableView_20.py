# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
copyright 2018 ijgnd
          2017 Glutanimate  <https://glutanimate.com/>

some code reused from browser_search_highlight_results.py, 
https://ankiweb.net/shared/info/225180905 which is 
          Copyright: (c) Glutanimate 2017 <https://glutanimate.com/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


###BEGIN USER CONFIG###
HOTKEY_TOGGLE_MINIMIZE_TABLE = "Alt+7"
HOTKEY_TOGGLE_TABLE = "Alt+6"
HOTKEY_TOGGLE_SIDEBAR = "Alt+5"
HOTKEY_TOOGLE_BOTH = "Alt+Shift+G"
HOTKEY_ADD_SELECTED_TO_SELECTED = "Ctrl+T, J" 
HOTKEY_CLEAR_SELECTED = "Ctrl+T, K"
HOTKEY_SEARCH_FOR_SELECTED = "Ctrl+T, L"
###END USER CONFIG###


from aqt.browser import Browser
from anki.hooks import addHook, wrap
from aqt.qt import *

Browser.showTableView = True
Browser.showSidebar = True
Browser.selection = []

def toggleShowHideTableView(self):
    """ 
    it's not enough to hide self.tableView because tableView and the search bar
    are in a widget. If I hide the tableView this widget will only hold the 
    search bar and a lot of grey space. Working around this sounds too 
    time consuming.
    """
    if self.showTableView:
        self.form.widget.hide()
        self.showTableView = False
    else:
        self.form.widget.show()
        self.showTableView = True
Browser.toggleShowHideTableView = toggleShowHideTableView


Browser.toggledMinimized = False
def toggleMinimizeTableView(self):
    """
    uses ugly workaround with absolute sizes.
    I didn't find a quick solution to set the minimum size or relative sizes
    This didn't work:
      self.form.splitter.setStretchFactor(0, 10) # widget0
      self.form.splitter.setStretchFactor(1, 2) # widget1
    """
    if not self.toggledMinimized:        
        self.prior_lower_height=self.form.fieldsArea.size().height()
        #https://stackoverflow.com/a/47843697
        h=self.form.splitter.size().height()
        self.form.splitter.setSizes([183,h-183])
        self.toggledMinimized = True
    else:
        h=self.form.splitter.size().height()
        if h > self.prior_lower_height + 183: # 150 minimum for table + 33 for buttons in search 
             self.form.splitter.setSizes([h-self.prior_lower_height,self.prior_lower_height])
        else:
            self.form.splitter.setSizes([h/2,h/2])
        self.toggledMinimized = False
Browser.toggleMinimizeTableView = toggleMinimizeTableView


def toggleSidebar(self):
    if self.showSidebar:
        self.form.tree.hide() 
        self.showSidebar = False
    else:
        self.form.tree.show()
        self.showSidebar = True
Browser.toggleSidebar = toggleSidebar


def Both(self):
    self.toggleSidebar()
    self.toggleShowHideTableView()
    #toggleMinimizeTableView()
Browser.Both = Both


def onThisFind(self):
    if not self.showSidebar:
        self.form.tree.show()
        self.showSidebar = True  
    if not self.showTableView:
        self.form.widget.show()
        self.showTableView = True
    self.onFind()
Browser.onThisFind = onThisFind


def add_to_selection(self):
    for n in self.selectedNotes():
        self.selection.append(n)
    Browser.add_to_selection = add_to_selection


def clear_selection(self):
    self.selection = []
Browser.clear_selection = clear_selection


def filterForSelected(self):
    o = " ".join(["nid:" + str(x) + " OR" for x in self.selection])
    self.form.searchEdit.lineEdit().setText(o[:-3])
    self.onSearch()   # in 2.1 it's different: self.onSearchActivated()
Browser.filterForSelected = filterForSelected


def onContextMenu(self, _point):
    m = QMenu()    

    a = QAction("Add selected to selection", self) 
    self.connect(a, SIGNAL("triggered()"), lambda e=self: add_to_selection(e))
    m.addAction(a)

    a = QAction("Clear selection", self) 
    self.connect(a, SIGNAL("triggered()"), lambda e=self: clear_selection(e))
    m.addAction(a)

    a = QAction("search for selected", self)
    self.connect(a, SIGNAL("triggered()"), lambda e=self: filterForSelected(e))
    m.addAction(a)

    m.addSeparator()
    if self.toggledMinimized:
        mstr = "unminimize this table"
    else:
        mstr = "minimize this table"
    a = QAction(mstr, self)
    self.connect(a, SIGNAL("triggered()"), lambda e=self: toggleMinimizeTableView(e))
    m.addAction(a)

    m.exec_(QCursor.pos())
Browser.onContextMenu = onContextMenu



def onSetupMenus(self):
    try:
        m = self.menuView
    except:
        self.menuView = QMenu(_("&View"))
        action = self.menuBar().insertMenu(
            self.mw.form.menuTools.menuAction(), self.menuView)
        m = self.menuView

    a = m.addAction('Show Table/Searchbar and Sidebar')
    a.setCheckable(True)
    a.setChecked(True)
    a.setShortcut(QKeySequence(HOTKEY_TOOGLE_BOTH))
    a.toggled.connect(self.Both)

    a = m.addAction('Show Table/Searchbar')
    a.setCheckable(True)
    a.setChecked(True)
    a.setShortcut(QKeySequence(HOTKEY_TOGGLE_TABLE))
    a.toggled.connect(self.toggleShowHideTableView)

    a = m.addAction('Minimize Table')
    a.setCheckable(True)
    a.setChecked(False)
    a.setShortcut(QKeySequence(HOTKEY_TOGGLE_MINIMIZE_TABLE))
    a.toggled.connect(self.toggleMinimizeTableView)

    a = m.addAction('Show Sidebar')
    a.setCheckable(True)
    a.setChecked(True)
    a.setShortcut(QKeySequence(HOTKEY_TOGGLE_SIDEBAR))
    a.toggled.connect(self.toggleSidebar)


    m.addSeparator()
    a = QAction("Add selected to selection", self)
    a.setShortcut(QKeySequence(HOTKEY_ADD_SELECTED_TO_SELECTED)) 
    self.connect(a, SIGNAL("triggered()"), lambda e=self: add_to_selection(e))
    m.addAction(a)

    a = QAction("clear selection", self)
    a.setShortcut(QKeySequence(HOTKEY_CLEAR_SELECTED)) 
    self.connect(a, SIGNAL("triggered()"), lambda e=self: clear_selection(e))
    m.addAction(a)

    a = QAction("search for selected", self)
    #a.setShortcut(QKeySequence(HOTKEY_SEARCH_FOR_SELECTED))   # doesn't work ?:  QAction::eventFilter: Ambiguous shortcut overload: Ctrl+T, L
    self.connect(a, SIGNAL("triggered()"), lambda e=self: filterForSelected(e))
    m.addAction(a)

    # a = m.addAction('search for selected')
    # a.setShortcut(QKeySequence(HOTKEY_SEARCH_FOR_SELECTED))
    # a.toggled.connect(self.filterForSelected)
    # #self.connect(a, SIGNAL("triggered()"), lambda b=self: filterForSelected(b))
addHook("browser.setupMenus", onSetupMenus)



def onSetupMenus(self):
    c = self.connect; f = self.form; s = SIGNAL("triggered()")
    c(f.actionFind, s, self.onThisFind)
    #self.onBoth = QShortcut(QKeySequence(HOTKEY_TOOGLE_BOTH), self)
    #c(self.onBoth, SIGNAL("activated()"), self.Both)
    self.onFilterForSelected = QShortcut(QKeySequence(HOTKEY_SEARCH_FOR_SELECTED), self)
    c(self.onFilterForSelected, SIGNAL("activated()"), self.Both)

    self.form.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
    self.form.tableView.customContextMenuRequested.connect(self.onContextMenu)
Browser.setupMenus = wrap(Browser.setupMenus, onSetupMenus, "after")



def stylesheetOnInit(self,mw):
    # QSplitter::handle:vertical doesn't work. 
    # applying the stylesheet should work in general. A different background color is applied.
    #https://doc.qt.io/archives/qt-4.8/stylesheet-examples.html#customizing-qsplitter via https://stackoverflow.com/questions/15382588/qsplitter-handle-bar
    #https://stackoverflow.com/questions/44924036/customize-qsplitter-handle-color)
    splitterstylesheet = """
    QSplitter::handle:vertical { 
        height: 151px;
    }
    QSplitter::handle:horizontal { 
        height: 151px;
    }
    QSplitter::handle
    {
        background-color: rgb(255, 85, 0);
    }
    """
    self.form.splitter.setStyleSheet(splitterstylesheet)
#Browser.__init__ = wrap(Browser.__init__,stylesheetOnInit,"after")
