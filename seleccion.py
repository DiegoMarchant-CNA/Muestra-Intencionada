# coding=utf-8
import numpy as np
import pandas as pd
import sys
import os

# Cargar base para muestra intencionada

# lista_IES = os.listdir('DB_OK')

# lista_IES = [inst.replace('.xlsx', "") for inst in lista_IES]

# IES = ""

# while IES not in lista_IES:
#     IES = input('Indique el nombre de la IES a la que calcular la MI: \n')
#     IES = IES.upper()
#     if IES not in lista_IES:
#         print('Nombre no en sistema. Intente de nuevo')

def funcion_seleccion(IES):

    PATH = 'DB_OK/{inst}.xlsx'.format(inst=IES)

    base = pd.read_excel(PATH)

    # Revisar número AC institución
    AREAS = base['AC'].unique()  # type: ignore
    N_AC = len(AREAS)
    print(['Número AC total = {fac}'.format(fac=N_AC)])

    AC_pre = base[base['nivel'] == 'Pregrado']['AC'].unique()  # type: ignore
    N_AC_pre = len(AC_pre)
    print('Número AC pregrado = {fac}'.format(fac=N_AC_pre))

    AC_post = base[base['nivel'] == 'Postgrado']['AC'].unique()  # type: ignore
    N_AC_post = len(AC_post)
    print('Número AC postgrado = {fac}'.format(fac=N_AC_post))

    # Revisar número AC institución, si hay postgrado entonces
    # calculamos el índice de AC a escoger

    if N_AC_post > 0:
        indice_post = int(np.floor(N_AC/(1 + (N_AC_pre/N_AC_post)) + 0.5))
        indice_pre = N_AC - indice_post
    else:
        indice_pre = N_AC
        indice_post = 0

    # Revisar el caso N_AC = 1


    def caso_1_AC():
        N_prog = base.shape[0]
        if N_prog == 1:
            data_seleccion_0 = np.empty((1, len(base.columns)), dtype=object)
            data_seleccion_0[0] = base.iloc[0]
        elif N_prog > 1 and N_prog < 10:
            data_seleccion_0 = np.empty((2, len(base.columns)), dtype=object)
            elegir = np.random.choice(np.arange(N_prog), 2, replace=False)
            data_seleccion_0[0] = base.iloc[elegir[0]]
            data_seleccion_0[1] = base.iloc[elegir[1]]
        elif N_prog > 9:
            elegir = np.random.choice(np.arange(N_prog), 3, replace=False)
            data_seleccion_0 = np.empty((3, len(base.columns)), dtype=object)
            data_seleccion_0[0] = base.iloc[elegir[0]]
            data_seleccion_0[1] = base.iloc[elegir[1]]
            data_seleccion_0[2] = base.iloc[elegir[2]]
        return pd.DataFrame(data=data_seleccion_0, columns=base.columns)


    if N_AC == 1:
        seleccion_final = caso_1_AC()
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

        n = 0
        for area in AREAS:
            base_AC = base[base['AC'] == area]
            if len(AC_bloqueada_TNS) > 0 and area == AC_bloqueada_TNS:
                base_AC = base_AC[base_AC['TNS'] == 'Si']
            N = base_AC.shape[0]  # filas
            escoger = np.random.randint(N)
            prog_elegido = base_AC.iloc[escoger]
            data_seleccion_0[n] = prog_elegido
            n += 1

        seleccion_0 = pd.DataFrame(data=data_seleccion_0, columns=base.columns)

        # Exportar tabla de selección antes de reemplazo

        seleccion_0.to_excel('DB_OK/selección/selección inicial.xlsx', index=False)

        # Algoritmo de reemplazo

        # Cantidad de postgrados de la MI
        if 'Postgrado' in seleccion_0['nivel'].value_counts(sort=False):
            post_en_MI = seleccion_0['nivel'].value_counts(sort=False)['Postgrado']
        else:
            post_en_MI = 0

        # Verificar grupo en exceso
        if post_en_MI == indice_post:
            print('Terminado')
            seleccion_0.to_excel('DB_OK/selección/selección final.xlsx',
                                 index=False)
            seleccion_final = seleccion_0
            return 
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
        areas_escasez = seleccion_0[seleccion_0['nivel'] ==
                                    nivel_escasez]['AC'].unique()

        if nivel_escasez == 'Pregrado':
            areas_base_escasez = AC_pre
        else:
            areas_base_escasez = AC_post

        conjunto_reemplazo = np.intersect1d(areas_en_exceso, areas_base_escasez)

        # Quitar la AC bloqueada, en caso que exista

        conjunto_reemplazo = np.setdiff1d(conjunto_reemplazo, AC_bloqueada_TNS)

        # Determinar las áreas a reemplazar

        if len(conjunto_reemplazo) == N_reemplazo:
            AC_reemplazo = conjunto_reemplazo
        elif len(conjunto_reemplazo) > N_reemplazo:
            AC_reemplazo = np.random.choice(conjunto_reemplazo, size=N_reemplazo,
                                            replace=False)
        else:
            print('ERROR')

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
            sedes_seleccionadas = np.random.choice(Sedes.loc[cod].dropna(), size=1,
                                                replace=False)
            seleccion_final['Sede 1'][i] = sedes_seleccionadas[0]
        elif len(Sedes.loc[cod].dropna()) in np.arange(4, 9 + 1):

            sedes_seleccionadas = np.random.choice(Sedes.loc[cod].dropna(), size=2,
                                                replace=False)
            seleccion_final['Sede 1'][i] = sedes_seleccionadas[0]
            seleccion_final['Sede 2'][i] = sedes_seleccionadas[1]
        elif len(Sedes.loc[cod].dropna()) >= 10:
            sedes_seleccionadas = np.random.choice(Sedes.loc[cod].dropna(), size=3,
                                                replace=False)
            seleccion_final['Sede 1'][i] = sedes_seleccionadas[0]
            seleccion_final['Sede 2'][i] = sedes_seleccionadas[1]
            seleccion_final['Sede 3'][i] = sedes_seleccionadas[2]


    # Guardar en excel
    seleccion_final.to_excel('DB_OK/selección/selección final.xlsx', index=False)


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

    columnas_demografia = ['IES', 'indice_pre0', 'indice_post', 'pre_elegibles',
                        'post_elegibles', 'Tiene TNS']

    demografia_IES = pd.DataFrame(data=demografia_IES,
                                columns=columnas_demografia)


    print(seleccion_final)

    return 
