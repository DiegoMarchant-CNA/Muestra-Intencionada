# coding=utf-8
import numpy as np
import pandas as pd
# import sys
# import os

# función Caso_1_AC:


def caso_1_AC(df):
    N_prog = df.shape[0]
    if N_prog == 1:
        data_seleccion_0 = np.empty((1, len(df.columns)), dtype=object)
        data_seleccion_0[0] = df.iloc[0]
    elif N_prog >= 2 and N_prog <= 9:
        data_seleccion_0 = np.empty((2, len(df.columns)), dtype=object)
        elegir = np.random.choice(np.arange(N_prog), 2, replace=False)
        data_seleccion_0[0] = df.iloc[elegir[0]]
        data_seleccion_0[1] = df.iloc[elegir[1]]
    elif N_prog >= 10:
        elegir = np.random.choice(np.arange(N_prog), 3, replace=False)
        data_seleccion_0 = np.empty((3, len(df.columns)), dtype=object)
        data_seleccion_0[0] = df.iloc[elegir[0]]
        data_seleccion_0[1] = df.iloc[elegir[1]]
        data_seleccion_0[2] = df.iloc[elegir[2]]
    return pd.DataFrame(data=data_seleccion_0, columns=df.columns)

# función Caso_FFAA:


def caso_FFAA(df):
    N_prog = df.shape[0]
    if N_prog == 1:
        data_seleccion_0 = np.empty((1, len(df.columns)), dtype=object)
        data_seleccion_0[0] = df.iloc[0]
    if N_prog == 2:
        data_seleccion_0 = np.empty((2, len(df.columns)), dtype=object)
        data_seleccion_0[0] = df.iloc[0]
        data_seleccion_0[1] = df.iloc[1]
    elif N_prog > 2 and N_prog <= 15:
        data_seleccion_0 = np.empty((2, len(df.columns)), dtype=object)
        elegir = np.random.choice(np.arange(N_prog), 2, replace=False)
        data_seleccion_0[0] = df.iloc[elegir[0]]
        data_seleccion_0[1] = df.iloc[elegir[1]]
    elif N_prog > 15 and N_prog <= 30:
        elegir = np.random.choice(np.arange(N_prog), 3, replace=False)
        data_seleccion_0 = np.empty((3, len(df.columns)), dtype=object)
        data_seleccion_0[0] = df.iloc[elegir[0]]
        data_seleccion_0[1] = df.iloc[elegir[1]]
        data_seleccion_0[2] = df.iloc[elegir[2]]
    elif N_prog > 30:
        elegir = np.random.choice(np.arange(N_prog), 4, replace=False)
        data_seleccion_0 = np.empty((4, len(df.columns)), dtype=object)
        data_seleccion_0[0] = df.iloc[elegir[0]]
        data_seleccion_0[1] = df.iloc[elegir[1]]
        data_seleccion_0[2] = df.iloc[elegir[2]]
        data_seleccion_0[3] = df.iloc[elegir[3]]
    return pd.DataFrame(data=data_seleccion_0, columns=df.columns)


# función Caso U_con_TNS:


def funcion_seleccion(IES):

    PATH = 'DB_OK/{inst}.xlsx'.format(inst=IES)

    base = pd.read_excel(PATH)

    # Revisar número AC institución
    AREAS = base['AC'].unique()
    N_AC = len(AREAS)

    AC_pre = base[base['nivel'] == 'Pregrado']['AC'].unique()
    N_AC_pre = len(AC_pre)

    AC_post = base[base['nivel'] == 'Postgrado']['AC'].unique()
    N_AC_post = len(AC_post)

    print(['Número AC total = {fac}'.format(fac=N_AC)])
    print('Número AC pregrado = {fac}'.format(fac=N_AC_pre))
    print('Número AC postgrado = {fac}'.format(fac=N_AC_post))

    # Revisar número AC institución, si hay postgrado entonces
    # calculamos el índice de AC a escoger

    def formula_post(ac, ac_pre, ac_post):
        # Fórmula usada en el cálculo de índices
        frac = ac/(1 + ac_pre/ac_post)
        if frac - np.floor(frac) <= 0.4:
            valor = np.floor(frac)
        elif frac - np.floor(frac) >= 0.5:
            valor = np.floor(frac) + 1
        return int(valor)

    if N_AC_post > 0:
        indice_post = formula_post(N_AC, N_AC_pre, N_AC_post)
        indice_pre = N_AC - indice_post
    else:
        indice_pre = N_AC
        indice_post = 0

    # Revisar el caso N_AC = 1

    if N_AC == 1:
        seleccion_final = caso_1_AC(base)
    elif 'FFAA' in IES.split(' '):
        seleccion_final = caso_FFAA(base)
    elif N_AC > 1:
        data_seleccion_0 = np.empty((N_AC, len(base.columns)), dtype=object)

        # Hacer excepción para el caso Universidad con TNS
        # (implementación alternativa 1)

        caso_universidad = 'UNIVERSIDAD' in IES.split(' ')
        caso_TNS = 'Si' in base['TNS'].unique()

        AC_bloqueada_TNS = np.array([])
        if caso_TNS and caso_universidad:
            base_TNS = base[base['TNS'] == 'Si']
            AC_TNS = base_TNS['AC'].unique()
            AC_bloqueada_TNS = np.random.choice(AC_TNS, size=1)

        for n, area in enumerate(AREAS):
            base_AC = base[base['AC'] == area]
            # Colocar índice 1..n al inicio
            if len(AC_bloqueada_TNS) > 0 and area == AC_bloqueada_TNS:
                base_AC = base_AC[base_AC['TNS'] == 'Si']
            N = base_AC.shape[0]  # filas
            escoger = np.random.randint(N)
            prog_elegido = base_AC.iloc[escoger]
            data_seleccion_0[n] = prog_elegido

        seleccion_0 = pd.DataFrame(data=data_seleccion_0, columns=base.columns)

        # Exportar tabla de selección antes de reemplazo

        seleccion_0.to_excel('DB_OK/'
                             + 'selección/'
                             + '{inst}_selección_inicial.xlsx'.format(inst=IES),
                             index=False)

        # Algoritmo de reemplazo

        # Cantidad de postgrados de la MI

        hist_nivel_seleccion = seleccion_0['nivel'].value_counts()
        if 'Postgrado' in hist_nivel_seleccion:
            post_en_MI = hist_nivel_seleccion['Postgrado']
        else:
            post_en_MI = 0

        # Verificar grupo en exceso
        if post_en_MI == indice_post:
            print('Terminado')
            seleccion_0.to_excel('DB_OK/selección/{inst}_selección.xlsx'.format(inst=IES),
                                 index=False)
            seleccion_final = seleccion_0
            return True
        elif post_en_MI > indice_post:
            print('Excedente en Postgrado')
            N_reemplazo = post_en_MI - indice_post
            nivel_en_exceso = 'Postgrado'
            nivel_escasez = 'Pregrado'
        else:
            print('Excedente en Pregrado')
            N_reemplazo = - (post_en_MI - indice_post)
            nivel_en_exceso = 'Pregrado'
            nivel_escasez = 'Postgrado'

        # Identificar áreas seleccionadas en exceso que también
        # estén en grupo en escasez
        areas_en_exceso = seleccion_0[seleccion_0['nivel'] ==
                                      nivel_en_exceso]['AC'].unique()
        # areas_escasez = seleccion_0[seleccion_0['nivel'] ==
        #                             nivel_escasez]['AC'].unique()

        if nivel_escasez == 'Pregrado':
            areas_base_escasez = AC_pre
        else:
            areas_base_escasez = AC_post

        conjunto_reemplazo = np.intersect1d(areas_en_exceso,
                                            areas_base_escasez)

        # Quitar la AC bloqueada, en caso que exista

        conjunto_reemplazo = np.setdiff1d(conjunto_reemplazo, AC_bloqueada_TNS)

        # Determinar las áreas a reemplazar

        if len(conjunto_reemplazo) == N_reemplazo:
            AC_reemplazo = conjunto_reemplazo
        elif len(conjunto_reemplazo) > N_reemplazo:
            AC_reemplazo = np.random.choice(conjunto_reemplazo,
                                            size=N_reemplazo,
                                            replace=False)
        else:
            print('ERROR')
            return False

        # Hacer el reemplazo en esta área, sólo tomando programas
        # del área en escasez

        seleccion_final = seleccion_0.copy()

        for area in AC_reemplazo:
            base_AC = base[base['AC'] == area]
            base_AC = base_AC[base_AC['nivel'] == nivel_escasez]
            N = base_AC.shape[0]  # filas
            escoger = np.random.randint(N)
            prog_elegido = base_AC.iloc[escoger]
            bool_AC = seleccion_final['AC'] == area
            seleccion_final[bool_AC] = prog_elegido.to_numpy()

    # Agregar sedes a cada programa elegido

    # Nuevas columnas donde escribir las sedes

    seleccion_final.insert(6, 'Sede 1', '')
    seleccion_final.insert(7, 'Sede 2', '')
    seleccion_final.insert(8, 'Sede 3', '')

    Sedes = pd.read_excel('DB_OK/sedes.xlsx', index_col=0)

    # Elegir las sedes de manera aleatoria, considera los 3 casos posibles
    # y escoge 1, 2 o 3 sedes para cada caso

    for i in np.arange(len(seleccion_final)):
        cod = seleccion_final['Codigo'][i]
        if len(Sedes.loc[cod].dropna()) in np.arange(1, 3 + 1):
            sedes_seleccionadas = np.random.choice(Sedes.loc[cod].dropna(),
                                                   size=1,
                                                   replace=False)
            seleccion_final['Sede 1'][i] = sedes_seleccionadas[0]
        elif len(Sedes.loc[cod].dropna()) in np.arange(4, 9 + 1):

            sedes_seleccionadas = np.random.choice(Sedes.loc[cod].dropna(),
                                                   size=2,
                                                   replace=False)
            seleccion_final['Sede 1'][i] = sedes_seleccionadas[0]
            seleccion_final['Sede 2'][i] = sedes_seleccionadas[1]
        elif len(Sedes.loc[cod].dropna()) >= 10:
            sedes_seleccionadas = np.random.choice(Sedes.loc[cod].dropna(),
                                                   size=3,
                                                   replace=False)
            seleccion_final['Sede 1'][i] = sedes_seleccionadas[0]
            seleccion_final['Sede 2'][i] = sedes_seleccionadas[1]
            seleccion_final['Sede 3'][i] = sedes_seleccionadas[2]

    # Guardar en excel

    seleccion_final.to_excel('DB_OK/selección/{inst}_selección.xlsx'.format(inst=IES),
                             index=False)

    # Generar tabla con datos de la IES que se calculó

    demografia_IES = np.empty((1, 6), dtype=object)

    demografia_IES[0, 0] = IES
    demografia_IES[0, 1] = indice_pre
    demografia_IES[0, 2] = indice_post
    demografia_IES[0, 3] = len(base[base['nivel'] == 'Pregrado'])
    demografia_IES[0, 4] = len(base[base['nivel'] == 'Postgrado'])
    if 'Si' in base['TNS'].unique():
        demografia_IES[0, 5] = 'Si'
    else:
        demografia_IES[0, 5] = 'No'

    columnas_demografia = ['IES', 'indice_pre',
                           'indice_post', 'pre_elegibles',
                           'post_elegibles', 'Tiene TNS']

    demografia_IES = pd.DataFrame(data=demografia_IES,
                                  columns=columnas_demografia)

    return True
