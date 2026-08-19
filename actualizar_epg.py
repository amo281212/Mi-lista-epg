import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# Red de fuentes EPG de toda Latinoamérica
FUENTES_EPG = [
    "https://iptv-epg.org/files/epg-cl.xml", # Chile
    "https://iptv-epg.org/files/epg-ar.xml", # Argentina
    "https://iptv-epg.org/files/epg-uy.xml", # Uruguay
    "https://iptv-epg.org/files/epg-co.xml", # Colombia
    "https://iptv-epg.org/files/epg-mx.xml", # México
    "https://iptv-epg.org/files/epg-pe.xml"  # Perú
]

# Lista masiva de alias por canal
MAPEO_CANALES = {
    'SONYMOVIES.uy': ['SONYMOVIES.uy', 'SonyMovies.uy', 'SonyMovies.lat', 'Sony Movies', 'SonyMovies.cl', 'SonyMovies.ar', 'Sony Movies HD'],
    'StudioUniversal.ar': ['StudioUniversal.ar', 'StudioUniversal.lat', 'Studio Universal', 'StudioUniversal.cl', 'Studio Universal HD', 'StudioUniversal.uy', 'StudioUniversal.co'],
    'film&arts.cl': ['film&arts.cl', 'FilmAndArts.cl', 'FilmAndArts.lat', 'Film & Arts', 'FilmAndArts.ar', 'Film & Arts HD', 'FilmAndArts.uy'],
    'USANetwork.bo': ['USANetwork.bo', 'USANetwork.lat', 'USA Network', 'USANetwork.cl', 'USANetwork.ar', 'USA Network HD'],
    'A&E.cl': ['A&E.cl', 'AE.cl', 'AE.lat', 'A&E', 'AE.ar', 'A&E HD', 'A&E Chile'],
    'E!.cl': ['E!.cl', 'EEntertainment.cl', 'EEntertainment.lat', 'E! Entertainment', 'E! Entertainment Television', 'EEntertainment.ar', 'E! Entertainment HD', 'E!'],
    'NickJr.ar': ['NickJr.ar', 'NickJr.lat', 'Nick Jr', 'NickJr.cl', 'Nick Jr.'],
    'FOODNETWORK.uy': ['FoodNetwork.uy', 'FOODNETWORK.uy', 'FoodNetwork.lat', 'Food Network', 'FoodNetwork.cl', 'FoodNetwork.ar'],
    'HGTV.ar': ['HGTV.ar', 'HGTV.lat', 'HGTV', 'HGTV.cl', 'HGTV HD'],
    'DiscoveryHome&Health.cl': ['DiscoveryHome&Health.cl', 'HomeAndHealth.cl', 'HomeAndHealth.lat', 'Discovery Home & Health', 'H&H', 'HomeAndHealth.ar'],
    'PASIONES.uy': ['Pasiones.uy', 'PASIONES.uy', 'Pasiones.lat', 'Pasiones', 'Pasiones.cl', 'Pasiones.ar'],
    'TelemundoInternacional.ar': ['TelemundoInternacional.ar', 'Telemundo.ar', 'Telemundo.lat', 'Telemundo Internacional', 'Telemundo.cl', 'Telemundo', 'Telemundo HD']
}

CANALES_NOTICIAS = [
    ('CHVNoticias.cl', 'CHV Noticias'),
    ('T13Noticias.cl', 'T13 En Vivo')
]

# Respaldo 100% garantizado para TODOS los canales si falla la búsqueda externa
RESPALDO_CANALES = {
    'ENTChannel.cl': ('ENT Channel', 'Cine / Películas', 'Selección de Cine 24/7', 'Las mejores producciones cinematográficas y largometrajes en emisión continua.'),
    'TelemundoInternacional.ar': ('Telemundo Internacional', 'Telenovelas / Series', 'Programación Telemundo', 'Series, telenovelas y producciones dramáticas internacionales en emisión continua.'),
    'DiscoveryHome&Health.cl': ('Discovery Home & Health', 'Estilo de Vida', 'Estilo de Vida & Bienestar', 'Programas de salud, hogar, estilo de vida y entretenidos docu-realitys.'),
    'A&E.cl': ('A&E', 'Series / Acción', 'Especiales & Series A&E', 'Series de acción, drama, investigación y grandes producciones de entretenimiento.'),
    'USANetwork.bo': ('USA Network', 'Series / Películas', 'Programación USA Network', 'El mejor entretenimiento con series exclusivas y producciones cinematográficas.'),
    'film&arts.cl': ('Film & Arts', 'Arte / Cultura', 'Especiales Film & Arts', 'Cine de autor, arte, música, series y espectáculos de nivel internacional.'),
    'StudioUniversal.ar': ('Studio Universal', 'Cine / Películas', 'Cine & Exitos Studio Universal', 'Grandes producciones cinematográficas, sagas y éxitos de taquilla las 24 horas.'),
    'E!.cl': ('E! Entertainment', 'Espectáculos / Reality', 'E! Pop Culture & Realitys', 'Noticias de espectáculos, alfombras rojas, moda y las series reality más populares.'),
    'SONYMOVIES.uy': ('Sony Movies', 'Cine / Películas', 'Cine Sony Movies', 'Películas de Hollywood, estrenos y cine de acción 24/7.'),
    'NickJr.ar': ('Nick Jr.', 'Infantil', 'Programación Nick Jr.', 'Dibujos animados, shows educativos y entretenimiento infantil.'),
    'FOODNETWORK.uy': ('Food Network', 'Cocina', 'Programas de Gastronomía', 'Competencias culinarias, recetas y programas de cocina internacional.'),
    'HGTV.ar': ('HGTV', 'Hogar / Diseño', 'Hogar & Remodelación', 'Diseño de interiores, remodelación de casas y competencias de bienes raíces.'),
    'PASIONES.uy': ('Pasiones', 'Telenovelas', 'Novelas & Dramas', 'Telenovelas internacionales y grandes dramas en emisión continua.')
}

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
            
            prog = ET.Element('programme', start=start_dt.strftime("%Y%m%d%H%M%S +0000"), stop=stop_dt.strftime("%Y%m%d%H%M%S +0000"), channel=channel_id)
            title = ET.SubElement(prog, 'title', lang='es')
            title.text = f"{channel_name} - Noticias en Vivo"
            desc = ET.SubElement(prog, 'desc', lang='es')
            desc.text = "Transmisión continua de noticias, información de último minuto y actualización de titulares en vivo."
            category = ET.SubElement(prog, 'category', lang='es')
            category.text = "Noticias"
            root.append(prog)

def generar_programas_respaldo(root, channel_id, channel_name, categoria, titulo_prog, desc_prog):
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
            
            prog = ET.Element('programme', start=start_dt.strftime("%Y%m%d%H%M%S +0000"), stop=stop_dt.strftime("%Y%m%d%H%M%S +0000"), channel=channel_id)
            title = ET.SubElement(prog, 'title', lang='es')
            title.text = f"{channel_name}: {titulo_prog}"
            desc = ET.SubElement(prog, 'desc', lang='es')
            desc.text = desc_prog
            category = ET.SubElement(prog, 'category', lang='es')
            category.text = categoria
            root.append(prog)

try:
    todas_las_guias = []
    root_chile = None
    canales_exitosos = set()
    
    print("1. Descargando fuentes EPG de Latinoamérica...")
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

    print("2. Buscando programación en la red...")
    for id_m3u, terminos_busqueda in MAPEO_CANALES.items():
        print(f" -> Buscando guía para: {id_m3u}...")
        encontrado = False
        
        for g_root in todas_las_guias:
            if encontrado:
                break
                
            for channel in g_root.findall('channel'):
                ch_id = channel.get('id', '')
                ch_name = channel.findtext('display-name', '')
                
                coincide = any(t.lower() == ch_id.lower() or t.lower() == ch_name.lower() for t in terminos_busqueda)
                
                if coincide:
                    programas_hallados = 0
                    programas_a_agregar = []
                    
                    for prog in g_root.findall('programme'):
                        if prog.get('channel') == ch_id:
                            new_prog = ET.fromstring(ET.tostring(prog))
                            new_prog.set('channel', id_m3u)
                            programas_a_agregar.append(new_prog)
                            programas_hallados += 1
                            
                    if programas_hallados > 5:  # Requiere al menos 5 programas válidos
                        new_chan = ET.Element('channel', id=id_m3u)
                        new_name = ET.SubElement(new_chan, 'display-name')
                        new_name.text = ch_name if ch_name else id_m3u
                        root_chile.append(new_chan)
                        
                        for p in programas_a_agregar:
                            root_chile.append(p)
                            
                        encontrado = True
                        canales_exitosos.add(id_m3u)
                        print(f"    ✔ ¡Enlazado con éxito! {id_m3u} ({programas_hallados} programas).")
                        break

    print("3. Generando guías para canales de noticias...")
    for ch_id, ch_name in CANALES_NOTICIAS:
        generar_programas_noticias(root_chile, ch_id, ch_name)
        print(f"    ✔ Noticias listas para: {ch_id}")

    print("4. Aplicando respaldo de seguridad a canales sin guía externa suficiente...")
    for ch_id, (ch_name, cat, tit, desc) in RESPALDO_CANALES.items():
        if ch_id not in canales_exitosos:
            generar_programas_respaldo(root_chile, ch_id, ch_name, cat, tit, desc)
            print(f"    ✔ Respaldo asignado a: {ch_id}")

    # Guardar EPG final
    tree = ET.ElementTree(root_chile)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Proceso completado exitosamente!")

except Exception as e:
    print(f"Error procesando la EPG: {e}")
    raise e
