# Archivo principal que toma recibe las bases de datos y retorna las tablas
# y archivos necesarios para ejecutar el programa

import numpy as np
import pandas as pd


def lecto_limpiador(archivo):
    # Carga el archivo de DB y le cambia las columnas
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


matricula = lecto_limpiador('DB/matricula_filtrado.csv')
titulados = lecto_limpiador('DB/titulados_filtrado.csv')

# Cambiar código de la carrera por el código único reducido


def cambiar_codigo(df):
    x = df.CODIGOCARRERA
    regex_codigo = r"[SJV]\d*"
    x = x.str.replace(pat=regex_codigo, repl='', regex=True)
    return x


matricula.CODIGOCARRERA = cambiar_codigo(matricula)
titulados.CODIGOCARRERA = cambiar_codigo(titulados)

# Generar diccionario de sedes por código reducido

cod_res = np.unique(matricula.CODIGOCARRERA)

sedes = {}

for codigo in cod_res:
    sedes.update({codigo: np.unique(matricula.NOMBRESEDE[
                                    matricula.CODIGOCARRERA == codigo])})

df_sedes = pd.DataFrame.from_dict(data=sedes, orient='Index')

# Guardar sedes en un archivo independiente

df_sedes.to_excel('DB_OK/sedes.xlsx')

# Hacer conjunto de carreras elegibles por requisito: debe tener matrícula,
# titulados, excluir todo lo que no sea EEMMOO en postítulo,

# Condiciones escritas para filtrar

eemmoo_str = "Especialidad Médica U Odontológica"
bachi_pc_ci_str = "Bachillerato, Ciclo Inicial o Plan Común"
TNS_str = 'Técnico de Nivel Superior'
Post_str = 'Postítulo'

set_matr_vigente = np.unique(matricula.CODIGOCARRERA.copy().loc[
                             matricula.TOTALMATRICULADOSPRIMERANO > 0])
set_titulados = np.unique(titulados.CODIGOCARRERA.copy().loc[
                          titulados.TOTALTITULADOS > 0])

eemmoo = np.unique(matricula.CODIGOCARRERA.copy().loc[
                   matricula.CARRERACLASIFICACIONNIVEL1 ==
                   eemmoo_str])
pre_post = np.unique(matricula.CODIGOCARRERA.copy().loc[
                     matricula.NIVELGLOBAL != Post_str])
bachi_pc_ci = np.unique(matricula.CODIGOCARRERA.copy().loc[
                        matricula.CARRERACLASIFICACIONNIVEL1 ==
                        bachi_pc_ci_str])

programas = np.setdiff1d(np.union1d(eemmoo, pre_post), bachi_pc_ci)
elegibles = np.intersect1d(np.intersect1d(programas,
                           set_matr_vigente), set_titulados)

tabla_con_datos = np.empty((len(elegibles), 6), dtype=object)

for i in np.arange(len(elegibles)):
    indice = elegibles[i]
    tabla_con_datos[i, 0] = indice
    tabla_con_datos[i, 1] = matricula.NOMBRECARRERA[matricula.CODIGOCARRERA ==
                                                    indice].unique()[0]
    tabla_con_datos[i, 2] = np.unique(matricula.NOMBREINSTITUCION[
                                      matricula.CODIGOCARRERA == indice])[0]
    tabla_con_datos[i, 3] = np.unique(matricula.AREADELCONOCIMIENTO[
                                      matricula.CODIGOCARRERA == indice])[0]
    tabla_con_datos[i, 4] = np.unique(matricula.NIVELGLOBAL[
                                      matricula.CODIGOCARRERA == indice])[0]
    if np.unique(matricula['CARRERACLASIFICACIONNIVEL1'][
                 matricula.CODIGOCARRERA == indice])[0] == TNS_str:
        tabla_con_datos[i, 5] = 'Si'

columnas_tabla_elegible = ['Codigo', 'Carrera', 'IES', 'AC', 'nivel', 'TNS']

tabla_elegible = pd.DataFrame(data=tabla_con_datos,
                              columns=columnas_tabla_elegible, dtype=str)
tabla_elegible = tabla_elegible.replace('Postítulo', 'Postgrado')


# De acá en adelante se trabajará con la tabla_elegible para los análisis

for i in tabla_elegible['IES'].unique():
    directorio = 'DB_OK/{fies}.xlsx'.format(fies=i)
    tabla_elegible[tabla_elegible['IES'] == i].to_excel(directorio,
                                                        index=False)

tabla_elegible.to_excel('DB_OK/elegibles.xlsx', index=False)

input('Presione ENTER tecla para cerrar')

# --------------------------------------------------------------------
