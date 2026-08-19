import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# Fuentes EPG
FUENTES_EPG = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-co.xml"
]

# Todos los canales (Nacionales de Chile + Cable)
MAPEO_CANALES = {
    # Nacionales Chile
    'TVN.cl': ['TVN.cl', 'TVN', 'Television Nacional de Chile'],
    'Canal13.cl': ['Canal13.cl', '13.cl', 'Canal 13', 'Canal 13 Chile'],
    'Mega.cl': ['Mega.cl', 'MEGA', 'Mega Chile'],
    'Chilevision.cl': ['Chilevision.cl', 'CHV.cl', 'CHV', 'Chilevisión'],
    'LaRed.cl': ['LaRed.cl', 'La Red', 'La Red Chile'],
    'TVMas.cl': ['TVMas.cl', 'TV+.cl', 'TV+', 'TV MAS'],
    'Telecanal.cl': ['Telecanal.cl', 'Telecanal'],
    'CHVNoticias.cl': ['CHVNoticias.cl', 'CHV Noticias'],
    'T13Noticias.cl': ['T13Noticias.cl', 'T13 En Vivo', 'T13 Noticias'],
    
    # Cable / Entretenimiento / Cine
    'StudioUniversal.cl': ['StudioUniversal.cl', 'StudioUniversal.ar', 'StudioUniversal.co', 'Studio Universal'],
    'EEntertainment.cl': ['E!.cl', 'EEntertainment.cl', 'E_EntertainmentTelevision.bo', 'E! Entertainment', 'E!'],
    'TelemundoInternacional.ar': ['TelemundoInternacional.ar', 'TelemundoInternacional.ec', 'Telemundo Internacional', 'Telemundo'],
    'SONYMOVIES.uy': ['SONYMOVIES.uy', 'SonyMovies.uy', 'Sony Movies'],
    'film&arts.cl': ['film&arts.cl', 'FilmAndArts.cl', 'Film & Arts'],
    'USANetwork.bo': ['USANetwork.bo', 'USA Network', 'USANetwork.cl'],
    'A&E.cl': ['A&E.cl', 'AE.cl', 'A&E'],
    'NickJr.ar': ['NickJr.ar', 'Nick Jr', 'Nick Jr.'],
    'FOODNETWORK.uy': ['FOODNETWORK.uy', 'FoodNetwork.uy', 'Food Network'],
    'HGTV.ar': ['HGTV.ar', 'HGTV'],
    'DiscoveryHome&Health.cl': ['DiscoveryHome&Health.cl', 'Discovery Home & Health', 'Home & Health'],
    'PASIONES.uy': ['PASIONES.uy', 'Pasiones.uy', 'Pasiones'],
    'ENTChannel.cl': ['ENTChannel.cl', 'ENT Channel'],
    'TNTSports.cl': ['TNTSports.cl', 'TNT Sports', 'TNT Sports Chile'],
    'ESPN.cl': ['ESPN.cl', 'ESPN Chile', 'ESPN'],
    'StarChannel.cl': ['StarChannel.cl', 'Star Channel'],
    'WarnerChannel.cl': ['WarnerChannel.cl', 'Warner Channel', 'Warner'],
    'Cinecanal.cl': ['Cinecanal.cl', 'Cinecanal'],
    'Space.cl': ['Space.cl', 'Space']
}

# Nombre visible y categoría por defecto para respaldos
DATOS_RESPALDO = {
    'TVN.cl': ('TVN', 'General', 'Programación TVN', 'Noticias, matinales, teleseries y entretenimientos.'),
    'Canal13.cl': ('Canal 13', 'General', 'Programación Canal 13', 'Noticieros, realitys y programas en vivo.'),
    'Mega.cl': ('Mega', 'General', 'Programación Mega', 'Teleseries nacionales, noticias y entretención.'),
    'Chilevision.cl': ('Chilevisión', 'General', 'Programación CHV', 'Programas de entretención, noticias y deportes.'),
    'LaRed.cl': ('La Red', 'General', 'Programación La Red', 'Cultura, conversación e información.'),
    'TVMas.cl': ('TV+', 'General', 'Programación TV+', 'Programación variada y entretención nocturna.'),
    'Telecanal.cl': ('Telecanal', 'General', 'Programación Telecanal', 'Cine, series y animación.'),
    'CHVNoticias.cl': ('CHV Noticias', 'Noticias', 'Noticias en Vivo', 'Información continua las 24 horas.'),
    'T13Noticias.cl': ('T13 En Vivo', 'Noticias', 'Noticias T13', 'Actualidad y noticias nacionales e internacionales.'),
    'ENTChannel.cl': ('ENT Channel', 'Cine', 'Selección de Cine 24/7', 'Las mejores producciones cinematográficas.'),
    'StudioUniversal.cl': ('Studio Universal', 'Cine', 'Cine Studio Universal', 'Películas y producciones cinematográficas.'),
    'EEntertainment.cl': ('E! Entertainment', 'Espectáculos', 'E! Pop Culture', 'Noticias de espectáculos, moda y reality shows.'),
    'TelemundoInternacional.ar': ('Telemundo Internacional', 'Series', 'Programación Telemundo', 'Series, telenovelas y superproducciones.'),
    'SONYMOVIES.uy': ('Sony Movies', 'Cine', 'Cine Sony Movies', 'Películas de Hollywood y éxitos de taquilla.'),
    'film&arts.cl': ('Film & Arts', 'Cultura', 'Especiales Film & Arts', 'Cine de autor, arte, música y espectáculos.'),
    'USANetwork.bo': ('USA Network', 'Series', 'Programación USA Network', 'Series exclusivas y cine de acción.'),
    'A&E.cl': ('A&E', 'Series', 'Especiales A&E', 'Series de investigación, drama y acción.'),
    'NickJr.ar': ('Nick Jr.', 'Infantil', 'Programación Nick Jr.', 'Dibujos animados y contenidos educativos.'),
    'FOODNETWORK.uy': ('Food Network', 'Cocina', 'Gastronomía Internacional', 'Programas de cocina y competencias culinarias.'),
    'HGTV.ar': ('HGTV', 'Hogar', 'Hogar & Remodelación', 'Diseño de interiores y remodelación de espacios.'),
    'DiscoveryHome&Health.cl': ('Discovery Home & Health', 'Estilo de Vida', 'Bienestar & Estilo', 'Salud, hogar y estilo de vida.'),
    'PASIONES.uy': ('Pasiones', 'Telenovelas', 'Novelas & Dramas', 'Telenovelas internacionales y grandes historias.'),
    'TNTSports.cl': ('TNT Sports', 'Deportes', 'Programación TNT Sports', 'Fútbol chileno e información deportiva.'),
    'ESPN.cl': ('ESPN', 'Deportes', 'Programación ESPN', 'Eventos deportivos en vivo y noticieros.'),
    'StarChannel.cl': ('Star Channel', 'Cine', 'Cine & Series Star', 'Las mejores series y películas.'),
    'WarnerChannel.cl': ('Warner Channel', 'Series', 'Programación Warner', 'Series de comedia, drama y superhéroes.'),
    'Cinecanal.cl': ('Cinecanal', 'Cine', 'Cinecanal Exitos', 'Grandes películas para toda la familia.'),
    'Space.cl': ('Space', 'Acción', 'Cine de Acción Space', 'Películas de acción, suspenso y deportes de contacto.')
}

def descargar_xml(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read()
    if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
        content = gzip.decompress(content)
    return ET.fromstring(content)

def agregar_bloque_respaldo(root, channel_id):
    ch_name, categoria, titulo_prog, desc_prog = DATOS_RESPALDO.get(
        channel_id, (channel_id, 'Variado', 'Programación General', 'Transmisión continua.')
    )
    
    ch_elem = ET.SubElement(root, 'channel', id=channel_id)
    dn_elem = ET.SubElement(ch_elem, 'display-name')
    dn_elem.text = ch_name
    
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
            title.text = f"{ch_name}: {titulo_prog}"
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
                
                # Búsqueda flexible por ID o Nombre
                if any(t.lower() == ch_id.lower() or t.lower() == ch_name.lower() or t.lower() in ch_id.lower() for t in terminos_busqueda):
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

    print("3. Aplicando respaldos a faltantes...")
    for id_m3u in MAPEO_CANALES.keys():
        if id_m3u not in canales_exitosos:
            agregar_bloque_respaldo(root_chile, id_m3u)
            print(f" ✔ Respaldo generado para: {id_m3u}")

    tree = ET.ElementTree(root_chile)
    ET.indent(tree, space="  ", level=0)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Proceso finalizado con éxito!")

except Exception as e:
    print(f"Error fatal: {e}")
    raise e
