# Deux usages : téléphone ou clavier officiel

Actualisation du 24 octobre 2026 : le démarrage sur eMMC avec clavier officiel
a sélectionné le paysage (écran et tactile transform=3). Le menu tactile a
depuis été confirmé par le propriétaire. Les essais exhaustifs de touches et
le hotplug restent non validés. Voir [l'état actuel](CURRENT-STATUS.md).

Cette intégration conserve Hyprland et Omarchy Mobile. Elle ajoute une connexion SDDM au toucher, sans connexion automatique ni changement de mot de passe.

| Situation au démarrage | Profil prévu |
|---|---|
| PinePhone Keyboard absent | Portrait, écran et tactile en transformation 0 ; Squeekboard actif |
| PinePhone Keyboard détecté | Paysage adapté au clavier, écran et tactile en transformation 3 ; clavier à l'écran masqué |

La console conserve ses propres rotations : 0 en portrait, 1 en paysage. Elles ne doivent pas être confondues avec celles du compositeur. La disposition XKB matérielle existante est conservée.

La détection vérifie le nom `PinePhone Keyboard` et le chemin I2C `5-0015` des entrées sysfs. Elle est effectuée à l'ouverture du greeter et de la session. **Ce n'est pas une détection fiable du retrait à chaud** : le noyau peut garder une entrée après retrait physique. Éteindre avant de monter ou de retirer le clavier, puis redémarrer. La détection avec clavier sous le noyau DanctNIX reste à tester.

Le greeter et la session disposent chacun de leur propre bus D-Bus et processus Squeekboard. Les demandes de visibilité utilisent l'interface existante `sm.puri.OSK0.SetVisible`. Le greeter fournit des champs utilisateur/mot de passe et un bouton de connexion au toucher ; SDDM garde la responsabilité de l'authentification. La sélection de session vise le fichier `/usr/share/wayland-sessions/omarchy-ppp.desktop` via le rôle `FileRole` de SDDM, indépendamment du libellé affiché.

Dans le lanceur, « Mode téléphone — portrait et clavier tactile » et « Mode clavier — paysage » permettent une correction manuelle. `ppp-display landscape` pointe maintenant vers la transformation 3, comme le profil paysage qui a déjà été observé dans le bon sens sur cet appareil. Les raccourcis existants continuent d'appeler ce helper.

## Installation sur la SD existante

Prérequis : base expérimentale déjà provisionnée, compte local avec mot de passe, Hyprland `0.56.2-7`, SDDM `0.21.0-7`, Squeekboard `1.43.1-6`, Python `3.14.8-1`, Qt base `6.12.0-3` et Qt declarative `6.12.0-2`. Ces versions figurent dans `installed-before.txt`. Aucun paquet nouveau n'est nécessaire.

Après examen du script, depuis le dépôt copié sur la SD :

```sh
sudo bash install-input-modes.sh
```

L'installateur refuse une racine sur eMMC, sauvegarde les configurations modifiées, installe les profils et le greeter, active SDDM et sélectionne `graphical.target`. Il ne redémarre pas le téléphone et n'active pas de connexion automatique. Il ne change aucun noyau, firmware ou partition. Il est également utilisable dans un chroot ARM64 correctement préparé de la SD, comme pendant cette intervention ; ne pas monter le `/run` du système hôte dans ce chroot.

**Limite de provisionnement :** le script refuse une base sans `/var/lib/omarchy-ppp/provisioned`. La création initiale du mot de passe entièrement au toucher dans une image neuve reste à réaliser. Le compte de la SD utilisée ici est déjà provisionné.

Les sauvegardes privées et le journal sont dans `/var/lib/omarchy-ppp/input-modes/`. Ne pas publier ces sauvegardes. La version initiale des fichiers modifiés est conservée dans `before/root/`, et l'ancienne cible systemd dans `before/default-target`.

## État des vérifications

| Point | État |
|---|---|
| Détection absente/présente, rotations écran et tactile | Tests simulés réussis |
| Rotation de console, erreur OSK, lancement OSK | Tests simulés réussis |
| Python et tests de logique sur ARM64 | Exécutés en chroot sur le PinePhone |
| Lua du greeter | `Hyprland --verify-config` réussi en chroot |
| Lua de la session complète et unités systemd | Vérifications Hyprland et `systemd-analyze verify` réussies en chroot |
| Formulaire QML et sélection de session | Chargement Qt 6 réussi avec modèles simulés, moteur RHI nul |
| Greeter SDDM en mode test | Thème chargé hors écran, sans authentification ni rendu réel |
| Reconnaissance de session | Régression reproduite, puis corrigée et contrôlée avec le vrai modèle SDDM en chroot |
| Greeter sans clavier physique et connexion tactile | Fonctionnement confirmé par l'utilisateur après correction du sélecteur |
| Session sans clavier | Racine SD, session locale seat0, Hyprland et Squeekboard en fonctionnement ; écran et tactile en transformation 0, aucune erreur de configuration |
| Saisie tactile dans Foot | Saisie de `echo test`, touche Entrée et résultat `test` confirmés par l'utilisateur |
| Paysage automatique avec clavier officiel | À tester après démarrage avec clavier monté |
| Montage/retrait du clavier à chaud | Non pris en charge par cette détection |

Les premiers essais QML avec un contexte OpenGL hors écran ont avorté dans le chroot. Avec `QSG_RHI_BACKEND=null`, le formulaire se charge et son modèle de session est reconnu ; cela ne valide aucun rendu GPU. Les essais en chroot utilisent le noyau Sailfish, pas le noyau de la SD.

Le premier essai matériel du greeter affichait « Session Omarchy Mobile absente ». Le sélecteur lisait `Qt.DisplayRole`, que `SessionModel` de SDDM 0.21 ne fournit pas ; le premier modèle simulé acceptait à tort tous les rôles. Le correctif utilise `FileRole` (`Qt.UserRole + 2`) et son chemin complet. Le test simulé refuse maintenant les rôles inconnus et un second test charge le vrai modèle de SDDM. Après installation du correctif sur la SD et nouveau démarrage, l'utilisateur confirme la connexion tactile. Les contrôles distants confirment une session locale Omarchy, l'écran interne et le tactile en transformation 0, le shell mobile et Foot lancés. Les journaux Squeekboard montrent le chargement du clavier `terminal/us`. L'utilisateur a ensuite confirmé la saisie de `echo test`, la touche Entrée et le résultat `test` dans Foot. Cela valide cette saisie simple, pas l'ensemble des symboles et modificateurs.

## Test matériel court

1. Clavier retiré, démarrer sur SD avec Volume bas avant et pendant la seconde vibration. L'écran attendu est le greeter graphique en portrait, avec le clavier tactile. Toucher le champ du mot de passe si nécessaire.
2. Saisir son mot de passe local, toucher « Se connecter », ouvrir Foot depuis le lanceur et vérifier la saisie tactile. Ne pas transmettre le mot de passe ni une capture de sa saisie.
3. Éteindre, débrancher la charge directe du téléphone, monter le clavier, puis démarrer à nouveau sur SD. L'écran attendu est le greeter en paysage, clavier tactile masqué. Tester ensuite `Ctrl+Alt+M`, le terminal et les symboles. Charger uniquement par le port du clavier lorsqu'il est monté ; son problème de charge reste ouvert.

Pour diagnostiquer par SSH :

```sh
ppp-profile detect
systemctl status sddm --no-pager
journalctl -b -u sddm --no-pager
cat ~/.local/state/omarchy-ppp/keyboard.log
```

Le journal du clavier du greeter est dans le répertoire personnel du compte `sddm`, sous `.local/state/omarchy-ppp/keyboard.log`. Les sorties peuvent contenir des informations personnelles : ne publier que les erreurs utiles, nettoyées. La présence d'un clavier virtuel ne prouve pas la réception des frappes ; le test au doigt est nécessaire.

## Retour à la connexion console

Sauvegarder ses travaux graphiques avant l'arrêt de SDDM. Depuis SSH sur la SD :

```sh
sudo systemctl disable --now sddm
sudo rm -f /etc/sddm.conf.d/90-pinephone-pro.conf /etc/systemd/system/sddm.service.d/pinephone-pro.conf
sudo cp -a /var/lib/omarchy-ppp/input-modes/before/root/. /
sudo systemctl set-default "$(sudo cat /var/lib/omarchy-ppp/input-modes/before/default-target)"
sudo systemctl daemon-reload
sudo systemctl start getty@tty1
```

Si SSH échoue, démarrer normalement sur Sailfish et réparer la SD depuis celui-ci, sans modifier l'eMMC ni le chargeur. Le téléphone doit être éteint avant de retirer sa carte.

## Contrôles logiciels

```sh
python3 tests/input-modes.py
python3 tests/check_console.py
bash -n install-input-modes.sh
```

Sur le système ARM64 cible, avec un `XDG_RUNTIME_DIR` privé et valide :

```sh
Hyprland --verify-config --config /usr/share/omarchy-ppp/hypr/greeter.lua
QT_QPA_PLATFORM=offscreen QT_QUICK_BACKEND=rhi QSG_RHI_BACKEND=null /usr/lib/qt6/bin/qml tests/greeter.qml
bash tests/sddm-session.sh
```

`tests/sddm-session.sh` lance un greeter de test hors écran pendant trois secondes, sans saisie ni authentification ; le marqueur `SDDM_SESSION_OK` est obligatoire, un simple délai expiré n'est pas un succès. Il utilise les modèles C++ de SDDM et les fichiers de session du système cible, contrairement au premier test QML simulé.

Ces contrôles ne valident ni l'authentification SDDM réelle, ni les protocoles de saisie Wayland entre Squeekboard et les applications. Les rôles sont documentés dans [SessionModel de SDDM 0.21.0](https://github.com/sddm/sddm/blob/v0.21.0/src/greeter/SessionModel.cpp), et la valeur renvoyée par `FileRole` dans [Session.cpp](https://github.com/sddm/sddm/blob/v0.21.0/src/common/Session.cpp). L'architecture Wayland de SDDM et ses limites sur les méthodes de saisie sont documentées dans les [sources du greeter](https://github.com/sddm/sddm/blob/v0.21.0/src/greeter/GreeterApp.cpp) ; le clavier externe est fourni par le compositeur dans cette intégration.
