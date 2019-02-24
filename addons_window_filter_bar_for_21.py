from PyQt5 import QtCore

from aqt.addons import AddonsDialog  
from anki.hooks import wrap
from aqt.qt import *

"""
anki addon that adds filter-bar to add-on window

copyright 2019 ijgnd

This add-on modifies some functions of aqt/addons.py which is
    Copyright: Ankitects Pty Ltd and contributors


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


def after_init(self, addonsManager):
    #add filter bar
    self.filterbar = QLineEdit(self)
    self.filterbar.setPlaceholderText('type here to filter')
    self.form.verticalLayout_2.addWidget(self.filterbar)
    QtCore.QTimer.singleShot(0, self.filterbar.setFocus) #https://stackoverflow.com/a/52858926
    self.filterbar.textChanged.connect(self.filterAddons) 
    #add shortcuts - future compatibility?
    #sconf = QShortcut(QKeySequence("Ctrl+E"), self)
    #sconf.activated.connect(self.onConfig)
AddonsDialog.__init__ = wrap(AddonsDialog.__init__, after_init)


#modification of redrawAddons
def filterAddons(self,text):
    terms = text.lower().split()
    addonList = self.form.addonList
    selected = set(self.selectedAddons())
    addonList.clear()
    for name, dir in self.addons:
        item = QListWidgetItem(name, addonList)
        nl = name.lower()
        for i in terms:
            if i not in nl:
                item.setHidden(True)
                break
        # else:
        #     item.setHidden(False)
        if dir in selected:
            item.setSelected(True)
    addonList.repaint()
AddonsDialog.filterAddons = filterAddons
