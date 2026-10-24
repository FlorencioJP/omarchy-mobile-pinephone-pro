# Migration de cette microSD vers l'eMMC

**Procédure spécifique au PinePhone Pro et au partitionnement Sailfish observé. La copie sur eMMC est effectuée et ses contrôles logiciels ont réussi ; le démarrage sans SD reste à valider.**

La première exécution a terminé avec `MIGRATION_COMPLETE` et un statut systemd réussi après environ dix minutes. Les sauvegardes Sailfish ont été créées et comparées aux fichiers d'origine, `pacman -Dk` ne rapporte aucune erreur, les fichiers noyau/initramfs copiés correspondent à la source, et la table de partitions avant/après est identique. Les volumes cibles ont été démontés et SDDM a été relancé sur la SD. Ils ont ensuite été remontés en lecture seule pour vérification et récupération. Les trois sauvegardes ont été transférées dans un dossier privé du Mac, avec leurs descriptions de partitions et leurs SHA-256 vérifiés : les trois contrôles réussissent. La configuration fstab, la référence de racine du script U-Boot et son en-tête ont aussi été vérifiés sur les fichiers eMMC. À ce stade le téléphone utilise toujours la SD : ne pas présenter ce résultat comme un démarrage eMMC réussi.

La source active doit être `/dev/mmcblk1p2`, avec `/boot` sur `/dev/mmcblk1p1`. La cible doit être l'eMMC `/dev/mmcblk2`, avec trois partitions ext4 : p1 pour le démarrage (213,6 Mio), p2 pour l'ancien système Sailfish (7,4 Gio), p3 pour son ancien `/home` (107,6 Gio). Le script refuse d'autres types de périphériques, des partitions cibles déjà montées, une batterie inférieure à 60 % ou un téléphone qui n'est pas en charge.

## Ce qui change

- Aucun formatage, aucun repartitionnement, aucune écriture dans la SPI ou les zones eMMC boot0/boot1.
- Les systèmes de fichiers et UUID existants sont conservés. La partition p3 devient la racine Omarchy avec `/home` inclus ; p1 reste `/boot`, en ext4.
- Avant modification du démarrage, sauvegarde brute de p1, archives des fichiers Sailfish de p2 et p3 avec propriétaires numériques, ACL et attributs étendus, contrôles de contenu puis SHA-256.
- La copie Omarchy est préparée dans un sous-dossier de p3. Les anciens fichiers personnels Sailfish sont ensuite déplacés dans `/.omarchy-migration/sailfish-home`, sans suppression. L'ancienne partition système p2 n'est pas modifiée.
- La configuration de la copie est adaptée aux UUID eMMC. Le branchement vers `encrypted.scr` est retiré : la SD utilisée n'est pas chiffrée et un ancien fichier Sailfish ne doit pas détourner le démarrage.
- Le noyau, l'initramfs et les DTB de la SD sont conservés. Les pilotes MMC nécessaires sont intégrés au noyau observé ; l'initramfs examiné contient un fstab vide et aucune configuration cmdline embarquée. Le script U-Boot `boot.scr`, fichier situé dans p1, est régénéré avec la nouvelle racine puis remplacé en dernier. Cela ne réinstalle pas le chargeur.

La SD reste amorçable avec ses propres références. L'ajout des applications et la validation des radios restent des sujets distincts de cette copie. La migration ne valide pas le mode clavier ou la charge à travers celui-ci.

## Lancer

Lire `migrate-emmc.sh`, `emmc-config.py` et `restore-sailfish.sh`, puis les copier ensemble dans `/home/terminal/portage` sur la SD. Depuis une session administrateur sur le PinePhone démarré sur SD :

```sh
sudo systemd-run --unit=omarchy-emmc-migration \
  /usr/bin/systemd-inhibit --what=sleep:idle --mode=block \
  --who=Omarchy-migration --why=Migration-eMMC \
  /usr/bin/bash /home/terminal/portage/migrate-emmc.sh
```

Le mot de passe sudo est saisi localement, jamais dans le dépôt ou une image. La tâche continue sans dépendre de la connexion SSH. Garder le téléphone alimenté et ne pas le redémarrer pendant la copie. La session graphique SD est arrêtée pour copier ses configurations, puis relancée en fin de traitement si elle était active. Aucun arrêt automatique n'est demandé.

Suivi :

```sh
journalctl -fu omarchy-emmc-migration.service
systemctl show omarchy-emmc-migration -p ActiveState -p Result -p ExecMainStatus
```

Les étapes sont `BACKUP`, `COPY_ROOT`, `COMMIT_ROOT`, puis `COMMIT_BOOT`. Le marqueur `MIGRATION_COMPLETE` n'est produit qu'après les contrôles et le démontage des partitions cibles. Une tentative interrompue laisse un marqueur `started` et le script refuse de recommencer automatiquement : examiner les journaux et les montages avant toute reprise.

Le fichier `/var/lib/omarchy-ppp/emmc-migration/migration.log` est aussi conservé. Son répertoire parent appartient à root et reste privé sur la base testée ; utiliser le journal systemd pour le suivi sans sudo.

Les sauvegardes résident sur p3 sous `/.omarchy-migration` une fois le système eMMC démarré. Depuis la SD, monter p3 pour y accéder. Les trois fichiers de récupération principaux sont `boot-before.img`, `sailfish-system.tar` et `sailfish-home.tar`, avec `SHA256SUMS`. Ils contiennent des secrets personnels : accès limité à root et au groupe du compte `terminal`. Les copier dans un dossier privé sur un autre support et vérifier leurs SHA-256 avant le premier essai eMMC. Ces fichiers ne sont pas une image complète du disque et leur copie sur la même eMMC ne protège pas d'une panne matérielle de celle-ci.

## Premier démarrage

Après confirmation de fin et récupération des sauvegardes, éteindre proprement le téléphone. Retirer la microSD, puis démarrer normalement. Ne pas modifier Tow-Boot.

Contrôles attendus, qui restent à exécuter :

```sh
findmnt -n -o SOURCE,FSTYPE /
findmnt -n -o SOURCE,FSTYPE /boot
df -h /
ppp-profile detect
```

La racine doit être `/dev/mmcblk2p3`, ext4, et `/boot` sur `/dev/mmcblk2p1`, ext4. Vérifier aussi connexion tactile, Foot, Wi-Fi, accès SSH et journaux du nouveau démarrage. Un système copié et cohérent n'est pas un démarrage validé.

## Retour arrière

Si le démarrage échoue, remettre la SD téléphone éteint, puis sélectionner celle-ci avec Volume bas au démarrage. Ne pas relancer une copie brute sur l'eMMC.

Après examen des sauvegardes et du script, depuis la SD :

```sh
sudo bash /home/terminal/portage/restore-sailfish.sh
```

Le script vérifie la table de partitions et les SHA-256, met de côté les fichiers Omarchy, remet les anciens fichiers personnels Sailfish et restaure l'image brute de p1. Il n'écrit ni la table de partitions ni le chargeur. Il s'arrête si la cible est déjà montée ou si une restauration antérieure est présente. Ne pas l'exécuter après avoir supprimé ou modifié les sauvegardes ; les nouveaux travaux Omarchy doivent également être sauvegardés avant restauration.

## Vérifications de code

```sh
python3 tests/emmc-config.py
python3 tests/emmc-moves.py
bash -n migrate-emmc.sh restore-sailfish.sh
```

Les tests contrôlent les UUID, les références de racine uniques, les options ext4, l'abandon de l'ancien branchement chiffré et le refus des liens qui sortent de la copie. Les boucles réelles de bascule et de retour des dossiers sont également exercées dans un répertoire jetable : anciens fichiers personnels, fichiers cachés et nouveau système sont conservés. Les opérations de sauvegarde, bascule et retour arrière restent à exercer sur le matériel ; aucun résultat de test logiciel ne les certifie.
