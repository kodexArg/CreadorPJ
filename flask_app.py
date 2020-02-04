#!/bin/python3
# creador aleatorio de pjs

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
import constantes as ct
import randomizadores as rnd
import rolls
import os
import pickle
import json
# import rolls as rolls


app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def home():
    opciones_clases = ct.CLASES
    opciones_pjs = listar_guardados()
    pj = cargar_personaje()
    return render_template('home.html', **locals())


@app.route('/cargado')
def cargado():
    opciones_clases = ct.CLASES
    opciones_pjs = listar_guardados()
    pj = cargar_personaje(request.args.get('nombre_archivo'))
    return render_template('home.html', **locals())


@app.route('/guardado')
def guardado():
    opciones_clases = ct.CLASES
    opciones_pjs = listar_guardados()
    pj = cargar_personaje()
    guardar_personaje(pj, request.args.get('nombre'))
    return render_template('home.html', **locals())


@app.route('/generar')
def generar():
    opciones_clases = ct.CLASES
    opciones_pjs = listar_guardados()
    pj = generar_personaje(request.args)
    guardar_personaje(pj, 'ultimo')

    return render_template('home.html', **locals())


@app.route('/mapa')
def mapa():
    return render_template('home.html', mapa=True)


@app.route('/historia')
def historia():
    request_historia = request.form

    with open(os.path.join(ct.STATIC_ROOT, 'historia.json'), 'r') as json_historia:
        json_historia = json.load(json_historia)

    if request.args.get('historia'):
        historia = json_historia[request.args.get('historia')]
        for k, v in historia['Personajes'].items():
            pass
    else:
        historia=[]

    return render_template('historia.html', json_historia=json_historia, historia=historia)


def generar_personaje(data):
    caracter = data.to_dict()
    caracteristicas = rnd.randomizar_caracteristicas(caracter)
    atributos = rnd.randomizar_atributos(caracter)
    habilidades = rnd.randomizar_habilidades(caracter, atributos)
    inventario = rnd.randomizar_inventario(caracter, habilidades, atributos, caracteristicas)
    dinero = rnd.randomizar_dinero(caracter)
    nombre = rnd.randomizar_nombre(caracter)
    iniciativa = rolls.roll_iniciativa(atributos, habilidades)
    defensa = rolls.roll_defensa(atributos, habilidades)
    rasgos = rnd.randomizar_rasgos(caracter, atributos, habilidades)
    return locals()


def guardar_personaje(pj, nombre_pickle):
    pickle.dump(pj, open(os.path.join(ct.PJS, nombre_pickle +
                                      '.pickle'), 'wb'), protocol=pickle.HIGHEST_PROTOCOL)


def cargar_personaje(nombre_archivo='ultimo.pickle'):
    ultimo = pickle.load(open(os.path.join(ct.PJS, nombre_archivo), 'rb'))
    ultimo.update({'iniciativa': rolls.roll_iniciativa(
        ultimo['atributos'], ultimo['habilidades'])})
    ultimo.update({'defensa': rolls.roll_defensa(
        ultimo['atributos'], ultimo['habilidades'])})
    return ultimo


def listar_guardados():
    listado_pjs = []
    for r, d, f in os.walk(ct.PJS):
        for file in f:
            if file != 'ultimo.pickle':
                listado_pjs.append(file)
    return listado_pjs


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')