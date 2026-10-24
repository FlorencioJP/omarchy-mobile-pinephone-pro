// SPDX-License-Identifier: MIT
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
  id: root
  width: 480
  height: 853
  color: "#1a1b26"
  property bool failed: false
  property int sessionIndex: {
    for (var i = 0; i < sessionModel.rowCount(); i++) {
      var name = String(sessionModel.data(sessionModel.index(i, 0), Qt.DisplayRole))
      if (name === "Omarchy Mobile (PinePhone Pro)") return i
    }
    return -1
  }
  function login() {
    if (sessionIndex >= 0 && username.text.length && password.text.length)
      sddm.login(username.text, password.text, sessionIndex)
  }
  Connections {
    target: sddm
    function onLoginFailed() {
      root.failed = true
      password.clear()
      password.forceActiveFocus()
    }
  }
  ColumnLayout {
    anchors.horizontalCenter: parent.horizontalCenter
    y: Math.max(20, root.height * 0.12)
    width: Math.min(360, root.width - 40)
    spacing: 14
    Label {
      text: "Omarchy"
      color: "#c0caf5"
      font.pixelSize: 32
      Layout.alignment: Qt.AlignHCenter
    }
    TextField {
      id: username
      text: userModel.lastUser || "terminal"
      placeholderText: "Utilisateur"
      font.pixelSize: 20
      Layout.fillWidth: true
      Layout.preferredHeight: 52
      inputMethodHints: Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
      onAccepted: password.forceActiveFocus()
    }
    TextField {
      id: password
      placeholderText: "Mot de passe"
      echoMode: TextInput.Password
      font.pixelSize: 20
      Layout.fillWidth: true
      Layout.preferredHeight: 52
      inputMethodHints: Qt.ImhSensitiveData | Qt.ImhNoPredictiveText | Qt.ImhNoAutoUppercase
      onAccepted: root.login()
      onTextChanged: root.failed = false
    }
    Button {
      text: "Se connecter"
      font.pixelSize: 20
      focusPolicy: Qt.NoFocus
      Layout.fillWidth: true
      Layout.preferredHeight: 52
      enabled: root.sessionIndex >= 0 && username.text.length > 0 && password.text.length > 0
      onClicked: root.login()
    }
    Label {
      text: root.sessionIndex < 0 ? "Session Omarchy Mobile absente" : root.failed ? "Connexion refusée" : ""
      color: "#f7768e"
      Layout.fillWidth: true
      wrapMode: Text.WordWrap
    }
  }
  Component.onCompleted: password.forceActiveFocus()
}
