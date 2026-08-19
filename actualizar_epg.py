import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# Fuentes EPG (Chile + Latinoamérica para canales de cable)
URL_EPG_CHILE = "https://iptv-epg.org/files/epg-cl.xml"
URL_EPG_LATAM = "https://epg.lat/files/latam.xml.gz"

# Canales específicos que queremos buscar y agregar desde la lista Latam
CANALES_EXTRA_DESEADOS = [
    "Sony Movies", "SonyMovies.cl", "SonyMovies.lat",
    "Studio Universal", "StudioUniversal.cl", "StudioUniversal.lat",
    "Film & Arts", "FilmAndArts.cl", "FilmAndArts.lat",
    "A&E", "AE.cl", "AE.lat",
    "Nick Jr", "NickJr.cl", "NickJr.lat",
    "Food Network", "FoodNetwork.cl", "FoodNetwork.lat",
    "HGTV", "HGTV.cl", "HGTV.lat",
    "Discovery Home & Health", "HomeAndHealth.cl", "HomeAndHealth.lat", "H&H",
    "Pasiones", "Pasiones.cl", "Pasiones.lat",
    "Telemundo", "Telemundo.cl", "Telemundo.lat",
    "CHV Noticias", "CHVNoticias.cl",
    "T13 En Vivo", "T13.cl", "T13Noticias.cl",
    "E! Entertainment", "E! Entertainment Television", "E! Entertainment Television (Chile)", "E! Entertainment (Chile)", "EEntertainment.cl", "EEntertainment.lat"
]

CANALES_MAS_1h = []
CANALES_MENOS_1h = []

def ajustar_hora(time_str, horas_diferencia):
    try:
        dt = datetime.datetime.strptime(time_str[:14], "%Y%m%d%H%M%S")
        dt += datetime.timedelta(hours=horas_diferencia)
        return dt.strftime("%Y%m%d%H%M%S") + time_str[14:]
    except Exception:
        return time_str

def descargar_xml(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read()
    if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
        content = gzip.decompress(content)
    return ET.fromstring(content)

try:
    print("1. Descargando guía principal de Chile...")
    root_chile = descargar_xml(URL_EPG_CHILE)
    
    # Mapear canales y verificar cuáles tienen programación real
    canales_con_programacion = set()
    for programme in root_chile.findall('programme'):
        canales_con_programacion.add(programme.get('channel'))
    
    canales_existentes = {c.get('id'): c for c in root_chile.findall('channel')}
    
    print("2. Descargando guía Latam para canales faltantes o sin datos...")
    try:
        root_latam = descargar_xml(URL_EPG_LATAM)
        
        # Filtrar canales extra necesarios
        ids_extra_encontrados = set()
        
        for channel in root_latam.findall('channel'):
            ch_id = channel.get('id', '')
            ch_name = channel.findtext('display-name', '')
            
            # Verificar si coincide con alguno de nuestros canales deseados
            for deseado in CANALES_EXTRA_DESEADOS:
                if deseado.lower() in ch_id.lower() or deseado.lower() in ch_name.lower():
                    # Si no existe en la guía o si existía pero no tenía programas (como E!)
                    if ch_id not in canales_con_programacion:
                        if ch_id not in canales_existentes:
                            root_chile.append(channel)
                            canales_existentes[ch_id] = channel
                        ids_extra_encontrados.add(ch_id)
                        print(f" -> Rescatando/Añadiendo datos para: {ch_name} ({ch_id})")
                    break

        # Traer la programación de los canales rescatados
        for programme in root_latam.findall('programme'):
            if programme.get('channel') in ids_extra_encontrados:
                root_chile.append(programme)
                
    except Exception as e_latam:
        print(f"Nota: No se pudo procesar la guía Latam secundaria: {e_latam}")

    print("3. Ajustando horarios de canales...")
    for programme in root_chile.findall('programme'):
        channel_id = programme.get('channel')
        if channel_id in CANALES_MAS_1h:
            if 'start' in programme.attrib:
                programme.set('start', ajustar_hora(programme.get('start'), 1))
            if 'stop' in programme.attrib:
                programme.set('stop', ajustar_hora(programme.get('stop'), 1))
        elif channel_id in CANALES_MENOS_1h:
            if 'start' in programme.attrib:
                programme.set('start', ajustar_hora(programme.get('start'), -1))
            if 'stop' in programme.attrib:
                programme.set('stop', ajustar_hora(programme.get('stop'), -1))

    # Guardar archivo optimizado
    tree = ET.ElementTree(root_chile)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Éxito! Archivo epg_final.xml guardado y optimizado.")

except Exception as e:
    print(f"Error procesando la EPG: {e}")
    raise e
