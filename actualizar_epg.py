import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# Fuentes EPG con cobertura en Latinoamérica
FUENTES_EPG = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-uy.xml",
    "https://iptv-epg.org/files/epg-co.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-bo.xml"
]

# Variantes exactas encontradas en iptv-epg.org
MAPEO_CANALES = {
    'StudioUniversal.cl': [
        'StudioUniversal.cl', 'StudioUniversal.ar', 'StudioUniversal.co', 
        'StudioUniversal.bo', 'StudioUniversal.lat', 'Studio Universal'
    ],
    'EEntertainment.cl': [
        'E!.cl', 'EEntertainment.cl', 'E_EntertainmentTelevision.bo', 
        'E!EntertainmentTelevisionAndes.ec', 'E_EntertainmentTelevision.dr', 
        'E! Entertainment', 'EEntertainment.lat'
    ],
    'TelemundoInternacional.ar': [
        'TelemundoInternacional.ar', 'TelemundoInternacional.ec', 
        'TelemundoInternacional.cl', 'Telemundo Internacional', 'Telemundo.ar'
    ],
    # Demás canales de tu lista
    'SONYMOVIES.uy': ['SONYMOVIES.uy', 'SonyMovies.uy', 'Sony Movies'],
    'film&arts.cl': ['film&arts.cl', 'FilmAndArts.cl', 'Film & Arts'],
    'USANetwork.bo': ['USANetwork.bo', 'USA Network'],
    'A&E.cl': ['A&E.cl', 'AE.cl', 'A&E'],
    'NickJr.ar': ['NickJr.ar', 'Nick Jr'],
    'FOODNETWORK.uy': ['FoodNetwork.uy', 'Food Network'],
    'HGTV.ar': ['HGTV.ar', 'HGTV'],
    'DiscoveryHome&Health.cl': ['DiscoveryHome&Health.cl', 'Discovery Home & Health'],
    'PASIONES.uy': ['Pasiones.uy', 'Pasiones']
}

CANALES_NOTICIAS = [
    ('CHVNoticias.cl', 'CHV Noticias'),
    ('T13Noticias.cl', 'T13 En Vivo')
]

RESPALDO_CANALES = {
    'ENTChannel.cl': ('ENT Channel', 'Cine / Películas', 'Selección de Cine 24/7', 'Las mejores producciones cinematográficas en emisión continua.'),
    'StudioUniversal.cl': ('Studio Universal', 'Cine / Películas', 'Cine & Éxitos Studio Universal', 'Grandes producciones cinematográficas y películas las 24 horas.'),
    'EEntertainment.cl': ('E! Entertainment', 'Espectáculos / Reality', 'E! Pop Culture & Realitys', 'Noticias de espectáculos, moda y reality shows.'),
    'TelemundoInternacional.ar': ('Telemundo Internacional', 'Telenovelas / Series', 'Programación Telemundo', 'Series, telenovelas y producciones dramáticas internacionales.')
}

def descargar_xml(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read()
    if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
        content = gzip.decompress(content)
    return ET.fromstring(content)

def agregar_bloque_respaldo(root, channel_id, channel_name, categoria, titulo_prog, desc_prog):
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
    root_chile = ET.Element('tv')
    canales_exitosos = set()
    
    print("1. Descargando fuentes EPG...")
    for url in FUENTES_EPG:
        try:
            guiaroot = descargar_xml(url)
            todas_las_guias.append(guiaroot)
            print(f"    ✔ Cargada fuente: {url}")
        except Exception as e_url:
            print(f"    ⚠ No se pudo cargar {url}: {e_url}")

    print("2. Rastreando programación REAL...")
    for id_m3u, terminos_busqueda in MAPEO_CANALES.items():
        encontrado = False
        for g_root in todas_las_guias:
            if encontrado:
                break
            for channel in g_root.findall('channel'):
                ch_id = channel.get('id', '')
                ch_name = channel.findtext('display-name', '')
                
                if any(t.lower() == ch_id.lower() or t.lower() == ch_name.lower() for t in terminos_busqueda):
                    programas = [p for p in g_root.findall('programme') if p.get('channel') == ch_id]
                    
                    if len(programas) > 3:
                        new_chan = ET.Element('channel', id=id_m3u)
                        new_name = ET.SubElement(new_chan, 'display-name')
                        new_name.text = ch_name if ch_name else id_m3u
                        root_chile.append(new_chan)
                        
                        for p in programas:
                            new_p = ET.fromstring(ET.tostring(p))
                            new_p.set('channel', id_m3u)
                            root_chile.append(new_p)
                            
                        encontrado = True
                        canales_exitosos.add(id_m3u)
                        print(f"    ✔ ¡Guía REAL enlazada para {id_m3u} desde '{ch_id}'! ({len(programas)} programas)")
                        break

    print("3. Generando noticias...")
    for ch_id, ch_name in CANALES_NOTICIAS:
        agregar_bloque_respaldo(root_chile, ch_id, ch_name, "Noticias", "Noticias en Vivo", "Transmisión continua de noticias en vivo.")

    print("4. Verificando respaldos de seguridad...")
    for ch_id, (ch_name, cat, tit, desc) in RESPALDO_CANALES.items():
        if ch_id not in canales_exitosos:
            agregar_bloque_respaldo(root_chile, ch_id, ch_name, cat, tit, desc)
            print(f"    ✔ Respaldo asignado a: {ch_id}")

    tree = ET.ElementTree(root_chile)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Proceso finalizado con éxito!")

except Exception as e:
    print(f"Error: {e}")
    raise e
