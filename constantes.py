import os
import pandas as pd

# necesario para pythonanywhere...creo.
STATIC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
PJS = os.path.join(STATIC_ROOT, 'pjs')
# PJS_GUARDADOS = os.path.join(STATIC_ROOT, 'pjs_guardados')

# Iniciar Clases, comodidad, sorry
df_clases = pd.read_json(os.path.join(STATIC_ROOT, 'clases.json'))

CLASES = (list(df_clases.columns.values))
ATRIBUTOS = (list(df_clases.index.values))
INTENTOS = 500
POSIBILIDAD_TRAIT = 3
POSIBILIDAD_INVENTARIO = 1.5