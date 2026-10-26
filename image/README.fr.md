<!-- SPDX-License-Identifier: MIT -->
# Construire et tester l'image microSD

Cette image est une intégration indépendante d'Omarchy sur PinePhone Pro,
avec certains composants d'interface d'Omarchy Mobile. Elle part d'une image
publique signée d'Arch Linux ARM et conserve le noyau `linux-megi`, le DTB,
les pilotes et le démarrage propres au PinePhone Pro.

Elle ne copie pas le téléphone du propriétaire. Aucun mot de passe partagé,
profil Wi-Fi, compte distant ou clé privée n'est incorporé. Les adaptations
privées Hyprperks et les essais non publiés du bouton du clavier sont exclus.

## Construction

Il faut Git, Python 3.11 ou plus récent, Docker avec un moteur Linux ARM64,
4 Gio de mémoire et au moins 24 Gio libres. Docker Desktop sur un Mac Apple
Silicon fournit cet environnement. Le mode privilégié donne accès aux périphériques
du moteur Docker : utiliser Docker Desktop ou une VM Linux dédiée, pas le moteur
natif d'un serveur de production. Les scripts sélectionnent uniquement leurs
nouveaux fichiers image ; aucun téléphone n'est nécessaire.

Depuis la racine du dépôt :

```sh
bash image/build.sh prepare
bash image/build.sh build
```

La préparation télécharge les entrées exactes et construit le conteneur d'outils.
La construction se déroule ensuite sans réseau. Elle vérifie les empreintes et
signatures, installe uniquement le lot verrouillé, applique le profil PinePhone
et contrôle le résultat. Les archives des paquets sont précompilées en amont :
ce n'est pas une recompilation complète du noyau ou de Hyprland.

Les résultats sont dans `image/out/` : image compressée `.img.xz`, SHA-256,
inventaire des paquets et manifeste des configurations. Le fichier décompressé
fait 12 Gio ; utiliser une carte
d'au moins 16 Go. Les journaux de construction sont dans `image/work/` lorsqu'on
redirige la sortie vers ce dossier. Conserver aussi `cache/image/` et le commit
du dépôt : les serveurs amont peuvent retirer les anciennes versions.

Le verrouillage porte sur les entrées et la configuration. Les métadonnées de
système de fichiers et certains caches peuvent varier entre deux constructions ;
une identité binaire de l'image n'est pas promise. Le [bilan](VALIDATION.md)
indique précisément ce qui a été exécuté et ce qui reste à tester.

Pour comparer deux constructions propres, utiliser `cmp` sur leurs fichiers
`.packages.txt` et `.configuration.json`. Ce manifeste couvre le profil PinePhone,
la connexion, le script de démarrage et la configuration utilisateur générée,
avec empreintes, liens, droits et propriétaires ; il ne couvre pas chaque octet
du système de fichiers.

## Installation et premier démarrage

1. Vérifier le SHA-256. Avec un lecteur externe, sélectionner une **microSD
   dédiée**, vérifier sa capacité, puis écrire l'image avec un outil d'images.
   Cela efface la carte choisie. Exiger une vérification finale sans erreur.
2. Éteindre le PinePhone Pro, insérer la carte et sélectionner le démarrage SD
   avec son chargeur existant. Avec Tow-Boot déjà installé, utiliser Volume bas.
   Si cela ne fonctionne pas, s'arrêter : ne pas modifier SPI/Tow-Boot ni l'eMMC.
3. Au premier démarrage, une session locale temporaire doit demander de créer
   le mot de passe du compte `terminal`. Après succès, l'autoconnexion est
   supprimée. Sans clavier, le profil prévu est portrait avec Squeekboard ;
   avec le clavier officiel, il est paysage. Ce parcours exige encore un test
   matériel sur l'image neuve.
4. Vérifier `findmnt /`, `findmnt /boot`, puis
   `grep . /sys/class/block/mmcblk*/device/type`. Les deux systèmes de fichiers
   doivent appartenir à la SD. Ne pas poursuivre si le disque racine est ambigu.
5. Configurer Wi-Fi, Bluetooth et éventuellement SIM/APN localement. Le menu
   PinePhone donne accès aux connexions et au tableau des batteries.

`Ctrl+Alt+Entrée` ouvre le terminal, `Ctrl+Alt+M` le menu Omarchy et `Ctrl+Alt+W`
les réglages réseau en mode texte. Le lanceur d'applications donne un accès
tactile au menu et aux applications installées.

Pour SSH, adapter `~/.ssh/config.example` dans `~/.ssh/config`, puis exécuter
`ppp-connect agents`. La session tmux est créée/reprise sur la machine distante,
qui doit avoir tmux installé. Le serveur SSH du téléphone reste désactivé par
défaut ; son activation est une opération locale séparée.

## Test court et retour arrière

Commencer sans clavier : démarrage, création du mot de passe, tactile, saisie,
Wi-Fi, menu et SSH. Puis éteindre, monter le clavier et redémarrer : vérifier
paysage, alignement du tactile, Ctrl/Alt/Esc/Tab/flèches et les symboles du
terminal. Photographier les erreurs et noter les résultats sans les déduire
des seuls tests logiciels.

Pour revenir au système interne, éteindre et retirer la SD. Le constructeur
ne migre rien vers l'eMMC. Ne pas placer simultanément deux copies de cette
image sur SD et eMMC : elles partageraient leurs UUID. La capacité inutilisée
de la SD n'est pas agrandie automatiquement.

Avec le clavier monté, charger par son port USB-C, sans chargeur simultané sur
le téléphone. Le fonctionnement du bouton, la charge, l'arrêt et l'autonomie
restent des vérifications séparées. La veille et la reconnexion Wi-Fi seront
testées après validation du premier démarrage et d'un moyen de récupération.

Pour les diagnostics détaillés, les limites et le renouvellement volontaire du
lot de paquets, consulter [les instructions techniques](README.md). Les journaux
du téléphone doivent être relus et expurgés avant publication.
