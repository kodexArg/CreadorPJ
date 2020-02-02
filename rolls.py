import numpy as np


def roll_objetivo(objetivo):
    d = sorted([np.random.randint(1, 10), np.random.randint(
        1, 10), np.random.randint(1, 10)])
    return d[objetivo-1]


def roll_defensa(a, h):
    defensa = int(a['DESTREZA'])

    for i, row in h.items():
        if i == "Esquivar":
            esquivar = row
            defensa = esquivar

    return str(defensa+10)


def roll_iniciativa(a, h):
    iniciativa = int(a['PERCEPCIÓN'])

    for i, row in h.items():
        if i == "Reflejos":
            reflejo = row
            iniciativa = reflejo

    roll = roll_objetivo(1)
    cadena = str(iniciativa) + ' + 1o3d10' + ' ( ' + \
        str(iniciativa) + '+'+str(roll)+'='+str(iniciativa+roll)+' )'
    return cadena
