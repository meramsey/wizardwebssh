import platform
import sqlite3
import threading
import time

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot, Qt
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QTabWidget, QApplication, QInputDialog, QFileDialog, QPushButton, QStyle

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


class WizardWebssh(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        """ Method that runs forever """
        while True:
            # Start WebSSH Service in background.
            print('Starting SSH websocket server in the background')
            import asyncio

            asyncio.set_event_loop(asyncio.new_event_loop())
            from wizardwebssh.main import main as wssh
            wssh()
            print('Stopped SSH websocket server in the background')
            QApplication.processEvents()
            time.sleep(self.interval)


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
        self.webSettings = browser.settings()
        style = self.style()
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
        browser.titleChanged.connect(lambda _, i=i, browser=browser:
                                     self.setTabText(i, browser.page().title()))
        browser.titleChanged.connect(lambda _, i=i, browser=browser:
                                     self.setTabToolTip(i, browser.page().title()))
        browser.titleChanged.connect(lambda _, i=i, browser=browser: self.setTabIcon(i, QtGui.QIcon(
            style.standardIcon(QStyle.SP_MessageBoxCritical))) if (
                    "WebSSH" in browser.page().title()) else self.setTabIcon(i, QtGui.QIcon(
            style.standardIcon(QStyle.SP_ComputerIcon))))
        # browser.loadFinished.connect(self.on_load_finished)

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

    wizardwebssh_service = WizardWebssh()
    time.sleep(.300)
    # sys.argv.append("--remote-debugging-port=8000")
    # sys.argv.append("--disable-web-security")
    app = QApplication(sys.argv)
    QApplication.setStyle("Fusion")
    #
    # # Now use a palette to switch to dark colors:
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))
    QApplication.setPalette(dark_palette)
    app.setApplicationName("Wizard Assistant SSH")
    app.setOrganizationName("Wizard Assistant")
    app.setOrganizationDomain("wizardassistant.com")
    win = TabbedTerminal()
    win.show()
    app.exec_()
