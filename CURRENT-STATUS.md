# État du projet

## Mise à jour vers Omarchy 4.5.0 — 5 novembre 2026

Installation eMMC du propriétaire, mise à jour depuis Omarchy `4.0.6-1`.

**Panne.** La mise à jour échouait. `/etc/pacman.conf` et
`/etc/pacman.d/mirrorlist` avaient été remplacés par la configuration x86
d'Omarchy : canal `rc`, `[multilib]`, miroirs `rc-mirror.omarchy.org` (aucun
paquet `aarch64`). Les dépôts DanctNIX et Arch Linux ARM avaient disparu. La
cause probable est un changement de canal (`omarchy-channel-set`) ; l'heure de
modification l'indique, la commande n'a pas été observée. `pacman.conf.bak` était
lui aussi la version x86 : la configuration d'origine était perdue.

**Réparation.** Les deux fichiers ont été sauvegardés (suffixe `.x86-20261105`),
puis remplacés par :

```ini
[danctnix]
Server = https://p64.arikawa-hi.me/$repo/$arch/

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist

[alarm]
Include = /etc/pacman.d/mirrorlist

[aur]
Include = /etc/pacman.d/mirrorlist

# En dernier : Omarchy ne remplace jamais la base du téléphone
[omarchy]
Server = https://pkgs.omarchy.org/stable/$arch
```

avec `Server = http://mirror.archlinuxarm.org/$arch/$repo` dans `mirrorlist`.
Le crochet pacman d'Omarchy bloque une mise à jour directe ; elle a été lancée
avec `sudo env OMARCHY_ALLOW_DIRECT_PACMAN=1 pacman -Syu`. 27 paquets : Omarchy
`4.5.0-3`, Hyprland `0.57.1-1`. Noyau `linux-megi 6.18.57-1` et amorçage inchangés.

**Initramfs.** `omarchy-settings` 4.5 installe
`/etc/mkinitcpio.conf.d/00-omarchy-hooks.conf`. Sur la plateforme `aarch64`, il
impose les crochets d'un PC (`encrypt`, `btrfs-overlayfs`, absent ici). Le
prochain noyau aurait donc produit un initramfs différent. Le fichier
`/etc/mkinitcpio.conf.d/zz-pinephone-pro-hooks.conf`, lu en dernier et hors
paquet, reprend la ligne `HOOKS=` de `/etc/mkinitcpio.conf`. Une construction de
test vers `/tmp` a réussi ; l'initramfs de `/boot` n'a pas été modifié.

**Migrations.** 98 migrations Omarchy étaient en attente ; `omarchy-migrate` les
lance à la connexion. Neuf ont été lancées : retrait des anciens droits sudo sans
mot de passe, protection polkit, BBR, ARP, rechargement de NetworkManager,
portail GNOME Keyring et trois réparations du fond d'écran. Les 89 autres ont
été marquées faites sans être lancées : matériel absent (N1x, ASUS, Dell, DGX,
Snapdragon, Intel), agents de code via `mise`, applications lourdes (fonds vidéo
OWE…), modifications de la barre et des raccourcis d'Omarchy (le téléphone a sa
propre configuration Hyprland), Limine, `usbguard`, `power-profiles-daemon`.
Leur liste est sur le téléphone, dans
`~/.local/state/omarchy/migrations-skipped-pinephone-20261105.txt`.

**Vérifié après redémarrage.** Démarrage eMMC, aucun service système ou
utilisateur en échec, Wi-Fi connecté, aucune migration en attente, Hyprland
avec la configuration du téléphone, barre Quickshell, Squeekboard, fond d'écran
présent, paysage avec clavier (`transform: 3`). Le propriétaire confirme un
affichage normal. Non testés : son, veille, Wi-Fi après reprise.

**Raccourcis `Ctrl+Alt` après la mise à jour.** `Ctrl+Alt+M` et tous les
raccourcis qui passent par la barre (`Espace`, `Tab`, `C`, `K`) ne faisaient
plus rien ; ceux qui lancent un programme marchaient. Le clavier envoyait bien
les touches. `omarchy-shell` 4.5 parle à la barre par son socket avec `socat`,
absent ici : chaque appel échouait avec « omarchy-shell is not responding ».
`socat` figure dans `/usr/share/omarchy/install/omarchy-base.packages`, pas dans
les dépendances du paquet `omarchy` : une mise à jour ne l'installe pas, et
aucune migration ne l'ajoute. Installé depuis Arch Linux ARM, le menu s'ouvre de
nouveau (confirmé par le propriétaire). Trois autres paquets de la même liste,
signalés par les journaux de la barre, ont été ajoutés : `qt6-imageformats`
(fond WebP de l'écran de verrouillage, « Unsupported image format »),
`imagemagick` et `inotify-tools`. Les autres absences de cette liste semblent
voulues pour le téléphone et n'ont pas été comblées.

**À éviter.** Ne pas lancer `omarchy-channel-set` ni `omarchy-refresh-pacman`
sur le téléphone : ils réécrivent les dépôts pour un PC. Avant un
`omarchy update`, relire les nouvelles migrations.

## Constructeur microSD — 26 octobre 2026

Le constructeur dans [`image/`](image/README.fr.md) part d'une base publique
signée et installe hors ligne 578 paquets verrouillés. Deux constructions propres
ont produit le même inventaire de 629 paquets et le même manifeste de configuration.
Le [rapport logiciel](image/BUILD-REPORT.md) et les [limites](image/VALIDATION.md) sont
distinctes des observations sur le téléphone ci-dessous. Le téléphone n'est
pas connecté ; aucun nouveau résultat matériel n'est annoncé.

## Installation historique — état vérifié au 24 octobre 2026

Portage expérimental sur un PinePhone Pro avec clavier officiel. Les confirmations
du propriétaire, contrôles logiciels sur téléphone et tests de logique sont
distingués ci-dessous. Les paquets ARM64 sont précompilés en amont : aucun de
ces contrôles ne constitue une recompilation complète ni un test d'endurance.

| Fonction | Implémentation / préparation | Preuve sur le téléphone | Limite |
|---|---|---|---|
| Démarrage microSD | Base DanctNIX et profil mobile conservés | Démarrage et connexion confirmés | Pas de nouvelle image publique |
| eMMC | Migration sans repartitionnement, noyau/initramfs conservés | Démarrages eMMC, interface/Wi-Fi/SSH ; SD non montée | Carte encore insérée, démarrage sans SD non testé |
| Tactile / portrait | SDDM et Squeekboard | Connexion et saisie tactile confirmées sur SD | Parcours entièrement tactile d'une image vierge incomplet |
| Clavier / paysage | Détection au démarrage, écran et tactile transform=3 | Chemin automatique paysage observé après démarrage avec clavier | Symboles, modificateurs et confort exhaustifs non validés ; pas de hotplug garanti |
| Bureau | Barre mobile conservée, terminal automatique retiré | Fond Omarchy, barre et menus actifs | Aucun remplacement silencieux par un autre shell |
| Menu tactile | Une tuile Menu Omarchy ajoutée aux réglages rapides | Le propriétaire confirme son fonctionnement | Patch utilisateur déployé localement ; pas encore d'installateur public de cette tuile |
| Thèmes | Tokyo Night, couleurs du shell, bordures et Foot ; GTK sombre | Choix de thème confirmé par le propriétaire | Toutes les applications non contrôlées |
| Batteries | Tableau des deux batteries, champs sysfs en lecture seule | Tableau confirmé ; dernier relevé Full/100 % sur les deux | Charge via clavier et autonomie non validées ; décharge auparavant observée sous les deux OS |
| Wi-Fi | NetworkManager | Connecté et utilisé pour SSH ; power save off | Reconnexion après veille non testée |
| Bluetooth / audio | Services, Blueman/Pavucontrol et menu | Services actifs, outils disponibles | Appairage et son non validés |
| 4G | ModemManager/eg25-manager ; trois paquets ARM64 signés pour l'éditeur | Modem détecté, fenêtre nm-connection-editor affichée | Aucune SIM, aucun profil opérateur ni test de données |
| SSH / tmux | OpenSSH, tmux et lanceurs | SSH de maintenance fonctionnel ; panneaux installés | Accès aux agents distants du propriétaire non configuré |
| Plugins | Huit instantanés figés ; six panneaux adaptés à Wayland | Six surfaces mappées ; mesures Vitals et débit réseau reçues | Gestes et fonctions détaillés à tester ; VPN non configurés |
| Battery Usage / Caffeine | Sources déposées, désactivées | Pas de test fonctionnel | Noms BAT* incompatibles / gestion de veille à valider |
| Veille et autonomie | Délais idle du shell à zéro ; deep exposé par le noyau | Aucun cycle suspend/reprise déclenché pendant cette étape | Réveil, verrouillage tactile, consommation et Wi-Fi après reprise non testés |
| Image reproductible | Lots et plugins figés, helpers et tests publics | Installation privée issue de ces travaux | Au 24 octobre : pas de constructeur complet ; voir le nouveau bilan ci-dessus |

## Versions et provenance

- Noyau `6.18.55-1-megi-danctnix`, Omarchy `4.0.6-1`, Hyprland `0.56.2-7`,
  Quickshell `0.3.2.r7.g2b4501a-1`.
- Lots applicatifs : `packages.lock.json` et `terminal.packages.lock.json`.
- Plugins : `plugins/plugins.lock.json`, avec commits et hashes des sources ;
  les notices des huit projets MIT sont conservées dans `LICENSES/plugins`.
- Éditeur cellulaire : libnma-common/libnma `1.10.6-3`,
  nm-connection-editor `1.36.0-2`. Le préparateur vérifie leurs signatures puis
  verrouille les empreintes pour l'installation locale.
- Les derniers helpers publics correspondent à des adaptations d'abord déployées
  en privé. Leur installation complète depuis un checkout public vierge n'a pas
  été rejouée sur le matériel ; le préparateur de plugins et les contrôles
  isolés sont vérifiés sur hôte. Voir les limites dans chaque README.

## Diagnostic et récupération

Les journaux et sauvegardes privés ne sont pas distribués. Sur le téléphone :
`journalctl --user -b`, `hyprctl configerrors`,
`~/hyprperks-local/plugins-runtime.json` et les journaux locaux d'installation
ont servi au diagnostic. Ce dernier chemin est historique et privé ; les
installateurs publics utilisent leur propre répertoire.
La session graphique utilise dbus-run-session : les diagnostics du clavier
doivent employer le bus de la session, pas forcément `/run/user/1000/bus`.

Les sauvegardes des configurations sont décrites dans [extras](extras/README.md)
et [plugins](plugins/README.md). La récupération eMMC est documentée dans
[EMMC-MIGRATION.md](EMMC-MIGRATION.md). Aucune modification de SPI/Tow-Boot n'a
été effectuée. Les fichiers Sailfish de récupération restent privés.

Les adaptations Hyprperks restent exclues : la licence MIT de sa racine ne
supprime pas la restriction de redistribution du snapshot utilisé. Le code et
les configurations publiés ici n'en contiennent aucun extrait.
