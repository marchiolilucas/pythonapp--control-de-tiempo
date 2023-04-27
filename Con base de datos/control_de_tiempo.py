from multiprocessing.sharedctypes import Value
import tkinter, locale
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from math import floor
from plyer import notification
from tkcalendar import Calendar
import conexion
import sys
import os

from babel.numbers import *

locale.setlocale(locale.LC_TIME, "es_ES")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

root = Tk()
root.attributes('-toolwindow')
root.title("Control de tiempos")
root.resizable(0,0)
root.eval('tk::PlaceWindow . center')
root.protocol("WM_DELETE_WINDOW", lambda: [sys.exit()])
root.attributes("-topmost", False)
root.iconbitmap(resource_path(r"imagenes\reloj.ico"))

frameTop=Frame(root)
frameTop.pack()

framePendientes=Frame(root)
framePendientes.pack(fill=tkinter.BOTH, expand=True, side=tkinter.LEFT, padx=10)

frameEnCurso=Frame(root)
frameEnCurso.pack(fill=tkinter.BOTH, expand=True, side=tkinter.LEFT)

frameFinalizado=Frame(root)
frameFinalizado.pack(fill=tkinter.BOTH, expand=True, side=tkinter.RIGHT)

hoy = datetime.now().strftime("%A %d de %B de %Y, %H:%M:%S hs")
textoFecha=Label(frameTop, text=f"Hoy es {hoy}")
textoFecha.grid(row=1, column=1, columnspan=4, pady=12, padx=12)

dicTareas = conexion.cargarDatos('dic') #Carga info de la base de datos
dicTareasSeleccionadas = {}

ventanaSeleccion = Tk()
ventanaSeleccion.attributes('-toolwindow', True)
ventanaSeleccion.wm_attributes("-topmost", True)
ventanaSeleccion.title("Lista de tareas")
ventanaSeleccion.resizable(0,0)
ventanaSeleccion.protocol("WM_DELETE_WINDOW", lambda: [ventanaSeleccion.withdraw(), duracionSeleccionada.config(text=""), cerrarVentana()])
ventanaSeleccion.eval('tk::PlaceWindow . center')
duracionSeleccionadaText = Label(ventanaSeleccion, text="Duración total:")
duracionSeleccionadaText.grid(row=3, column=1, columnspan=2, padx=2, pady=2)

duracionSeleccionada = Label(ventanaSeleccion)
duracionSeleccionada.grid(row=4, column=1, columnspan=2, padx=2, pady=2)

listaSeleccion = Listbox()
horasJornada = str(0)
minutosJornada = str(0)
minutosTotales = 0
duracionTarea = 0
duracionFinal = ""
totalTrabajado = 0
segundosContados = 0
horasPendientes = 0
minutosPendientes = 0
play = False
ventanaAbierta = 0

dia = datetime.now().strftime("%d")
mes = datetime.now().strftime("%m")
anho = datetime.now().strftime("%Y")
valorMinutos = conexion.finalizarDia(dia, mes, anho, totalTrabajado)
horasDelDia = str( floor(valorMinutos/60))
minutosDelDia = str( (valorMinutos%60))

class Tarea:
    def __init__(self, nombre, duracion):
        self.nombre = nombre
        self.duracion = duracion

tareaEnCurso = Tarea("", 0)

#----FUNCIONES----#
def updateHora():
    hoy = datetime.now().strftime("%A %d de %B de %Y, %H:%M:%S hs")
    textoFecha.config(text=f"Hoy es {hoy}")

    root.after(1000, updateHora)

def ventanaSumarTarea(): 
    global ventanaAbierta

    if ventanaAbierta < 2:
        ventanaAbierta += 1

        nombre=StringVar()
        horas=IntVar()
        minutos=IntVar()

        ventanaSumar = Tk()
        ventanaSumar.attributes('-toolwindow', True)
        ventanaSumar.wm_attributes("-topmost", True)
        ventanaSumar.title("Sumar tarea")
        ventanaSumar.resizable(0,0)
        ventanaSumar.protocol("WM_DELETE_WINDOW", lambda: [ventanaSumar.destroy(), cerrarVentana(), ventanaSeleccion.wm_attributes("-topmost", True), ventanaSeleccion.wm_attributes("-disabled", False)])
        ventanaSumar.eval('tk::PlaceWindow . center')

        textoNombre = Label(ventanaSumar, text="Nombre: ")
        textoNombre.grid(row=1, column=1, padx=5, pady=5)
        cuadroNombre = Entry(ventanaSumar, textvariable=nombre)
        cuadroNombre.grid(row=1, column=2, columnspan=4, pady=5, sticky=W)

        textoDuracion = Label(ventanaSumar, text="Duración: ")
        textoDuracion.grid(row=2, column=1, padx=5, pady=5)
        cuadroHoras = Entry(ventanaSumar, textvariable=horas, width=3)
        cuadroHoras.grid(row=2, column=2, padx=2, pady=2, sticky=E)
        textoHoras = Label(ventanaSumar, text="horas")
        textoHoras.grid(row=2, column=3, padx=2, pady=2, sticky=W)
        cuadroMinutos = Entry(ventanaSumar, textvariable=minutos, width=3)
        cuadroMinutos.grid(row=2, column=4, padx=2, pady=2, sticky=E)
        textoMinutos = Label(ventanaSumar, text="minutos")
        textoMinutos.grid(row=2, column=5, padx=2, pady=2, sticky=W)

        cuadroHoras.insert(END, 0)
        cuadroMinutos.insert(END, 0)

        botonAceptar = tkinter.Button(ventanaSumar, text="Aceptar", command=lambda: [sumarTarea(cuadroNombre, cuadroHoras, cuadroMinutos), ventanaSumar.destroy(), ventanaSeleccion.wm_attributes("-topmost", True), ventanaSeleccion.wm_attributes("-disabled", False)])
        botonAceptar.grid(row=3, column=3, pady=5)
    else:
        pass

def sumarTarea(nombre, horas, minutos):
    if horas.get().isnumeric() == False or minutos.get().isnumeric() == False:
        messagebox.showerror(message="Ingrese valores compatibles", title="Alerta")
    elif horas.get() == "0" and minutos.get() == "0":
        messagebox.showerror(message="Ingrese valores compatibles", title="Alerta")
    else:
        if nombre.get() == "":
            messagebox.showerror(message="No se ha rellenado el nombre", title="Alerta")
        else:
            i = 0

            #LISTA CON LAS CLAVES DEL DICCIONARIO PARA COMPARAR SI YA EXISTE EL NOMBRE A AGREGAR
            listaTareas = []

            for pos in dicTareas:
                listaTareas.append(pos)

            while i < len(listaTareas):
                if nombre.get() == listaTareas[i]:
                    messagebox.showerror(message="Ya existe una tarea con ese nombre", title="Alerta")
                    cerrarVentana()
                    return None
                else:
                    i+=1
            ##########################################################################################

            horasEnMinutos=int(horas.get())*60
            minutosTotales=horasEnMinutos+int(minutos.get())

            conexion.cargarTarea(nombre.get(), minutosTotales)
            dicTareas[nombre.get()]=minutosTotales
            listaSeleccion.insert(0, nombre.get())
            #duracionTotal("parcial")
            nombre.delete(0, "end")
            horas.delete(0, "end")
            minutos.delete(0, "end")

    cerrarVentana()

def cerrarVentana():
    global ventanaAbierta, primeraApertura
    ventanaAbierta -= 1

def eliminarTarea():
    i = listaSeleccion.curselection()

    for i in i[::-1]:
        #for i in listaPendientes.curselection():
        tareaSeleccionada = listaSeleccion.get(i)
        conexion.eliminarTarea(tareaSeleccionada)
        del dicTareas[tareaSeleccionada]
        listaSeleccion.delete(i)
        
def eliminarTareaPendiente():
    i = listaPendientes.curselection()
    listaPendientes.delete(i)

    textoDuracionSeleccion.configure(text="")

def duracionTotal(condicion):
    global horasPendientes, minutosPendientes, totalTrabajado, horasJornada, minutosJornada, horasEnCurso, minutosEnCurso, horasDelDiaActual, minutosDelDiaActual

    minutosTotales = 0

    i = 0

    while i < listaPendientes.size():
            minutosTotales += dicTareas[listaPendientes.get(i)]
            i += 1

    #totalMinutos = int(sum(dicTareas.values())) - int(minutosTotales)

    horasPendientes = str(int(floor(minutosTotales/60)))
    minutosPendientes = str(int(minutosTotales%60))

    horas = str(int(horasPendientes) + floor(int(duracionTarea)/60))
    minutos = str(int(minutosPendientes) + (int(duracionTarea)%60))

    stringTiempo(horas, minutos, textoDuracionTotalPendiente)

    if condicion == "terminado":
        diaHoy = datetime.now().strftime("%d")
        mesHoy = datetime.now().strftime("%m")
        if dia == diaHoy:
            valorMinutos = conexion.finalizarDia(dia, mes, anho, totalTrabajado)
        else:
            valor = messagebox.askyesno("Días distintos", f"El día de inicio de jornada laboral es distinto al día de hoy. \n Día de inicio: {dia}-{mes} / Día de hoy: {diaHoy}-{mesHoy} \n ¿Cargarlo como día de hoy?")
            if valor:
                valorMinutos = conexion.finalizarDia(diaHoy, mesHoy, anho, totalTrabajado)
            else:
                valorMinutos = conexion.finalizarDia(dia, mes, anho, totalTrabajado)

        horasDelDia = str( floor(valorMinutos/60))
        minutosDelDia = str( (valorMinutos%60))
        #----TOTAL HORAS TRABAJADAS----#
        if horasJornada == "0" and minutosJornada == "0":
            messagebox.showinfo(message="No se ha trabajado.", title="Día terminado")
        elif horasJornada == "1" and minutosJornada == "0":
            messagebox.showinfo(message="Se ha trabajado " + horasJornada + " hora.", title="Día terminado")
        elif horasJornada == "0" and minutosJornada == "1":
            messagebox.showinfo(message="Se ha trabajado " + minutosJornada + " minuto.", title="Día terminado")
        elif horasJornada == "1" and minutosJornada != "0" and minutosJornada != "1":
            messagebox.showinfo(message="Se han trabajado " + horasJornada + " hora, " + minutosJornada + " minutos.", title="Día terminado")
        elif horasJornada == "1" and minutosJornada == "1":
            messagebox.showinfo(message="Se han trabajado " + horasJornada + " hora, " + minutosJornada + " minuto.", title="Día terminado")    
        elif horasJornada != "0" and horasJornada != "1" and minutosJornada != "0" and minutosJornada != "1":
            messagebox.showinfo(message="Se han trabajado " + horasJornada + " horas, " + minutosJornada + " minutos.", title="Día terminado")
        elif horasJornada != "0" and horasJornada != "1" and minutosJornada == "1":
            messagebox.showinfo(message="Se han trabajado " + horasJornada + " horas, " + minutosJornada + " minuto.", title="Día terminado")    
        elif horasJornada != "0" and horasJornada != "1" and minutosJornada == "0":
            messagebox.showinfo(message="Se han trabajado " + horasJornada + " horas.", title="Día terminado")
        elif horasJornada == "0" and minutosJornada != "1" and minutosJornada !="0":
            messagebox.showinfo(message="Se han trabajado " + minutosJornada + " minutos.", title="Día terminado")
        else:
            messagebox.showinfo(message="Se han trabajado " + horasJornada + " horas y " + minutosJornada + " minutos.", title="Día terminado")
        ##################################
        if horasDelDia == "0" and minutosDelDia == "0":
            pass
        elif horasDelDia == "1" and minutosDelDia == "0":
            messagebox.showinfo(message="Total del día: " + horasDelDia + " hora.", title="Día terminado")
        elif horasDelDia == "0" and minutosDelDia == "1":
            messagebox.showinfo(message="Total del día: " + minutosDelDia + " minuto.", title="Día terminado")
        elif horasDelDia == "1" and minutosDelDia != "0" and minutosDelDia != "1":
            messagebox.showinfo(message="Total del día: " + horasDelDia + " hora, " + minutosDelDia + " minutos.", title="Día terminado")
        elif horasDelDia == "1" and minutosDelDia == "1":
            messagebox.showinfo(message="Total del día: " + horasDelDia + " hora, " + minutosDelDia + " minuto.", title="Día terminado")    
        elif horasDelDia != "0" and horasDelDia != "1" and minutosDelDia != "0" and minutosDelDia != "1":
            messagebox.showinfo(message="Total del día: " + horasDelDia + " horas, " + minutosDelDia + " minutos.", title="Día terminado")
        elif horasDelDia != "0" and horasDelDia != "1" and minutosDelDia == "1":
            messagebox.showinfo(message="Total del día: " + horasDelDia + " horas, " + minutosDelDia + " minuto.", title="Día terminado")    
        elif horasDelDia != "0" and horasDelDia != "1" and minutosDelDia == "0":
            messagebox.showinfo(message="Total del día: " + horasDelDia + " horas.", title="Día terminado")
        elif horasDelDia == "0" and minutosDelDia != "1" and minutosDelDia !="0":
            messagebox.showinfo(message="Total del día: " + minutosDelDia + " minutos.", title="Día terminado")
        else:
            messagebox.showinfo(message="Total del día: " + horasDelDia + " horas y " + minutosDelDia + " minutos.", title="Día terminado")
        ##################################
        
        sys.exit()

def duracionTareaSeleccionada(event):
    global tareaSeleccionada

    for i in listaPendientes.curselection():
        tareaSeleccionada = listaPendientes.get(i)
    horas = str(floor(int(dicTareas[tareaSeleccionada])/60))
    minutos = str(int(dicTareas[tareaSeleccionada])%60)

    stringTiempo(horas, minutos, textoDuracionSeleccion)

def pendientesACurso():
    global duracionTarea

    if listaPendientes.curselection():
        if tareaEnCurso.nombre == "":
            i = listaPendientes.curselection()

            for i in i[::-1]:
                for i in listaPendientes.curselection():
                    nombreTarea=listaPendientes.get(i)
                    duracionTarea=int(dicTareas[nombreTarea])
                    tareaEnCurso.nombre = nombreTarea
                    tareaEnCurso.duracion = duracionTarea

            horas=str(floor(int(duracionTarea)/60))
            minutos=str(int(duracionTarea)%60)
            
            textoTareaEnCurso.config(text=tareaEnCurso.nombre)

            stringTiempo(horas, minutos, textoDuracionEnCurso)

            eliminarTareaPendiente()
            #duracionTotal("parcial")
            textoDuracionSeleccion.configure(text="")
        else:
            messagebox.showerror(message="Aún hay una tarea en curso", title="Alerta")
    else:
        messagebox.showerror(message="No se ha seleccionado ninguna tarea", title="Alerta")

def botonPlay():
    global play
    
    if tareaEnCurso.nombre != "":
        if play:
            play = False
            botonPlay.config(text="Play")
            enEjecucion.config(text="Pausado", fg="red")
        else:
            play = True
            textoRest.config(text="RESTANTE")
            botonPlay.config(text="Pausar")
            enEjecucion.config(text="En ejecución", fg="green")
            duracionTotal("parcial")
            playStop()
    else:
        messagebox.showerror(message="No hay ninguna tarea en curso", title="Alerta")

def playStop():
    global duracionTarea, play, totalTrabajado, segundosContados, horasPendientes, minutosPendientes, horasJornada, minutosJornada

    if play:
        horasEnCurso = str(floor(int(duracionTarea)/60))
        minutosEnCurso = str(int(duracionTarea)%60)

        horas = str(int(horasPendientes) + floor(int(duracionTarea)/60))
        minutos = str(int(minutosPendientes) + (int(duracionTarea)%60))

        horasJornada = str( floor(int(totalTrabajado)/60))
        minutosJornada = str( (int(totalTrabajado)%60))

        horasDelDiaActual = str( int(horasDelDia) + int(horasJornada))
        minutosDelDiaActual = str( int(minutosDelDia) + int(minutosJornada))

        stringTiempo(horasEnCurso, minutosEnCurso, textoRestanteEnCurso)
        stringTiempo(horas, minutos, textoDuracionTotalPendiente)
        stringTiempo(horasJornada, minutosJornada, textoTiempoTrabajado)
        stringTiempo(horasDelDiaActual, minutosDelDiaActual, textoTiempoDia)

        segundosContados += 1
        root.after(1000, playStop)

        if segundosContados > 59:
            duracionTarea -= 1
            totalTrabajado += 1
            segundosContados = 0

        if duracionTarea == 0:
            play = False
            segundosContados = 0
            finalizarTarea()

def habilitacion(funcion):
    def fInterior():
        listaFinalizados.config(state=NORMAL)
        funcion()
        listaFinalizados.config(state=DISABLED)
    return fInterior

@habilitacion
def finalizarTarea():
    if tareaEnCurso.nombre != "":
        global minutosTotales, play, segundosContados, horasEnCurso, minutosEnCurso, duracionTarea
        minutosTotales+=tareaEnCurso.duracion

        listaFinalizados.insert(0, tareaEnCurso.nombre)

        notification.notify(title = "Tarea finalizada", message = f"Se ha finalizado la tarea '{tareaEnCurso.nombre}'", app_icon = resource_path(r"imagenes\reloj.ico"), timeout = 5)

        tareaEnCurso.nombre = ""
        tareaEnCurso.duracion = 0
        duracionTarea = 0

        textoTareaEnCurso.config(text="")
        textoDuracionEnCurso.config(text="")
        textoRest.config(text="")
        textoRestanteEnCurso.config(text="")

        play = False
        botonPlay.config(text="Play")
        enEjecucion.config(text="")
        segundosContados = 0
        horasEnCurso = 0
        minutosEnCurso = 0

        duracionTotal("parcial")
        
    else:
        messagebox.showerror(message="No hay ninguna tarea en curso", title="Alerta")

@habilitacion
def terminarDia():
    if tareaEnCurso.nombre != "":
        messagebox.showerror(message="Aún hay una tarea en curso", title="Alerta")
    else:
        terminar = messagebox.askyesno(message="¿Está seguro que desea terminar el día?", title="¿Terminar el día?")
        if terminar:
            duracionTotal("terminado")
        
def stringTiempo(horas, minutos, etiqueta):
    if horas == "0" and minutos == "0":
        etiqueta.configure(text="")
    elif horas == "1" and minutos == "0":
        etiqueta.configure(text=horas + " hora")
    elif horas == "0" and minutos == "1":
        etiqueta.configure(text=minutos + " minuto")
    elif horas == "1" and minutos != "0" and minutos != "1":
        etiqueta.configure(text=horas + " hora, " + minutos + " minutos")
    elif horas == "1" and minutos == "1":
        etiqueta.configure(text=horas + " hora, " + minutos + " minuto")    
    elif horas != "0" and horas != "1" and minutos != "0" and minutos != "1":
        etiqueta.configure(text=horas + " horas, " + minutos + " minutos")
    elif horas != "0" and horas != "1" and minutos == "1":
        etiqueta.configure(text=horas + " horas, " + minutos + " minuto")    
    elif horas != "0" and horas != "1" and minutos == "0":
        etiqueta.configure(text=horas + " horas")
    elif horas == "0" and minutos != "1" and minutos !="0":
        etiqueta.configure(text=minutos + " minutos")
    else:
        etiqueta.configure(text=horas + " horas, " + minutos + " minutos")

def ventanaCalendario():
    global ventanaAbierta

    if ventanaAbierta < 1:
        ventanaAbierta = 1

        ventanaCalendario = Tk()
        ventanaCalendario.attributes('-toolwindow', True)
        ventanaCalendario.title("Calendario")
        ventanaCalendario.resizable(0,0)
        ventanaCalendario.protocol("WM_DELETE_WINDOW", lambda: [ventanaCalendario.destroy(), cerrarVentana()])
        ventanaCalendario.eval('tk::PlaceWindow . center')
        ventanaCalendario.wm_attributes("-topmost", True)

        cal = Calendar(ventanaCalendario)
        cal.pack(pady = 5)
        
        textTrabajado = Label(ventanaCalendario, text = "", fg='green')
        textTrabajado.pack()
        
        info = Label(ventanaCalendario, text = "", fg='green')
        info.pack()
  
        def grad_date():
            #Si se ejecuta en el editor de código
            #fecha = datetime.strptime(cal.get_date(), "%d/%m/%y")
            fecha = datetime.strptime(cal.get_date(), "%m/%d/%y")

            minutosTotales=conexion.fecha(fecha.day, fecha.month, fecha.year)

            if minutosTotales != "":
                horas=str(floor(int(minutosTotales[0])/60))
                minutos=str(int(minutosTotales[0])%60)

                textTrabajado.config(text="Tiempo trabajado:", fg='green')
                stringTiempo(horas, minutos, info)
            else:
                textTrabajado.config(text="No se trabajó ese día", fg='red')
                info.config(text = "")

            ventanaCalendario.after(100, grad_date)

        grad_date()
    else:
        pass

def ventanaDeSeleccion():
    global ventanaAbierta, dicTareasSeleccionadas, listaSeleccion, duracionSeleccionada
    
    if ventanaAbierta < 1:
        ventanaAbierta += 1
        
        ventanaSeleccion.deiconify()

        def duracionSeleccion(event):
            horas = 0
            minutos = 0

            for i in listaSeleccion.curselection():
                tareaSeleccionada = listaSeleccion.get(i)
                dicTareasSeleccionadas[tareaSeleccionada]=int(dicTareas[tareaSeleccionada])
                horas += int(floor(int(dicTareasSeleccionadas[tareaSeleccionada])/60))
                minutos += int(int(dicTareasSeleccionadas[tareaSeleccionada])%60)

            stringTiempo(str(horas), str(minutos), duracionSeleccionada)

        listaSeleccion = Listbox(ventanaSeleccion, selectmode='multiple')
        listaSeleccion.bind("<<ListboxSelect>>", duracionSeleccion)
        listaSeleccion.grid(row=1, column=1, columnspan=2, padx=2, pady=2)

        #################
        def cargarTareas():
            selected_text_list = [listaSeleccion.get(i) for i in listaSeleccion.curselection()]

            i = 0
            while i < len(selected_text_list):
                listaPendientes.insert(0, str(selected_text_list[i]))
                i+=1

            duracionTotal("parcial")
        #################

        botonSumar = tkinter.Button(ventanaSeleccion, width=2, text="+", command=lambda: [ventanaSumarTarea(), ventanaSeleccion.wm_attributes("-topmost", False), ventanaSeleccion.wm_attributes("-disabled", True)])
        botonSumar.grid(row=2, column=1, padx=2)
        botonRestar = tkinter.Button(ventanaSeleccion, width=2, text="-", command=lambda: [eliminarTarea(), duracionSeleccionada.config(text="")])
        botonRestar.grid(row=2, column=2, padx=2)

        botonAgregar = tkinter.Button(ventanaSeleccion, text="Agregar", command=lambda: [cargarTareas(), duracionSeleccionada.config(text=""), ventanaSeleccion.withdraw(), cerrarVentana()])
        botonAgregar.grid(row=5, column=1, columnspan=2, padx=2, pady=2)

        #--CARGAR LISTBOX CON LAS TAREAS--#
        claves = conexion.cargarDatos('tareas')
        pendientes = listaPendientes.get(0, tkinter.END)
        finalizados = listaFinalizados.get(0, tkinter.END)
        esta = False
        i = 0        

        while i < len(claves):
            j = 0
            while j < len(pendientes):
                if claves[i] != pendientes[j]:
                    j+=1
                else:
                    esta = True
                    break

            k = 0
            if claves[i] == tareaEnCurso.nombre:
                esta = True

            l = 0
            while l < len(finalizados):
                if claves[i] != finalizados[l]:
                    l+=1
                else:
                    esta = True
                    break
                
            if esta == False:
                listaSeleccion.insert(0, str(claves[i]))
            else:
                esta = False

            i+=1
        ###################################
#####FIN DE FUNCIONES#####
#####VENTANA PRINCIPAL#####        
#----TERMINAR DÍA---#
terminar = PhotoImage(file=resource_path(r"imagenes\ok.png"))
terminarimage = terminar.subsample(1, 1)
botonTerminarDia = tkinter.Button(image=terminarimage, command=terminarDia)
botonTerminarDia.place(x=450, y=210)
#------------------#

#----BOTÓN CALENDARIO----#
calendar = PhotoImage(file=resource_path(r"imagenes\calendar.gif"))
calendarimage = calendar.subsample(1, 1)
botonCalendario = tkinter.Button(image=calendarimage, command=ventanaCalendario)
botonCalendario.place(x=450, y=10)

#----PENDIENTES----#
textoPendiente = Label(framePendientes, text="Pendiente")
textoPendiente.grid(row=1, column=1, columnspan=3, padx=2, pady=2)

listaPendientes = Listbox(framePendientes, width=25)
listaPendientes.grid(row=2, column=1, columnspan=3, padx=2, pady=2)
listaPendientes.bind("<<ListboxSelect>>", duracionTareaSeleccionada)

botonSumar = tkinter.Button(framePendientes, width=2, text="+", command=ventanaDeSeleccion)
botonSumar.grid(row=3, column=1, padx=2)
botonRestar = tkinter.Button(framePendientes, width=2, text="-", command=lambda: [eliminarTareaPendiente(), duracionTotal("parcial")])
botonRestar.grid(row=3, column=2, padx=2, sticky="w")

botonCursar = tkinter.Button(framePendientes, text="Cursar", command=pendientesACurso)
botonCursar.grid(row=3, column=3, padx=2, pady=2, sticky="w")

textoDuracionSeleccion = Label(framePendientes)
textoDuracionSeleccion.grid(row=4, column=1, columnspan=3, padx=2, pady=2)
#------------------#

#----EN CURSO----#
textoEnCurso = Label(frameEnCurso, text="En curso")
textoEnCurso.grid(row=1, column=1, padx=40, pady=2)

textoTareaEnCurso = Label(frameEnCurso)
textoTareaEnCurso.grid(row=2, column=1, pady=3, padx=2)

textoDuracionEnCurso = Label(frameEnCurso)
textoDuracionEnCurso.grid(row=3, column=1, pady=3, padx=2)

textoRest = Label(frameEnCurso)
textoRest.grid(row=4, column=1, pady=3, padx=2, sticky="s")

textoRestanteEnCurso = Label(frameEnCurso)
textoRestanteEnCurso.grid(row=5, column=1, sticky="n")

botonPlay = tkinter.Button(frameEnCurso, text="Play", command=botonPlay)
botonPlay.grid(row=6, column=1, padx=2, pady=3)

botonFinalizar = tkinter.Button(frameEnCurso, text="Finalizar", command=finalizarTarea)
botonFinalizar.grid(row=7, column=1, padx=2, pady=3)

diaInicio = Label(frameEnCurso, text=f"Día de inicio: {dia}-{mes}")
diaInicio.grid(row=8, column=1, padx=2, pady=3)

enEjecucion = Label(frameEnCurso)
enEjecucion.grid(row=9, column=1, padx=2, pady=3)
#------------------#

#----FINALIZADO----#
textoFinalizado = Label(frameFinalizado, text="Finalizado")
textoFinalizado.grid(row=1, column=1, padx=60, pady=2)

listaFinalizados = Listbox(frameFinalizado, state=DISABLED, width=25)
listaFinalizados.grid(row=2, column=1, padx=2, pady=2)
#------------------#

#----DURACIÓN TOTAL----#
textoDuracionTotalPendiente = Label(text="0")
textoDuracionTotalPendiente.place(x=363, y=240)
textoFALTA = Label(text="FALTA", fg='red', font=("Arial", 8))
textoFALTA.place(x=320, y=240)

textoTiempoTrabajado = Label(text="0")
textoTiempoTrabajado.place(x=363, y=255)
textoHECHO = Label(text="HECHO", fg='green', font=("Arial", 8))
textoHECHO.place(x=320, y=255)

textoTiempoDia = Label(text="0")
stringTiempo(horasDelDia, minutosDelDia, textoTiempoDia)
textoTiempoDia.place(x=363, y=270)
textoHOY = Label(text="HOY", fg='green', font=("Arial", 8))
textoHOY.place(x=332, y=270)
#------------------#

ventanaDeSeleccion()
root.after(1000, updateHora)
root.mainloop()
