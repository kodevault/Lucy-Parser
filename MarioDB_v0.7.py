#v7
import os
import ftplib
import sys
from datetime import datetime

tenants = {
    "d410ef36a1814b9ea69f5bec1de75c1a": "JUNTA",
    "59c6d3cde3d34cc8a53017a783046420": "TADA2",
    "784c46e470674ac8a0ea53fd456e4d09": "TADA1",
    "65a33b216a10460b9e550319f9a19548": "TSANIT",
    "c7df6001bc1b4be4b10195d3c26c8126": "TSAE",
    "3f8a7c04ca0247179625c328dcf57b86": "TJUST",
    "b27b3c55ce9541f5b876befe5c83ad9d": "TEXT",
    "66655463695146d3b1e2da4f2e56e563": "TRTVA",
    "31782757c9e14494b4876cce182b6276": "TSAND",
    "17121a38ab604c1090954895d577dd1b": "EPES"
}

def buscar(objetivo_busqueda, fichero_txt):
    resultados = []
    with open(fichero_txt, 'r') as f:
        omitirprimeralinea = f.readline()
        lineas_txt = f.readlines()
        for cada_linea in lineas_txt:
            campos = cada_linea.strip().split(',')
            if campos[1] == objetivo_busqueda:
                tenant = tenants[campos[2]]
                resultado_formateado = f"{tenant}  ||  {campos[3]}  ||  {campos[4]}"
                resultados.append(resultado_formateado)

    if resultados:        
        resultados.sort()        
        
        print(f'Encontradas {len(resultados)} coincidencias para:\n')
        print(f"> {objetivo_busqueda} <\n")   
        print("TENANT  ||  HOSTNAME  ||  REPORTADO")
        print("------------------------------------")
        for resultado in resultados:
            print(resultado)       
    else:
        print(f"NOT FOUND > {objetivo_busqueda} < NOT FOUND")

def fechaHoy_igual(fecha_fichero):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    return fecha_fichero == fecha_hoy 

def conectar_ftp():
    try:
        ftp = ftplib.FTP('NAS.synology.me') # REPOSITORY
        ftp.login('user', 'password')   # HARDCODED LOGIN
        ftp.cwd('/FOLDER/')
        return ftp
    except ftplib.all_errors as e:
        return False
        
def descargar_BD(ftp):
    with open('output.txt', 'wb+') as f:
        ftp.retrbinary('RETR output.txt', f.write)

def main():
    fichero_txt = 'reportados.txt' # <-- !BD!
    descargado_al_inicio = False
    
    if not os.path.exists(fichero_txt):
        ftp = conectar_ftp()
        
        if ftp == False:
            print("FALLO CRITICO!")
            print("No se encuentra la BD y no se puede acceder al FTP.")
            input("Imposible continuar. Presiona Enter para salir...")
            sys.exit()
            
        descargar_BD(ftp)
        ftp.quit()
        descargado_al_inicio = True
        os.rename('output.txt', 'reportados.txt')

    with open(fichero_txt, 'r') as f:        
        fecha_BDlocal = f.readline().strip()  
        fecha_final = fecha_BDlocal
        
    if not descargado_al_inicio:      
        if not fechaHoy_igual(fecha_BDlocal):
            ftp = conectar_ftp()
            
            if not ftp:           
                print("No se pudo acceder al FTP.")     
                print(f"Version actual: {fecha_final}")                
                input("Pulsa Enter para continuar con la BD existente.")
                os.system('cls' if os.name == 'nt' else 'clear')                
                
            else:    
                descargar_BD(ftp)
                ftp.quit()
                
                with open('output.txt', 'r') as f:
                    fecha_ftp = f.readline().strip()
                    
                if fecha_ftp != fecha_BDlocal:
                    os.remove('reportados.txt')
                    os.rename('output.txt', 'reportados.txt')
                    fecha_final = fecha_ftp
                else:
                    os.remove('output.txt')
                
    print("MarioDB")
    print(f"Database version: {fecha_final}")
    
    while True:          
        busqueda = input("\nQue buscamos?\n")
        if busqueda.lower() == 'exit':
            break
        os.system('cls' if os.name == 'nt' else 'clear')
        buscar(busqueda, fichero_txt)

# Go Go Go!
main()