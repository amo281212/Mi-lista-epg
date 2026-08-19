import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# Fuentes EPG por país (específicas)
FUENTES_EPG = [
    "https://iptv-epg.org/files/epg-cl.xml", # Chile
    "https://iptv-epg.org/files/epg-ar.xml", # Argentina
    "https://iptv-epg.org/files/epg-uy.xml"  # Uruguay
]

# Mapeo super extendido con todas las posibles variantes de IDs en las guías
MAPEO_CANALES = {
    'SONYMOVIES.uy': ['SONYMOVIES.uy', 'SonyMovies.uy', 'SonyMovies.lat', 'Sony Movies', 'SonyMovies.cl', 'SonyMovies.ar', 'Sony Movies HD'],
    'StudioUniversal.ar': ['StudioUniversal.ar', 'StudioUniversal.lat', 'Studio Universal', 'StudioUniversal.cl', 'Studio Universal HD', 'StudioUniversal.uy'],
    'film&arts.cl': ['film&arts.cl', 'FilmAndArts.cl', 'FilmAndArts.lat', 'Film & Arts', 'FilmAndArts.ar', 'Film & Arts HD', 'FilmAndArts.uy', 'FilmArts.cl'],
    'USANetwork.bo': ['USANetwork.bo', 'USANetwork.lat', 'USA Network', 'USANetwork.cl', 'USANetwork.ar', 'USA Network HD'],
    'A&E.cl': ['A&E.cl', 'AE.cl', 'AE.lat', 'A&E', 'AE.ar', 'A&E HD', 'A&E Chile'],
    'E!.cl': ['E!.cl', 'EEntertainment.cl', 'EEntertainment.lat', 'E! Entertainment', 'E! Entertainment Television', 'EEntertainment.ar', 'E! Entertainment HD', 'E!'],
    'NickJr.ar': ['NickJr.ar', 'NickJr.lat', 'Nick Jr', 'NickJr.cl', 'Nick Jr.'],
    'FOODNETWORK.uy': ['FoodNetwork.uy', 'FOODNETWORK.uy', 'FoodNetwork.lat', 'Food Network', 'FoodNetwork.cl', 'FoodNetwork.ar', 'Food Network HD'],
    'HGTV.ar': ['HGTV.ar', 'HGTV.lat', 'HGTV', 'HGTV.cl', 'HGTV HD'],
    'DiscoveryHome&Health.cl': ['DiscoveryHome&Health.cl', 'HomeAndHealth.cl', 'HomeAndHealth.lat', 'Discovery Home & Health', 'H&H', 'HomeAndHealth.ar', 'Discovery Home & Health HD'],
    'PASIONES.uy': ['Pasiones.uy', 'PASIONES.uy', 'Pasiones.lat', 'Pasiones', 'Pasiones.cl', 'Pasiones.ar', 'Pasiones HD'],
    'TelemundoInternacional.ar': ['TelemundoInternacional.ar', 'Telemundo.ar', 'Telemundo.lat', 'Telemundo Internacional', 'Telemundo.cl', 'Telemundo', 'Telemundo HD']
}

# Canales de noticias para generarles guía automática
CANALES_NOTICIAS = [
    ('CHVNoticias.cl', 'CHV Noticias'),
    ('T13Noticias.cl', 'T13 En Vivo')
]

# Canales de cine continuo con bloques temáticos
BLOQUES_CINE = [
    ("00:00", "03:00", "Cine Nocturno: Selección de Medianoche", "Las mejores producciones cinematográficas para acompañar la madrugada."),
    ("03:00", "06:00", "Cine Continuo 24/7", "Transmisión ininterrumpida con el mejor entretenimiento cinematográfico."),
    ("06:00", "09:00", "Cine Matinal: Éxitos de la Pantalla", "Comienza el día con una selección especial de películas de catálogo y clásicos modernos."),
    ("09:00", "12:00", "Grandes Historias del Séptimo Arte", "Largometrajes destacados de diversos géneros e historias atrapantes."),
    ("12:00", "15:00", "Cine de Mediodía: Selección Especial", "Una propuesta cinematográfica ideal para disfrutar a mitad de jornada."),
    ("15:00", "18:00", "Maratón de Cine & Entretenimiento", "Bloque continuo de películas seleccionadas con las mejores historias de la pantalla."),
    ("18:00", "21:00", "Cine Estelar: Grandes Producciones", "Películas aclamadas, títulos destacados y el mejor cine sin interrupciones."),
    ("21:00", "00:00", "Noche de Película: Selección Premium", "Lo mejor del catálogo cinematográfico para disfrutar en el horario estelar.")
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

def generar_programas_noticias(root, channel_id, channel_name):
    ch_elem = ET.Element('channel', id=channel_id)
    dn_elem = ET.SubElement(ch_elem, 'display-name')
    dn_elem.text = channel_name
    root.append(ch_elem)
    
    ahora = datetime.datetime.now(datetime.timezone.utc)
    inicio_base = ahora.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    
    for dia in range(4):
        for bloque in range(8):
            start_dt = inicio_base + datetime.timedelta(days=dia, hours=bloque*3)
            stop_dt = start_dt + datetime.timedelta(hours=3)
            
            start_str = start_dt.strftime("%Y%m%d%H%M%S +0000")
            stop_str = stop_dt.strftime("%Y%m%d%H%M%S +0000")
            
            prog = ET.Element('programme', start=start_str, stop=stop_str, channel=channel_id)
            title = ET.SubElement(prog, 'title', lang='es')
            title.text = f"{channel_name} - Noticias en Vivo"
            desc = ET.SubElement(prog, 'desc', lang='es')
            desc.text = "Transmisión continua de noticias, información de último minuto y actualización de titulares en vivo."
            category = ET.SubElement(prog, 'category', lang='es')
            category.text = "Noticias"
            
            root.append(prog)

def generar_programas_cine(root, channel_id, channel_name):
    ch_elem = ET.Element('channel', id=channel_id)
    dn_elem = ET.SubElement(ch_elem, 'display-name')
    dn_elem.text = channel_name
    root.append(ch_elem)
    
    ahora = datetime.datetime.now(datetime.timezone.utc)
    inicio_base = ahora.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    
    for dia in range(4):
        fecha_dia = inicio_base + datetime.timedelta(days=dia)
        for h_ini, h_fin, titulo, descripcion in BLOQUES_CINE:
            h_i, m_i = map(int, h_ini.split(':'))
            h_f, m_f = map(int, h_fin.split(':'))
            
            start_dt = fecha_dia.replace(hour=h_i, minute=m_i)
            if h_fin == "00:00":
                stop_dt = start_dt + datetime.timedelta(hours=3)
            else:
                stop_dt = fecha_dia.replace(hour=h_f, minute=m_f)
                
            start_str = start_dt.strftime("%Y%m%d%H%M%S +0000")
            stop_str = stop_dt.strftime("%Y%m%d%H%M%S +0000")
            
            prog = ET.Element('programme', start=start_str, stop=stop_str, channel=channel_id)
            title = ET.SubElement(prog, 'title', lang='es')
            title.text = titulo
            desc = ET.SubElement(prog, 'desc', lang='es')
            desc.text = descripcion
            category = ET.SubElement(prog, 'category', lang='es')
            category.text = "Cine / Películas"
            
            root.append(prog)

try:
    todas_las_guias = []
    root_chile = None
    
    print("1. Descargando guías por país (Chile, Argentina, Uruguay)...")
    for url in FUENTES_EPG:
        try:
            guiaroot = descargar_xml(url)
            todas_las_guias.append(guiaroot)
            if root_chile is None:
                root_chile = guiaroot
            print(f"    ✔ Cargada fuente: {url}")
        except Exception as e_url:
            print(f"    ⚠ No se pudo cargar {url}: {e_url}")

    if root_chile is None:
        root_chile = ET.Element('tv')

    print("2. Procesando canales de cable mapeados a tu M3U8...")
    for id_m3u, terminos_busqueda in MAPEO_CANALES.items():
        print(f" -> Buscando programación para ID M3U: {id_m3u}...")
        encontrado = False
        
        for g_root in todas_las_guias:
            if encontrado:
                break
                
            for channel in g_root.findall('channel'):
                ch_id = channel.get('id', '')
                ch_name = channel.findtext('display-name', '')
                
                coincide = any(t.lower() == ch_id.lower() or t.lower() == ch_name.lower() for t in terminos_busqueda)
                
                if coincide:
                    new_chan = ET.Element('channel', id=id_m3u)
                    new_name = ET.SubElement(new_chan, 'display-name')
                    new_name.text = ch_name if ch_name else id_m3u
                    root_chile.append(new_chan)
                    
                    programas_hallados = 0
                    for prog in g_root.findall('programme'):
                        if prog.get('channel') == ch_id:
                            new_prog = ET.fromstring(ET.tostring(prog))
                            new_prog.set('channel', id_m3u)
                            root_chile.append(new_prog)
                            programas_hallados += 1
                            
                    if programas_hallados > 0:
                        encontrado = True
                        print(f"    ✔ ¡Mapeado con éxito {id_m3u} ({programas_hallados} programas creados desde {ch_id})!")
                        break

    print("3. Generando programación automática para canales de noticias...")
    for ch_id, ch_name in CANALES_NOTICIAS:
        generar_programas_noticias(root_chile, ch_id, ch_name)
        print(f"    ✔ Creada guía 'Noticias en vivo' para: {ch_id}")

    print("4. Generando programación temática para ENT Channel...")
    generar_programas_cine(root_chile, 'ENTChannel.cl', 'ENT Channel')
    print("    ✔ Creados bloques de cine variados para: ENTChannel.cl")

    print("5. Aplicando correcciones de horario si aplican...")
    for programme in root_chile.findall('programme'):
        channel_id = programme.get('channel')
        if channel_id in CANALES_MAS_1h:
            if 'start' in programme.attrib:
                programme.set('start', ajustar_hora(programme.get('start'), 1))
            if 'stop' in programme.attrib:
                programme.set('stop', ajustar_hora(programme.get('stop'), -1))

    # Guardar archivo optimizado
    tree = ET.ElementTree(root_chile)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Éxito! El archivo EPG personalizado se ha creado de forma impecable.")

except Exception as e:
    print(f"Error procesando la EPG: {e}")
    raise e
