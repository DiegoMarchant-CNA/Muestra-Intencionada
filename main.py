"""Archivo principal que toma recibe las bases de datos y retorna las tablas
y archivos necesarios para ejecutar el programa
"""

import numpy as np
import pandas as pd
import sys


def Main(foldername, oferta_path, mat_path, titulados_path):
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
    #     return x

    def lecto_limpiador(archivo):
        """"Carga archivo, normaliza strings y retorna Data Frame."""
        x = pd.read_csv(archivo, encoding='utf-8', sep=";",
                        low_memory=False)
        x.columns = x.columns.str.strip()
        x.columns = x.columns.str.replace(' ', '')
        regex_reemplazo = r'\W'
        x.columns = x.columns.str.replace(regex_reemplazo, '', regex=True)
        x.columns = x.columns.str.normalize('NFKD')
        x.columns = x.columns.str.encode('ascii', errors='ignore')
        x.columns = x.columns.str.decode('utf-8')
        x.columns = x.columns.str.upper()
        return x

    oferta = lecto_limpiador(oferta_path)
    matricula = lecto_limpiador(mat_path)
    titulados = lecto_limpiador(titulados_path)

    # Cambiar columna Código Único por
    # columna de código corto con sede en bases
    # de Matrícula y Titulados.
    # Para base de Oferta, crear columna calculada
    # como concatenación de Código IES y Código carrera

    def codigo_corto(df):
        """Cambiar código de la carrera por el código único reducido."""
        x = df
        regex_codigo = r"[SJV]\d*"
        x = x.str.replace(pat=regex_codigo, repl='', regex=True)
        return x

    matricula['CÓDIGO CARRERA'] = codigo_corto(matricula['CÓDIGO CARRERA'])
    titulados['CÓDIGO CARRERA'] = codigo_corto(titulados['CÓDIGO CARRERA'])

    codigo_oferta = (
                     'I'
                     + oferta['Código IES'].astype(str)
                     + 'C'
                     + oferta['Código Carrera'].astype(str)
                     )

    oferta.insert(0, 'Código Corto', codigo_oferta)

    # Exportar base de Sedes

    Sedes = matricula[[
                       'CÓDIGO CARRERA',
                       'NOMBRE SEDE',
                       'TOTAL MATRICULADOS'
                       ]]

    Sedes = Sedes.groupby(by=['CÓDIGO CARRERA', 'NOMBRE SEDE'],
                          as_index=False).sum()

    Sedes.to_excel('DB_OK/sedes.xlsx')

    # Crear subtablas con exportables y datos usados para cruce:

    # Oferta: [Código corto CS, Tipo Institución 1, Nombre IES,
    # Nombre Carrera, Nivel Global, Nivel Carrera, Área del Conocimiento]

    # Matrícula: [Código corto CS, Nombre Sede, Total Matriculados,
    # Total Matr. 1er Año]

    # Titulados: [Código corto, Total Titulados]

    # Subtablas con info. necesaria para seleccionar elegibles
    Base_oferta = oferta[[
                          'Código Corto',
                          'Tipo Institución 1',
                          'Nombre IES',
                          'Nombre Carrera',
                          'Nivel Global',
                          'Nivel Carrera',
                          'Área del conocimiento'
                          ]]

    Base_matricula = matricula[[
                                'CÓDIGO CARRERA',
                                'TOTAL MATRICULADOS',
                                'TOTAL MATRICULADOS PRIMER AÑO'
                                ]]
    Base_matricula = Base_matricula.rename(columns={
                            'CÓDIGO CARRERA': 'Código Corto',
                            'TOTAL MATRICULADOS': 'Total Matriculados',
                            'TOTAL MATRICULADOS PRIMER AÑO':
                            'Matrícula Primer Año'}
                          )

    Base_titulados = titulados[[
                                'CÓDIGO CARRERA',
                                'TOTAL TITULADOS'
                                ]]
    Base_titulados = Base_titulados.rename(columns={
                            'CÓDIGO CARRERA': 'Código Corto',
                            'TOTAL TITULADOS': 'Titulados'}
                          )

    # Quedarse con una base de casos únicos
    Base_oferta = Base_oferta.drop_duplicates()

    # En los casos de matrícula y titulados,
    # agregar los datos usando suma. Ej. la matrícula de la carrera
    # es la suma de las matrículas en cada sede
    # y de cada versión y modalidad

    Base_matricula = Base_matricula.groupby(by=['Código Corto'],
                                            as_index=False).sum()

    Base_titulados = Base_titulados.groupby(by=['Código Corto'],
                                            as_index=False).sum()

    # Generar base con cruce

    base_general = pd.merge(Base_oferta, Base_matricula, on='Código Corto', how='left')

    base_general = pd.merge(base_general, Base_titulados, on='Código Corto', how='left')

    base_general.to_excel(path+'prueba.xlsx', index=False)

    # Proceder con la filtración. Se consideran las condiciones de:
    # Tener matrícula vigente de primer año > 0,
    # Tener titulados
    # sólo seleccionar EEMMOO en postítulo (quitar diplomados, bachi, PC, CI)

    # Condiciones escritas para filtrar.
    eemmoo_str = "Especialidad Médica U Odontológica"
    bachi_pc_ci_str = "Bachillerato, Ciclo Inicial o Plan Común"
    TNS_str = 'Técnico de Nivel Superior'
    Postitulo_str = 'Postítulo'

    def Filtro_codigos(df, condition_mask):
        """Retorna Data Frame df filtrado según condition_mask"""
        return df['Código Corto'].copy().loc[condition_mask].unique()

    set_matr_vigente = Filtro_codigos(
        base_general,
        base_general['Matrícula Primer Año'] > 0)

    set_titulados = Filtro_codigos(
        base_general,
        base_general['Titulados'] > 0)

    eemmoo = Filtro_codigos(
        base_general,
        base_general['Nivel Carrera'] == eemmoo_str)

    pre_post = Filtro_codigos(
        base_general,
        base_general['Nivel Global'] != Postitulo_str)

    bachi_pc_ci = Filtro_codigos(
        base_general,
        base_general['Nivel Carrera'] == bachi_pc_ci_str)

    programas = np.setdiff1d(np.union1d(eemmoo, pre_post), bachi_pc_ci)
    elegibles = np.intersect1d(np.intersect1d(programas,
                               set_matr_vigente), set_titulados)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # def codigo_corto(df):
    #     """Cambiar código de la carrera por el código único reducido."""
    #     x = df
    #     regex_codigo = r"[SJV]\d*"
    #     x = x.str.replace(pat=regex_codigo, repl='', regex=True)
    #     return x

    # def codigo_corto_sede(df):
    #     """Cambiar código de la carrera por el código único reducido."""
    #     x = df
    #     regex_codigo = r"[JV]\d*"
    #     x = x.str.replace(pat=regex_codigo, repl='', regex=True)
    #     return x

#     matricula['CODIGOCARRERA'] = codigo_corto(matricula['CODIGOCARRERA'])
#     titulados['CODIGOCARRERA'] = codigo_corto(titulados['CODIGOCARRERA'])

#     # Generar diccionario de sedes por código corto únicos.
#     cod_no_duplicados = np.unique(matricula.CODIGOCARRERA)

#     sedes = {}

# # Diccionario = matriz sin orden particular
# # {código1: [sede1, sede2, sede3, ...],
# # código2: ...}

#     for codigo in cod_no_duplicados:
#         sedes.update({codigo: np.unique(matricula['NOMBRESEDE'][
#                                         matricula['CODIGOCARRERA'] == codigo
#                                         ])})

#     df_sedes = pd.DataFrame.from_dict(data=sedes, orient='Index')

#     # Guardar sedes en un archivo independiente
#     df_sedes.to_excel('DB_OK/sedes.xlsx')

#     # Hacer conjunto de carreras elegibles por requisito: debe tener
#     # matrícula vigente de primer año > 0,
#     # titulados, sólo seleccionar EEMMOO en postítulo,

#     # Condiciones escritas para filtrar.
#     eemmoo_str = "Especialidad Médica U Odontológica"
#     bachi_pc_ci_str = "Bachillerato, Ciclo Inicial o Plan Común"
#     TNS_str = 'Técnico de Nivel Superior'
#     Postitulo_str = 'Postítulo'

#     def Filtro_codigos(df, condition_mask):
#         """Retorna Data Frame df filtrado según condition_mask"""
#         return df['CODIGOCARRERA'].copy().loc[condition_mask].unique()

#     set_matr_vigente = Filtro_codigos(
#         matricula,
#         matricula['TOTALMATRICULADOSPRIMERANO'] > 0)
#     set_titulados = Filtro_codigos(
#         titulados,
#         titulados['TOTALTITULADOS'] > 0)

#     eemmoo = Filtro_codigos(
#         matricula,
#         matricula['CARRERACLASIFICACIONNIVEL1'] == eemmoo_str)
#     pre_post = Filtro_codigos(
#         matricula,
#         matricula['NIVELGLOBAL'] != Postitulo_str)
#     bachi_pc_ci = Filtro_codigos(
#         matricula,
#         matricula['CARRERACLASIFICACIONNIVEL1'] == bachi_pc_ci_str)

#     programas = np.setdiff1d(np.union1d(eemmoo, pre_post), bachi_pc_ci)
#     elegibles = np.intersect1d(np.intersect1d(programas,
#                                set_matr_vigente), set_titulados)

#     tabla_con_datos = np.empty((len(elegibles), 6), dtype=object)

#     def Filtrar(column, indice):
#         """Retorna elemento en column e indice dados."""
#         mask_indice = matricula['CODIGOCARRERA'] == indice
#         return matricula[column][mask_indice].unique()[0]

#     for i, indice in enumerate(elegibles):
#         tabla_con_datos[i, 0] = indice
#         tabla_con_datos[i, 1] = Filtrar('NOMBRECARRERA', indice)
#         tabla_con_datos[i, 2] = Filtrar('NOMBREINSTITUCION', indice)
#         tabla_con_datos[i, 3] = Filtrar('AREADELCONOCIMIENTO', indice)
#         tabla_con_datos[i, 4] = Filtrar('NIVELGLOBAL', indice)
#         if Filtrar('CARRERACLASIFICACIONNIVEL1', indice) == TNS_str:
#             tabla_con_datos[i, 5] = 'Si'

#     columnas_tabla_elegible = ['Codigo', 'Carrera', 'IES',
#                                'AC', 'nivel', 'TNS']

#     tabla_elegible = pd.DataFrame(data=tabla_con_datos,
#                                   columns=columnas_tabla_elegible, dtype=str)
#     tabla_elegible = tabla_elegible.replace('Postítulo', 'Postgrado')

#     # De acá en adelante se trabajará con la tabla_elegible para los análisis.



#     # Guardar tabla de datos  y elegibles en formato .xlsx.
#     for i in tabla_elegible['IES'].unique():
#         directorio = foldername + '/{fies}.xlsx'.format(fies=i)
#         tabla_elegible[tabla_elegible['IES'] == i].to_excel(directorio,
#                                                             index=True)

#     tabla_elegible.to_excel(foldername + '/elegibles.xlsx', index=False)


if __name__ == "__main__":
    foldername = sys.argv[1] if len(sys.argv) > 1 else "DB_OK/"
    Main(foldername)
