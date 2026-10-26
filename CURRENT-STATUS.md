# État du projet

## Constructeur microSD — 26 octobre 2026

Une nouvelle construction depuis une base publique signée est développée dans
[`image/`](image/README.md). Ses [preuves et limites](image/VALIDATION.md) sont
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
| Image reproductible | Lots et plugins figés, helpers et tests publics | Installation privée issue de ces travaux | Pas de constructeur d'image complet ni d'image publique |

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
