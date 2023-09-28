"""Archivo principal que toma recibe las bases de datos y retorna las tablas
y archivos necesarios para ejecutar el programa
"""

import os
import sys
import errno
import numpy as np
import pandas as pd


def Main(foldername, off_path, mat_path, titul_path):
    """Ejecuta programa para ordenar bases de datos
    y guardarlas en archivo xlsx en el directorio foldername.

    Keyword arguments:
    foldername -- Nombre del directorio donde guardar archivos
    """

    # Nuevo archivo limpiador para archivos de base SIES
    # def lecto_limpiador(archivo):
    #     x = pd.read_csv(archivo,
    #                     encoding='Windows 1252',
    #                     sep=";",
    #                     low_memory=False)
    #     x.columns = x.columns.str.strip()

    def lecto_limpiador(archivo):
        """"Carga archivo, normaliza strings y retorna Data Frame."""
        x = pd.read_csv(archivo, encoding='utf-8', sep=";",
                        low_memory=False)
        x.columns = x.columns.str.replace(' ', '')
        regex_reemplazo = r'\W'
        x.columns = x.columns.str.replace(regex_reemplazo, '', regex=True)
        x.columns = x.columns.str.normalize('NFKD')
        x.columns = x.columns.str.encode('ascii', errors='ignore')
        x.columns = x.columns.str.decode('utf-8')
        x.columns = x.columns.str.upper()
        return x

    matricula = lecto_limpiador(mat_path)
    titulados = lecto_limpiador(titul_path)

    def codigo_corto(df):
        """Cambiar código de la carrera por el código único reducido."""
        x = df
        regex_codigo = r"[SJV]\d*"
        x = x.str.replace(pat=regex_codigo, repl='', regex=True)
        return x

    def codigo_corto_sede(df):
        """Cambiar código de la carrera por el código único reducido."""
        x = df
        regex_codigo = r"[JV]\d*"
        x = x.str.replace(pat=regex_codigo, repl='', regex=True)
        return x

    matricula['CODIGOCARRERA'] = codigo_corto(matricula['CODIGOCARRERA'])
    titulados['CODIGOCARRERA'] = codigo_corto(titulados['CODIGOCARRERA'])

    # Generar diccionario de sedes por código corto únicos.
    cod_no_duplicados = np.unique(matricula.CODIGOCARRERA)

    sedes = {}

# Diccionario = matriz sin orden particular
# {código1: [sede1, sede2, sede3, ...],
# código2: ...}

    for codigo in cod_no_duplicados:
        sedes.update({codigo: np.unique(matricula['NOMBRESEDE'][
                                        matricula['CODIGOCARRERA'] == codigo
                                        ])})

    df_sedes = pd.DataFrame.from_dict(data=sedes, orient='Index')

    # Guardar sedes en un archivo independiente
    df_sedes.to_excel('DB_OK/sedes.xlsx')

    # Hacer conjunto de carreras elegibles por requisito: debe tener
    # matrícula vigente de primer año > 0,
    # titulados, sólo seleccionar EEMMOO en postítulo,

    # Condiciones escritas para filtrar.
    eemmoo_str = "Especialidad Médica U Odontológica"
    bachi_pc_ci_str = "Bachillerato, Ciclo Inicial o Plan Común"
    TNS_str = 'Técnico de Nivel Superior'
    Postitulo_str = 'Postítulo'

    def Filtro_codigos(df, condition_mask):
        """Retorna Data Frame df filtrado según condition_mask"""
        return df['CODIGOCARRERA'].copy().loc[condition_mask].unique()

    set_matr_vigente = Filtro_codigos(
        matricula,
        matricula['TOTALMATRICULADOSPRIMERANO'] > 0)
    set_titulados = Filtro_codigos(
        titulados,
        titulados['TOTALTITULADOS'] > 0)

    eemmoo = Filtro_codigos(
        matricula,
        matricula['CARRERACLASIFICACIONNIVEL1'] == eemmoo_str)
    pre_post = Filtro_codigos(
        matricula,
        matricula['NIVELGLOBAL'] != Postitulo_str)
    bachi_pc_ci = Filtro_codigos(
        matricula,
        matricula['CARRERACLASIFICACIONNIVEL1'] == bachi_pc_ci_str)

    programas = np.setdiff1d(np.union1d(eemmoo, pre_post), bachi_pc_ci)
    elegibles = np.intersect1d(np.intersect1d(programas,
                               set_matr_vigente), set_titulados)

    tabla_con_datos = np.empty((len(elegibles), 6), dtype=object)

    def Filtrar(column, indice):
        """Retorna elemento en column e indice dados."""
        mask_indice = matricula['CODIGOCARRERA'] == indice
        return matricula[column][mask_indice].unique()[0]

    for i, indice in enumerate(elegibles):
        tabla_con_datos[i, 0] = indice
        tabla_con_datos[i, 1] = Filtrar('NOMBRECARRERA', indice)
        tabla_con_datos[i, 2] = Filtrar('NOMBREINSTITUCION', indice)
        tabla_con_datos[i, 3] = Filtrar('AREADELCONOCIMIENTO', indice)
        tabla_con_datos[i, 4] = Filtrar('NIVELGLOBAL', indice)
        if Filtrar('CARRERACLASIFICACIONNIVEL1', indice) == TNS_str:
            tabla_con_datos[i, 5] = 'Si'

    columnas_tabla_elegible = ['Codigo', 'Carrera', 'IES',
                               'AC', 'nivel', 'TNS']

    tabla_elegible = pd.DataFrame(data=tabla_con_datos,
                                  columns=columnas_tabla_elegible, dtype=str)
    tabla_elegible = tabla_elegible.replace('Postítulo', 'Postgrado')

    # De acá en adelante se trabajará con la tabla_elegible para los análisis.

    # Crear directorio en caso de no existir.
    if not os.path.exists(os.path.dirname(foldername + '/')):
        try:
            os.makedirs(os.path.dirname(foldername + '/'))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

    # Guardar tabla de datos  y elegibles en formato .xlsx.
    for i in tabla_elegible['IES'].unique():
        directorio = foldername + '/{fies}.xlsx'.format(fies=i)
        tabla_elegible[tabla_elegible['IES'] == i].to_excel(directorio,
                                                            index=True)

    tabla_elegible.to_excel(foldername + '/elegibles.xlsx', index=False)


if __name__ == "__main__":
    foldername = sys.argv[1] if len(sys.argv) > 1 else "DB_OK/"
    Main(foldername)
