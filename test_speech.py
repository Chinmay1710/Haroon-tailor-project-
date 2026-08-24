import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QTimer

app = QApplication(sys.argv)
view = QWebEngineView()
view.setHtml("""
<!DOCTYPE html>
<html>
<body>
<h1 id="res">Testing...</h1>
<script>
    if ('MediaRecorder' in window && navigator.mediaDevices) {
        document.getElementById('res').innerText = 'SUPPORTED';
    } else {
        document.getElementById('res').innerText = 'NOT_SUPPORTED';
    }
</script>
</body>
</html>
""")
view.show()

def check():
    view.page().toHtml(lambda html: print(html))
    QTimer.singleShot(500, app.quit)

QTimer.singleShot(1000, check)
app.exec()
