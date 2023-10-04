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


# Set logger para mostrar en pantalla

class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


# display_log = logging.getLogger('Display')

# display_log.setLevel(logging.INFO)

# handler = logging.FileHandler('output.log')
# formatter = logging.Formatter(
#     '%(asctime)s - %(message)s',
#     datefmt='[ %d-%m-%Y %H:%M:%S ]')
# handler.setFormatter(formatter)
# handler.setLevel(logging.INFO)

# display_log.addHandler(handler)

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
ctk.set_appearance_mode('light')
ctk.set_default_color_theme('CNA_colors')


class App(ctk.CTk):
    """Ventana principal y propiedades de pestañas."""
    def __init__(self):
        super().__init__()

        self.geometry('1366x718')
        self.title('Muestra Intencionada - CNA Chile')
        self.after(201, lambda: self.iconbitmap('icon.ico'))
        interfaz_log.info('Inicializar interfaz grafica')

        self.tabview = MyTabView(master=self, command=self.refresh)
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

    def refresh(self):
        tab_name = self.tabview.get()
        if tab_name == "Selección":
            self.frame_seleccion.refrescar_lista()
        print("lel")


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

        self.tituloLabel = ctk.CTkLabel(
                self,
                text='Le damos la bienvenida al Programa' +
                ' para Selección de Muestra Intencionada',
                font=('D-DIN-PRO', 24))
        self.tituloLabel.grid(row=0, column=0, pady=10)

        TextoInicio = (
            'En el contexto de la acreditación institucional obligatoria, ' +
            'dispuesto por la Ley 20.129, se debe asegurar la evaluación ' +
            'de una muestra intencionada de las carreras y programas ' +
            'de estudios impartidos por la institución en la totalidad ' +
            'de sus sedes, la que deberá considerar carreras y programas ' +
            'de estudio de las distintas áreas del conocimiento en las ' +
            'que la institución desarrolla sus funciones, y en sus ' +
            'diversas modalidades, evaluando integralmente la diversidad ' +
            'de la institución.' +
            'De acuerdo con el reglamento que aprueba el procedimiento ' +
            'de selección de la muestra intencionada (Resolución ' +
            'Exenta DJ N°346-45 de 2023), existen ciertos requisitos ' +
            'de elegibilidad para ser parte del conjunto de carreras ' +
            'y programas que podrían ser seleccionadas en la ' +
            'muestra intencionada. ')

        self.InicioText = ctk.CTkTextbox(
            self,
            height=280,
            width=400,
            fg_color='transparent',
            font=('D-DIN-PRO', 16),
            wrap='word',
            )
        self.InicioText.tag_config("center", justify="center")
        self.InicioText.insert('0.0', TextoInicio)
        self.InicioText.grid(row=1, column=0, pady=10, sticky='NS')


# ---------------------------------------------------------------------
class FrameElegibles(ctk.CTkFrame):
    """Pestaña para ejecutar programa de elegibilidad."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.Oferta_path = ''
        self.Matricula_path = ''
        self.Titulados_path = ''

        self.OfertaLabel = ctk.CTkLabel(
                self,
                text='Seleccione el archivo de Oferta SIES',
                font=('D-DIN-PRO', 16))
        self.OfertaLabel.grid(row=0, column=0, pady=10, sticky='NS')

        self.Oferta_boton = ctk.CTkButton(
                self,
                text='Oferta SIES',
                command=self.select_file_oferta)
        self.Oferta_boton.grid(row=1, column=0, pady=10, sticky='NS')

        self.MatriculaLabel = ctk.CTkLabel(
                self,
                text='Seleccione el archivo de Matrícula SIES',
                font=('D-DIN-PRO', 16))
        self.MatriculaLabel.grid(row=2, column=0, pady=10, sticky='NS')

        self.Matricula_boton = ctk.CTkButton(
                self,
                text='Matrícula SIES',
                command=self.select_file_matricula)
        self.Matricula_boton.grid(row=3, column=0, pady=10, sticky='NS')

        self.TituladosLabel = ctk.CTkLabel(
                self,
                text='Seleccione el archivo de Titulados SIES',
                font=('D-DIN-PRO', 16))
        self.TituladosLabel.grid(row=4, column=0, pady=10, sticky='NS')

        self.Titulados_boton = ctk.CTkButton(
                self,
                text='Titulados SIES',
                command=self.select_file_titulados)
        self.Titulados_boton.grid(row=5, column=0, pady=10, sticky='NS')

        self.Run_Main_boton = ctk.CTkButton(
                self,
                text='Filtrar elegibles',
                fg_color='#009a44',
                hover_color='#005224',
                command=self.Run_Main)
        self.Run_Main_boton.grid(row=6, column=0, pady=10, sticky='NS')

        self.progressbar = ctk.CTkProgressBar(self,
                                              orientation="horizontal",
                                              mode="determinate")
        self.progressbar.grid(row=7, column=0, pady=10, sticky='NS')
        self.progressbar.set(0)

    def select_file_oferta(self):
        """Función para botón de selección archivo Oferta."""
        filetypes = (
                ('csv (archivo separado por comas)', '.csv'),
                ('Todos los archivos', '*.*')
        )

        file = fd.askopenfilename(
                title='Abrir archivo',
                initialdir='/',
                filetypes=filetypes)
        if file != '':
            self.Oferta_boton.configure(text=file)
        self.Oferta_path = file

    def select_file_matricula(self):
        """Función para botón de selección archivo Matrícula."""
        filetypes = (
                ('csv (archivo separado por comas)', '.csv'),
                ('Todos los archivos', '*.*')
        )

        file = fd.askopenfilename(
                title='Abrir archivo',
                initialdir='/',
                filetypes=filetypes)
        if file != '':
            self.Matricula_boton.configure(text=file)
        self.Matricula_path = file

    def select_file_titulados(self):
        """Función para botón de selección archivo Titulados."""
        filetypes = (
                ('csv (archivo separado por comas)', '.csv'),
                ('Todos los archivos', '*.*')
        )

        file = fd.askopenfilename(
                title='Abrir archivo',
                initialdir='/',
                filetypes=filetypes)
        if file != '':
            self.Titulados_boton.configure(text=file)
        self.Titulados_path = file

    def mal_cargados(self):
        tk.messagebox.showerror(
            'Error en pestaña Elegibles',
            'Archivos mal cargados'
            )

    def Run_Main(self):
        """Ejecuta código de elegibilidad."""
        self.progressbar.set(0)
        try:
            Main(
                outputfolder,
                self.Oferta_path,
                self.Matricula_path,
                self.Titulados_path
                )
            self.Run_Main_boton.configure(text='Elegibles listos!')
            self.Oferta_boton.configure(text='Oferta SIES')
            self.Matricula_boton.configure(text='Matrícula SIES')
            self.Titulados_boton.configure(text='Titulados SIES')
            self.progressbar.set(1)
        except:
            self.mal_cargados()
            print('Archivos mal ingresados')
            self.Oferta_boton.configure(text='Oferta SIES')
            self.Matricula_boton.configure(text='Matrícula SIES')
            self.Titulados_boton.configure(text='Titulados SIES')

    def update_bar(self, progreso):
        self.progressbar.set(progreso)
        self.update()


# ---------------------------------------------------------------------
class FrameSeleccion(ctk.CTkFrame):
    """Pestaña para ejecutar programa de selección."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

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
        self.tituloLabel.grid(row=0, column=0, pady=10)

        self.subtituloLabel = ctk.CTkLabel(
                self,
                text='Elija la institución para hacer la Muestra Intencionada',
                font=('D-DIN-PRO', 16))
        self.subtituloLabel.grid(row=1, column=0, pady=10)

        self.lista_IES = os.listdir(outputfolder)

        self.lista_IES = [inst.replace('.xlsx', "") for inst in self.lista_IES]

        self.combobox = ctk.CTkComboBox(self, width=500)
        self.combobox.grid(row=2, column=0, pady=10)

        CTkScrollableDropdown(self.combobox, values=self.lista_IES,
                              justify="left", button_color="transparent",
                              autocomplete=True)

        self.boton = ctk.CTkButton(master=self,
                                   text='Generar selección',
                                   font=('D-DIN-PRO', 16),
                                   command=self.funcion_boton)
        self.boton.grid(row=3, column=0, pady=10)

        self.caja = ctk.CTkTextbox(master=self, width=800,
                                   height=250,
                                   fg_color='light gray',
                                   text_color='black',
                                   font=('D-DIN-PRO', 14),
                                   corner_radius=5,
                                   state='disabled')
        self.caja.grid(row=4, column=0, pady=10)

        self.boton_limpiar = ctk.CTkButton(master=self,
                                           text='Limpiar cuadro de texto',
                                           font=('D-DIN-PRO', 16),
                                           command=self.limpiar)
        self.boton_limpiar.grid(row=5, column=0, pady=10)

        self.boton_carpeta = ctk.CTkButton(master=self,
                                           text='Ir a carpeta',
                                           font=('D-DIN-PRO', 16),
                                           command=self.ir_a_carpeta)
        self.boton_carpeta.grid(row=6, column=0, pady=10)

        text_handler = TextHandler(self.caja)

        display_log = logging.getLogger()
        display_log.addHandler(text_handler)

    def funcion_boton(self):
        """Función para iniciar código de selección."""
        # Borrar caja de texto antes de mostrar nuevo caso
        self.caja.configure(state='normal')
        self.caja.delete('0.0', 'end')
        self.caja.configure(state='disabled')

        self.caja.configure(state='normal')
        eleccion = self.combobox.get()
        seleccion.funcion_seleccion(eleccion)

        self.caja.configure(state='disabled')

    def limpiar(self):
        """Función para borrar el texto en la caja de output."""
        self.caja.configure(state='normal')
        self.caja.delete('0.0', 'end')
        self.caja.configure(state='disabled')

    def refrescar_lista(self):
        self.lista_IES = os.listdir(outputfolder)
        self.lista_IES = [inst.replace('.xlsx', "") for inst in self.lista_IES]
        CTkScrollableDropdown(self.combobox, values=self.lista_IES,
                              justify="left", button_color="transparent",
                              autocomplete=True)
        
    def ir_a_carpeta(self):
        path = outputfolder + "/selección/"
        path = os.path.realpath(path)
        os.startfile(path)


app = App()
app.mainloop()
