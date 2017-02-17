import ScreenCloud
from PythonQt.QtCore import QFile, QSettings, QStandardPaths
from PythonQt.QtGui import QDesktopServices, QMessageBox
from PythonQt.QtUiTools import QUiLoader
import time, requests, tempfile, json

class DesuUploader():
    def __init__(self):
        self.uil = QUiLoader()
        self.loadSettings()
        #self.apiUrl = "http://httpbin.org/post" # For debugging only.
        self.apiUrl = "https://doko.moe/upload.php"
        self.linkUrl = "https://a.doko.moe/%s"

    def isConfigured(self):
        return True

    def loadSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("doko.moe")

        self.nameFormat = settings.value("name-format", "screenshot-%H-%M-%S")
        self.copyLink = settings.value("copy-link", "true") in ["true", True]

        settings.endGroup()
        settings.endGroup()

    def saveSettings(self):
        settings = QSettings()
        settings.beginGroup("uploaders")
        settings.beginGroup("doko.moe")

        settings.setValue("name-format", self.settingsDialog.group_name.input_name.text)
        settings.setValue("copy-link", self.settingsDialog.group_clipboard.checkbox_copy_link.checked)

        settings.endGroup()
        settings.endGroup()

    def getFilename(self):
        self.loadSettings()
        return ScreenCloud.formatFilename(self.nameFormat)

    def showSettingsUI(self, parentWidget):
        self.parentWidget = parentWidget
        self.settingsDialog = self.uil.load(QFile(workingDir + "/settings.ui"), parentWidget)
        self.settingsDialog.group_name.input_name.connect("textChanged(QString)", self.nameFormatEdited)
        self.settingsDialog.connect("accepted()", self.saveSettings)
        self.updateUi()
        self.settingsDialog.open()

    def updateUi(self):
        self.loadSettings()
        self.settingsDialog.group_name.input_name.setText(self.nameFormat)
        self.settingsDialog.group_clipboard.checkbox_copy_link.setChecked(self.copyLink)

    def upload(self, screenshot, name):
        self.loadSettings()
        tmpFilename = tempfile.gettempdir() + "/" + ScreenCloud.formatFilename(str(time.time()))
        screenshot.save(QFile(tmpFilename), ScreenCloud.getScreenshotFormat())
        #data = {"name": name}

        try:
            imgFormat = "image/%s" % ScreenCloud.getScreenshotFormat()
            files = [
              ('files[]', (name, open(tmpFilename, 'rb'), imgFormat))
            ]

            response = requests.post(self.apiUrl, files=files)
            #response.raise_for_status()

            print(name)
            print(tmpFilename)
            print(imgFormat)
            print(response.text)

            res = json.loads(response.text)
            file_url = self.linkUrl % res["files"][0]["url"]
            print(file_url)

            if self.copyLink:
                ScreenCloud.setUrl(file_url)

        except requests.exceptions.RequestException as e:
            ScreenCloud.setError("Failed to upload to doko.moe: " + e.message)
            return False

        return True

    def nameFormatEdited(self, nameFormat):
        self.settingsDialog.group_name.label_example.setText(ScreenCloud.formatFilename(nameFormat, False))
