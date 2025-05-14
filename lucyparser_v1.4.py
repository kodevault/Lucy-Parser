# Esta aplicacion parsea el fichero XML que podemos extraer de Lucia, extrae los incidentes junto con sus campos mas relevantes y permite hacer busquedas para asociar una deteccion a un ticket
# Coded By Mario Rueda

import re   # REGEX
import os   # CMD commands
import sys

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
#    Carga los datos del archivo XML y extrae los campos relevantes usando regex.
#    Devuelve un diccionario, cada entrada contiene un IR.

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
                    'fecha': IRdate,
                    'tenant': tenant_nombre,
                    'analisis_tecnico': analisis_tecnico
                }
                Diccionario_IRs.append(incidente)

    return Diccionario_IRs

def Buscador(Diccionario_IRs, objetivo_busqueda):
#   Busca en el diccionario y devuelve la lista de IRs que matchean la busqueda.

    IRs_encontrados = []

    for IR in Diccionario_IRs:
        if IR['ioc_value'] == objetivo_busqueda or IR['hash'] == objetivo_busqueda or (IR['archivo'] and objetivo_busqueda in IR['archivo']):
            IRs_encontrados.append(IR)
    
    return IRs_encontrados

def main():
#   Core

    XMLfilename = 'datoslucia.xml'  # !!! RUTA AL FICHERO XML !!!
    DBdate = XMLtimestamp(XMLfilename)
    DatosLucia = XMLDataImport(XMLfilename)

    banner() 
    print(f" Fecha .XML: {DBdate} ")
    
    objetivo_busqueda = input("\n Que buscamos? \n > ")
    os.system('cls')
    
    while True:
        print(f" Fecha .XML: {DBdate} ")
        IRs_encontrados = Buscador(DatosLucia, objetivo_busqueda)

        if IRs_encontrados:           
            print(f"\n {objetivo_busqueda}")
            for i, incidente in enumerate(reversed(IRs_encontrados), 1): # reversed() para mostrar los mas recientes primero
                print("\n" + "-"*40 + "\n")
                print(f"  Fecha IR: {incidente['fecha'] or ' --- '}")
                print(f"  Tenant: {incidente['tenant']}")
                print(f"  Hostname: {incidente['hostname'] or ' --- '}")               
                print(f"  Enlace: {incidente['link']}")
                print(f"  Analisis:\n  {incidente['analisis_tecnico']}")

        else:       
            print(f"\n No se encontraron resultados para: {objetivo_busqueda}\n")
            
        print("\n" + "-"*40 + "\n")
        objetivo_busqueda = input("\n Que buscamos? \n > ")
        os.system('cls')
        
# Go! Go! Go!
main()