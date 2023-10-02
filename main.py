"""Archivo principal que toma recibe las bases de datos y retorna las tablas
y archivos necesarios para ejecutar el programa
"""

import numpy as np
import pandas as pd
import logging
import sys

# Llamar logger

main_log = logging.getLogger('Main')


# Archivo principal

def Main(foldername, oferta_path, mat_path, titulados_path):
    """Ejecuta programa para ordenar bases de datos
    y guardarlas en archivo xlsx en el directorio foldername.

    Keyword arguments:
    foldername -- Nombre del directorio donde guardar archivos
    """
    main_log.info('Se inicia Main')

    # Nuevo archivo limpiador para archivos de base SIES
    def lecto_limpiador(archivo):
        main_log.info(f'Función para depurar archivo {archivo}')
        x = pd.read_csv(archivo,
                        encoding='Windows 1252',
                        sep=";",
                        low_memory=False)
        x.columns = x.columns.str.strip()
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
    
    Sedes = Sedes.rename(columns={
                        'CÓDIGO CARRERA': 'Código Corto',
                        'NOMBRE SEDE': 'Nombre Sede',
                        'TOTAL MATRICULADOS': 'Matrícula Total'}
                        )

    PATH_sedes = 'DB_OK/sedes.xlsx'

    Sedes.to_excel(PATH_sedes, index=False)
    main_log.debug(f'Se guarda archivo sedes en {PATH_sedes}')

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
                            'TOTAL MATRICULADOS': 'Matrícula Total',
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

    base_general = pd.merge(Base_oferta,
                            Base_matricula,
                            on='Código Corto',
                            how='left')
    main_log.debug('Se cruza base oferta con base matricula')

    base_general = pd.merge(base_general,
                            Base_titulados,
                            on='Código Corto',
                            how='left')
    main_log.debug('Se cruza base oferta con base titulados')

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
    main_log.debug('Se filtra base por condicion Matrícula Primer Año > 0')

    set_titulados = Filtro_codigos(
        base_general,
        base_general['Titulados'] > 0)
    main_log.debug('Se filtra base por condicion Titulados > 0')

    eemmoo = Filtro_codigos(
        base_general,
        base_general['Nivel Carrera'] == eemmoo_str)
    main_log.debug('Se filtra base por condicion Nivel Carrera == eemmoo_str')

    pre_post = Filtro_codigos(
        base_general,
        base_general['Nivel Global'] != Postitulo_str)
    main_log.debug('Se filtra base por condicion Nivel Global' +
                   ' != Postitulo_str')

    bachi_pc_ci = Filtro_codigos(
        base_general,
        base_general['Nivel Carrera'] == bachi_pc_ci_str)
    main_log.debug('Se filtra base por condicion Nivel Carrera ' +
                   '== bachi_pc_ci_str')

    programas = np.setdiff1d(np.union1d(eemmoo, pre_post), bachi_pc_ci)
    elegibles = np.intersect1d(np.intersect1d(programas,
                               set_matr_vigente), set_titulados)
    main_log.debug('Se calcula vector de elegibles')

    # Agregar columna caso TNS

    base_general.insert(base_general.shape[1], 'TNS', '')

    base_general.loc[base_general['Nivel Carrera'] == TNS_str, 'TNS'] = 'Sí'

    # Agregar columna con elegibilidad

    base_general.insert(base_general.shape[1], 'Elegibles', '')

    base_general.loc[np.isin(base_general['Código Corto'], elegibles),
                     'Elegibles'] = 'Sí'

    base_general.loc[base_general['Nivel Carrera'] == eemmoo_str,
                     'Nivel Global'] = 'Postgrado'

    # Renombrar columnas a nomenclatura CNA

    base_general = base_general.rename(columns={
                                       'Tipo Institución 1':
                                       'Tipo Institución',
                                       'Nombre Carrera':
                                       'Nombre  Carrera o Programa',
                                       'Nombre IES': 'IES',
                                       'Nivel Global': 'Nivel CNA',
                                       'Nivel Carrera': 'Nivel Carrera SIES'}
                                       )

    # Quitar las IES en convenio

    bool_convenio = base_general['IES'].str.contains('convenio',
                                                     case=False)
    base_general = base_general.loc[~bool_convenio]

    # Quitar los postítulos

    bool_postitulo = base_general['Nivel CNA'].str.contains('Postítulo',
                                                             case=False)
    base_general = base_general.loc[~bool_postitulo]

    base_general.to_excel(foldername + '/prueba.xlsx', index=False)

    # Guardar tabla de datos  y elegibles en formato .xlsx.
    for i in base_general['IES'].unique():
        directorio = foldername + '/{fies}.xlsx'.format(fies=i)
        base_general[base_general['IES'] == i].to_excel(directorio,
                                                        index=False)
        main_log.info(f'IES {i} guardado en archivo {directorio}')    


if __name__ == "__main__":
    foldername = sys.argv[1] if len(sys.argv) > 1 else "DB_OK/"
    Main(foldername)
