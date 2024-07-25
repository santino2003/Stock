from tkinter import *
import rego as rg
from tkinter import ttk
from tkinter import messagebox
import os

def main():

    VAL = "validaciones.csv"
    UBI = "ubi.csv"
    PROD = "prod.csv"
    usuarios = {}
    ubi = []
    prod = []


    rg.cargar_desplegables(UBI,PROD,ubi,prod)
    ## estetica Raiz

    raiz=Tk()
    raiz.title("Control de Stock")
    raiz.resizable(0,0)
    raiz.geometry("500x350")

    miFrame=Frame()
    miFrame.pack()
    miFrame.config(width="500",height="350")


    # labele producto
    texto_datos=Label(miFrame,text="Producto",font="14")
    texto_datos.place(x=20,y=7) 

    #cuadro producto
    menu_producto = ttk.Combobox(state="readonly",
    values=prod,
    width="10"
    )
    menu_producto.place(x=20,y=28)

    # label peso 

    texto_peso=Label(miFrame,text="Peso",font="14")
    texto_peso.place(x=200,y=7) 
    texto_kg = Label(miFrame,text="Kg",font="10")
    texto_kg.place(x=265,y=28)

    #cuadro peso
    cuadro_peso = ttk.Entry(width="10")
    cuadro_peso.place(x=200,y=28)


    #label ubicacion
    texto_ubicacion=Label(miFrame,text="Ubi/Precinto",font="14") 
    texto_ubicacion.place(x=380,y=7)

    #cuadro ubicacion
    menu_ubicacion =  ttk.Entry(width="10")
    menu_ubicacion.place(x=380,y=28)

    #boton agregar producto
    def borrar_cuadros():
        menu_producto.set('')
        cuadro_peso.delete("0","end")
        menu_ubicacion.delete("0","end")

    def nuevo_codigo():
        producto = menu_producto.get()
        peso = cuadro_peso.get()
        ubicacion = menu_ubicacion.get()
        if producto == "" or peso == "" or ubicacion == "" or (not peso.isnumeric()):
            messagebox.showerror(raiz,message="Es necesario completar todos los campos correctamente")
            borrar_cuadros()
        else:
            messagebox.showinfo(message="Carga exitosa")
            rg.cargar_producto(producto,peso,ubicacion)
            borrar_cuadros()

            
            

            
    def llamar_nuevo_codigo(event):
        nuevo_codigo()

    boton= Button(miFrame, text="GENERAR CODIGO", width=15, command=nuevo_codigo)
    boton.place(x=7,y=200)
    raiz.bind('<Return>', llamar_nuevo_codigo)
    raiz.bind('<KP_Enter>', llamar_nuevo_codigo)

    def obtener_usuarios():
        with open(VAL, "r") as f:
            for fila in f:
                if fila != "" :
                    elemento = fila.rstrip().split(",")
                    usuarios[elemento[0]]= elemento[1]

    def regen():
        raiz2=Toplevel(raiz)
        raiz2.title("Reimpresion")
        raiz2.resizable(0,0)
        raiz2.transient(raiz)
        raiz2.geometry("300x120")
        raiz2.focus()
        raiz2.grab_set()

    
    
        #label regen
        texto_regen=Label(raiz2,text="Ingrese el codigo a reeimprimir",font="14")
        texto_regen.place(x=1,y=1)

        #cuadro regenerar codigo
        cuadro_regen = ttk.Entry(raiz2,width="20")
        cuadro_regen.place(x=70,y=45)
        cuadro_regen.focus_set()
            
        #boton aceptar
        def cod():
            cod = cuadro_regen.get()
            if rg.reimp_cod(cod):
                messagebox.showinfo(message="Reimpresion exitosa")
                raiz2.destroy()
                botonr_reg_cod.config(state='normal')
            else:
                messagebox.showerror(message="Codigo invalido")
                
        def llamar_cod(event):
            cod()
        
        bot_a_prodcep= Button(raiz2, text="ACEPTAR", width=10, command=cod)
        bot_a_prodcep.place(x=75,y=75)
        raiz2.bind('<Return>', llamar_cod)
        raiz2.bind('<KP_Enter>', llamar_cod)
        raiz2.mainloop()
    

    def usuario_val(n_label,n_funcion):
        raiz3=Toplevel(raiz)
        raiz3.title(n_label)
        raiz3.transient(raiz)
        raiz3.resizable(0,0)
        raiz3.geometry("300x120")
        
        raiz3.focus()
        raiz3.grab_set()
        
        #validar_contra
        def ingresar():
            usuario = cuadro_usuario.get()
            contraseña = cuadro_c.get()
            obtener_usuarios()
            if (usuario in usuarios) and usuarios[usuario] == contraseña:
                raiz3.destroy()
                n_funcion()
            
            else:
                messagebox.showerror(message="Usuario y/o contraseña invalido")
        def llamar_botont(event):
            ingresar()
        

        #label u
        texto_usuario=Label(raiz3,text="Usuario",font="14")
        texto_usuario.place(x=1,y=1)

        #cuadro u
        cuadro_usuario = ttk.Entry(raiz3,width="12")
        cuadro_usuario.place(x=1,y=20)
        cuadro_usuario.focus_set()

        #label c
        texto_contraseña=Label(raiz3,text="Contraseña",font="14")
        texto_contraseña.place(x=1,y=45)

        #cuadro c
        cuadro_c = ttk.Entry(raiz3,width="12",show="*")
        cuadro_c.place(x=1,y=65)

        #boton ingresar
        bot_ingresar= Button(raiz3, text="INGRESAR", width=10, command=ingresar)
        bot_ingresar.place(x=95,y=90)
        raiz3.bind('<Return>', llamar_botont)
        raiz3.bind('<KP_Enter>', llamar_botont)
        raiz3.mainloop()

    def usuario_regen():
        usuario_val("Regenerar",regen)
    #boton regen
    botonr_reg_cod= Button(miFrame, text="REGENERAR CODIGO", width=15, command=usuario_regen)
    botonr_reg_cod.place(x=7,y=170)

    def escanear():
        raiz4=Toplevel(raiz)
        raiz4.title("Escanear")
        raiz4.resizable(0,0)
        raiz4.transient(raiz)
        raiz4.geometry("300x120")
        
        raiz4.focus()
        raiz4.grab_set()
        

        #label regen
        texto_escan=Label(raiz4,text="Escanee o ingrese el codigo de barras",font="14")
        texto_escan.place(x=1,y=1)

        #cuadro regenerar codigo
        cuadro_escan = ttk.Entry(raiz4,width="20")
        cuadro_escan.place(x=70,y=45)
        cuadro_escan.focus_set()
        

            #boton aceptar
        def cod():
            cod = cuadro_escan.get()
            if rg.entregar_producto(cod):
                cuadro_escan.delete("0","end")
            else:
                cuadro_escan.delete("0","end")
        
        def llamar_cod(event):
            cod()

        bot_a_prodcep= Button(raiz4, text="ACEPTAR", width=10, command=cod)
        bot_a_prodcep.place(x=75,y=75)
        raiz4.bind('<Return>', llamar_cod)
        raiz4.bind('<KP_Enter>', llamar_cod)

        raiz4.mainloop()
    

    #boton escanear
    bot_entregar= Button(miFrame, text="ESCANEAR", width=15, command=escanear)
    bot_entregar.place(x=7,y=140)

    def copia_archivo():
        rg.descargar_datos_a_csv("stock","stock.csv")
        rg.descargar_datos_a_csv("historico","historico.csv")
        rg.descargar_datos_a_csv("entregados","entregados.csv")

    def copia_stock():
        rg.descargar_datos_a_csv("historico","historico.csv")

    #boton copia stok
    bot_entregar= Button(miFrame, text="DESC S/E", width=15, command=copia_archivo)
    bot_entregar.place(x=7,y=260)

    #boton copia stok
    bot_entregar= Button(miFrame, text="S HISTORICO", width=15, command=copia_stock)
    bot_entregar.place(x=7,y=290)

    # #boton agregar producto
    def inter_a_prod():
        messagebox.showinfo(message="Finalizado los ingresos, por favor reinicie el programa")
        raiz5=Toplevel(raiz)
        raiz5.title("Agregar Producto")
        raiz5.resizable(0,0)
        raiz5.transient(raiz)
        raiz5.geometry("300x120")
        

        raiz5.focus()
        raiz5.grab_set()
       
        #label prod
        texto_prod=Label(raiz5,text="Ingrese el prodcuto",font="14")
        texto_prod.place(x=1,y=1)

        #cuadro prod
        cuadro_escan = ttk.Entry(raiz5,width="20")
        cuadro_escan.place(x=70,y=45)
        cuadro_escan.focus_set()
        

            #boton aceptar
        def prod():
            prod = cuadro_escan.get()
            messagebox.showinfo(message="Producto agregado con exito")
            
            rg.agregar_ubi_prod(PROD,prod,"a")
            cuadro_escan.delete("0","end")
            rg.cargar_desplegables(UBI,PROD,ubi,prod)
            
            
            
        def llamar_cod(event):
            prod()

        bot_a_prodcep= Button(raiz5, text="ACEPTAR", width=10, command=prod)
        bot_a_prodcep.place(x=75,y=75)
        raiz5.bind('<Return>', llamar_cod)
        raiz5.bind('<KP_Enter>', llamar_cod)

        raiz5.mainloop()

    def llamar_val_n_prod():
        usuario_val("Nuevo Producto",inter_a_prod)

    
    bot_a_prod= Button(miFrame, text="NUEVO PRODUCTO", width=15, command=llamar_val_n_prod)
    bot_a_prod.place(x=130,y=260)


    def borrar_producto():
        messagebox.showinfo(message="Finalizado las eliminaciones, por favor reinicie el programa")
        raiz7=Toplevel(raiz)
        raiz7.title("Eliminar Producto")
        raiz7.resizable(0,0)
        raiz7.transient(raiz)
        raiz7.geometry("300x120")
        
        raiz7.focus()
        raiz7.grab_set()

        
        #label regen
        texto_escan=Label(raiz7,text="Ingrese el producto",font="14")
        texto_escan.place(x=1,y=1)

        #cuadro regenerar codigo
        c_prod = ttk.Entry(raiz7,width="20")
        c_prod.place(x=70,y=45)
        c_prod.focus_set()

            #boton aceptar
        def cod():
            cod = c_prod.get()
            if cod in prod:
                rg.borrar_agregar_ubi(ubi,prod,PROD,UBI,cod)
                c_prod.delete("0","end")
                messagebox.showinfo(message="Producto eliminado con exito")
            else:
                messagebox.showerror(message="El producto no se encuentra en la lista")
            
            
        def llamar_cod(event):
            cod()

        bot_a_prodcep= Button(raiz7, text="ACEPTAR", width=10, command=cod)
        bot_a_prodcep.place(x=75,y=75)
        raiz7.bind('<Return>', llamar_cod)
        raiz7.bind('<KP_Enter>', llamar_cod)

        raiz7.mainloop()

    def val_b_producto():
        usuario_val("Borrar producto",borrar_producto)

    bot_b_prod = Button(miFrame, text="BORRAR PRODUCTO", width=15, command=val_b_producto)
    bot_b_prod.place(x=130,y=290)

    def ventana_de_modificacion(cod):
        raiz7=Toplevel(raiz)
        raiz7.title("Modificar Producto")
        raiz7.resizable(0,0)
        raiz7.transient(raiz)
        raiz7.geometry("300x120")
        
        raiz7.focus()
        raiz7.grab_set()

        
        #label regen
        texto_escan=Label(raiz7,text="Ingrese los datos a modificar",font="14")
        texto_escan.place(x=1,y=1)

        #cuadro modificar producto
        c_mod = ttk.Entry(raiz7,width="20")
        c_mod.place(x=70,y=45)
        c_mod.focus_set()
        
        def mod_prod():
            dato = c_mod.get()
            rg.modificar_archivos(cod,"producto","dato")
            raiz7.destroy()
        boton_producto = Button(raiz7, text="M Producto", width=8, command=mod_prod)
        boton_producto.place(x=1,y=80)

        def mod_peso():
            dato = c_mod.get()
            rg.modificar_archivos(cod,"peso",dato)
            raiz7.destroy()
        boton_peso = Button(raiz7, text="M Peso", width=8, command=mod_peso)
        boton_peso.place(x=100,y=80)       

        def mod_precinto():
            dato = c_mod.get()
            rg.modificar_archivos(cod,"ubicacion",dato)
            raiz7.destroy()
        boton_peso = Button(raiz7, text="M Precinto", width=8, command=mod_precinto)
        boton_peso.place(x=199,y=80)       


    def modifcar_archivo():
        raiz7=Toplevel(raiz)
        raiz7.title("Modificar Producto")
        raiz7.resizable(0,0)
        raiz7.transient(raiz)
        raiz7.geometry("300x120")
        
        raiz7.focus()
        raiz7.grab_set()

        
        #label regen
        texto_escan=Label(raiz7,text="Ingrese el codigo del producto",font="14")
        texto_escan.place(x=1,y=1)

        #cuadro modificar producto
        c_mod = ttk.Entry(raiz7,width="20")
        c_mod.place(x=70,y=45)
        c_mod.focus_set()



            #boton aceptar
        def cod():
            codigo = c_mod.get()
            producto = rg.buscar_producto(c_mod.get())

            if producto == None:
                messagebox.showerror(message="El codigo es equivocado")
            else:
                raiz7.destroy()
                ventana_de_modificacion(codigo)
        
        def llamar_cod(event):
            cod()

        bot_a_prodcep= Button(raiz7, text="ACEPTAR", width=10, command=cod)
        bot_a_prodcep.place(x=75,y=75)
        raiz7.bind('<Return>', llamar_cod)
        raiz7.bind('<KP_Enter>', llamar_cod)

        raiz7.mainloop()
            

    def val_b_mod():
        usuario_val("Modificar Archivo",modifcar_archivo)

    bot_mod_arch = Button(miFrame, text="MODIFICAR STOCK", width=15, command=val_b_mod)
    bot_mod_arch.place(x=253,y=260)


    raiz.mainloop()


main()

