-- SPDX-License-Identifier: MIT
-- Compléter le profil mobile sans remplacer sa session ni ses réglages matériels.
o.bind('CTRL + ALT + M', 'Menu Omarchy', 'omarchy-menu summon root')
o.bind('CTRL + ALT + TAB', 'Applications actives', 'omarchy-shell shell toggle omamobile.switcher')
o.bind('CTRL + ALT + C', 'Presse-papiers', 'omarchy-shell shell toggle omarchy.clipboard')
o.bind('CTRL + ALT + B', 'Navigateur', 'omarchy-launch-browser')
o.bind('CTRL + ALT + F', 'Fichiers', 'nautilus')
o.bind('CTRL + ALT + E', 'Éditeur', 'gnome-text-editor')
