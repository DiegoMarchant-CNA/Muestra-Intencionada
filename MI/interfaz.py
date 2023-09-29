import os
import errno

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog as fd
from PIL import Image
import logging

import seleccion
from CTkScrollableDropdown import CTkScrollableDropdown
from main import Main

# Set logger para cada módulo

main_log = logging.getLogger('Main')
seleccion_log = logging.getLogger('Seleccion')
interfaz_log = logging.getLogger('Interfaz')

main_log.setLevel(logging.DEBUG)
seleccion_log.setLevel(logging.DEBUG)
interfaz_log.setLevel(logging.DEBUG)

handler = logging.FileHandler('MI.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='[ %d-%m-%Y %H:%M:%S ]')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

main_log.addHandler(handler)
seleccion_log.addHandler(handler)
interfaz_log.addHandler(handler)

# Carpeta donde guardar todo lo nuevo

outputfolder = "DB_OK"

# Configuración inicial de la app


ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('CNA_colors')

# Instanciar la app como ventana

app = ctk.CTk()
app.geometry('1366x718')
app.title('Muestra Intencionada - CNA Chile')
app.after(201, lambda: app.iconbitmap('icon.ico'))
interfaz_log.info('Inicializar interfaz grafica')

# Agregar barra inicial con tabs

tabview = ctk.CTkTabview(master=app)
tabview.pack(anchor=ctk.NW,
             fill='both',
             expand=True)

tabview.add("Inicio")  # add tab at the end
tabview.add("Elegibles")  # add tab at the end
tabview.add("Selección")  # add tab at the end
tabview.set("Inicio")  # set currently visible tab

# ---------------------------------------------------------------------
# Pestaña con descripción inicial

frame_inicio = ctk.CTkFrame(master=tabview.tab('Inicio'),
                            width=1366,
                            height=718)

frame_inicio.pack()

# ---------------------------------------------------------------------
# Pestaña para ejecutar programa de elegibilidad

Oferta_path = ''
Matricula_path = ''
Titulados_path = ''


def select_file_oferta():
    """Función para botón de selección archivo Oferta"""
    filetypes = (
        ('csv (archivo separado por comas)', '.csv'),
        ('Todos los archivos', '*.*')
    )

    global Oferta_path
    file = fd.askopenfilename(
        title='Abrir archivo',
        initialdir='/',
        filetypes=filetypes)
    if file != '':
        Oferta_boton.configure(text=file)
    Oferta_path = file


def select_file_matricula():
    """Función para botón de selección archivo Matrícula"""
    filetypes = (
        ('csv (archivo separado por comas)', '.csv'),
        ('Todos los archivos', '*.*')
    )

    global Matricula_path
    file = fd.askopenfilename(
        title='Abrir archivo',
        initialdir='/',
        filetypes=filetypes)
    if file != '':
        Matricula_boton.configure(text=file)
    Matricula_path = file


def select_file_titulados():
    """Función para botón de selección archivo Titulados"""
    filetypes = (
        ('csv (archivo separado por comas)', '.csv'),
        ('Todos los archivos', '*.*')
    )

    global Titulados_path
    file = fd.askopenfilename(
        title='Abrir archivo',
        initialdir='/',
        filetypes=filetypes)
    if file != '':
        Titulados_boton.configure(text=file)
    Titulados_path = file


def Run_Main():
    Main(outputfolder,
         Oferta_path,
         Matricula_path,
         Titulados_path)
    Run_Main_boton.configure(text='Elegibles listos!')


frame_elegibles = ctk.CTkFrame(master=tabview.tab('Elegibles'),
                               width=1366,
                               height=718)

frame_elegibles.pack(
                     fill='both',
                     expand=True)

OfertaLabel = ctk.CTkLabel(frame_elegibles,
                           text='Seleccione el archivo de Oferta SIES',
                           font=('D-DIN-PRO', 16))
OfertaLabel.pack(pady=10)

Oferta_boton = ctk.CTkButton(
    frame_elegibles,
    text='Oferta SIES',
    command=select_file_oferta)

Oferta_boton.pack(pady=10)


MatriculaLabel = ctk.CTkLabel(frame_elegibles,
                              text='Seleccione el archivo de Matrícula SIES',
                              font=('D-DIN-PRO', 16))
MatriculaLabel.pack(pady=10)

Matricula_boton = ctk.CTkButton(
    frame_elegibles,
    text='Matrícula SIES',
    command=select_file_matricula)

Matricula_boton.pack(pady=10)

TituladosLabel = ctk.CTkLabel(frame_elegibles,
                              text='Seleccione el archivo de Titulados SIES',
                              font=('D-DIN-PRO', 16))
TituladosLabel.pack(pady=10)

Titulados_boton = ctk.CTkButton(
    frame_elegibles,
    text='Titulados SIES',
    command=select_file_titulados)

Titulados_boton.pack(pady=10)

Run_Main_boton = ctk.CTkButton(
    frame_elegibles,
    text='Filtrar elegibles',
    fg_color='#009a44',
    hover_color='#005224',
    command=Run_Main
    )

Run_Main_boton.pack(pady=10)


# ---------------------------------------------------------------------
# Pestaña para ejecutar programa de selección


# Función para iniciar código de selección

def funcion_boton():
    caja.configure(state='normal')
    eleccion = combobox.get()
    seleccion.funcion_seleccion(eleccion)
    var = 'Generando selección...'
    caja.insert('0.0', var+'\n')
    caja.insert('0.0', 'Se ha completado la selección de la institución:\n'
                + eleccion + '\n')

    caja.configure(state='disabled')


# Función para borrar el texto en la caja de output


def limpiar():
    caja.configure(state='normal')
    caja.delete('0.0', 'end')
    caja.configure(state='disabled')


frame_seleccion = ctk.CTkFrame(master=tabview.tab('Selección'),
                               width=1366,
                               height=718)
frame_seleccion.pack(expand=True,
                     fill='both')

fondo = ctk.CTkImage(light_image=Image.open("fondo2.png"),
                     dark_image=Image.open("fondo2.png"),
                     size=(274, 208))
ImageLabel = ctk.CTkLabel(master=frame_seleccion,
                          text='',
                          image=fondo)
ImageLabel.place(anchor=ctk.SW,
                 relx=0.0,
                 rely=1.0)

tituloLabel = ctk.CTkLabel(frame_seleccion,
                           text='Le damos la bienvenida al Programa' +
                           ' para Selección de Muestra Intencionada',
                           font=('D-DIN-PRO', 24))
tituloLabel.pack(pady=10)

subtituloLabel = ctk.CTkLabel(frame_seleccion,
                              text='Elija la institución para hacer la MI',
                              font=('D-DIN-PRO', 16))
subtituloLabel.pack(pady=10)

lista_IES = os.listdir(outputfolder)

lista_IES = [inst.replace('.xlsx', "") for inst in lista_IES]

combobox = ctk.CTkComboBox(frame_seleccion, width=500)
combobox.pack(pady=10)

CTkScrollableDropdown(combobox, values=lista_IES, justify="left",
                      button_color="transparent", autocomplete=True)

# Crear directorio en caso de no existir.
if not os.path.exists(os.path.dirname(outputfolder + '/')):
    try:
        os.makedirs(os.path.dirname(outputfolder + '/'))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

boton = ctk.CTkButton(master=frame_seleccion,
                      text='Generar selección',
                      font=('D-DIN-PRO', 16),
                      command=funcion_boton)
boton.pack(pady=10)

caja = ctk.CTkTextbox(master=frame_seleccion, width=800,
                      height=250,
                      fg_color='light gray',
                      text_color='black',
                      font=('D-DIN-PRO', 14),
                      corner_radius=5,
                      state='disabled')
caja.pack(pady=10)

boton_limpiar = ctk.CTkButton(master=frame_seleccion,
                              text='Limpiar cuadro de texto',
                              font=('D-DIN-PRO', 16),
                              command=limpiar)
boton_limpiar.pack(pady=10)

app.mainloop()
