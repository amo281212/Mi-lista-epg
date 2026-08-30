import datetime
import gzip
import urllib.request
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from zoneinfo import ZoneInfo


# ============================================================
# CANALESS
# ============================================================

MIS_CANALES = {
    'TVN.cl','Mega.cl','Chilevision.cl','Canal13.cl',
    'AMC.cl','Cinecanal.cl','Cinemax.cl','Golden.cl',
    'GoldenEdge.cl','HBO.cl','HBO2.cl','HBOFamily.cl',
    'HBOPop.cl','HBOXtreme.cl','ENTChannel.cl',
    'SONYMOVIES.uy','Sony.cl','Space.cl','StudioUniversal.ar',
    'TNT.cl','TNTSeries.cl','StarChannel.cl','UniversalTV.cl',
    'WarnerChannel.cl','USANetwork.bo','AXN.cl','AE.cl','FX.cl',
    'FilmAndArts.cl','ComedyCentral.cl','E_Entertainment.cl',
    'DIRECTVSports.cl','ESPN.cl','ESPN2.cl','ESPN3.cl',
    'ESPN4.cl','ESPN5.cl','ESPN6.cl','ESPN7.cl',
    'TNTSportsPremium.cl','TyCSports.cl',
    'CartoonNetwork.cl','DiscoveryKids.cl','DisneyChannel.cl',
    'DisneyJunior.cl','NickJr.bo','Nick.cl','Tooncast.cl',
    'AnimalPlanet.cl','Discovery.cl','DiscoveryScience.cl',
    'DiscoveryTheater.cl','DiscoveryTurbo.cl','DiscoveryWorld.cl',
    'ElGourmet.cl','FOODNETWORK.uy','HGTV.ar',
    'DiscoveryHomeAndHealth.cl','History.cl','History2.cl1',
    'InvestigationDiscovery.cl','NationalGeographic.cl',
    'LasEstrellas.cl','PASIONES.uy',
    'TelemundoInternacional.ar','TLNovelas.cl','EnlaceTBN.cl',
    'CNNChile.cl','CHVNoticias.cl','T13Noticias.cl','24Horas.cl'
}


# ============================================================
# MAPEO DE IDS
# ============================================================

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


# ============================================================
# FUENTES PÚBLICAS
# ============================================================

FUENTES_PUBLICAS = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-co.xml",
    "https://iptv-epg.org/files/epg-uy.xml",
    "https://iptv-epg.org/files/epg-bo.xml",
]


# ============================================================
# TU GUÍA PROPIA
#
# ESTA SE CARGA ANTES DE GATOTV.
# GATOTV TENDRÁ LA ÚLTIMA PALABRA.
# ============================================================

GUIA_PROPIA = (
    "https://raw.githubusercontent.com/amo281212/"
    "epg_que_actualizo.xml/refs/heads/main/guia.xml"
)


# ============================================================
# DESFASES
# ============================================================

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


DESFASE_GUIA_PROPIA = {
    'GoldenEdge.cl': -2,
}


DESFASE_GATOTV = {
    'GoldenEdge.cl': -2,
}


# ============================================================
# GATOTV
# ============================================================

GATOTV_CANALES = {

    'TVN.cl': 'https://www.gatotv.com/canal/tvn_chile',
    'Mega.cl': 'https://www.gatotv.com/canal/mega_chile',
    'Chilevision.cl': 'https://www.gatotv.com/canal/chilevision',
    'Canal13.cl': 'https://www.gatotv.com/canal/13_de_chile',

    'AMC.cl': 'https://www.gatotv.com/canal/amc_mexico',
    'Cinecanal.cl': 'https://www.gatotv.com/canal/cinecanal_chile',
    'Cinemax.cl': 'https://www.gatotv.com/canal/cinemax_chile',
    'Golden.cl': 'https://www.gatotv.com/canal/golden_chile',
    'GoldenEdge.cl': 'https://www.gatotv.com/canal/golden_edge',

    'HBO.cl': 'https://www.gatotv.com/canal/hbo_chile',
    'HBO2.cl': 'https://www.gatotv.com/canal/hbo_2_latinoamerica',
    'HBOFamily.cl': 'https://www.gatotv.com/canal/hbo_family_latinoamerica',
    'HBOPop.cl': 'https://www.gatotv.com/canal/hbo_pop',
    'HBOXtreme.cl': 'https://www.gatotv.com/canal/hbo_xtreme',

    'SONYMOVIES.uy': 'https://www.gatotv.com/canal/sony_movies_chile',
    'Sony.cl': 'https://www.gatotv.com/canal/sony_centro',
    'Space.cl': 'https://www.gatotv.com/canal/space_chile',
    'StudioUniversal.ar': 'https://www.gatotv.com/canal/studio_universal_panregional',

    'TNT.cl': 'https://www.gatotv.com/canal/tnt_chile',
    'TNTSeries.cl': 'https://www.gatotv.com/canal/tnt_series',
    'StarChannel.cl': 'https://www.gatotv.com/canal/star_channel_chile',
    'UniversalTV.cl': 'https://www.gatotv.com/canal/universal_tv_panregional',
    'WarnerChannel.cl': 'https://www.gatotv.com/canal/warner_tv_chile',

    'FX.cl': 'https://www.gatotv.com/canal/fx_chile',
    'AXN.cl': 'https://www.gatotv.com/canal/axn_chile',
    'AE.cl': 'https://www.gatotv.com/canal/a_y_e_chile',
    'USANetwork.bo': 'https://www.gatotv.com/canal/usa_network_chile',

    'FilmAndArts.cl': 'https://www.gatotv.com/canal/film_and_arts',
    'ComedyCentral.cl': 'https://www.gatotv.com/canal/comedy_central_bolivia',
    'E_Entertainment.cl': 'https://www.gatotv.com/canal/e_entertainment_television_chile',

    'ESPN.cl': 'https://www.gatotv.com/canal/espn_chile',
    'ESPN2.cl': 'https://www.gatotv.com/canal/espn_2_colombia',
    'ESPN3.cl': 'https://www.gatotv.com/canal/espn_3_chile',
    'ESPN4.cl': 'https://www.gatotv.com/canal/espn_4_sur',
    'ESPN6.cl': 'https://www.gatotv.com/canal/espn_6_chile',
    'ESPN7.cl': 'https://www.gatotv.com/canal/espn_7_chile',
    'TyCSports.cl': 'https://www.gatotv.com/canal/tyc_sports',

    'CartoonNetwork.cl': 'https://www.gatotv.com/canal/cartoon_network_chile',
    'DiscoveryKids.cl': 'https://www.gatotv.com/canal/discovery_kids_chile',
    'DisneyChannel.cl': 'https://www.gatotv.com/canal/disney_channel_chile',
    'DisneyJunior.cl': 'https://www.gatotv.com/canal/disney_junior_chile',
    'NickJr.bo': 'https://www.gatotv.com/canal/nick_junior_latinoamerica',
    'Nick.cl': 'https://www.gatotv.com/canal/nickelodeon_chile',
    'Tooncast.cl': 'https://www.gatotv.com/canal/tooncast',

    'AnimalPlanet.cl': 'https://www.gatotv.com/canal/animal_planet_chile',
    'Discovery.cl': 'https://www.gatotv.com/canal/discovery_channel_chile',
    'DiscoveryScience.cl': 'https://www.gatotv.com/canal/discovery_science_latinoamerica',
    'DiscoveryTheater.cl': 'https://www.gatotv.com/canal/discovery_theater_latinoamerica',
    'DiscoveryTurbo.cl': 'https://www.gatotv.com/canal/discovery_turbo_latinoamerica',
    'DiscoveryWorld.cl': 'https://www.gatotv.com/canal/discovery_world_latinoamerica',

    'ElGourmet.cl': 'https://www.gatotv.com/canal/elgourmet',
    'History.cl': 'https://www.gatotv.com/canal/history_chile',
    'History2.cl1': 'https://www.gatotv.com/canal/history_2_chile',
    'InvestigationDiscovery.cl': 'https://www.gatotv.com/canal/investigation_discovery_panregional',
    'NationalGeographic.cl': 'https://www.gatotv.com/canal/national_geographic_chile',

    'LasEstrellas.cl': 'https://www.gatotv.com/canal/las_estrellas_chile',
    'PASIONES.uy': 'https://www.gatotv.com/canal/pasiones_latinoamerica',
    'TelemundoInternacional.ar': 'https://www.gatotv.com/canal/telemundo_chile',
    'TLNovelas.cl': 'https://www.gatotv.com/canal/tlnovelas_chile',

    'EnlaceTBN.cl': 'https://www.gatotv.com/canal/enlace',
    'CNNChile.cl': 'https://www.gatotv.com/canal/cnn_chile',
    '24Horas.cl': 'https://www.gatotv.com/canal/24_horas_chile',
}


GATOTV_DIAS = 3

ZONA_HORARIA_GATOTV = ZoneInfo("America/Santiago")


# ============================================================
# DESCARGAR XML
# ============================================================

def descargar_xml(url):

    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        content = response.read()

    if url.endswith('.gz') or content[:2] == b'\x1f\x8b':
        content = gzip.decompress(content)

    return ET.fromstring(content)


# ============================================================
# NORMALIZAR HORARIOS
# ============================================================

def normalizar_a_utc(time_str, horas_desfase=0):

    if not time_str or len(time_str) < 14:
        return time_str, None

    try:

        clean = time_str.strip()

        dt = datetime.datetime.strptime(
            clean[:14],
            "%Y%m%d%H%M%S"
        )

        tz_part = clean[14:].strip()

        if tz_part and tz_part[0] in '+-':

            sign = 1 if tz_part[0] == '+' else -1

            h = int(tz_part[1:3])

            m = int(tz_part[3:5]) if len(tz_part) >= 5 else 0

            dt -= datetime.timedelta(
                hours=sign * h,
                minutes=sign * m
            )

        dt += datetime.timedelta(
            hours=horas_desfase
        )

        return (
            dt.strftime("%Y%m%d%H%M%S") + " +0000",
            dt
        )

    except Exception:

        return time_str, None


# ============================================================
# PARSER GATOTV
# ============================================================

class GatoTVParser(HTMLParser):

    def __init__(self):

        super().__init__(
            convert_charrefs=True
        )

        self.rows = []

        self.in_tr = False
        self.in_cell = False
        self.in_a = False

        self.current_row = []
        self.current_cell = []
        self.current_anchor = []

    def handle_starttag(self, tag, attrs):

        tag = tag.lower()

        if tag == 'tr':

            self.in_tr = True
            self.current_row = []

        elif self.in_tr and tag in ('td', 'th'):

            self.in_cell = True
            self.current_cell = []
            self.current_anchor = []

        elif self.in_cell and tag == 'a':

            self.in_a = True
            self.current_anchor = []

    def handle_data(self, data):

        if not self.in_cell:
            return

        texto = data.strip()

        if not texto:
            return

        self.current_cell.append(texto)

        if self.in_a:
            self.current_anchor.append(texto)

    def handle_endtag(self, tag):

        tag = tag.lower()

        if tag == 'a' and self.in_a:

            self.in_a = False

        elif tag in ('td', 'th') and self.in_cell:

            self.current_row.append({
                'texto': ' '.join(self.current_cell).strip(),
                'enlace': ' '.join(self.current_anchor).strip()
            })

            self.in_cell = False
            self.current_cell = []
            self.current_anchor = []

        elif tag == 'tr' and self.in_tr:

            if self.current_row:
                self.rows.append(self.current_row)

            self.current_row = []
            self.in_tr = False


# ============================================================
# HORA GATOTV
# ============================================================

def convertir_hora_gatotv(hora, fecha):

    hora = " ".join(hora.strip().split())

    for formato in ("%H:%M", "%I:%M %p", "%I:%M%p"):

        try:

            t = datetime.datetime.strptime(
                hora,
                formato
            ).time()

            return datetime.datetime.combine(
                fecha,
                t,
                tzinfo=ZONA_HORARIA_GATOTV
            )

        except ValueError:
            pass

    return None


# ============================================================
# EXTRAER GATOTV
# ============================================================

def extraer_programacion_gatotv(
    url,
    channel_id,
    fecha
):

    print(
        f"    → GatoTV {channel_id} | {fecha}"
    )

    req = urllib.request.Request(
        url,
        headers={
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language':
                'es-ES,es;q=0.9,en;q=0.8'
        }
    )

    try:

        with urllib.request.urlopen(
            req,
            timeout=30
        ) as response:

            html = response.read().decode(
                'utf-8',
                errors='replace'
            )

    except Exception as e:

        print(
            f"       ❌ Error GatoTV: {e}"
        )

        return []

    parser = GatoTVParser()

    try:
        parser.feed(html)

    except Exception as e:

        print(
            f"       ❌ Error parser: {e}"
        )

        return []

    programas = []

    for row in parser.rows:

        if len(row) < 3:
            continue

        hora_inicio = row[0]['texto']
        hora_fin = row[1]['texto']

        if not re.match(
            r'^\d{1,2}:\d{2}$',
            hora_inicio
        ):
            continue

        if not re.match(
            r'^\d{1,2}:\d{2}$',
            hora_fin
        ):
            continue

        titulo = (
            row[2]['enlace']
            or row[2]['texto']
        ).strip()

        if not titulo:
            continue

        titulo = re.sub(
            r'\s+',
            ' ',
            titulo
        )

        descripcion = ""

        texto_celda = re.sub(
            r'\s+',
            ' ',
            row[2]['texto']
        ).strip()

        if (
            row[2]['enlace']
            and texto_celda.startswith(
                row[2]['enlace']
            )
        ):

            descripcion = texto_celda[
                len(row[2]['enlace']): 
            ].strip()

        inicio = convertir_hora_gatotv(
            hora_inicio,
            fecha
        )

        fin = convertir_hora_gatotv(
            hora_fin,
            fecha
        )

        if not inicio or not fin:
            continue

        # Si termina después de medianoche.
        if fin <= inicio:
            fin += datetime.timedelta(days=1)

        inicio_utc = inicio.astimezone(
            datetime.timezone.utc
        )

        fin_utc = fin.astimezone(
            datetime.timezone.utc
        )

        desfase = DESFASE_GATOTV.get(
            channel_id,
            0
        )

        if desfase:
            ajuste = datetime.timedelta(
                hours=desfase
            )
            inicio_utc += ajuste
            fin_utc += ajuste

        if fin_utc <= inicio_utc:
            continue

        prog = ET.Element(
            'programme',
            {
                'start':
                    inicio_utc.strftime(
                        "%Y%m%d%H%M%S"
                    ) + " +0000",

                'stop':
                    fin_utc.strftime(
                        "%Y%m%d%H%M%S"
                    ) + " +0000",

                'channel':
                    channel_id
            }
        )

        title = ET.SubElement(
            prog,
            'title',
            {'lang': 'es'}
        )

        title.text = titulo

        if descripcion:

            desc = ET.SubElement(
                prog,
                'desc',
                {'lang': 'es'}
            )

            desc.text = descripcion

        programas.append(
            (
                prog,
                channel_id,
                inicio_utc.replace(tzinfo=None),
                fin_utc.replace(tzinfo=None)
            )
        )

        print(
            f"       📺 {hora_inicio}-{hora_fin} → {titulo}"
        )

    print(
        f"       ✔ {len(programas)} programas"
    )

    return programas


# ============================================================
# ELIMINAR CONFLICTOS
#
# El programa nuevo gana SIEMPRE.
# ============================================================

def eliminar_conflictos(
    programas_lista,
    nuevos_programas
):

    for (
        _,
        channel_id,
        nuevo_inicio,
        nuevo_fin
    ) in nuevos_programas:

        programas_lista[:] = [
            p
            for p in programas_lista
            if not (
                p[1] == channel_id
                and p[2] < nuevo_fin
                and p[3] > nuevo_inicio
            )
        ]


# ============================================================
# CARGAR GATOTV
# ============================================================

def cargar_gatotv(
    programas_lista,
    canales_dict
):

    print("")
    print("3. Cargando GatoTV...")
    print("")

    ahora = datetime.datetime.now(
        ZONA_HORARIA_GATOTV
    )

    fecha_base = ahora.date()

    total = 0

    for channel_id, base_url in GATOTV_CANALES.items():

        canal_programas = []

        for dia in range(GATOTV_DIAS):

            fecha = (
                fecha_base
                + datetime.timedelta(days=dia)
            )

            url = (
                base_url
                + "/"
                + fecha.strftime("%Y-%m-%d")
            )

            encontrados = (
                extraer_programacion_gatotv(
                    url,
                    channel_id,
                    fecha
                )
            )

            canal_programas.extend(
                encontrados
            )

        if not canal_programas:

            print(
                f"    ⚠️ Sin datos GatoTV: {channel_id}"
            )

            continue

        # GatoTV gana a TODO lo anterior.
        eliminar_conflictos(
            programas_lista,
            canal_programas
        )

        programas_lista.extend(
            canal_programas
        )

        if channel_id not in canales_dict:

            ch = ET.Element(
                'channel',
                {'id': channel_id}
            )

            name = ET.SubElement(
                ch,
                'display-name'
            )

            name.text = channel_id

            canales_dict[channel_id] = ch

        total += len(canal_programas)

        print(
            f"    ✔ GatoTV integrado: "
            f"{channel_id} "
            f"({len(canal_programas)})"
        )

    print("")
    print(
        f"✔ GatoTV finalizado: {total} programas"
    )


# ============================================================
# CARGAR CUALQUIER XML COMO FUENTE
# ============================================================

def cargar_fuente_xml(
    url,
    programas_lista,
    canales_dict,
    desfases
):

    try:

        root = descargar_xml(url)

        for elem in root:

            if elem.tag == 'channel':

                original = elem.get('id')

                target = MAPEO_IDS.get(
                    original,
                    original
                )

                if target not in MIS_CANALES:
                    continue

                elem.set(
                    'id',
                    target
                )

                if target not in canales_dict:

                    canales_dict[target] = elem

            elif elem.tag == 'programme':

                original = elem.get('channel')

                target = MAPEO_IDS.get(
                    original,
                    original
                )

                if target not in MIS_CANALES:
                    continue

                elem.set(
                    'channel',
                    target
                )

                desfase = desfases.get(
                    target,
                    0
                )

                start, st = normalizar_a_utc(
                    elem.get('start', ''),
                    desfase
                )

                stop, sp = normalizar_a_utc(
                    elem.get('stop', ''),
                    desfase
                )

                elem.set(
                    'start',
                    start
                )

                elem.set(
                    'stop',
                    stop
                )

                if st and sp and sp > st:

                    programas_lista.append(
                        (
                            elem,
                            target,
                            st,
                            sp
                        )
                    )

        return True

    except Exception as e:

        print(
            f"❌ Error cargando {url}: {e}"
        )

        return False


# ============================================================
# PROCESO PRINCIPAL
# ============================================================

try:

    print("")
    print("==========================================")
    print("🚀 GENERADOR EPG")
    print("==========================================")
    print("")

    root_final = ET.Element(
        'tv',
        {
            'generator-info-name':
                'CustomEPGGenerator',

            'generator-info-url':
                'https://github.com'
        }
    )

    canales_dict = {}

    programas_lista = []


    # ========================================================
    # 1. FUENTES PÚBLICAS
    # ========================================================

    print("1. Cargando fuentes públicas...")
    print("")

    for url in FUENTES_PUBLICAS:

        if cargar_fuente_xml(
            url,
            programas_lista,
            canales_dict,
            DESFASE_CANALES
        ):

            print(
                f" ✔ {url}"
            )


    # ========================================================
    # 2. TU GUÍA PROPIA
    #
    # IMPORTANTE:
    # GatoTV viene DESPUÉS.
    # ========================================================

    print("")
    print("2. Cargando tu guía propia...")
    print("")

    cargar_fuente_xml(
        GUIA_PROPIA,
        programas_lista,
        canales_dict,
        DESFASE_GUIA_PROPIA
    )


    # ========================================================
    # 3. GATOTV
    #
    # GATOTV ES LA ÚLTIMA FUENTE.
    #
    # Por lo tanto:
    #
    # GatoTV > guía propia > fuentes públicas
    #
    # Esto es exactamente lo que queremos.
    # ========================================================

    cargar_gatotv(
        programas_lista,
        canales_dict
    )


    # ========================================================
    # 4. NO CREAR RESPALDOS
    #
    # NUNCA agregamos:
    #
    # "NO DATA"
    # "Programación General"
    # "Programación continua"
    #
    # Si no existe información real,
    # simplemente queda sin programa.
    # ========================================================

    print("")
    print(
        "4. Sin respaldos artificiales."
    )
    print(
        "   No se generan NO DATA."
    )


    # ========================================================
    # 5. ASEGURAR CANALES
    # ========================================================

    for channel_id in MIS_CANALES:

        if channel_id not in canales_dict:

            ch = ET.Element(
                'channel',
                {'id': channel_id}
            )

            name = ET.SubElement(
                ch,
                'display-name'
            )

            name.text = channel_id

            canales_dict[channel_id] = ch


    # ========================================================
    # 6. ORDENAR PROGRAMAS
    # ========================================================

    programas_lista.sort(
        key=lambda x: (
            x[1],
            x[2]
        )
    )


    # ========================================================
    # 7. CONSTRUIR XML
    # ========================================================

    print("")
    print(
        "5. Generando epg_final.xml..."
    )

    for channel_id in sorted(
        canales_dict.keys()
    ):

        root_final.append(
            canales_dict[channel_id]
        )

    for (
        elem,
        channel_id,
        start,
        stop
    ) in programas_lista:

        root_final.append(elem)


    # ========================================================
    # 8. GUARDAR
    # ========================================================

    tree = ET.ElementTree(
        root_final
    )

    ET.indent(
        tree,
        space="  "
    )

    tree.write(
        "epg_final.xml",
        encoding="utf-8",
        xml_declaration=True
    )


    print("")
    print("==========================================")
    print("🎉 EPG GENERADO CORRECTAMENTE")
    print("==========================================")
    print("")
    print("Archivo: epg_final.xml")
    print("")
    print(
        "Prioridad:"
    )
    print(
        "GatoTV > Guía propia > Fuentes públicas"
    )
    print("")
    print(
        "❌ NO DATA artificial: DESACTIVADO"
    )
    print(
        "❌ Respaldos artificiales: DESACTIVADOS"
    )
    print("")


except Exception as e:

    print("")
    print("==========================================")
    print("❌ ERROR FATAL")
    print("==========================================")
    print("")
    print(e)
    print("")

    raise
