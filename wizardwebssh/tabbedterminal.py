from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PySide2.QtWidgets import QTabWidget, QApplication, QInputDialog, QFileDialog
from PySide2 import QtPrintSupport

import os
import sys


class TabbedTerminal(QTabWidget):
    def __init__(self, parent=None):
        super(TabbedTerminal, self).__init__(parent)

        self.setDocumentMode(True)
        self.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.currentChanged.connect(self.current_tab_changed)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_current_tab)

        # Uncomment to disable native menubar on Mac
        # self.menuBar().setNativeMenuBar(False)

        self.add_new_tab(QUrl('http://localhost:8888/'), 'Homepage')

        # self.show()

        self.setWindowTitle("Wizard Assistant SSH")
        self.setWindowIcon(QIcon(os.path.join('images', 'ma-icon-64.png')))

    def add_new_tab(self, qurl=None, label="Blank"):

        if qurl is None:
            qurl = QUrl('http://localhost:8888/')

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
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

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
        self.currentWidget().setUrl(QUrl("http://localhost:8888/"))

    def navigate_home(self):
        self.currentWidget().setUrl(QUrl("http://localhost:8888/"))

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
