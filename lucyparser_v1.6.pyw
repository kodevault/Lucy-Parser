# Esta aplicacion parsea el fichero XML que podemos extraer de Lucia, extrae los incidentes junto con sus campos mas relevantes y permite hacer busquedas para asociar una deteccion a un ticket
# Coded By Mario Rueda

import tkinter as tk    # GUI
import sys  # Redireccion de consola
import os   # CMD commands
import re   # REGEX

# GLOBAL
XMLfilename = 'datoslucia.xml'  # Ruta al fichero XML
campo_activo = "HASH/IP/DOMAIN"  # Default search
interruptores = []  

class Console2GUI:
#   Integra la consola en la GUI y la hace 'read only'

    def __init__(self, widget_texto):
        self.widget = widget_texto

    def write(self, mensaje):       
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, mensaje)
        self.widget.see(tk.END)
        self.widget.config(state=tk.DISABLED)

    def flush(self):
        pass

#>> FUNCIONES <<# #>> FUNCIONES <<# #>> FUNCIONES <<# #>> FUNCIONES <<# #>> FUNCIONES <<# #>> FUNCIONES <<# #>> FUNCIONES <<# 
def banner():
    
    print(r"    _     _   _  ____ _     _     _____  _____  _____  _____  _____  _____ ")
    print(r"   | |   | | | ||  __|\\   //    |  _  ||  _  ||  _  ||  ___||  ___||  _  | ")
    print(r"   | |   | | | || |    \\_// ___ | |_| || |_| || |_| || |___ | |___ | |_| | ")
    print(r"   | |   | | | || |     \ / |___||  ___||  _  ||   __||___  ||  ___||   __| ")
    print(r"   | |__ | |_| || |__   | |      | |    | | | || |\ \  ___| || |___ | |\ \ ")
    print(r"   |____||_____||____|  |_|      |_|    |_| |_||_| \_\|_____||_____||_| \_\ ")
    print(r" ############################################################################ ")

def XMLtimestamp(XMLfilename):
#   Extrae la fecha del xml en uso

    # Verifica que la BD existe y es accesible
    if not os.path.exists(XMLfilename):
            print(f"\n ERROR: No se encuentra la base de datos.")
            print(f"\n Revisa que 'datoslucia.xml' se encuentra en la misma carpeta que este ejecutable.")
            input("\n Presiona Enter para salir...")
            sys.exit(0)

    REGEX_DBtimestamp = re.compile(r"<syn:updateBase>(\d{4})-(\d{2})-(\d{2})T")
    
    with open(XMLfilename, 'r', encoding='utf-8', errors='ignore') as archivo_xml:
        contenido_xml = archivo_xml.read()
        DBtimestamp = REGEX_DBtimestamp.search(contenido_xml)
    
    # Reformateo de fecha    
    if DBtimestamp:
        year = DBtimestamp.group(1)   
        month = DBtimestamp.group(2) 
        day = DBtimestamp.group(3)    

        DBdate = f"{day}-{month}-{year}"
        return DBdate

def XMLDataImport(XMLfilename):
#    Carga los datos del archivo XML en memoria, separa los IR y parsea los los campos relevantes usando regex.
#    Devuelve un diccionario con los datos extraidos, cada entrada contiene un IR.

    diccionario_tenants = {
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

    # Declaramos las expresiones regulares
    REGEX_link = re.compile(r'<link>(.*?)</link>')
    REGEX_iocValue = re.compile(r'IOC Value:.*?([^\s]+)')
    REGEX_hash = re.compile(r'Hash:\s*([a-fA-F0-9]{64})')
    REGEX_archivo = re.compile(r'Archivo:\s*([A-Za-z0-9\._\-]+)')
    REGEX_hostname = re.compile(r'Hostname:\s*([A-Za-z0-9\-_]+)')
    REGEX_username = re.compile(r'Username:\s*([A-Za-z0-9\-_]+)')
    REGEX_timestamp = re.compile(r'Fecha y Hora:\s*([\d\-T:]+Z)')
    REGEX_tenant = re.compile(r'Tenant:\s*([a-fA-F0-9]+)')
    REGEX_analisis = re.compile(r'AN[AÁ]LISIS T[EÉ]CNICO:(.*?)Los datos mostrados', re.DOTALL)

    # Inicializamos el diccionario
    Diccionario_IRs = []

    with open(XMLfilename, 'r', encoding='utf-8', errors='ignore') as archivo_xml:
        contenido_xml = archivo_xml.read()    

        # Detecta, separa y almacena los IR (<item> en el XML)
        each_XML_item = re.findall(r'<item rdf:about="(.*?)">(.*?)</item>', contenido_xml, re.DOTALL)

        # Parseo y extraccion de campos
        for _, contenido_item in each_XML_item:               
            link_Lucia = REGEX_link.search(contenido_item)
            iocValue = REGEX_iocValue.search(contenido_item) 
            hash = REGEX_hash.search(contenido_item)
            archivo = REGEX_archivo.search(contenido_item)
            hostname = REGEX_hostname.search(contenido_item)
            username = REGEX_username.search(contenido_item)
            timestamp = REGEX_timestamp.search(contenido_item)
            tenant = REGEX_tenant.search(contenido_item)
            analisis = REGEX_analisis.search(contenido_item)

            # Solo añadimos IR si se encuentra enlace a Lucia
            if link_Lucia:                       
                if tenant: # Traduccion de tenant
                    valor_tenant = tenant.group(1)  
                    tenant_nombre = diccionario_tenants.get(valor_tenant, valor_tenant)
                else:
                    tenant_nombre = " --- "

                # Reformateo del analisis tecnico
                if analisis:
                    analisis_tecnico = analisis.group(1).strip()
                    analisis_tecnico = analisis_tecnico.replace("&#xF3;", "ó").replace("&#xC9;", "É").replace("&#xE1;", "á").replace("&#xE9;", "é").replace("&#xED;", "í").replace("&#xFA;", "ú").replace("&#x26;#34;", '"').replace("&#x26;#40;", '(').replace("&#xF1;", 'ñ').replace("&#x26;#39;", "'").replace("&#x26;#41;", ')')
                    lineas = analisis_tecnico.splitlines()  # Divide por lineas
                    lineas_formateadas = [linea for linea in lineas if "LUCIA" not in linea]
                    analisis_tecnico = "\n  ".join(lineas_formateadas) if lineas_formateadas else "No encontrado. Revise el ticket."
                else:
                    analisis_tecnico = "No parseable. Revise el ticket." 
                    
                # Reformateo de fecha
                if timestamp:
                    fecha_completa = timestamp.group(1)
                    fecha_dividida = fecha_completa.split("T")[0].split("-")
                    year, month, day = fecha_dividida 
                    IRdate = f"{day}-{month}-{year}" 
                else:
                    IRdate = " --- "              
                
                # Volcado a diccionario                
                incidente = {
                    'link': link_Lucia.group(1),
                    'ioc_value': iocValue.group(1) if iocValue else None,
                    'hash': hash.group(1) if hash else None,
                    'archivo': archivo.group(1) if archivo else None,
                    'hostname': hostname.group(1) if hostname else None,
                    'username': username.group(1) if username else None,
                    'fecha': IRdate,
                    'tenant': tenant_nombre,
                    'analisis_tecnico': analisis_tecnico
                }
                Diccionario_IRs.append(incidente)

    return Diccionario_IRs

def buscar(Diccionario_IRs, event=None):
#   Busqueda de coincidencias
    
    IRs_encontrados = []
    objetivo_busqueda = searchbox.get().strip()
    caja_consola.config(state=tk.NORMAL)
    caja_consola.delete("1.0", tk.END)
    searchbox.delete(0, tk.END)
    
    if not objetivo_busqueda:
        return
    
    match campo_activo:
        case "HASH/IP/DOMAIN":
            for IR in Diccionario_IRs:
                if IR['ioc_value'] == objetivo_busqueda or IR['hash'] == objetivo_busqueda:
                    IRs_encontrados.append(IR)
        case "EJECUTABLE":
            for IR in Diccionario_IRs:
                if (IR['archivo'] and objetivo_busqueda in IR['archivo']):
                    IRs_encontrados.append(IR)         
        case "HOSTNAME":
            for IR in Diccionario_IRs:
                if IR['hostname'] == objetivo_busqueda:
                    IRs_encontrados.append(IR)             
        case "USERNAME":
            for IR in Diccionario_IRs:
                if IR['username'] == objetivo_busqueda:
                    IRs_encontrados.append(IR)     
    
    if IRs_encontrados:           
            print(f"\n {objetivo_busqueda}")
            for i, incidente in enumerate(reversed(IRs_encontrados), 1):
                print("\n" + "-"*40 + "\n")
                print(f"  Fecha IR: {incidente['fecha'] or ' --- '}")
                print(f"  Tenant: {incidente['tenant']}")
                print(f"  Hostname: {incidente['hostname'] or ' --- '}")               
                print(f"  Enlace: {incidente['link']}")
                print(f"  Analisis:\n  {incidente['analisis_tecnico']}")

    else:       
        print(f"\n No se encontraron resultados en '{campo_activo}' para: \n '{objetivo_busqueda}' \n")
            
    print("\n" + "-"*40 + "\n")
                        
def interruptor(boton_activado, nombre_campo):
    global campo_activo

    for boton in interruptores:
        boton_nombre = boton.cget("text").replace(">", "").replace("<", "")
        if boton == boton_activado:
            boton.config(relief="sunken", text=f">{nombre_campo}<")
            campo_activo = nombre_campo
        else:
            boton.config(relief="raised", text=boton_nombre)
            

#>> GUI <<# #>> GUI <<# #>> GUI <<# #>> GUI <<# #>> GUI <<# #>> GUI <<# #>> GUI <<# #>> GUI <<##>> GUI <<#
# MAIN WINDOW
LucyGUI = tk.Tk()
LucyGUI.title("Lucy-Parser")
LucyGUI.geometry("730x400")

# INTERRUPTORES-REGEX
frame_interruptores = tk.Frame(LucyGUI)
frame_interruptores.pack(pady=10)

toggle_btn_1 = tk.Button(frame_interruptores, text=">HASH/IP/DOMAIN<", relief="sunken", command=lambda: interruptor(toggle_btn_1, "HASH/IP/DOMAIN"))
toggle_btn_1.grid(row=0, column=0, padx=5)

toggle_btn_2 = tk.Button(frame_interruptores, text="EJECUTABLE", relief="raised", command=lambda: interruptor(toggle_btn_2, "EJECUTABLE"))
toggle_btn_2.grid(row=0, column=1, padx=5)

toggle_btn_3 = tk.Button(frame_interruptores, text="HOSTNAME", relief="raised", command=lambda: interruptor(toggle_btn_3, "HOSTNAME"))
toggle_btn_3.grid(row=0, column=2, padx=5)

toggle_btn_4 = tk.Button(frame_interruptores, text="USERNAME", relief="raised", command=lambda: interruptor(toggle_btn_4, "USERNAME"))
toggle_btn_4.grid(row=0, column=3, padx=5)

interruptores.extend([toggle_btn_1, toggle_btn_2, toggle_btn_3, toggle_btn_4])

# SEARCHBOX
frame_busqueda = tk.Frame(LucyGUI)
frame_busqueda.pack(pady=10)

searchbox = tk.Entry(frame_busqueda, width=40, validate="key")
searchbox.pack(side=tk.LEFT, padx=5)
searchbox.bind("<Return>", lambda event: buscar(DatosLucia, event))
searchbox.focus()

tk.Button(frame_busqueda, text="Buscar", command=lambda: buscar(DatosLucia)).pack(side=tk.LEFT)

# CONSOLA EMBEBIDA
caja_consola = tk.Text(LucyGUI, height=10, bg="black", fg="white", insertbackground="white", font=("Consolas", 12))
caja_consola.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
sys.stdout = Console2GUI(caja_consola)

#>> MAIN <<# #>> MAIN <<# #>> MAIN <<# #>> MAIN <<# #>> MAIN <<# #>> MAIN <<# #>> MAIN <<# #>> MAIN <<# #>> MAIN <<#

DBdate = XMLtimestamp(XMLfilename)
DatosLucia = XMLDataImport(XMLfilename)
banner()   
print(f" Fecha .XML: {DBdate} ")
LucyGUI.mainloop()