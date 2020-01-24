#!/bin/python3
#creador aleatorio de pjs

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import pandas as pd
import numpy as np
import json
import os
import pickle
from shutil import copy

app = Flask(__name__)
from sqlalchemy import create_engine

Bootstrap(app)
STATIC_ROOT = os.path.join(app.root_path, 'static') #necesario para pythonanywhere...creo.
PJS = os.path.join(STATIC_ROOT, 'pjs')
PJS_GUARDADOS = os.path.join(STATIC_ROOT, 'pjs_guardados')

#Iniciar Clases, comodidad, sorry
df_clases = pd.read_json(os.path.join(STATIC_ROOT, 'clases.json'))
CLASES = (list(df_clases.columns.values))
ATRIBUTOS = (list(df_clases.index.values))
INTENTOS = 2
#////////////////////////comienzan routes:


@app.route('/mapa')
def mapa():
    return render_template('mapa.html')


@app.route('/historia', methods = ['GET'])
def historia():
    request_historia = request.form

    with open(os.path.join(app.root_path, 'historia.json'), 'r') as json_historia:
        json_historia = json.load(json_historia)

    if request.args.get('historia'):
        historia = json_historia[request.args.get('historia')]
    else:
        historia=[]

    return render_template('historia.html', json_historia=json_historia, historia=historia)

@app.route('/')
def main():
    print('///////////////////// M A I N /////////////////////')
    pjs_guardados = []
    for r, d, f in os.walk(PJS_GUARDADOS):
        for file in f:
            if file[-13:] == 'nombre.pickle':
                pjs_guardados.append(file[:-14])

    data = request.args.to_dict()
    if request.args.get('save', False):
        nombre = pickle.load(open(os.path.join(PJS, 'nombre.pickle'), 'rb'))

        for r, d, f in os.walk(PJS):
            for file in f:
                copy(os.path.join(PJS, file), os.path.join(PJS_GUARDADOS, nombre['nombre']+' '+nombre['apellido']+' '+file))

        data = pickle.load(open(os.path.join(PJS, 'data.pickle'), 'rb'))
        caracter = pickle.load(open(os.path.join(PJS, 'character.pickle'), 'rb'))
        caracteristicas = pickle.load(open(os.path.join(PJS, 'caracteristicas.pickle'), 'rb'))
        atributos = pickle.load(open(os.path.join(PJS, 'atributos.pickle'), 'rb'))
        habilidades = pickle.load(open(os.path.join(PJS, 'habilidades.pickle'), 'rb'))
        nombre = pickle.load(open(os.path.join(PJS, 'nombre.pickle'), 'rb'))
        inventario = pickle.load(open(os.path.join(PJS, 'inventario.pickle'), 'rb'))
        dinero = pickle.load(open(os.path.join(PJS, 'dinero.pickle'), 'rb'))

        iniciativa = roll_iniciativa(atributos, habilidades)
        defensa = roll_defensa(atributos, habilidades)

        return render_template('inicio.html', opciones=CLASES, data=data,
            caracter=caracter, atributos=atributos, habilidades=habilidades, nombre=nombre,
            iniciativa=iniciativa, defensa=defensa, inventario=inventario,
            dinero=dinero, caracteristicas=caracteristicas, pjs_guardados=pjs_guardados)

    elif request.args.get('poder', False):
        caracter = request.args.to_dict()

        caracteristicas = randomizar_caracteristicas(caracter)
        atributos = randomizar_atributos(caracter)
        habilidades = randomizar_habilidades(caracter, atributos)
        nombre = randomizar_nombre(caracter)
        inventario = randomizar_inventario(caracter, habilidades)
        dinero = randomizar_dinero(caracter)
        iniciativa = roll_iniciativa(atributos, habilidades)
        defensa = roll_defensa(atributos, habilidades)
        guardar_temporalmente(data, caracter, caracteristicas, atributos, habilidades, nombre, inventario, dinero)

        return render_template('inicio.html', opciones=CLASES, data=data,
            caracter=caracter, atributos=atributos, habilidades=habilidades, nombre=nombre,
            iniciativa=iniciativa, defensa=defensa, inventario=inventario,
            dinero=dinero, caracteristicas=caracteristicas, pjs_guardados=pjs_guardados)
    else:
        return render_template('inicio.html', opciones=CLASES, data=data, pjs_guardados=pjs_guardados)


def guardar_temporalmente(data, caracter, caracteristicas, atributos, habilidades, nombre, inventario, dinero):
    pickle.dump(data, open(os.path.join(PJS, 'data.pickle'), 'wb'))
    pickle.dump(caracter, open(os.path.join(PJS, 'character.pickle'), 'wb'))
    pickle.dump(caracteristicas, open(os.path.join(PJS, 'caracteristicas.pickle'), 'wb'))
    pickle.dump(atributos, open(os.path.join(PJS, 'atributos.pickle'), 'wb'))
    pickle.dump(habilidades, open(os.path.join(PJS, 'habilidades.pickle'), 'wb'))
    pickle.dump(nombre, open(os.path.join(PJS, 'nombre.pickle'), 'wb'))
    pickle.dump(inventario, open(os.path.join(PJS, 'inventario.pickle'), 'wb'))
    pickle.dump(dinero, open(os.path.join(PJS, 'dinero.pickle'), 'wb'))


def randomizar_caracteristicas(caracter):
    with open(os.path.join(STATIC_ROOT,'caracteristicas.list')) as f:
        lines = [line.strip('\n') for line in f]

    #se peude mejorar, pero ¿lo voy a entender el año que viene?, no, no lo voy a entender
    c = []
    for line in lines:
        c.append(line.split(','))

    caracteristicas = {}
    indice = 0
    for test in c:
        if caracter['sexo'] == "Mujer":
            test = [w.replace('0','a') for w in test]
        else:
            test = [w.replace('0','o') for w in test]

        if np.random.randint(1, 10) < 3:
            caracteristicas.update({indice: np.random.choice(test).strip()})
            indice += 1
    
    return caracteristicas


def randomizar_atributos(caracter):
    c = caracter['clase']
    p = int(caracter['poder'])
    atributos = df_clases[[c]]\
        .apply(lambda x: np.round(x * p * np.random.normal(1, 0.1)), axis=1)\
        .astype(np.int)\
        .clip(upper=10, lower=4)\
        .to_dict()

    return atributos[caracter['clase']]


def randomizar_habilidades(caracter, atributos):
    c = caracter['clase']
    hlist = []

    with open(os.path.join(STATIC_ROOT, 'skills.json'), 'r') as json_file:
        d = json.load(json_file)

    for atribs, habils in d[c].items():
        for habil in habils.items():
            hkey = habil[0]
            h_inicial = int(habil[1])                              #valor
            h_wiggle = int(np.round(np.random.normal(h_inicial, 1)))  #wiggle
            h_valor = h_wiggle + int(atributos[atribs])      #aumento base
            hlist.append([hkey, int(atributos[atribs]), h_inicial, h_wiggle, h_valor])

    df_habilidades = pd.DataFrame(hlist, columns=['HABILIDAD', 'ATR', 'INI', 'WIG', 'VALOR']).sample(n=12)
    df_habilidades = df_habilidades[['HABILIDAD','VALOR']].set_index('HABILIDAD').sort_values(by=['VALOR'], ascending=False)
    habilidades = df_habilidades.to_dict()

    return habilidades['VALOR']


def randomizar_inventario(caracter, habilidades):
    inventario = pd.read_json(os.path.join(STATIC_ROOT, 'inventario.json'))
    hab_pj = list(habilidades.keys())
    selection = {}

    for inv in inventario:
        if inv in hab_pj:
            inv_posible = inventario[inv].dropna()
            for item, atr in inv_posible.iteritems():
                if np.random.random() <= atr[0]:
                    selection.update({item: atr})

    return selection


def randomizar_dinero(caracter):
    cash =np.random.randint(0, np.int(caracter['poder'])) * 10
    return {'dinero': cash}


def randomizar_nombre(caracter):
    if caracter['sexo'] == 'Mujer':
        nombres = pd.read_csv(os.path.join(STATIC_ROOT, 'spanish-names/mujeres.csv'))
    else:
        nombres = pd.read_csv(os.path.join(STATIC_ROOT, 'spanish-names/hombres.csv'))

    apellidos = pd.read_csv(os.path.join(STATIC_ROOT, 'spanish-names/apellidos.csv'))
    
    todrop = nombres[nombres['edad_media'] > int(caracter['poder'])].index
    nombres.drop(todrop, inplace=True)
    nombres_max = np.max(nombres[['frec']])

    pruebas = 0
    while pruebas < INTENTOS:
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
    while pruebas < INTENTOS:
        pruebas += 1
        test = apellidos.sample(n=1)
        chances_aceptar = np.float(test['frec_pri'].values[0]/nombres_max)
        if np.random.random() < chances_aceptar:
            break
    apellido = test['apellido'].values[0]

    return {'nombre': nombre, 'apellido': apellido, 'edad': edad}


def roll_objetivo(objetivo):
    d = sorted([np.random.randint(1, 10), np.random.randint(1, 10), np.random.randint(1, 10)])
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
    cadena = str(iniciativa) + ' + 1o3d10' + ' ( ' + str(iniciativa) +'+'+str(roll)+'='+str(iniciativa+roll)+' )'
    return cadena


if __name__ == '__main__':
    app.run(debug=True)