#!/bin/python3
#creador aleatorio de pjs

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import pandas as pd
import numpy as np
import json


df_clases = pd.read_json('static/clases.json')
CLASES = (list(df_clases.columns.values))
ATRIBUTOS = (list(df_clases.index.values))

app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def main():
    data = request.args
    if request.method == 'GET' and request.args.get('poder', False):
        atributos = randomizar_atributos(data)
        habilidades = randomizar_habilidades(data, atributos)
        nombre = randomizar_nombre(data)
        iniciativa = roll_iniciativa(atributos, habilidades)
        defensa = roll_defensa(atributos, habilidades)
        inventario = randomizar_inventario(data, habilidades)

        return render_template('inicio.html', opciones=CLASES, data=data,
            atributos=atributos, habilidades=habilidades, nombre=nombre,
            iniciativa=iniciativa, defensa=defensa, inventario=inventario)
    else:
        return render_template('inicio.html', opciones=CLASES, data=data)


def roll_objetivo(objetivo):
    d = sorted([np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10)])
    return d[objetivo-1]


def roll_defensa(a, h):
    defensa_row = a.iloc[2]
    defensa = int(defensa_row[0])

    for i, row in h.iterrows():
        if i == "Esquivar":
            esquivar = row['VALOR']
            defensa = esquivar

    return str(defensa+10)


def roll_iniciativa(a, h):
    iniciativa_row = a.iloc[4]
    iniciativa = int(iniciativa_row[0])

    for i, row in h.iterrows():
        if i == "Reflejos":
            reflejo = row['VALOR']
            iniciativa = reflejo

    return str(iniciativa) + ' + 1o3d10'


def randomizar_inventario(data, habilidades):
    inventario = pd.read_json('static/inventario.json')
    hab_pj = habilidades.index.tolist()
    selection = []

    for inv in inventario:
        if inv in hab_pj:
            inv_posible = inventario[inv].dropna()
            for item, atr in inv_posible.iteritems():
                if np.random.random() <= atr[0]:
                    selection.append([item, atr])

    return selection

def randomizar_atributos(data):
    c = data['clase']
    p = int(data['poder'])
    sel_df = df_clases[[c]]\
        .apply(lambda x: np.round(x * p * np.random.normal(1, 0.1)), axis=1)\
        .astype(np.int)\
        .clip(upper=10, lower=4)
    return sel_df


def randomizar_habilidades(data, atributos):
    c = data['clase']
    hlist = []

    with open('static/skills.json', 'r') as json_file:
        d = json.load(json_file)

    for atribs, habils in d[c].items():
        for habil in habils.items():
            hkey = habil[0]
            h_inicial = int(habil[1])                              #valor
            h_wiggle = int(np.round(np.random.normal(h_inicial, 1)))  #wiggle
            h_valor = h_wiggle + int(atributos[c][atribs])      #aumento base
            hlist.append([hkey, int(atributos[c][atribs]), h_inicial, h_wiggle, h_valor])

    df_habilidades = pd.DataFrame(hlist, columns=['HABILIDAD', 'ATR', 'INI', 'WIG', 'VALOR']).sample(n=12)
    df_habilidades = df_habilidades[['HABILIDAD','VALOR']].set_index('HABILIDAD').sort_values(by=['VALOR'], ascending=False)

    return df_habilidades


def randomizar_nombre(data):
    if data['sexo'] == 'Mujer':
        nombres = pd.read_csv('static/spanish-names/mujeres.csv')
    else:
        nombres = pd.read_csv('static/spanish-names/hombres.csv')

    apellidos = pd.read_csv('static/spanish-names/apellidos.csv')
    
    todrop = nombres[nombres['edad_media'] > int(data['poder'])].index
    nombres.drop(todrop, inplace=True)
    nombres_max = np.max(nombres[['frec']])

    pruebas = 0
    while pruebas < 200:
        pruebas += 1
        test = nombres.sample(n=1)
        chances_aceptar = np.float(test['frec'].values[0]/nombres_max)
        if np.random.random() < chances_aceptar:
            break
    nombre = test['nombre'].values[0]
    e = test['edad_media'].values[0]
    if e < 15:
        e = 15 + np.random.randint(0,10)
    edad = str(int(e))

    pruebas = 0
    while pruebas < 200:
        pruebas += 1
        test = apellidos.sample(n=1)
        chances_aceptar = np.float(test['frec_pri'].values[0]/nombres_max)
        if np.random.random() < chances_aceptar:
            break
    apellido = test['apellido'].values[0]

    return nombre+'<br><small>'+apellido+' '+edad+' años</small>'


if __name__ == '__main__':
    app.run(debug=True)