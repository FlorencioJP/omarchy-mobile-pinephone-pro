// SPDX-License-Identifier: MIT
// Chargement réel du thème ; les modèles de connexion restent simulés.
import QtQuick
import QtQuick.Window

Window {
  width: 480
  height: 853
  visible: true
  property QtObject userModel: QtObject { property string lastUser: "terminal" }
  property QtObject sessionModel: QtObject {
    function rowCount() { return 2 }
    function index(row, column) { return row }
    // SDDM 0.21 ne fournit pas Qt.DisplayRole ; FileRole vaut UserRole + 2.
    function data(index, role) {
      if (role !== Qt.UserRole + 2) return undefined
      return index === 1 ? "/usr/share/wayland-sessions/omarchy-ppp.desktop" : "/usr/share/wayland-sessions/hyprland.desktop"
    }
  }
  property QtObject sddm: QtObject {
    signal loginFailed()
    function login(user, password, session) { throw new Error("Authentification interdite pendant le test") }
  }
  Loader {
    id: theme
    anchors.fill: parent
    source: "../overlay/usr/share/sddm/themes/omarchy-ppp/Main.qml"
  }
  Timer {
    interval: 500
    running: true
    onTriggered: {
      if (theme.status !== Loader.Ready || theme.item.sessionIndex !== 1) {
        console.error("GREETER_QML_FAILED")
        Qt.exit(1)
      } else {
        console.log("GREETER_QML_OK : thème chargé, session reconnue, aucune authentification")
        Qt.quit()
      }
    }
  }
}
