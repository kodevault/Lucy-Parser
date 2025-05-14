import email
from email import policy
from email.parser import BytesParser
import os
import re
import shutil
from datetime import datetime

def parsear_correo(ruta_correo, errores_txt):
    with open(ruta_correo, 'rb') as XfX:
        correo_parseado = BytesParser(policy=policy.default).parse(XfX)

    # Comprobar que el correo viene de falcon@crowdstrike.com
    if correo_parseado['From'] != 'falcon@crowdstrike.com':
        with open(errores_txt, 'a') as errorlog:
            errorlog.write(f"Remitente incorrecto. Correo omitido: {ruta_correo}\n")
        return []

    # Extraer y trimear la fecha
    fecha_correo = correo_parseado['Delivery-date']
    fecha_reportado = fecha_correo[5:7] + fecha_correo[8:11] + fecha_correo[12:16]

    # Extraer el HTML del correo
    contenidoHTML = None
    for etiquetaHTML in correo_parseado.walk():
        if etiquetaHTML.get_content_type() == 'text/html':
            contenidoHTML = etiquetaHTML.get_payload(decode=True).decode(etiquetaHTML.get_content_charset())

    if contenidoHTML:
        # REGEX para localizar el parrafo con los datos
        parrafo_localizado = re.search(r'ANALISIS TECNICO:<br>(.*?)Grouping Tags:', contenidoHTML, re.DOTALL)
        #DATOS DE LA DETECCION:<br>(.*?)<br>ANALISIS TECNICO:<br>
        if parrafo_localizado:
            parrafo_completo = parrafo_localizado.group(1)
            lineas_parrafo = parrafo_completo.split('<br>')
            sacadatos = {
                'IOC Type': '',
                'IOC Value': '',
                'Tenant': '',
                'Hostname': ''
            }

            # Extraccion y limpieza
            for linea_extraida in lineas_parrafo:
                linea_extraida = linea_extraida.strip()
                if 'IOC Type:' in linea_extraida:
                    partes = linea_extraida.split(': ')
                    if len(partes) > 1:
                        sacadatos['IOC Type'] = partes[1].strip().replace(' address', '').replace('Domain', 'DOMAIN').replace('MD5 hash', 'MD5').replace('SHA256 hash', 'SHA256').replace('IPv4', 'IPV4')
                if 'IOC Value:' in linea_extraida:
                    partes = linea_extraida.split(': ')
                    if len(partes) > 1:
                        sacadatos['IOC Value'] = partes[1].strip().replace('=', '')
                if 'Tenant:' in linea_extraida:
                    partes = linea_extraida.split(': ')
                    if len(partes) > 1:
                        sacadatos['Tenant'] = partes[1].strip().replace('=', '')
                if 'Hostname:' in linea_extraida:
                    partes = linea_extraida.split(': ')
                    if len(partes) > 1:
                        sacadatos['Hostname'] = partes[1].strip().replace('=', '')

            valor_ioc = sacadatos['IOC Value'].split(',')

            # Si la deteccion no tiene IOC
            if not sacadatos['IOC Type'] and not sacadatos['IOC Value']:
                for linea_extraida in lineas_parrafo:
                    if 'Hash:' in linea_extraida:
                        partes = linea_extraida.split(': ')
                        if len(partes) > 1:
                            sacadatos['IOC Type'] = 'SHA256'
                            sacadatos['IOC Value'] = partes[1].strip().replace('=', '')
                            valor_ioc = sacadatos['IOC Value'].split(',')
                            break

            # Comprobar que se han recogido todos los datos 
            if not sacadatos['IOC Type'] or not valor_ioc[0] or not sacadatos['Tenant'] or not sacadatos['Hostname']:
                with open(errores_txt, 'a') as errorlog:
                    errorlog.write(f"Datos incompletos en el correo: {ruta_correo}\n")
                return []

            # Devuelve resultado final
            return [f"{sacadatos['IOC Type']},{ioc.strip()},{sacadatos['Tenant']},{sacadatos['Hostname']},{fecha_reportado}" for ioc in valor_ioc]

    # Reportar correos sin HTML
    with open(errores_txt, 'a') as errorlog:
        errorlog.write(f"Contenido HTML no encontrado en el correo: {ruta_correo}\n")
    return []

# Comprobar si ya existe la deteccion
def check_b4_write(output_txt, lineaAañadir):
    with open(output_txt, 'r') as XfX:
        lineas_txt = XfX.readlines()

    datos_nuevos = lineaAañadir.split(',')
    if len(datos_nuevos) < 5:
        return False

    for i, cada_linea in enumerate(lineas_txt):
        datos_existentes = cada_linea.strip().split(',')
        if datos_existentes[:4] == datos_nuevos[:4]:
            datos_existentes[4] += '+' + datos_nuevos[4]
            lineas_txt[i] = ','.join(datos_existentes) + '\n'
            with open(output_txt, 'w') as XfX:
                XfX.writelines(lineas_txt)
            return True
    return False

# DATESTAMP en primera linea
def actualizar_fecha(output_txt):
    fecha_hoy = datetime.now().strftime('%d/%m/%Y')
    with open(output_txt, 'r') as file:
        lineas = file.readlines()

    # Sobrescribir la primera línea
    lineas = [fecha_hoy + '\n'] + lineas[1:]

    with open(output_txt, 'w') as file:
        file.writelines(lineas)

# Directorio con los archivos .eml
carpeta_correos = '/home/kali/Desktop/edrparser/eml'
output_txt = '/home/kali/Desktop/edrparser/output.txt'
errores_txt = '/home/kali/Desktop/edrparser/log.txt'
carpeta_done = '/home/kali/Desktop/edrparser/eml/done'

# Crear los archivos si no existen
if not os.path.exists(carpeta_done):
    os.makedirs(carpeta_done)
if not os.path.exists(output_txt):
    open(output_txt, 'w').close()
if not os.path.exists(errores_txt):
    open(errores_txt, 'w').close()

# Actualizar la fecha en la primera línea del archivo output.txt
actualizar_fecha(output_txt)

# Procesar todos los archivos .eml en el directorio
for archivo_correo in os.listdir(carpeta_correos):
    if archivo_correo.endswith('.eml'):
        ruta_correo = os.path.join(carpeta_correos, archivo_correo)
        lineas_totales = parsear_correo(ruta_correo, errores_txt)
        if lineas_totales:
            for lineaAañadir in lineas_totales:
                if not check_b4_write(output_txt, lineaAañadir):
                    with open(output_txt, 'a') as Xf_outX:
                        Xf_outX.write(lineaAañadir + '\n')
            nombre_final = os.path.join(carpeta_done, archivo_correo)
            i = 1
            while os.path.exists(nombre_final):
                nombre, extension = os.path.splitext(archivo_correo)
                nombre_final = os.path.join(carpeta_done, f"{nombre}_{i}{extension}")
                i += 1
            shutil.move(ruta_correo, nombre_final)
        
# Renombrar output.txt
fecha_hoy = datetime.now().strftime('%d%m%Y')
nuevo_nombre = f"/home/kali/Desktop/edrparser/{fecha_hoy}.txt"
shutil.copy(output_txt, nuevo_nombre)

print(f"Datos extraidos y guardados en {nuevo_nombre}")
