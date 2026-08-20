import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# 🎯 CANALES QUE TU LISTA M3U ESPERA
MIS_CANALES = {
    'TVN.cl', 'Mega.cl', 'Chilevision.cl', 'Canal13.cl', 'AMC.cl',
    'Cinecanal.cl', 'Cinemax.cl', 'Golden.cl', 'GoldenEdge.cl', 'HBO.cl',
    'HBO2.cl', 'HBOFamily.cl', 'HBOPop.cl', 'HBOXtreme.cl', 'ENTChannel.cl',
    'SONYMOVIES.uy', 'Sony.cl', 'Space.cl', 'StudioUniversal.bo', 'TNT.cl',
    'TNTSeries.cl', 'film&arts.cl', 'USANetwork.bo', 'A&E.cl', 'AXN.cl',
    'ComedyCentral.cl', 'E_EntertainmentTelevision.bo', 'FX.cl', 'StarChannel.cl',
    'UniversalTV.cl', 'WarnerChannel.cl', 'DIRECTVSports.cl', 'ESPN.cl',
    'ESPN2.cl', 'ESPN3.cl', 'ESPN4.cl', 'ESPN5.cl', 'ESPN6.cl', 'ESPN7.cl',
    'TNTSportsPremium.cl', 'TyCSports.cl', 'CartoonNetwork.cl', 'DiscoveryKids.cl',
    'DisneyChannel.cl', 'DisneyJunior.cl', 'NickJr.ar', 'Nick.cl', 'Tooncast.cl',
    'AnimalPlanet.cl', 'Discovery.cl', 'DiscoveryScience.cl', 'DiscoveryTheater.cl',
    'DiscoveryTurbo.cl', 'DiscoveryWorld.cl', 'ElGourmet.cl', 'FOODNETWORK.uy',
    'HGTV.ar', 'DiscoveryHome&Health.cl', 'History.cl', 'History2.cl1',
    'InvestigationDiscovery.cl', 'NationalGeographic.cl', 'LasEstrellas.cl',
    'PASIONES.uy', 'TelemundoInternacional.ar', 'TLNovelas.cl', 'EnlaceTBN.cl',
    'CNNChile.cl', 'CHVNoticias.cl', 'T13Noticias.cl', '24Horas.cl',
}

# 🔄 MAPEO COMPLETO Y EXPLICITO DESDE TODAS LAS FUENTES POSIBLES
MAPEO_IDS = {
    # Discovery Home & Health
    'DiscoveryHomeAndHealth.cl': 'DiscoveryHome&Health.cl',
    'DiscoveryHomeAndHealth.ar': 'DiscoveryHome&Health.cl',
    'DiscoveryHome&Health.cl': 'DiscoveryHome&Health.cl',
    'DiscoveryHome&Health.ar': 'DiscoveryHome&Health.cl',

    # Film & Arts
    'FilmAndArts.cl': 'film&arts.cl',
    'FilmAndArts.ar': 'film&arts.cl',
    'film&arts.cl': 'film&arts.cl',
    'film&arts.ar': 'film&arts.cl',

    # A&E
    'AE.cl': 'A&E.cl',
    'AE.ar': 'A&E.cl',
    'A&E.cl': 'A&E.cl',
    'A&E.ar': 'A&E.cl',

    # History 2
    'History2.cl': 'History2.cl1',
    'History2.cl1': 'History2.cl1',
}

FUENTES_EPG = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-co.xml",
    "https://iptv-epg.org/files/epg-uy.xml",
    "https://iptv-epg.org/files/epg-bo.xml"
]

DESFASE_CANALES = {
    'ESPN3.cl': -1,
    'ESPN4.cl': -1,
    'ESPN5.cl': -1,
    'ESPN6.cl': -1,
    'ESPN7.cl': -1,
    'DIRECTVSports.cl': -1,
    'TyCSports.cl': -1,
}

DATOS_RESPALDO = {
    'TVN.cl': ('TVN', 'General', 'Programación TVN', 'Noticias, matinales, teleseries y entretención.'),
    'Canal13.cl': ('Canal 13', 'General', 'Programación Canal 13', 'Noticieros, realitys y programas en vivo.'),
    'Mega.cl': ('Mega', 'General', 'Programación Mega', 'Teleseries nacionales, noticias y entretención.'),
    'Chilevision.cl': ('Chilevisión', 'General', 'Programas de entretención, noticias y deportes.'),
    'LaRed.cl': ('La Red', 'General', 'Programación La Red', 'Cultura, conversación e información.'),
    'TVMas.cl': ('TV+', 'General', 'Programación TV+', 'Programación variada y entretención nocturna.'),
    'Telecanal.cl': ('Telecanal', 'General', 'Programación Telecanal', 'Cine, series y animación.'),
    'CHVNoticias.cl': ('CHV Noticias', 'Noticias', 'Noticias en Vivo', 'Información continua las 24 horas.'),
    'T13Noticias.cl': ('T13 En Vivo', 'Noticias', 'Noticias T13', 'Actualidad y noticias nacionales e internacionales.'),
    'ENTChannel.cl': ('ENT Channel', 'Cine', 'Selección de Cine 24/7', 'Las mejores producciones cinematográficas.'),
    'StudioUniversal.cl': ('Studio Universal', 'Cine', 'Cine Studio Universal', 'Películas y producciones cinematográficas.'),
    'EEntertainment.cl': ('E! Entertainment', 'Espectáculos', 'E! Pop Culture', 'Noticias de espectáculos, moda y realitys.'),
    'TelemundoInternacional.ar': ('Telemundo Internacional', 'Series', 'Programación Telemundo', 'Series, telenovelas y producciones.'),
    'SONYMOVIES.uy': ('Sony Movies', 'Cine', 'Cine Sony Movies', 'Películas de Hollywood y éxitos de taquilla.'),
    'film&arts.cl': ('Film & Arts', 'Cultura', 'Especiales Film & Arts', 'Cine de autor, arte, música y espectáculos.'),
    'USANetwork.bo': ('USA Network', 'Series', 'Programación USA Network', 'Series exclusivas y cine de acción.'),
    'A&E.cl': ('A&E', 'Series', 'Especiales A&E', 'Series de investigación, drama y acción.'),
    'NickJr.ar': ('Nick Jr.', 'Infantil', 'Programación Nick Jr.', 'Dibujos animados y contenidos educativos.'),
    'FOODNETWORK.uy': ('Food Network', 'Cocina', 'Gastronomía Internacional', 'Programas de cocina y competencias culinarias.'),
    'HGTV.ar': ('HGTV', 'Hogar', 'Hogar & Remodelación', 'Diseño de interiores y remodelación de espacios.'),
    'DiscoveryHome&Health.cl': ('Discovery Home & Health', 'Estilo de Vida', 'Bienestar & Estilo', 'Salud, hogar y estilo de vida.'),
    'PASIONES.uy': ('Pasiones', 'Telenovelas', 'Novelas & Dramas', 'Telenovelas internacionales y grandes historias.'),
    'History2.cl1': ('History 2', 'Documentales', 'Programación History 2', 'Documentales, historia y ciencia.')
}

def ajustar_hora(time_str, horas_desfase):
    if not time_str or len(time_str) < 14:
        return time_str
    try:
        dt_part = time_str[:14]
        tz_part = time_str[14:] if len(time_str) > 14 else ""
        dt = datetime.datetime.strptime(dt_part, "%Y%m%d%H%M%S")
        dt += datetime.timedelta(hours=horas_desfase)
        return dt.strftime("%Y%m%d%H%M%S") + tz_part
    except Exception:
        return time_str

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
    root_final = ET.Element('tv', {
        'generator-info-name': 'CustomEPGGenerator',
        'generator-info-url': 'https://github.com'
    })
    
    canales_existentes = set()
    
    print("1. Cargando y filtrando canales de las guías originales...")
    for url in FUENTES_EPG:
        try:
            guiaroot = descargar_xml(url)
            for elem in guiaroot:
                if elem.tag == 'channel':
                    ch_id = elem.get('id')
                    target_id = MAPEO_IDS.get(ch_id, ch_id)
                    
                    if target_id in MIS_CANALES and target_id not in canales_existentes:
                        canales_existentes.add(target_id)
                        elem.set('id', target_id)
                        root_final.append(elem)
                        
                elif elem.tag == 'programme':
                    ch_id = elem.get('channel')
                    target_id = MAPEO_IDS.get(ch_id, ch_id)
                    
                    if target_id in MIS_CANALES:
                        elem.set('channel', target_id)
                        if target_id in DESFASE_CANALES:
                            horas = DESFASE_CANALES[target_id]
                            elem.set('start', ajustar_hora(elem.get('start', ''), horas))
                            elem.set('stop', ajustar_hora(elem.get('stop', ''), horas))
                        root_final.append(elem)
            print(f" ✔ Cargada guía filtrada: {url}")
        except Exception as e:
            print(f" ❌ Error en {url}: {e}")

    print("2. Verificando respaldos únicamente para tus canales...")
    for ch_id in MIS_CANALES:
        if ch_id not in canales_existentes:
            agregar_bloque_respaldo(root_final, ch_id)
            print(f" ✔ Respaldo creado para: {ch_id}")

    tree = ET.ElementTree(root_final)
    ET.indent(tree, space="  ", level=0)
    
    # Escribir directamente codificado en UTF-8 para garantizar validez de sintaxis XML
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
        
    print("¡Proceso finalizado con éxito!")

except Exception as e:
    print(f"Error fatal: {e}")
    raise e
