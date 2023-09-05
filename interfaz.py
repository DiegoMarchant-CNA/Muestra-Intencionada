import customtkinter as ctk
import tkinter as tk
from PIL import Image

def funcion_boton():
    var = 'Has apretado el botón!'
    caja.insert('0.0', var+'\n')


ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')

app = ctk.CTk()
app.geometry('720x480')
app.title('Muestra Intencionada - CNA Chile')
app.after(201, lambda: app.iconbitmap('icon.ico'))

fondo = ctk.CTkImage(light_image=Image.open("fondo2.png"),
                     dark_image=Image.open("fondo2.png"),
                     size=(274, 208))
ImageLabel = ctk.CTkLabel(app, text='', image=fondo)
ImageLabel.pack(anchor=ctk.CENTER)

tituloLabel = ctk.CTkLabel(app, text='Bienvenido', font=('Aptos', 24))
tituloLabel.pack()

boton = ctk.CTkButton(master=app, text='El Botón', font=('Aptos', 16),
                      command=funcion_boton)
boton.pack()

caja = ctk.CTkTextbox(master=app, width=300, height=150, fg_color='light gray',
                      text_color='black', font=('Aptos', 14), corner_radius=5)
caja.pack()


app.mainloop()
