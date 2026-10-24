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
      } else {
        console.log("SDDM_SESSION_OK : session mobile reconnue par le vrai modèle SDDM")
      }
    }
  }
}
