import numpy as np
import pandas as pd

# Función para limpiar bases


def limpiar_depurar(df):
    # Limpia el DataFrame para trabajarlo en pandas
    df.columns = df.columns.str.replace(' ', '')
    df.columns = df.columns.str.replace('\W', '', regex=True)
    df.columns = df.columns.str.normalize('NFKD')
    df.columns = df.columns.str.encode('ascii', errors='ignore')
    df.columns = df.columns.str.decode('utf-8')
    df.columns = df.columns.str.upper()
    return df


# Cargar tablas de cada contraparte

tabla_CNA = pd.read_excel('sedes CNA-SIES.xlsx', sheet_name='CNA')
tabla_SIES = pd.read_excel('sedes CNA-SIES.xlsx', sheet_name='SIES')

tabla_CNA = limpiar_depurar(tabla_CNA)
tabla_SIES = limpiar_depurar(tabla_SIES)

# Quedarse con casos únicos para reemplazo

tabla_CNA = tabla_CNA.drop_duplicates()
tabla_SIES = tabla_SIES.drop_duplicates()

# Generar lista de IES que permitan reemplazo, se reemplazará datos
# EN LA TABLA DE CNA, de esta manera, la base de SIES se mantiene intacta

lista_IES = tabla_CNA['INSTITUCION'].unique()

# funcion de cambio en tablas


def cambiar_sedes(id_origen, id_destino,
                  tabla_origen,
                  tabla_destino):
    dato = tabla_origen['NOMBRESEDE'].iloc[id_origen]
    tabla_destino['SEDE'].iloc[id_destino] = dato


for inst in lista_IES:
    tabla_CNA_inst = tabla_CNA.query('INSTITUCION == "' + inst + '"')
    tabla_SIES_inst = tabla_SIES.query('NOMBREIES == "' + inst + '"')
    if tabla_SIES_inst.empty:
        print('Institución ' + inst + ' no en SIES \n')
    else:
        while True:
            print('Versión CNA: \n')
            print(tabla_CNA_inst)
            print("\n")
            print('Versión SIES: \n')
            print(tabla_SIES_inst)
            id_SIES = input('\n Entrada de SIES: \n')
            id_CNA = input('\n Salida de CNA a cambiar: \n')
            if id_SIES == 's' or id_CNA == 's':
                break
            id_SIES = int(id_SIES)
            id_CNA = int(id_CNA)
            cambiar_sedes(id_SIES, id_CNA,
                          tabla_SIES_inst, tabla_CNA_inst)

