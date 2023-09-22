import customtkinter as ctk
# import tkinter as tk
from PIL import Image
import os
import seleccion
from CTkScrollableDropdown import CTkScrollableDropdown
# from main import Main


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

# Configuración inicial de la app


ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')

# Instanciar la app como ventana

app = ctk.CTk()
app.geometry('1366x718')
app.title('Muestra Intencionada - CNA Chile')
app.after(201, lambda: app.iconbitmap('icon.ico'))

# Agregar barra inicial con tabs

tabview = ctk.CTkTabview(master=app)
tabview.pack(anchor=ctk.NW)

tabview.add("Inicio")  # add tab at the end
tabview.add("Elegibles")  # add tab at the end
tabview.add("Selección")  # add tab at the end
tabview.set("Inicio")  # set currently visible tab

frame = ctk.CTkFrame(master=tabview.tab('Inicio'), width=1366, height=700)
frame.pack()

frame = ctk.CTkFrame(master=tabview.tab('Elegibles'), width=1366, height=700)
frame.pack()

frame = ctk.CTkFrame(master=tabview.tab('Selección'), width=1366, height=700)
frame.pack()

fondo = ctk.CTkImage(light_image=Image.open("fondo2.png"),
                     dark_image=Image.open("fondo2.png"),
                     size=(274, 208))
ImageLabel = ctk.CTkLabel(frame, text='', image=fondo)
ImageLabel.pack(anchor=ctk.CENTER)

tituloLabel = ctk.CTkLabel(frame, text='Le damos la bienvenida al Programa' +
                           ' para Selección de Muestra Intencionada',
                           font=('Aptos', 24))
tituloLabel.pack(pady=10)

subtituloLabel = ctk.CTkLabel(frame,
                              text='Elija la institución para hacer la MI',
                              font=('Aptos', 16))
subtituloLabel.pack(pady=10)

foldername = "DB_OK"

# Main(foldername)

lista_IES = os.listdir(foldername)

lista_IES = [inst.replace('.xlsx', "") for inst in lista_IES]

combobox = ctk.CTkComboBox(frame, width=450)
combobox.pack(pady=10)

CTkScrollableDropdown(combobox, values=lista_IES, justify="left",
                      button_color="transparent", autocomplete=True)


boton = ctk.CTkButton(master=frame,
                      text='Generar selección',
                      font=('Aptos', 16),
                      command=funcion_boton)
boton.pack(pady=10)

caja = ctk.CTkTextbox(master=frame, width=1366,
                      height=300,
                      fg_color='light gray',
                      text_color='black',
                      font=('Aptos', 14),
                      corner_radius=5,
                      state='disabled')
caja.pack(pady=10)

boton_limpiar = ctk.CTkButton(master=frame, text='Limpiar cuadro de texto',
                              font=('Aptos', 16),
                              command=limpiar)
boton_limpiar.pack(pady=10)

app.mainloop()
