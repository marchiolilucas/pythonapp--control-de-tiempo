import mysql.connector as SQLC
from numpy import empty

#--------------------FUNCIONES--------------------#
def conectarBD():
    DataBase = SQLC.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        db='bdtiempos'
        )
    cursor = DataBase.cursor()
    return DataBase, cursor

def cargarTarea(tarea, tiempo):
    DataBase, cursor = conectarBD()

    cursor.execute(f"INSERT INTO tiempos (Tarea, Tiempo) VALUES ('{tarea}', '{tiempo}')")
    DataBase.commit()
    DataBase.close()

def eliminarTarea(tarea):
    DataBase, cursor = conectarBD()

    cursor.execute(f"DELETE FROM tiempos WHERE Tarea = '{tarea}'")
    DataBase.commit()
    DataBase.close()

def cargarDatos(devolver):
    DataBase, cursor = conectarBD()

    tareas = []
    tiempos = []
    diccionario = {}

    cursor.execute("SELECT Tarea FROM tiempos")
    registros = cursor.fetchall()

    for item in registros:
        tareas.insert(0, item[0])

    cursor.execute("SELECT Tiempo FROM tiempos")
    registros = cursor.fetchall()

    for item in registros:
        tiempos.insert(0, item[0])

    i = 0

    while i < len(tareas):
        diccionario[tareas[i]]=int(tiempos[i])
        i+=1

    DataBase.close()

    if devolver == 'dic':
        return diccionario
    else:
        return tareas   

def finalizarDia(dia, mes, anho, tiempoTotal):
    DataBase, cursor = conectarBD()

    cursor.execute(f"SELECT Tiempo FROM finalizados WHERE Dia = '{anho}-{mes}-{dia}'")
    minutos = cursor.fetchone()
    
    if minutos == None: 
        cursor.execute(f"INSERT INTO finalizados (Dia, Tiempo) VALUES (STR_TO_DATE('{dia}-{mes}-{anho}', '%d-%m-%Y'),'{tiempoTotal}')")
        DataBase.commit()
        DataBase.close()
        return int(minutos)
    else:
        cursor.execute(f"SELECT Tiempo FROM finalizados WHERE Dia = '{anho}-{mes}-{dia}'")
        obtenido = cursor.fetchone()[0]
        actualizado = int(obtenido) + tiempoTotal
        cursor.execute(f"UPDATE finalizados SET Tiempo = '{actualizado}' WHERE Dia = '{anho}-{mes}-{dia}'")
        DataBase.commit()
        DataBase.close()
        return int(actualizado)

def fecha(dia, mes, anho):
    DataBase, cursor = conectarBD()
    
    cursor.execute(f"SELECT Tiempo FROM finalizados WHERE Dia = '{anho}-{mes}-{dia}'")
    minutos=cursor.fetchone()

    DataBase.close()

    if minutos == None:
        return ""
    else:
        return minutos
####################################################

try:
    conectarBD()
except:
    DataBase = SQLC.connect(
    host='localhost',
    port=3306,
    user='root',
    password=''
    )

    cursor=DataBase.cursor()
    cursor.execute("CREATE DATABASE bdtiempos")
    DataBase.database='bdtiempos'
finally:
    try:
        cursor.execute("CREATE TABLE tiempos (Tarea VARCHAR(50), Tiempo VARCHAR(10))")
        cursor.execute("CREATE TABLE finalizados (Dia DATE, Tiempo VARCHAR(10))")
    except:
        pass