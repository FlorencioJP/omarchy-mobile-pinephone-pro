# Omarchy Mobile sur PinePhone Pro — complément expérimental

[English overview](README.md)

Ce dépôt complète le prototype microSD existant. Il conserve DanctNIX, son noyau et le profil mobile, puis rétablit les accès aux outils Omarchy et prépare un premier lot d'applications graphiques ARM64. Ce n'est pas l'installateur Omarchy officiel et il ne lance pas celui-ci.

## État après installation sur le téléphone

Le premier lot est installé : 203 paquets ajoutés, aucun paquet préexistant modifié, et `pacman -Dk` réussit. Le profil Hyprland charge maintenant le module de raccourcis et `hyprctl configerrors` ne rapporte pas d'erreur. Chromium a chargé le site Omarchy ; des fenêtres Nautilus et GNOME Text Editor ainsi que le catalogue du menu ont été contrôlés par captures sur le téléphone. Le premier démarrage des applications GTK a demandé l'initialisation des portails ; la présence d'une fenêtre n'est pas assimilée à une validation fonctionnelle exhaustive.

Le complément terminal est également installé : 37 paquets supplémentaires, soit 710 paquets au total, sans remplacement ni suppression de paquet préexistant. Le verrou `terminal.packages.lock.json` contient versions, architectures, tailles, SHA-256, URL et licences déclarées. Les 37 signatures ont été vérifiées ; `pacman -Dk` réussit après installation. Le lot représente 30,7 Mio téléchargés et 124,4 Mio installés. Il ajoute notamment Neovim, tmux, bash-completion, bat, eza, fd, fzf, lazygit, less, man-db, ripgrep, rsync, starship, unzip, wget, zip, zoxide et xdg-terminal-exec.

Les tests Neovim sans interface, session tmux isolée, filtrage fzf/ripgrep et sélection de Foot par `xdg-terminal-exec` réussissent sur le processeur du PinePhone, dans un chroot de la SD, sous le noyau Sailfish. Cela ne valide ni la nouvelle session graphique ni le clavier physique sous le noyau DanctNIX. Les SHA-256 du noyau SD, de son initramfs et de `boot.scr` sont restés identiques. NetworkManager, Bluetooth, ModemManager et eg25-manager sont activés dans la SD ; cela ne constitue pas un test Bluetooth ou 4G.

Le compositeur identifie `Mali-T860 MC4 (Panfrost)` dans son journal. Le contexte GLES 3.2 échoue puis le rendu utilise le contexte de repli GLES 3.0. Aucun benchmark graphique ni essai prolongé n'a été effectué.

La charge depuis le clavier reste un obstacle avant migration : pendant ces essais, la batterie du clavier était en charge, vers 77 %, mais le téléphone à 11–12 % avec un courant rapporté proche de −665 mA. Le changement de chargeur et un appui bref sur le bouton du clavier n'ont pas fait passer le téléphone en charge. La limite d'entrée du téléphone est déjà de 2 A ; elle n'a pas été modifiée. Le pilote `ppkb-power` est lié et la sortie `ip5xxx-boost` indique 1. Cela ne démontre pas une alimentation effective du téléphone. Pour charger directement le téléphone, le clavier doit être retiré au préalable, appareil éteint ; sa batterie peut alimenter le téléphone même lorsque son propre câble est débranché. Après retrait du clavier, la charge directe sous Sailfish a atteint 100 % ; cela ne résout pas la charge à travers le clavier.

Le test comparatif a ensuite été effectué par redémarrage normal sur Sailfish `4.5.0.24`, noyau `6.5.0-pinephonepro`, avec le même clavier et le même chargeur. Sailfish rapporte également le téléphone en décharge : 10 %, courant −1 319 mA, clavier en charge à 80 %, limite d'entrée téléphone 2 A et pilote `ppkb-power` lié. Le courant a été relevé après le démarrage, avec une charge système différente : ces valeurs ne permettent pas de comparer l'efficacité des deux OS. Elles montrent que l'absence de charge n'est pas exclusive au portage. Le téléphone a été éteint proprement depuis Sailfish pour permettre une recharge directe, clavier retiré. Aucune calibration ou modification des limites de charge n'a été effectuée, et aucune installation sur eMMC n'a commencé.

## Sources et versions

L'amont examiné est [omacom/omarchy](https://github.com/omacom/omarchy), sous licence MIT, au commit `f643adc38ad65c4900609c5c1b0b5c359fef147a`. Ses consignes `AGENTS.md`, d'installation et de vérification visuelle ont été lues. Le système testé utilise Omarchy `4.0.6-1`, Hyprland `0.56.2-7`, Quickshell `0.3.2.r7.g2b4501a-1` et le noyau `6.18.55-1-megi-danctnix`. `upstream.lock.json` distingue la référence examinée du runtime réellement installé : aucun remplacement automatique par la branche amont courante.

`installed-before.txt` fige l'inventaire précédent et `packages.lock.json` les noms, versions, architectures, tailles, SHA-256 et URL des 203 paquets supplémentaires. La résolution dans des bases actuelles isolées n'ajoute que de nouveaux paquets et ne remplace aucun paquet déjà installé. Le lot représente environ 391 Mio compressés et 1 616,5 Mio installés.

## Ce qui est ajouté

Les [deux modes d'entrée](INPUT-MODES.md) sont maintenant implémentés et installés sur la SD : portrait avec clavier tactile sans clavier physique, paysage avec le clavier officiel, et greeter graphique SDDM avec authentification par mot de passe. Après correction du sélecteur de session, l'utilisateur confirme la connexion tactile sans clavier physique. La session locale est ouverte sur SD, écran et tactile en transformation 0, Hyprland, Squeekboard et Foot en fonctionnement, sans erreur de configuration. Le nouveau chemin automatique avec clavier physique et la saisie tactile dans Foot restent à tester. Le premier provisionnement entièrement tactile d'une image neuve reste bloqué.

- Entrée « Menu Omarchy » dans le lanceur mobile et activation des panneaux natifs menu, thèmes, presse-papiers, emojis et agent d'authentification. Les extensions et la barre mobiles sont conservées.
- `Ctrl+Alt+M` : menu ; `Ctrl+Alt+Tab` : applications actives ; `Ctrl+Alt+C` : presse-papiers. Après installation des applications : `Ctrl+Alt+B` navigateur, `Ctrl+Alt+F` fichiers et `Ctrl+Alt+E` éditeur.
- Chromium, Nautilus, GNOME Text Editor, Evince, imv, mpv, LibreOffice, pavucontrol, Blueman, btop, gum, grim et wl-clipboard, avec leurs dépendances.

Le clavier graphique utilise déjà Alt droit + 9 pour le trait d'union, et Alt droit + Maj + 9 pour le soulignement, d'après le fichier XKB installé. Cela ne valide pas la même combinaison dans la console Linux, qui utilise une autre disposition.

## Installer sur la SD déjà démarrée

Copier ce dépôt dans `/home/terminal/portage` sur le téléphone, sans clé privée. Depuis ce dossier, avec le compte `terminal` :

```sh
python3 download.py
bash configure-user.sh
sudo bash install.sh
```

Puis ajouter le complément terminal, sans relancer le premier lot :

```sh
python3 download.py --terminal
sudo bash install.sh --terminal
bash tests/terminal-smoke.sh
```

Ce second mode refuse également tout remplacement d'un paquet installé par une autre version. Il calcule son besoin d'espace à partir des tailles installées verrouillées, avec une réserve de 128 Mio. Les journaux et inventaires avant/après sont dans `/var/lib/omarchy-ppp/terminal`. La sauvegarde privée `config-and-pacman-before.tar.gz`, créée pendant l'intervention, contient des configurations personnelles : elle reste sur la SD avec des droits restreints et ne doit pas être publiée. Elle ne remplace pas une sauvegarde complète de la carte.

L'installation observée a été effectuée depuis Sailfish dans un chroot ARM64 de la SD, avec `/dev`, `/dev/pts`, `/proc` et `/sys` disponibles et `SYSTEMD_OFFLINE=1`. Les hooks ont été examinés et exécutés normalement ; le rechargement du gestionnaire système a été explicitement ignoré en chroot. Le script public ci-dessus reste destiné à une SD Omarchy déjà démarrée. L'accès SSH administratif a été activé sur cette SD pour le prochain démarrage, avec la clé temporaire déjà présente ; cette activation n'est pas incorporée à une image publique.

Le téléchargement s'effectue sans privilèges. Chaque archive est contrôlée par SHA-256 et par sa signature avec le trousseau public Arch Linux ARM du système. `install.sh` vérifie à nouveau le lot et impose `LocalFileSigLevel = Required` à sa transaction pacman, dans une configuration séparée. Il refuse une racine active sur eMMC, une autre architecture, les paquets de noyau/chargeur et les archives altérées ou sans signature. Il ne lance ni `pacman -Syu`, ni mise à jour du noyau, ni procédure Pixel.

Les bases de paquets présentes dans l'image dataient de décembre 2025 et produisaient des conflits avec les bibliothèques installées en octobre 2026. Les métadonnées récentes ont été téléchargées dans `~/.cache/omarchy-ppp-audit/db` pour la résolution ; les bases système n'ont pas été rafraîchies pendant cet audit. Les paquets sont installés depuis le lot figé avec `pacman -U`.

L'installateur sauvegarde le profil graphique dans `/var/lib/omarchy-ppp/desktop/hyprland.lua.before`, installe le module Lua puis ajoute son chargement au profil PinePhone. Les contrôles Lua et `pacman -Dk` doivent réussir. Le marqueur final attendu est `DESKTOP_INSTALL_COMPLETE`. Le journal est `/var/lib/omarchy-ppp/desktop/install.log`. La configuration utilisateur précédente reste dans `~/.config/omarchy/shell.json.before-portage`.

Les scripts d'installation et hooks contenus dans les nouvelles archives ont été examinés : caches GTK4, notification GVFS, cache Graphviz et activation du service de dossiers utilisateur XDG. Ils sont conservés sur le téléphone dans `~/portage/scriptlets-review.log` pour diagnostic.

## Stockage et migration eMMC

La microSD physique fait 512 Go, mais la partition racine actuelle ne fait que 7,9 Gio (7,7 Gio utilisables). Le premier lot tient dans l'espace disponible ; l'agrandissement de la partition reste une étape séparée, non effectuée ici. Le script d'installation ne repartitionne rien.

L'utilisateur a autorisé l'installation finale sur eMMC en remplacement de Sailfish. Elle reste à préparer après les essais du lot applicatif. Il faudra relever sa capacité et son partitionnement, conserver le chargeur existant, adapter les références de racine et vérifier un démarrage sans SD. Une SD agrandie à 512 Go ne doit pas être copiée brute sur une eMMC de capacité inférieure. Aucune migration n'est exécutée par ces scripts.

## Validation

| Élément | État au moment de la préparation |
|---|---|
| SD, console paysage, saisie et connexion | Testés par l'utilisateur |
| Hyprland et interface mobile | Démarrés sur le téléphone |
| Sens du paysage graphique | Confirmé par l'utilisateur |
| Wi-Fi | Confirmé par l'utilisateur |
| Menu Omarchy et raccourcis M/Tab/C | Configurés dans la session ; menu contrôlé par capture distante |
| Configuration utilisateur | Tests de préservation, sauvegarde et idempotence passés sur ARM64 |
| Téléchargement du lot | 203 archives et signatures vérifiées sur le téléphone |
| Applications du lot | Installées ; navigateur, fenêtres de fichiers, éditeur et catalogue contrôlés par captures |
| Complément terminal | 37 paquets installés et signés ; tests logiciels ARM64 en chroot réussis ; session graphique après ajout non testée |
| Connexion tactile et deux profils | Connexion sans clavier confirmée sur SD après correction ; portrait écran/tactile et session contrôlés ; détection automatique avec clavier à tester |
| Persistance des nouveaux raccourcis | Module installé et chargé ; redémarrage encore à tester |
| Rendu du compositeur | Pilote Panfrost identifié sur le téléphone ; aucun benchmark |
| Tactile précis, veille et autonomie | Non validés |
| Charge du téléphone depuis le clavier | Problème constaté : téléphone toujours en décharge |
| Agrandissement de la SD et migration eMMC | Non effectués |

Une capture d'écran ne prouve pas l'accélération matérielle. Les fonctions Omarchy qui supposent son installation complète, notamment noyaux, chiffrement, snapshots ou réinstallation système, ne sont pas validées sur cette base ext4 mobile.

## Complétude par rapport au dépôt officiel

`upstream-defaults.packages` conserve les 164 noms du socle et des ajouts ARM64 du commit étudié. Après le complément terminal, 56 correspondent à un paquet installé ou à un fournisseur identifié ; 108 restent à examiner, ce qui ne constitue pas une installation complète d'Omarchy. `upstream-coverage.tsv` distingue les versions installées, les dépôts et les architectures annoncées. La comparaison par nom exact ne remplace pas une vérification des fournisseurs virtuels ou des alias : `dotnet-runtime-bin` fournit notamment `dotnet-runtime`. Sur l'appareil, `pacman -Qo` confirme que `nvim` appartient à `neovim 0.12.6-1` et `vi` à `ex-vi-compat 3-1`, déjà présent dans la base ; la disponibilité actuelle de ce dernier fournisseur n'a pas été réauditée.

Lors de l'audit précédant le complément terminal, les métadonnées stables Omarchy contenaient 31 des autres noms manquants, dont Omacalc, Omawrite, Omasnap, Obsidian et LocalSend ; 91 figuraient dans les bases Arch Linux ARM. Ce sont des disponibilités annoncées ; les applications Omarchy citées restent non installées et non testées. Le dépôt Omarchy ARM64 officiel examiné utilise `https://pkgs.omarchy.org/stable/aarch64` et un miroir système ARM dédié. Ces fournisseurs n'ont pas été ajoutés à la configuration pacman active du téléphone pendant cette étape.

`packages.licenses.tsv` conserve les licences déclarées des 203 archives du premier lot, associées à leur version. Ces données proviennent des entrées de dépôt dont le SHA-256 correspond exactement au verrou ; il ne s'agit pas d'un audit juridique exhaustif.

## Contrôles et retour arrière

```sh
python3 tests/download.py
python3 tests/terminal-lock.py
bash tests/user-configure.sh
bash -n install.sh
luac5.4 -p overlay/usr/share/omarchy-ppp/hypr/desktop.lua
```

Sur le système ARM64 cible, sans sudo : `bash tests/terminal-smoke.sh`. Ce test crée puis détruit sa propre session tmux ; les sessions persistantes de travail restent hébergées sur les machines distantes.

Restaurer `shell.json.before-portage` permet de revenir à la configuration mobile précédente. La restauration de `hyprland.lua.before` retire le chargement des nouveaux raccourcis. Cela ne désinstalle pas les paquets ajoutés. Conserver la SD pour récupérer le téléphone pendant la future migration eMMC ; aucune manipulation de la SPI n'est prévue.

Ne pas redistribuer une copie du système utilisé sans retirer les secrets créés ensuite par l'utilisateur. Ce dépôt ne contient aucun identifiant de connexion, mot de passe, clé privée ou configuration Wi-Fi personnelle. La clé SSH d'administration temporaire utilisée depuis le Mac n'appartient pas au dépôt et devra être révoquée à la fin de l'intervention.
