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

outputfolder = "../DB_OK"

# Verificar existencia de directorio.
# Crear directorio en caso de no existir.
for nombre_directorio in ["", "selección/", "elegibles/"]:
    directorio = outputfolder + "/" + nombre_directorio
    if not os.path.exists(os.path.dirname(directorio)):
        try:
            os.makedirs(os.path.dirname(directorio))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

# Configuración inicial de la app
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('CNA_colors')


class App(ctk.CTk):
    """Ventana principal y propiedades de pestañas."""
    def __init__(self):
        super().__init__()

        self.geometry('1366x718')
        self.title('Muestra Intencionada - CNA Chile')
        self.after(201, lambda: self.iconbitmap('icon.ico'))
        interfaz_log.info('Inicializar interfaz grafica')

        self.tabview = MyTabView(master=self)
        self.tabview.pack(anchor=ctk.NW,
                          fill='both',
                          expand=True)
        self.tabview.set("Inicio")  # set currently visible tab

        self.frame_inicio = FrameInicio(
                master=self.tabview.tab('Inicio'),
                width=1366,
                height=718)
        self.frame_inicio.pack()

        self.frame_elegibles = FrameElegibles(
                master=self.tabview.tab('Elegibles'),
                width=1366,
                height=718)
        self.frame_elegibles.pack(fill='both',
                                  expand=True)

        self.frame_seleccion = FrameSeleccion(
                master=self.tabview.tab('Selección'),
                width=1366,
                height=718)
        self.frame_seleccion.pack(expand=True,
                                  fill='both')


class MyTabView(ctk.CTkTabview):
    """Pestañas disponibles."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("Inicio")  # add tab at the end
        self.add("Elegibles")  # add tab at the end
        self.add("Selección")  # add tab at the end


# ---------------------------------------------------------------------
class FrameInicio(ctk.CTkFrame):
    """Pestaña con descripción inicial."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


# ---------------------------------------------------------------------
class FrameElegibles(ctk.CTkFrame):
    """Pestaña para ejecutar programa de elegibilidad."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.Oferta_path = ''
        self.Matricula_path = ''
        self.Titulados_path = ''

        self.OfertaLabel = ctk.CTkLabel(
                self,
                text='Seleccione el archivo de Oferta SIES',
                font=('D-DIN-PRO', 16))
        self.OfertaLabel.pack(pady=10)

        self.Oferta_boton = ctk.CTkButton(
                self,
                text='Oferta SIES',
                command=self.select_file_oferta)

        self.Oferta_boton.pack(pady=10)

        self.MatriculaLabel = ctk.CTkLabel(
                self,
                text='Seleccione el archivo de Matrícula SIES',
                font=('D-DIN-PRO', 16))
        self.MatriculaLabel.pack(pady=10)

        self.Matricula_boton = ctk.CTkButton(
                self,
                text='Matrícula SIES',
                command=self.select_file_matricula)

        self.Matricula_boton.pack(pady=10)

        self.TituladosLabel = ctk.CTkLabel(
                self,
                text='Seleccione el archivo de Titulados SIES',
                font=('D-DIN-PRO', 16))
        self.TituladosLabel.pack(pady=10)

        self.Titulados_boton = ctk.CTkButton(
                self,
                text='Titulados SIES',
                command=self.select_file_titulados)

        self.Titulados_boton.pack(pady=10)

        self.Run_Main_boton = ctk.CTkButton(
                self,
                text='Filtrar elegibles',
                fg_color='#009a44',
                hover_color='#005224',
                command=self.Run_Main)

        self.Run_Main_boton.pack(pady=10)

    def select_file_oferta(self):
        """Función para botón de selección archivo Oferta."""
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
            self.Oferta_boton.configure(text=file)
        Oferta_path = file

    def select_file_matricula(self):
        """Función para botón de selección archivo Matrícula."""
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
            self.Matricula_boton.configure(text=file)
        Matricula_path = file

    def select_file_titulados(self):
        """Función para botón de selección archivo Titulados."""
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
            self.Titulados_boton.configure(text=file)
        Titulados_path = file

    def Run_Main(self):
        """Ejecuta código de elegibilidad."""
        Main(outputfolder,
             self.Oferta_path,
             self.Matricula_path,
             self.Titulados_path)
        self.Run_Main_boton.configure(text='Elegibles listos!')


# ---------------------------------------------------------------------
class FrameSeleccion(ctk.CTkFrame):
    """Pestaña para ejecutar programa de selección."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.fondo = ctk.CTkImage(light_image=Image.open("fondo2.png"),
                                  dark_image=Image.open("fondo2.png"),
                                  size=(274, 208))
        self.ImageLabel = ctk.CTkLabel(master=self,
                                       text='',
                                       image=self.fondo)
        self.ImageLabel.place(anchor=ctk.SW,
                              relx=0.0,
                              rely=1.0)

        self.tituloLabel = ctk.CTkLabel(
                self,
                text='Le damos la bienvenida al Programa' +
                ' para Selección de Muestra Intencionada',
                font=('D-DIN-PRO', 24))
        self.tituloLabel.pack(pady=10)

        self.subtituloLabel = ctk.CTkLabel(
                self,
                text='Elija la institución para hacer la MI',
                font=('D-DIN-PRO', 16))
        self.subtituloLabel.pack(pady=10)

        self.lista_IES = os.listdir(outputfolder)

        self.lista_IES = [inst.replace('.xlsx', "") for inst in self.lista_IES]

        self.combobox = ctk.CTkComboBox(self, width=500)
        self.combobox.pack(pady=10)

        CTkScrollableDropdown(self.combobox, values=self.lista_IES,
                              justify="left", button_color="transparent",
                              autocomplete=True)

        self.boton = ctk.CTkButton(master=self,
                                   text='Generar selección',
                                   font=('D-DIN-PRO', 16),
                                   command=self.funcion_boton)
        self.boton.pack(pady=10)

        self.caja = ctk.CTkTextbox(master=self, width=800,
                                   height=250,
                                   fg_color='light gray',
                                   text_color='black',
                                   font=('D-DIN-PRO', 14),
                                   corner_radius=5,
                                   state='disabled')
        self.caja.pack(pady=10)

        self.boton_limpiar = ctk.CTkButton(master=self,
                                           text='Limpiar cuadro de texto',
                                           font=('D-DIN-PRO', 16),
                                           command=self.limpiar)
        self.boton_limpiar.pack(pady=10)

    def funcion_boton(self):
        """Función para iniciar código de selección."""
        self.caja.configure(state='normal')
        eleccion = self.combobox.get()
        seleccion.funcion_seleccion(eleccion)
        var = 'Generando selección...'
        self.caja.insert('0.0', var+'\n')
        self.caja.insert('0.0',
                         'Se ha completado la selección de la institución:\n'
                         + eleccion + '\n')

        self.caja.configure(state='disabled')

    def limpiar(self):
        """Función para borrar el texto en la caja de output."""
        self.caja.configure(state='normal')
        self.caja.delete('0.0', 'end')
        self.caja.configure(state='disabled')


app = App()
app.mainloop()
