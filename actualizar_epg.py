import datetime
import gzip
import re
import urllib.request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# 🎯 TUS CANALES CON IDS LIMPIOS
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
    'E_Entertainment.cl',
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

# 🐱 CONFIGURACIÓN DE CANALES GATOTV
CANALES_GATOTV = {
    'TVN.cl': ('tvn_chile', 0),
    'Mega.cl': ('mega_chile', 0),
    'Chilevision.cl': ('chilevision', 0),
    'Canal13.cl': ('13_de_chile', 0),
    'AMC.cl': ('amc_mexico', 0),
    'Cinecanal.cl': ('cinecanal_chile', 0),
    'Cinemax.cl': ('cinemax_chile', 0),
    'Golden.cl': ('golden_chile', 0),
    'GoldenEdge.cl': ('golden_edge', -2),
    'HBO.cl': ('hbo_chile', 0),
    'HBO2.cl': ('hbo_2_latinoamerica', 0),
    'HBOFamily.cl': ('hbo_family_latinoamerica', 0),
    'HBOPop.cl': ('hbo_pop', 0),
    'HBOXtreme.cl': ('hbo_xtreme', 0),
    'SONYMOVIES.uy': ('sony_movies_chile', 0),
    'Sony.cl': ('sony_centro', 0),
    'Space.cl': ('space_chile', 0),
    'StudioUniversal.ar': ('studio_universal_panregional', 0),
    'TNT.cl': ('tnt_chile', 0),
    'TNTSeries.cl': ('tnt_series', 0),
    'StarChannel.cl': ('star_channel_chile', 0),
    'UniversalTV.cl': ('universal_tv_panregional', 0),
    'WarnerChannel.cl': ('warner_tv_chile', 0),
    'FX.cl': ('fx_chile', 0),
    'AXN.cl': ('axn_chile', 0),
    'AE.cl': ('a_y_e_chile', 0),
    'USANetwork.bo': ('usa_network_chile', 0),
    'FilmAndArts.cl': ('film_and_arts', 0),
    'ComedyCentral.cl': ('comedy_central_bolivia', 0),
    'E_Entertainment.cl': ('e_entertainment_television_chile', 0),
    'ESPN.cl': ('espn_chile', 0),
    'ESPN2.cl': ('espn_2_colombia', 0),
    'ESPN3.cl': ('espn_3_chile', 0),
    'ESPN4.cl': ('espn_4_sur', 0),
    'ESPN6.cl': ('espn_6_chile', 0),
    'ESPN7.cl': ('espn_7_chile', 0),
    'TyCSports.cl': ('tyc_sports', 0),
    'CartoonNetwork.cl': ('cartoon_network_chile', 0),
    'DiscoveryKids.cl': ('discovery_kids_chile', 0),
    'DisneyChannel.cl': ('disney_channel_chile', 0),
    'DisneyJunior.cl': ('disney_junior_chile', 0),
    'NickJr.bo': ('nick_junior_latinoamerica', 0),
    'Nick.cl': ('nickelodeon_chile', 0),
    'Tooncast.cl': ('tooncast', 0),
    'AnimalPlanet.cl': ('animal_planet_chile', 0),
    'Discovery.cl': ('discovery_channel_chile', 0),
    'DiscoveryScience.cl': ('discovery_science_latinoamerica', 0),
    'DiscoveryTheater.cl': ('discovery_theater_latinoamerica', 0),
    'DiscoveryTurbo.cl': ('discovery_turbo_latinoamerica', 0),
    'DiscoveryWorld.cl': ('discovery_world_latinoamerica', 0),
    'ElGourmet.cl': ('elgourmet', 0),
    'History.cl': ('history_chile', 0),
    'History2.cl1': ('history_2_chile', 0),
    'InvestigationDiscovery.cl': ('investigation_discovery_panregional', 0),
    'NationalGeographic.cl': ('national_geographic_chile', 0),
    'LasEstrellas.cl': ('las_estrellas_chile', 0),
    'PASIONES.uy': ('pasiones_latinoamerica', 0),
    'TelemundoInternacional.ar': ('telemundo_chile', 0),
    'TLNovelas.cl': ('tlnovelas_chile', 0),
    'EnlaceTBN.cl': ('enlace', 0),
    'CNNChile.cl': ('cnn_chile', 0),
    '24Horas.cl': ('24_horas_chile', 0),
}

# 🔄 MAPEO COMPLETO
MAPEO_IDS = {
    'E_EntertainmentTelevision.bo': 'E_Entertainment.cl',
    'EEntertainment.cl': 'E_Entertainment.cl',
    'E!Entertainment.cl': 'E_Entertainment.cl',
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

# 🌐 FUENTES PÚBLICAS
FUENTES_PUBLICAS = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-co.xml",
    "https://iptv-epg.org/files/epg-uy.xml",
    "https://iptv-epg.org/files/epg-bo.xml",
]

# 📝 GUÍA MANUAL
GUIA_PROPIA = "https://raw.githubusercontent.com/amo281212/epg_que_actualizo.xml/refs/heads/main/guia.xml"

# 🕒 DESFASES FUENTES PÚBLICAS
DESFASE_CANALES = {
    'Cinemax.cl': 1,
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

# 🕒 DESFASES GUÍA PROPIA
DESFASE_GUIA_PROPIA = {
    'GoldenEdge.cl': -2,
}

DATOS_RESPALDO = {
    'E_Entertainment.cl': ('E! Entertainment', 'Variado', 'Programación E! Entertainment', 'Espectáculos, moda, realities y cultura pop.'),
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

def normalizar_a_utc(time_str, horas_desfase=0):
    if not time_str or len(time_str) < 14:
        return time_str, None
    try:
        clean = time_str.strip()
        dt_part = clean[:14]
        tz_part = clean[14:].strip()
        
        dt = datetime.datetime.strptime(dt_part, "%Y%m%d%H%M%S")
        
        if tz_part and (tz_part.startswith('+') or tz_part.startswith('-')):
            sign = 1 if tz_part[0] == '+' else -1
            tz_hours = int(tz_part[1:3])
            tz_mins = int(tz_part[3:5]) if len(tz_part) >= 5 else 0
            offset_delta = datetime.timedelta(hours=sign * tz_hours, minutes=sign * tz_mins)
            dt_utc = dt - offset_delta
        else:
            dt_utc = dt
            
        if horas_desfase != 0:
            dt_utc += datetime.timedelta(hours=horas_desfase)
            
        str_utc = dt_utc.strftime("%Y%m%d%H%M%S") + " +0000"
        return str_utc, dt_utc
    except Exception:
        return time_str, None

def descargar_xml(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read()
    if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
        content = gzip.decompress(content)
    return ET.fromstring(content)

# 🐱 SCRAPER DE GATOTV OPTIMIZADO
def extraer_gatotv(channel_id, slug, horas_desfase, canales_dict, programas_lista):
    url = f"https://www.gatotv.com/canal/{slug}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
        soup = BeautifulSoup(html, 'html.parser')
        
        if channel_id not in canales_dict:
            ch_elem = ET.Element('channel', id=channel_id)
            dn_elem = ET.SubElement(ch_elem, 'display-name')
            title_tag = soup.find('title')
            dn_elem.text = title_tag.text.split('-')[0].strip() if title_tag else channel_id
            canales_dict[channel_id] = ch_elem
            
        filas = soup.select('table.tbl_schedules tr, tr.tbl_schedules_row')
        if not filas:
            filas = soup.find_all('tr')
            
        hoy = datetime.datetime.utcnow().date()
        programas_temp = []
        
        for tr in filas:
            tds = tr.find_all('td')
            if len(tds) < 2:
                continue
                
            time_td = tds[0].text.strip()
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_td)
            if not time_match:
                continue
                
            hora = int(time_match.group(1))
            minuto = int(time_match.group(2))
            
            time_upper = time_td.upper()
            if 'PM' in time_upper and hora < 12:
                hora += 12
            elif 'AM' in time_upper and hora == 12:
                hora = 0
                
            dt_inicio = datetime.datetime(hoy.year, hoy.month, hoy.day, hora, minuto)
            
            # GatoTV publica en horario local Chile/Argentina (UTC-3 / UTC-4) -> Convertir a UTC (+4)
            dt_inicio_utc = dt_inicio + datetime.timedelta(hours=4)
            if horas_desfase != 0:
                dt_inicio_utc += datetime.timedelta(hours=horas_desfase)
                
            info_td = tds[1]
            titulo_elem = info_td.find('span', class_='tbl_schedules_title') or info_td.find('a') or info_td.find('strong')
            if not titulo_elem:
                continue
            titulo = titulo_elem.text.strip()
            if not titulo or titulo.lower() in ['hora', 'programa']:
                continue
                
            desc_elem = info_td.find('div', class_='tbl_schedules_desc') or info_td.find('span', class_='tbl_schedules_desc')
            desc = desc_elem.text.strip() if desc_elem else "Sin descripción disponible."
            
            img_elem = info_td.find('img')
            img_url = None
            if img_elem:
                img_url = img_elem.get('src') or img_elem.get('data-src')
            
            programas_temp.append({
                'title': titulo,
                'desc': desc,
                'start': dt_inicio_utc,
                'img': img_url
            })

        # Calcular hora de fin según la hora de inicio del siguiente programa
        programas_encontrados = 0
        for i in range(len(programas_temp)):
            p = programas_temp[i]
            st_dt = p['start']
            
            if i + 1 < len(programas_temp):
                sp_dt = programas_temp[i+1]['start']
                if sp_dt <= st_dt:
                    sp_dt = st_dt + datetime.timedelta(days=1)
            else:
                sp_dt = st_dt + datetime.timedelta(hours=1)
                
            prog = ET.Element('programme', 
                              start=st_dt.strftime("%Y%m%d%H%M%S +0000"), 
                              stop=sp_dt.strftime("%Y%m%d%H%M%S +0000"), 
                              channel=channel_id)
            
            title_xml = ET.SubElement(prog, 'title', lang='es')
            title_xml.text = p['title']
            
            desc_xml = ET.SubElement(prog, 'desc', lang='es')
            desc_xml.text = p['desc']
            
            if p['img']:
                img_url = p['img']
                if not img_url.startswith('http'):
                    img_url = "https://www.gatotv.com" + (img_url if img_url.startswith('/') else '/' + img_url)
                ET.SubElement(prog, 'icon', src=img_url)
                
            programas_lista.append((prog, channel_id, st_dt, sp_dt))
            programas_encontrados += 1

        if programas_encontrados > 0:
            print(f"   └─ {channel_id}: {programas_encontrados} programas extraídos de GatoTV.")

    except Exception as e:
        print(f" ⚠️ No se pudo extraer GatoTV para {channel_id}: {e}")

def agregar_bloque_respaldo(canales_dict, programas_lista, channel_id):
    ch_name, categoria, titulo_prog, desc_prog = DATOS_RESPALDO.get(
        channel_id, (channel_id, 'Variado', 'Programación General', 'Transmisión continua.')
    )
    
    ch_elem = ET.Element('channel', id=channel_id)
    dn_elem = ET.SubElement(ch_elem, 'display-name')
    dn_elem.text = ch_name
    canales_dict[channel_id] = ch_elem
    
    ahora_utc = datetime.datetime.utcnow()
    inicio_base = ahora_utc.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    
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

    print("1. Extrayendo guías desde GatoTV...")
    for target_id, (slug, horas_desfase) in CANALES_GATOTV.items():
        if target_id in MIS_CANALES:
            extraer_gatotv(target_id, slug, horas_desfase, canales_dict, programas_lista)
    print(" ✔ GatoTV procesado exitosamente.")

    print("2. Cargando fuentes públicas (relleno adicional)...")
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
                        elem.set('channel', target_id)

                        horas = DESFASE_CANALES.get(target_id, 0)
                        start_str, st_dt = normalizar_a_utc(elem.get('start', ''), horas)
                        stop_str, sp_dt = normalizar_a_utc(elem.get('stop', ''), horas)

                        elem.set('start', start_str)
                        elem.set('stop', stop_str)

                        if st_dt and sp_dt:
                            programas_lista.append((elem, target_id, st_dt, sp_dt))

            print(f" ✔ Cargada guía pública: {url}")
        except Exception as e:
            print(f" ❌ Error en {url}: {e}")

    print("3. Aplicando tu guía propia (Sobreescribiendo conflictos)...")
    try:
        guiaroot = descargar_xml(GUIA_PROPIA)
        for elem in guiaroot:
            if elem.tag == 'channel':
                ch_id = elem.get('id')
                target_id = MAPEO_IDS.get(ch_id, ch_id)
                if target_id in MIS_CANALES:
                    elem.set('id', target_id)
                    canales_dict[target_id] = elem
                    
            elif elem.tag == 'programme':
                ch_id = elem.get('channel')
                target_id = MAPEO_IDS.get(ch_id, ch_id)
                
                if target_id in MIS_CANALES:
                    elem.set('channel', target_id)

                    horas = DESFASE_GUIA_PROPIA.get(target_id, 0)
                    start_str, st_dt = normalizar_a_utc(elem.get('start', ''), horas)
                    stop_str, sp_dt = normalizar_a_utc(elem.get('stop', ''), horas)

                    elem.set('start', start_str)
                    elem.set('stop', stop_str)

                    if st_dt and sp_dt:
                        programas_lista = [
                            p for p in programas_lista 
                            if not (p[1] == target_id and p[2] < sp_dt and p[3] > st_dt)
                        ]
                        programas_lista.append((elem, target_id, st_dt, sp_dt))

        print(f" ✔ Guía propia aplicada con éxito: {GUIA_PROPIA}")
    except Exception as e:
        print(f" ❌ Error cargando tu guía propia: {e}")

    print("4. Verificando respaldos para canales sin programación...")
    for ch_id in MIS_CANALES:
        tiene_programas = any(p[1] == ch_id for p in programas_lista)
        if ch_id not in canales_dict or not tiene_programas:
            agregar_bloque_respaldo(canales_dict, programas_lista, ch_id)
            print(f" ✔ Respaldo creado para: {ch_id}")

    # 5. ENSAMBLAJE FINAL
    for ch_id in sorted(canales_dict.keys()):
        root_final.append(canales_dict[ch_id])

    programas_lista.sort(key=lambda x: x[2])

    for p in programas_lista:
        root_final.append(p[0])

    tree = ET.ElementTree(root_final)
    ET.indent(tree, space="  ", level=0)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
        
    print("¡Proceso finalizado con éxito!")

except Exception as e:
    print(f"Error fatal: {e}")
    raise e
