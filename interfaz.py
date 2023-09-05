import tkinter as tk
import customtkinter as ctk

ctk.set_appearance_mode('system')
ctk.set_default_color_theme('blue')

app = ctk.CTk()
app.geometry('720x480')
app.title('MI')

boton = ctk.CTkButton(master = app, text='El Botón', font =('Aptos', 20))
boton.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

app.mainloop()