import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# 🎯 TUS CANALES CON IDS LIMPIOS. EL HASHTAG SE USA PARA PODER DEJAR COMENTARIOS Y ANULAR EL CODIGO EN ESA LÍNEA.
MIS_CANALES = {
    'TVN.cl',
    'Mega.cl',
    'Chilevision.cl',
    'Canal13.cl',
    'AMC.cl',
    'Cinecanal.cl',
    'Cinemax.cl',
    'Golden.cl',
    'GoldenEdge.cl',
    'HBO.cl',
    'HBO2.cl',
    'HBOFamily.cl',
    'HBOPop.cl',
    'HBOXtreme.cl',
    'ENTChannel.cl',
    'SONYMOVIES.uy',
    'Sony.cl',
    'Space.cl',
    'StudioUniversal.ar',
    'TNT.cl',
    'TNTSeries.cl',
    'StarChannel.cl',
    'UniversalTV.cl',
    'WarnerChannel.cl',
    'USANetwork.bo',
    'AXN.cl',
    'AE.cl',
    'FX.cl',
    'FilmAndArts.cl',
    'ComedyCentral.cl',
    'E_EntertainmentTelevision.pa',
    'DIRECTVSports.cl',
    'ESPN.cl',
    'ESPN2.cl',
    'ESPN3.cl',
    'ESPN4.cl',
    'ESPN5.cl',
    'ESPN6.cl',
    'ESPN7.cl',
    'TNTSportsPremium.cl',
    'TyCSports.cl',
    'CartoonNetwork.cl',
    'DiscoveryKids.cl',
    'DisneyChannel.cl',
    'DisneyJunior.cl',
    'NickJr.bo',
    'Nick.cl',
    'Tooncast.cl',
    'AnimalPlanet.cl',
    'Discovery.cl',
    'DiscoveryScience.cl',
    'DiscoveryTheater.cl',
    'DiscoveryTurbo.cl',
    'DiscoveryWorld.cl',
    'ElGourmet.cl',
    'FOODNETWORK.uy',
    'HGTV.ar',
    'DiscoveryHomeAndHealth.cl',
    'History.cl',
    'History2.cl1',
    'InvestigationDiscovery.cl',
    'NationalGeographic.cl',
    'LasEstrellas.cl',
    'PASIONES.uy',
    'TelemundoInternacional.ar',
    'TLNovelas.cl',
    'EnlaceTBN.cl',
    'CNNChile.cl',
    'CHVNoticias.cl',
    'T13Noticias.cl',
    '24Horas.cl',
}

# 🔄 MAPEO COMPLETO (Recupera AXN y otros canales desde las guías externas)
MAPEO_IDS = {
    'StudioUniversal.bo': 'StudioUniversal.ar',
    'Sony.co': 'Sony.cl',
    'AXN.ar': 'AXN.cl',
    'AXN.co': 'AXN.cl',
    'DiscoveryHomeAndHealth.ar': 'DiscoveryHomeAndHealth.cl',
    'DiscoveryHome&Health.cl': 'DiscoveryHomeAndHealth.cl',
    'FilmAndArts.ar': 'FilmAndArts.cl',
    'film&arts.cl': 'FilmAndArts.cl',
    'AE.ar': 'AE.cl',
    'A&E.cl': 'AE.cl',
    'History2.cl': 'History2.cl1',
}

FUENTES_PUBLICAS = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-co.xml",
    "https://iptv-epg.org/files/epg-uy.xml",
    "https://iptv-epg.org/files/epg-bo.xml",
    "https://raw.githubusercontent.com/amo281212/epg_que_actualizo.xml/refs/heads/main/guia.xml",
]

DESFASE_CANALES = {
    'Cinemax.cl': +1,
    'ESPN2.cl': -1,
    'ESPN3.cl': -1,
    'ESPN4.cl': -1,
    'ESPN5.cl': -1,
    'ESPN6.cl': -1,
    'ESPN7.cl': -1,
    'DIRECTVSports.cl': -1,
    'TNTSportsPremium.cl': -1,
    'TyCSports.cl': -1,
}

DATOS_RESPALDO = {
    'AXN.cl': ('AXN', 'Series', 'Series y Acción', 'Películas de acción, suspenso y series policiales.'),
    'TVN.cl': ('TVN', 'General', 'Programación TVN', 'Noticias, matinales, teleseries y entretención.'),
    'Canal13.cl': ('Canal 13', 'General', 'Programación Canal 13', 'Noticieros, realitys y programas en vivo.'),
    'Mega.cl': ('Mega', 'General', 'Programación Mega', 'Teleseries nacionales, noticias y entretención.'),
    'Chilevision.cl': ('Chilevisión', 'General', 'Programas de entretención, noticias y deportes.'),
    'CHVNoticias.cl': ('CHV Noticias', 'Noticias', 'Noticias en Vivo', 'Información continua las 24 horas.'),
    'T13Noticias.cl': ('T13 En Vivo', 'Noticias', 'Noticias T13', 'Actualidad y noticias nacionales e internacionales.'),
    'ENTChannel.cl': ('ENT Channel', 'Cine', 'Selección de Cine 24/7', 'Las mejores producciones cinematográficas.'),
    'StudioUniversal.cl': ('Studio Universal', 'Cine', 'Cine Studio Universal', 'Películas y producciones cinematográficas.'),
    'TelemundoInternacional.ar': ('Telemundo Internacional', 'Series', 'Programación Telemundo', 'Series, telenovelas y producciones.'),
    'SONYMOVIES.uy': ('Sony Movies', 'Cine', 'Cine Sony Movies', 'Películas de Hollywood y éxitos de taquilla.'),
    'FilmAndArts.cl': ('Film & Arts', 'Cultura', 'Especiales Film & Arts', 'Cine de autor, arte, música y espectáculos.'),
    'USANetwork.bo': ('USA Network', 'Series', 'Programación USA Network', 'Series exclusivas y cine de acción.'),
    'AE.cl': ('A&E', 'Series', 'Especiales A&E', 'Series de investigación, drama y acción.'),
    'NickJr.ar': ('Nick Jr.', 'Infantil', 'Programación Nick Jr.', 'Dibujos animados y contenidos educativos.'),
    'FOODNETWORK.uy': ('Food Network', 'Cocina', 'Gastronomía Internacional', 'Programas de cocina y competencias culinarias.'),
    'HGTV.ar': ('HGTV', 'Hogar', 'Hogar & Remodelación', 'Diseño de interiores y remodelación de espacios.'),
    'DiscoveryHomeAndHealth.cl': ('Discovery Home & Health', 'Estilo de Vida', 'Bienestar & Estilo', 'Salud, hogar y estilo de vida.'),
    'PASIONES.uy': ('Pasiones', 'Telenovelas', 'Novelas & Dramas', 'Telenovelas internacionales y grandes historias.'),
    'History2.cl1': ('History 2', 'Documentales', 'Programación History 2', 'Documentales, historia y ciencia.')
}

def parse_time(time_str):
    if not time_str or len(time_str) < 14:
        return None
    try:
        clean = time_str.strip()
        dt_part = clean[:14]
        tz_part = clean[14:].strip()
        dt = datetime.datetime.strptime(dt_part, "%Y%m%d%H%M%S")
        
        if tz_part and (tz_part.startswith('+') or tz_part.startswith('-')):
            sign = -1 if tz_part[0] == '+' else 1
            tz_hours = int(tz_part[1:3])
            tz_mins = int(tz_part[3:5]) if len(tz_part) >= 5 else 0
            dt += datetime.timedelta(hours=sign * tz_hours, minutes=sign * tz_mins)
            
        return dt.replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None

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

def agregar_bloque_respaldo(canales_dict, programas_lista, channel_id):
    ch_name, categoria, titulo_prog, desc_prog = DATOS_RESPALDO.get(
        channel_id, (channel_id, 'Variado', 'Programación General', 'Transmisión continua.')
    )
    
    ch_elem = ET.Element('channel', id=channel_id)
    dn_elem = ET.SubElement(ch_elem, 'display-name')
    dn_elem.text = ch_name
    canales_dict[channel_id] = ch_elem
    
    ahora = datetime.datetime.now(datetime.timezone.utc)
    inicio_base = ahora.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    
    for dia in range(4):
        for bloque in range(8):
            start_dt = inicio_base + datetime.timedelta(days=dia, hours=bloque*3)
            stop_dt = start_dt + datetime.timedelta(hours=3)
            
            prog = ET.Element(
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
            
            programas_lista.append((prog, channel_id, start_dt, stop_dt))

try:
    root_final = ET.Element('tv', {
        'generator-info-name': 'CustomEPGGenerator',
        'generator-info-url': 'https://github.com'
    })
    
    canales_dict = {}     # {channel_id: Element}
    programas_lista = []  # [(Element, channel_id, st_dt, sp_dt)]

    print("1. Cargando fuentes públicas...")
    for url in FUENTES_PUBLICAS:
        try:
            guiaroot = descargar_xml(url)
            for elem in guiaroot:
                if elem.tag == 'channel':
                    ch_id = elem.get('id')
                    target_id = MAPEO_IDS.get(ch_id, ch_id)
                    
                    if target_id in MIS_CANALES and target_id not in canales_dict:
                        elem.set('id', target_id)
                        canales_dict[target_id] = elem
                        
                elif elem.tag == 'programme':
                    ch_id = elem.get('channel')
                    target_id = MAPEO_IDS.get(ch_id, ch_id)
                    
                    if target_id in MIS_CANALES:
                        start_time = elem.get('start', '')
                        
                        if target_id in DESFASE_CANALES:
                            horas = DESFASE_CANALES[target_id]
                            start_time = ajustar_hora(start_time, horas)
                            elem.set('start', start_time)
                            elem.set('stop', ajustar_hora(elem.get('stop', ''), horas))

                        elem.set('channel', target_id)
                        
                        st_dt = parse_time(elem.get('start'))
                        sp_dt = parse_time(elem.get('stop'))
                        
                        if st_dt and sp_dt:
                            programas_lista.append((elem, target_id, st_dt, sp_dt))

            print(f" ✔ Cargada guía pública: {url}")
        except Exception as e:
            print(f" ❌ Error en {url}: {e}")

    print("2. Aplicando tu guía propia (Sobreescribiendo conflictos)...")
    try:
        guiaroot = descargar_xml(GUIA_PROPIA)
        for elem in guiaroot:
            if elem.tag == 'channel':
                ch_id = elem.get('id')
                target_id = MAPEO_IDS.get(ch_id, ch_id)
                if target_id in MIS_CANALES and target_id not in canales_dict:
                    elem.set('id', target_id)
                    canales_dict[target_id] = elem
                    
            elif elem.tag == 'programme':
                ch_id = elem.get('channel')
                target_id = MAPEO_IDS.get(ch_id, ch_id)
                
                if target_id in MIS_CANALES:
                    elem.set('channel', target_id)
                    st_dt = parse_time(elem.get('start'))
                    sp_dt = parse_time(elem.get('stop'))
                    
                    if st_dt and sp_dt:
                        # 🧹 ELIMINACIÓN DE BLOQUES CHOQUE: Quita cualquier programa público que choque con el rango
                        programas_lista = [
                            p for p in programas_lista 
                            if not (p[1] == target_id and p[2] < sp_dt and p[3] > st_dt)
                        ]
                        programas_lista.append((elem, target_id, st_dt, sp_dt))

        print(f" ✔ Guía propia aplicada con éxito: {GUIA_PROPIA}")
    except Exception as e:
        print(f" ❌ Error cargando tu guía propia: {e}")

    print("3. Verificando respaldos para canales sin programación...")
    for ch_id in MIS_CANALES:
        # Verificar si no hay canal o no hay ningún programa registrado para este canal
        tiene_programas = any(p[1] == ch_id for p in programas_lista)
        if ch_id not in canales_dict or not tiene_programas:
            agregar_bloque_respaldo(canales_dict, programas_lista, ch_id)
            print(f" ✔ Respaldo creado para: {ch_id}")

    # 4. ENSAMBLAJE FINAL CON ORDENAMIENTO CRONOLÓGICO
    # Agregar primero todas las etiquetas <channel>
    for ch_id in sorted(canales_dict.keys()):
        root_final.append(canales_dict[ch_id])

    # Ordenar estrictamente los programas por fecha de inicio para que la TV los interprete correctamente
    programas_lista.sort(key=lambda x: x[2])

    # Agregar todos los elementos <programme> en orden cronológico
    for p in programas_lista:
        root_final.append(p[0])

    tree = ET.ElementTree(root_final)
    ET.indent(tree, space="  ", level=0)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
        
    print("¡Proceso finalizado con éxito!")

except Exception as e:
    print(f"Error fatal: {e}")
    raise e
