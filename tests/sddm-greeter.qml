// SPDX-License-Identifier: MIT
// À charger par sddm-greeter-qt6 --test-mode : vrais modèles, aucune saisie.
import QtQuick
Rectangle {
  Loader {
    id: theme
    source: "../overlay/usr/share/sddm/themes/omarchy-ppp/Main.qml"
  }
  Timer {
    interval: 300
    running: true
    onTriggered: {
      if (theme.status !== Loader.Ready || theme.item.sessionIndex < 0) {
        console.error("SDDM_SESSION_FAILED")
        console.error("SDDM model rows: " + sessionModel.rowCount())
        for (var i = 0; i < sessionModel.rowCount(); i++) {
          console.error("SDDM row " + i + " file: " + sessionModel.data(sessionModel.index(i, 0), Qt.UserRole + 2))
        }
      } else {
        console.log("SDDM_SESSION_OK : session mobile reconnue par le vrai modèle SDDM")
      }
    }
  }
}
