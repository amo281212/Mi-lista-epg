import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET
f
# Fuentes EPG gratuitas
FUENTES_EPG = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-co.xml"
]

# Todos tus canales unificados (antiguos + nuevos)
MAPEO_CANALES = {
    'StudioUniversal.cl': ['StudioUniversal.cl', 'StudioUniversal.ar', 'StudioUniversal.co', 'Studio Universal'],
    'EEntertainment.cl': ['E!.cl', 'EEntertainment.cl', 'E_EntertainmentTelevision.bo', 'E! Entertainment'],
    'TelemundoInternacional.ar': ['TelemundoInternacional.ar', 'TelemundoInternacional.ec', 'Telemundo Internacional'],
    'SONYMOVIES.uy': ['SONYMOVIES.uy', 'SonyMovies.uy', 'Sony Movies'],
    'film&arts.cl': ['film&arts.cl', 'FilmAndArts.cl', 'Film & Arts'],
    'USANetwork.bo': ['USANetwork.bo', 'USA Network'],
    'A&E.cl': ['A&E.cl', 'AE.cl', 'A&E'],
    'NickJr.ar': ['NickJr.ar', 'Nick Jr'],
    'FOODNETWORK.uy': ['FOODNETWORK.uy', 'FoodNetwork.uy', 'Food Network'],
    'HGTV.ar': ['HGTV.ar', 'HGTV'],
    'DiscoveryHome&Health.cl': ['DiscoveryHome&Health.cl', 'Discovery Home & Health'],
    'PASIONES.uy': ['PASIONES.uy', 'Pasiones.uy', 'Pasiones']
}

CANALES_NOTICIAS = [
    ('CHVNoticias.cl', 'CHV Noticias'),
    ('T13Noticias.cl', 'T13 En Vivo')
]

# Respaldos automáticos para evitar vacíos
RESPALDO_CANALES = {
    'ENTChannel.cl': ('ENT Channel', 'Cine / Películas', 'Selección de Cine 24/7', 'Las mejores producciones cinematográficas en emisión continua.'),
    'StudioUniversal.cl': ('Studio Universal', 'Cine / Películas', 'Cine Studio Universal', 'Películas y producciones cinematográficas en emisión continua.'),
    'EEntertainment.cl': ('E! Entertainment', 'Espectáculos', 'E! Pop Culture & Realitys', 'Noticias de espectáculos, moda y reality shows.'),
    'TelemundoInternacional.ar': ('Telemundo Internacional', 'Series / Novelas', 'Programación Telemundo', 'Series, telenovelas y producciones dramáticas.'),
    'SONYMOVIES.uy': ('Sony Movies', 'Cine / Películas', 'Cine Sony Movies', 'Películas de Hollywood y éxitos cinematográficos.'),
    'film&arts.cl': ('Film & Arts', 'Arte / Cultura', 'Especiales Film & Arts', 'Cine de autor, arte, música y espectáculos.'),
    'USANetwork.bo': ('USA Network', 'Series / Películas', 'Programación USA Network', 'Series exclusivas y cine de acción.'),
    'A&E.cl': ('A&E', 'Series / Acción', 'Especiales A&E', 'Series de investigación, drama y acción.'),
    'NickJr.ar': ('Nick Jr.', 'Infantil', 'Programación Nick Jr.', 'Dibujos animados y programas educativos.'),
    'FOODNETWORK.uy': ('Food Network', 'Cocina', 'Gastronomía Internacional', 'Programas de cocina y competencias culinarias.'),
    'HGTV.ar': ('HGTV', 'Hogar / Diseño', 'Hogar & Remodelación', 'Diseño de interiores y remodelación de casas.'),
    'DiscoveryHome&Health.cl': ('Discovery Home & Health', 'Estilo de Vida', 'Bienestar & Estilo', 'Programas de salud, hogar y estilo de vida.'),
    'PASIONES.uy': ('Pasiones', 'Telenovelas', 'Novelas & Dramas', 'Telenovelas internacionales y grandes dramas.')
}

def descargar_xml(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read()
    if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
        content = gzip.decompress(content)
    return ET.fromstring(content)

def agregar_bloque_respaldo(root, channel_id, channel_name, categoria, titulo_prog, desc_prog):
    ch_elem = ET.SubElement(root, 'channel', id=channel_id)
    dn_elem = ET.SubElement(ch_elem, 'display-name')
    dn_elem.text = channel_name
    
    ahora = datetime.datetime.now(datetime.timezone.utc)
    inicio_base = ahora.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    
    for dia in range(4):
        for bloque in range(8):
            start_dt = inicio_base + datetime.timedelta(days=dia, hours=bloque*3)
            stop_dt = start_dt + datetime.timedelta(hours=3)
            
            prog = ET.SubElement(
                root, 
                'programme', 
                start=start_dt.strftime("%Y%m%d%H%M%S +0000"), 
                stop=stop_dt.strftime("%Y%m%d%H%M%S +0000"), 
                channel=channel_id
            )
            title = ET.SubElement(prog, 'title', lang='es')
            title.text = f"{channel_name}: {titulo_prog}"
            desc = ET.SubElement(prog, 'desc', lang='es')
            desc.text = desc_prog
            category = ET.SubElement(prog, 'category', lang='es')
            category.text = categoria

try:
    todas_las_guias = []
    root_chile = ET.Element('tv', {
        'generator-info-name': 'CustomEPGGenerator',
        'generator-info-url': 'https://github.com'
    })
    canales_exitosos = set()
    
    print("1. Descargando fuentes EPG...")
    for url in FUENTES_EPG:
        try:
            guiaroot = descargar_xml(url)
            todas_las_guias.append(guiaroot)
            print(f" ✔ Fuente ok: {url}")
        except Exception as e:
            print(f" ❌ Error en {url}: {e}")

    print("2. Procesando canales...")
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
                    if len(programas) > 0:
                        new_chan = ET.SubElement(root_chile, 'channel', id=id_m3u)
                        new_name = ET.SubElement(new_chan, 'display-name')
                        new_name.text = ch_name if ch_name else id_m3u
                        
                        for p in programas:
                            new_p = ET.SubElement(
                                root_chile, 
                                'programme', 
                                start=p.get('start', ''), 
                                stop=p.get('stop', ''), 
                                channel=id_m3u
                            )
                            for child in p:
                                new_p.append(ET.fromstring(ET.tostring(child)))
                            
                        encontrado = True
                        canales_exitosos.add(id_m3u)
                        print(f" ✔ Guía externa hallada para: {id_m3u}")
                        break

    print("3. Agregando canales de noticias...")
    for ch_id, ch_name in CANALES_NOTICIAS:
        agregar_bloque_respaldo(root_chile, ch_id, ch_name, "Noticias", "Noticias en Vivo", "Transmisión continua de noticias en vivo.")

    print("4. Aplicando respaldos a faltantes...")
    for ch_id, (ch_name, cat, tit, desc) in RESPALDO_CANALES.items():
        if ch_id not in canales_exitosos:
            agregar_bloque_respaldo(root_chile, ch_id, ch_name, cat, tit, desc)
            print(f" ✔ Respaldo aplicado a: {ch_id}")

    tree = ET.ElementTree(root_chile)
    ET.indent(tree, space="  ", level=0)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Proceso finalizado con éxito!")

except Exception as e:
    print(f"Error fatal: {e}")
    raise e
