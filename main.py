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
        nombre = randomizar_nombre(data.args.get('sexo'))

        return render_template('inicio.html', opciones=CLASES, data=data,
            atributos=atributos, habilidades=habilidades)
    else:
        return render_template('inicio.html', opciones=CLASES, data=data)


def randomizar_atributos(data):
    c = data['clase']
    p = int(data['poder'])
    sel_df = df_clases[[c]]\
        .apply(lambda x: np.round(x * p * np.random.normal(1, 0.1)), axis=1)\
        .astype(np.int)\
        .clip(upper=11, lower=4)
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

    df_habilidades = pd.DataFrame(hlist, columns=['HABILIDAD', 'ATR', 'INI', 'WIG', 'VALOR']).sample(n=9)
    df_habilidades = df_habilidades[['HABILIDAD','VALOR']].set_index('HABILIDAD').sort_values(by=['VALOR'], ascending=False)

    return df_habilidades

def randomizar_nombre(sexo):
    print(sexo)


if __name__ == '__main__':
    app.run(debug=True)