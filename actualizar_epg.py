import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# Red de fuentes EPG de toda Latinoamérica para máxima cobertura
FUENTES_EPG = [
    "https://iptv-epg.org/files/epg-cl.xml", # Chile
    "https://iptv-epg.org/files/epg-ar.xml", # Argentina
    "https://iptv-epg.org/files/epg-uy.xml", # Uruguay
    "https://iptv-epg.org/files/epg-co.xml", # Colombia
    "https://iptv-epg.org/files/epg-mx.xml", # México
    "https://iptv-epg.org/files/epg-pe.xml"  # Perú
]

# Lista masiva de alias para que Python explore miles de posibilidades por canal
MAPEO_CANALES = {
    'SONYMOVIES.uy': [
        'SONYMOVIES.uy', 'SonyMovies.uy', 'SonyMovies.lat', 'Sony Movies', 'SonyMovies.cl', 
        'SonyMovies.ar', 'Sony Movies HD', 'SonyMovies.co', 'SonyMovies.mx', 'Sony Movies Latin America'
    ],
    'StudioUniversal.ar': [
        'StudioUniversal.ar', 'StudioUniversal.lat', 'Studio Universal', 'StudioUniversal.cl', 
        'Studio Universal HD', 'StudioUniversal.uy', 'StudioUniversal.co', 'StudioUniversal.mx', 'Studio Universal Latin'
    ],
    'film&arts.cl': [
        'film&arts.cl', 'FilmAndArts.cl', 'FilmAndArts.lat', 'Film & Arts', 'FilmAndArts.ar', 
        'Film & Arts HD', 'FilmAndArts.uy', 'FilmArts.cl', 'FilmAndArts.co', 'FilmAndArts.mx', 'Film & Arts Latin America'
    ],
    'USANetwork.bo': [
        'USANetwork.bo', 'USANetwork.lat', 'USA Network', 'USANetwork.cl', 'USANetwork.ar', 
        'USA Network HD', 'USANetwork.co', 'USANetwork.mx', 'USA Network Latin America', 'USA.cl', 'USA.ar'
    ],
    'A&E.cl': [
        'A&E.cl', 'AE.cl', 'AE.lat', 'A&E', 'AE.ar', 'A&E HD', 'A&E Chile', 'A&E Latin America', 
        'A&E.co', 'A&E.mx', 'A&E.uy', 'AeNetwork.cl'
    ],
    'E!.cl': [
        'E!.cl', 'EEntertainment.cl', 'EEntertainment.lat', 'E! Entertainment', 'E! Entertainment Television', 
        'EEntertainment.ar', 'E! Entertainment HD', 'E!', 'EEntertainment.co', 'EEntertainment.mx', 'E! Latin America'
    ],
    'NickJr.ar': [
        'NickJr.ar', 'NickJr.lat', 'Nick Jr', 'NickJr.cl', 'Nick Jr.', 'NickJr.co', 'NickJr.mx', 'Nick Jr HD'
    ],
    'FOODNETWORK.uy': [
        'FoodNetwork.uy', 'FOODNETWORK.uy', 'FoodNetwork.lat', 'Food Network', 'FoodNetwork.cl', 
        'FoodNetwork.ar', 'Food Network HD', 'FoodNetwork.co', 'FoodNetwork.mx'
    ],
    'HGTV.ar': [
        'HGTV.ar', 'HGTV.lat', 'HGTV', 'HGTV.cl', 'HGTV HD', 'HGTV.co', 'HGTV.mx', 'HGTV Latin America'
    ],
    'DiscoveryHome&Health.cl': [
        'DiscoveryHome&Health.cl', 'HomeAndHealth.cl', 'HomeAndHealth.lat', 'Discovery Home & Health', 
        'H&H', 'HomeAndHealth.ar', 'Discovery Home & Health HD', 'HomeAndHealth.co', 'HomeAndHealth.mx', 'Discovery Home and Health'
    ],
    'PASIONES.uy': [
        'Pasiones.uy', 'PASIONES.uy', 'Pasiones.lat', 'Pasiones', 'Pasiones.cl', 'Pasiones.ar', 
        'Pasiones HD', 'Pasiones.co', 'Pasiones.mx'
    ],
    'TelemundoInternacional.ar': [
        'TelemundoInternacional.ar', 'Telemundo.ar', 'Telemundo.lat', 'Telemundo Internacional', 
        'Telemundo.cl', 'Telemundo', 'Telemundo HD', 'Telemundo.co', 'Telemundo.mx', 'TelemundoInternacional.cl'
    ]
}

CANALES_NOTICIAS = [
    ('CHVNoticias.cl', 'CHV Noticias'),
    ('T13Noticias.cl', 'T13 En Vivo')
]

# Red de seguridad: si no se encuentra en NINGUNA guía de Latam, se aplica esto
RESPALDO_CANALES = {
    'ENTChannel.cl': ('ENT Channel', 'Cine / Películas', 'Selección de Cine 24/7', 'Las mejores producciones cinematográficas y largometrajes en emisión continua.'),
    'TelemundoInternacional.ar': ('Telemundo Internacional', 'Telenovelas / Series', 'Programación Telemundo', 'Series, telenovelas y producciones dramáticas internacionales en emisión continua.'),
    'DiscoveryHome&Health.cl': ('Discovery Home & Health', 'Estilo de Vida', 'Estilo de Vida & Bienestar', 'Programas de salud, hogar, estilo de vida y entretenidos docu-realitys.'),
    'A&E.cl': ('A&E', 'Series / Acción', 'Especiales & Series A&E', 'Series de acción, drama, investigación y grandes producciones de entretenimiento.'),
    'USANetwork.bo': ('USA Network', 'Series / Películas', 'Programación USA Network', 'El mejor entretenimiento con series exclusivas y producciones cinematográficas.'),
    'film&arts.cl': ('Film & Arts', 'Arte / Cultura', 'Especiales Film & Arts', 'Cine de autor, arte, música, series y espectáculos de nivel internacional.')
}

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
            
            start_str = start_dt.strftime("%Y%m%d%H%M%S +0000")
            stop_str = stop_dt.strftime("%Y%m%d%H%M%S +0000")
            
            prog = ET.Element('programme', start=start_str, stop=stop_str, channel=channel_id)
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
    
    print("1. Descargando guías masivas de Latinoamérica (Chile, Argentina, Uruguay, Colombia, México, Perú)...")
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

    print("2. Buscando programación en la red para tus canales...")
    for id_m3u, terminos_busqueda in MAPEO_CANALES.items():
        print(f" -> Rastreando guía para: {id_m3u}...")
        encontrado = False
        
        for g_root in todas_las_guias:
            if encontrado:
                break
                
            for channel in g_root.findall('channel'):
                ch_id = channel.get('id', '')
                ch_name = channel.findtext('display-name', '')
                
                # Revisa si coincide con la extensa lista de alias
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
                        canales_exitosos.add(id_m3u)
                        print(f"    ✔ ¡ENCONTRADO Y ENLAZADO! {id_m3u} desde ID original '{ch_id}' ({programas_hallados} programas en vivo).")
                        break

    print("3. Generando noticias automáticas...")
    for ch_id, ch_name in CANALES_NOTICIAS:
        generar_programas_noticias(root_chile, ch_id, ch_name)
        print(f"    ✔ Noticias listas para: {ch_id}")

    print("4. Aplicando respaldos inteligentes a los canales restantes...")
    for ch_id, (ch_name, cat, tit, desc) in RESPALDO_CANALES.items():
        if ch_id not in canales_exitosos:
            generar_programas_respaldo(root_chile, ch_id, ch_name, cat, tit, desc)
            print(f"    ✔ Respaldo automático asignado a: {ch_id}")

    # Guardar archivo EPG final
    tree = ET.ElementTree(root_chile)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Éxito total! Archivo EPG súper optimizado y guardado.")

except Exception as e:
    print(f"Error procesando la EPG: {e}")
    raise e
