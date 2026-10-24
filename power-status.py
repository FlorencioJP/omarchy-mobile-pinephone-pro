#!/usr/bin/env python3
"""Lecture seule des batteries et sources d'alimentation PinePhone Pro."""
from pathlib import Path

FIELDS = ('type', 'status', 'capacity', 'present', 'online', 'voltage_now', 'current_now')
LABELS = {'rk818-battery': 'Téléphone', 'ip5xxx-battery': 'Clavier'}
STATES = {'Full': 'Pleine', 'Charging': 'En charge', 'Discharging': 'Décharge',
          'Not charging': 'Au repos', 'Unknown': 'Inconnu'}


def supplies(root=Path('/sys/class/power_supply')):
    result = {}
    for device in sorted(root.iterdir()):
        values = {}
        for field in FIELDS:
            try:
                values[field] = (device / field).read_text().strip()
            except OSError:
                pass
        if values:
            result[device.name] = values
    return result


def measurement(raw, divisor, digits):
    try:
        return f'{int(raw) / divisor:.{digits}f}'
    except (ValueError, TypeError):
        return '—'


def charge(raw):
    try:
        percent = int(raw)
        if 0 <= percent <= 100:
            filled = percent * 5 // 100
            return '█' * filled + '░' * (5 - filled) + f' {percent} %'
    except (ValueError, TypeError):
        pass
    return '—'


def table(headers, rows):
    widths = [max(len(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    def border(left, middle, right):
        return left + middle.join('─' * (width + 2) for width in widths) + right
    def row(values):
        return '│ ' + ' │ '.join(value.ljust(width) for value, width in zip(values, widths)) + ' │'
    return [border('┌', '┬', '┐'), row(headers), border('├', '┼', '┤'),
            *(row(values) for values in rows), border('└', '┴', '┘')]


def display(devices):
    lines = ['BATTERIES · PinePhone Pro', '']
    batteries = []
    for name, values in devices.items():
        if values.get('type') == 'Battery':
            batteries.append([LABELS.get(name, name), charge(values.get('capacity')),
                              STATES.get(values.get('status'), 'Inconnu'),
                              measurement(values.get('voltage_now'), 1_000_000, 2),
                              measurement(values.get('current_now'), 1_000, 1)])
    if batteries:
        lines.extend(table(['Batterie', 'Charge', 'État', 'V', 'mA'], batteries))
    sources = []
    for name, values in devices.items():
        if values.get('type') != 'Battery':
            label = {'rk818-usb': 'USB téléphone', 'ip5xxx-usb': 'USB clavier',
                     'ip5xxx-boost': 'Sortie clavier',
                     'tcpm-source-psy-4-0022': 'USB-C téléphone'}.get(name, name)
            sources.append([label, {'1': 'Oui', '0': 'Non'}.get(values.get('present'), '—'),
                            {'1': 'Oui', '0': 'Non'}.get(values.get('online'), '—')])
    if sources:
        lines.extend(['', *table(['Alimentation', 'Présente', 'Active'], sources)])
    if not devices:
        lines.append('Aucune source exposée par le noyau.')
    lines.extend(['', '— : information non fournie par le pilote.',
                  'Relevé instantané ; ne mesure pas l’autonomie.',
                  'Le signe du courant dépend du pilote.',
                  'Avec le clavier monté : chargeur sur le clavier uniquement.'])
    return '\n'.join(lines)


if __name__ == '__main__':
    print(display(supplies()))
