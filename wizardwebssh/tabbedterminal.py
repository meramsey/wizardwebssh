import platform
import sqlite3
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QTabWidget, QApplication, QInputDialog, QFileDialog, QPushButton


# if platform.system() == "Linux":
#     try:
#          import ctypes
#          ctypes.CDLL('libGL.so.1', ctypes.RTLD_GLOBAL)
#          libgcc_s = ctypes.CDLL("libgcc_s.so.1")
#     except:
#          pass

import os
import sys

free_port = '8889'

settings = QtCore.QSettings('WizardAssistant', 'WizardAssistantDesktop')

if settings.contains("wizardwebsshport"):
    # there is the key in QSettings
    # print('Checking for wizardwebsshport in config')
    wizardwebsshport = settings.value('wizardwebsshport')
    # print('Found wizardwebsshport port in config:' + wizardwebsshport)
    free_port = wizardwebsshport
else:
    print('wizardwebsshport not found in config')
    pass

try:
    ssh_terminal_url = 'http://localhost:' + str(free_port)
    print(ssh_terminal_url)
except:
    pass


class TabbedTerminal(QTabWidget):
    def __init__(self, parent=None):
        super(TabbedTerminal, self).__init__(parent)

        self.setDocumentMode(True)
        self.setTabPosition(QTabWidget.South)
        self._new_button = QPushButton(self)
        self._new_button.setText("New SSH Session")
        self._new_button.clicked.connect(self.add_new_tab)
        self.setCornerWidget(self._new_button)
        self.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.currentChanged.connect(self.current_tab_changed)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_current_tab)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)
        self.add_new_tab(QUrl(ssh_terminal_url), 'Homepage')

        # self.show()

        self.setWindowTitle("Wizard Assistant SSH")
        self.setWindowIcon(QIcon(os.path.join('images', 'ma-icon-64.png')))

    def add_new_tab(self, qurl=ssh_terminal_url, label="Blank"):

        # if qurl is None:
        # qurl = QUrl('http://localhost:8888/')
        qurl = QUrl(ssh_terminal_url)

        browser = QWebEngineView()
        # self.webSettings = browser.settings()
        # self.webSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        # self.webSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        # self.webSettings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        # self.webSettings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        # self.webSettings.setAttribute(QWebEngineSettings.JavascriptCanPaste, True)
        # self.webSettings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        # self.webSettings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        # self.webSettings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        # self.webSettings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        browser.setUrl(qurl)
        i = self.addTab(browser, label)

        self.setCurrentIndex(i)

        # More difficult! We only want to update the url when it's from the
        # correct tab
        # browser.urlChanged.connect(lambda qurl, browser=browser:
        #                           self.update_urlbar(qurl, browser))

        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:  # No tab under the click
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.currentWidget().url()
        self.update_title(self.currentWidget())

    def close_current_tab(self, i):
        if self.count() < 2:
            return

        self.removeTab(i)

    def update_title(self, browser):
        if browser != self.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.currentWidget().page().title()
        self.setWindowTitle("%s - Wizard Assistant SSH" % title)

    def navigate_webssh(self):
        self.currentWidget().setUrl(QUrl(ssh_terminal_url))

    def navigate_home(self):
        self.currentWidget().setUrl(QUrl(ssh_terminal_url))

    def navigate_to_url(self):  # Does not receive the Url
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        self.currentWidget().setUrl(q)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                                  "SSH Private Key (id_*);;"
                                                  "All files (*.*)")

        if filename:
            with open(filename, 'rb') as f:
                sshkeyprivate = f.read()
        f.close()


if __name__ == "__main__":
    import sys

    # sys.argv.append("--remote-debugging-port=8000")
    # sys.argv.append("--disable-web-security")
    app = QApplication(sys.argv)
    app.setApplicationName("Wizard Assistant SSH")
    app.setOrganizationName("Wizard Assistant")
    app.setOrganizationDomain("wizardassistant.com")
    win = TabbedTerminal()
    win.show()
    app.exec_()
