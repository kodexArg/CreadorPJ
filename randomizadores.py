import constantes as ct
import os
import pandas as pd
import numpy as np
import json
import random
from collections import OrderedDict


def randomizar_caracteristicas(caracter):
    chances = ct.POSIBILIDAD_TRAIT
    with open(os.path.join(ct.STATIC_ROOT, 'caracteristicas.list')) as f:
        lines = [line.strip('\n') for line in f]

    # se peude mejorar, pero ¿lo voy a entender el año que viene?, no, no lo voy a entender
    c = []
    for line in lines:
        c.append(line.split(','))

    caracteristicas = {}
    indice = 0
    for test in c:
        if caracter['sexo'] == "Mujer":
            test = [w.replace('0', 'a') for w in test]
            test = [w.replace('1', 'a') for w in test]
        else:
            test = [w.replace('0', 'o') for w in test]
            test = [w.replace('1', '') for w in test]

        if np.random.randint(1, 10) < chances:
            caracteristicas.update({indice: np.random.choice(test).strip()})
            chances = chances * 0.8
            indice += 1

    return caracteristicas


def randomizar_atributos(caracter):
    c = caracter['clase']
    p = int(caracter['poder'])
    atributos = ct.df_clases[[c]]\
        .apply(lambda x: np.round(x * p * np.random.normal(1, 0.1)), axis=1)\
        .astype(np.int)\
        .clip(upper=10, lower=4)\
        .to_dict()

    return atributos[caracter['clase']]


def randomizar_habilidades(caracter, atributos):
    c = caracter['clase']
    hlist = []

    with open(os.path.join(ct.STATIC_ROOT, 'skills.json'), 'r') as json_file:
        d = json.load(json_file)

    for atribs, habils in d[c].items():
        for habil in habils.items():
            hkey = habil[0]
            h_inicial = int(habil[1])  # valor
            h_wiggle = int(np.round(np.random.normal(h_inicial, 1)))  # wiggle
            h_valor = h_wiggle + int(atributos[atribs])  # aumento base
            hlist.append([hkey, int(atributos[atribs]),
                          h_inicial, h_wiggle, h_valor])
    df_habilidades = pd.DataFrame(
        hlist, columns=['HABILIDAD', 'ATR', 'INI', 'WIG', 'VALOR']).sample(n=round((12*(int(caracter['poder'])/40))))
    df_habilidades = df_habilidades[['HABILIDAD', 'VALOR']].set_index(
        'HABILIDAD').sort_values(by=['VALOR'], ascending=False)
    habilidades = df_habilidades.to_dict()

    return habilidades['VALOR']


def randomizar_inventario(caracter, habilidades, atributos, caracteristicas):
    inventario = pd.read_json(os.path.join(ct.STATIC_ROOT, 'inventario.json'))
    selection = {}

    # items por HABILIDADES
    hab_pj = list(habilidades.keys())
    for inv in inventario:
        if inv in hab_pj:
            inv_posible = inventario[inv].dropna()
            for item, atr in inv_posible.iteritems():
                if np.random.random() <= (atr[0]*ct.POSIBILIDAD_INVENTARIO):
                    selection.update({item: atr})

    # items por CARACTERISTICAS

    if len(selection) > 1:
        l = list(selection.items())
        np.random.shuffle(l)
        selection = dict(l)

    return selection


def randomizar_dinero(caracter):
    cash = np.random.randint(0, np.int(caracter['poder'])) * 10
    return {'dinero': cash}


def randomizar_nombre(caracter):

    if caracter['sexo'] == 'Mujer':
        nombres = pd.read_csv(os.path.join(
            ct.STATIC_ROOT, 'spanish-names/mujeres.csv'))
    else:
        nombres = pd.read_csv(os.path.join(
            ct.STATIC_ROOT, 'spanish-names/hombres.csv'))

    apellidos = pd.read_csv(os.path.join(
        ct.STATIC_ROOT, 'spanish-names/apellidos.csv'))

    todrop = nombres[nombres['edad_media'] > int(caracter['poder'])].index
    nombres.drop(todrop, inplace=True)
    nombres_max = np.max(nombres[['frec']])

    if caracter['opt_nombre']:
        nombre = str(caracter['opt_nombre'])
    else:
        pruebas = 0
        while pruebas < ct.INTENTOS:
            pruebas += 1
            test = nombres.sample(n=1)
            chances_aceptar = np.float(test['frec'].values[0]/nombres_max)
            if np.random.random() < chances_aceptar:
                break
        nombre = test['nombre'].values[0]

    if caracter['opt_edad']:
        edad = caracter['opt_edad']
    else:
        e = test['edad_media'].values[0]
        if e < 15:
            e = 15 + np.random.randint(0, 10)
        edad = str(int(e))

    if caracter['opt_apellido']:
        apellido = caracter['opt_apellido']
    else:
        pruebas = 0
        while pruebas < ct.INTENTOS:
            pruebas += 1
            test = apellidos.sample(n=1)
            chances_aceptar = np.float(test['frec_pri'].values[0]/nombres_max)
            if np.random.random() < chances_aceptar:
                break
        apellido = test['apellido'].values[0]

    return {'nombre': nombre, 'apellido': apellido, 'edad': edad}


def randomizar_rasgos(caracter, atributos, habilidades):
    rasgos = pd.read_json(os.path.join(ct.STATIC_ROOT, 'rasgos.json'))
    rasgo_aceptado = {}
    for i, row in rasgos.iteritems():

        rasgo = i
        habil_asociado = row[0]
        atrib_asociado = row[1]
        proba_asociado = row[2]

        # debe tener las habilidades asociadas
        if set(habil_asociado).issubset(set(list(habilidades.keys()))):
            # mayor chance entre mayor su atributo asociado
            if atributos[atrib_asociado] >= np.random.randint(4, 10):
                rasgo_valor = max([habilidades[h] for h in habil_asociado]) + np.random.randint(0, proba_asociado)
            
                if caracter['sexo'] == "Mujer": #esto falla DRY, por lo menos lo hace sólo en aciertos
                    rasgo = [w.replace('0', 'a') for w in rasgo]
                    rasgo = [w.replace('1', 'a') for w in rasgo]
                else:
                    rasgo = [w.replace('0', 'o') for w in rasgo]
                    rasgo = [w.replace('1', '') for w in rasgo]

                rasgo_aceptado[''.join(rasgo)] =  rasgo_valor

    rasgos = OrderedDict(rasgo_aceptado)

    return rasgos