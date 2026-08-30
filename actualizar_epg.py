import datetime
import gzip
import urllib.request
import urllib.error
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from zoneinfo import ZoneInfo


# ============================================================
# 🎯 TUS CANALES CON IDS LIMPIOS
# ============================================================

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


# ============================================================
# 🔄 MAPEO COMPLETO
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
# 🌐 SOLO FUENTES PÚBLICAS EXTERNAS
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
# 📝 TU GUÍA MANUAL
# ============================================================

GUIA_PROPIA = "https://raw.githubusercontent.com/amo281212/epg_que_actualizo.xml/refs/heads/main/guia.xml"


# ============================================================
# 🕒 DESFASES PARA LAS FUENTES PÚBLICAS
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


# ============================================================
# 🕒 DESFASES EXCLUSIVOS PARA TU GUÍA PROPIA
# ============================================================

DESFASE_GUIA_PROPIA = {
    'GoldenEdge.cl': -2,
}


# ============================================================
# 🐱 GATOTV
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


# ============================================================
# 🕒 DESFASES EXCLUSIVOS PARA GATOTV
# ============================================================

DESFASE_GATOTV = {
    'GoldenEdge.cl': -2,
}


# ============================================================
# 📅 GATOTV: CUÁNTOS DÍAS CONSULTAR
# ============================================================

GATOTV_DIAS = 3


# ============================================================
# 🌎 ZONA HORARIA BASE DE GATOTV
# ============================================================

ZONA_HORARIA_GATOTV = ZoneInfo("America/Santiago")


# ============================================================
# 📝 DATOS DE RESPALDO
# ============================================================

DATOS_RESPALDO = {
    'E_Entertainment.cl': (
        'E! Entertainment',
        'Variado',
        'Programación E! Entertainment',
        'Espectáculos, moda, realities y cultura pop.'
    ),

    'AXN.cl': (
        'AXN',
        'Series',
        'Series y Acción',
        'Películas de acción, suspenso y series policiales.'
    ),

    'TVN.cl': (
        'TVN',
        'General',
        'Programación TVN',
        'Noticias, matinales, teleseries y entretención.'
    ),

    'Canal13.cl': (
        'Canal 13',
        'General',
        'Programación Canal 13',
        'Noticieros, realitys y programas en vivo.'
    ),

    'Mega.cl': (
        'Mega',
        'General',
        'Programación Mega',
        'Teleseries nacionales, noticias y entretención.'
    ),

    'Chilevision.cl': (
        'Chilevisión',
        'General',
        'Programas de entretención, noticias y deportes.'
    ),

    'CHVNoticias.cl': (
        'CHV Noticias',
        'Noticias',
        'Noticias en Vivo',
        'Información continua las 24 horas.'
    ),

    'T13Noticias.cl': (
        'T13 En Vivo',
        'Noticias',
        'Noticias T13',
        'Actualidad y noticias nacionales e internacionales.'
    ),

    'ENTChannel.cl': (
        'ENT Channel',
        'Cine',
        'Selección de Cine 24/7',
        'Las mejores producciones cinematográficas.'
    ),

    'StudioUniversal.cl': (
        'Studio Universal',
        'Cine',
        'Cine Studio Universal',
        'Películas y producciones cinematográficas.'
    ),

    'TelemundoInternacional.ar': (
        'Telemundo Internacional',
        'Series',
        'Programación Telemundo',
        'Series, telenovelas y producciones.'
    ),

    'SONYMOVIES.uy': (
        'Sony Movies',
        'Cine',
        'Cine Sony Movies',
        'Películas de Hollywood y éxitos de taquilla.'
    ),

    'FilmAndArts.cl': (
        'Film & Arts',
        'Cultura',
        'Especiales Film & Arts',
        'Cine de autor, arte, música y espectáculos.'
    ),

    'USANetwork.bo': (
        'USA Network',
        'Series',
        'Programación USA Network',
        'Series exclusivas y cine de acción.'
    ),

    'AE.cl': (
        'A&E',
        'Series',
        'Especiales A&E',
        'Series de investigación, drama y acción.'
    ),

    'NickJr.ar': (
        'Nick Jr.',
        'Infantil',
        'Programación Nick Jr.',
        'Dibujos animados y contenidos educativos.'
    ),

    'FOODNETWORK.uy': (
        'Food Network',
        'Cocina',
        'Gastronomía Internacional',
        'Programas de cocina y competencias culinarias.'
    ),

    'HGTV.ar': (
        'HGTV',
        'Hogar',
        'Hogar & Remodelación',
        'Diseño de interiores y remodelación de espacios.'
    ),

    'DiscoveryHomeAndHealth.cl': (
        'Discovery Home & Health',
        'Estilo de Vida',
        'Bienestar & Estilo',
        'Salud, hogar y estilo de vida.'
    ),

    'PASIONES.uy': (
        'Pasiones',
        'Telenovelas',
        'Novelas & Dramas',
        'Telenovelas internacionales y grandes historias.'
    ),

    'History2.cl1': (
        'History 2',
        'Documentales',
        'Programación History 2',
        'Documentales, historia y ciencia.'
    )
}


# ============================================================
# 🔧 NORMALIZAR CUALQUIER ZONA HORARIA A UTC
# ============================================================

def normalizar_a_utc(time_str, horas_desfase=0):

    if not time_str or len(time_str) < 14:
        return time_str, None

    try:

        clean = time_str.strip()

        dt_part = clean[:14]
        tz_part = clean[14:].strip()

        dt = datetime.datetime.strptime(
            dt_part,
            "%Y%m%d%H%M%S"
        )

        if tz_part and (
            tz_part.startswith('+')
            or tz_part.startswith('-')
        ):

            sign = (
                1
                if tz_part[0] == '+'
                else -1
            )

            tz_hours = int(
                tz_part[1:3]
            )

            tz_mins = (
                int(tz_part[3:5])
                if len(tz_part) >= 5
                else 0
            )

            offset_delta = datetime.timedelta(
                hours=sign * tz_hours,
                minutes=sign * tz_mins
            )

            dt_utc = dt - offset_delta

        else:

            dt_utc = dt

        if horas_desfase != 0:

            dt_utc += datetime.timedelta(
                hours=horas_desfase
            )

        str_utc = (
            dt_utc.strftime(
                "%Y%m%d%H%M%S"
            )
            + " +0000"
        )

        return str_utc, dt_utc

    except Exception:

        return time_str, None


# ============================================================
# 🌐 DESCARGAR XML
# ============================================================

def descargar_xml(url):

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    req = urllib.request.Request(
        url,
        headers=headers
    )

    with urllib.request.urlopen(
        req,
        timeout=30
    ) as response:

        content = response.read()

    if (
        url.endswith('.gz')
        or content[:2] == b'\x1f\x8b'
    ):

        content = gzip.decompress(
            content
        )

    return ET.fromstring(
        content
    )


# ============================================================
# 🧹 LIMPIAR TEXTO HTML
# ============================================================

def limpiar_texto_html(texto):

    if not texto:
        return ''

    texto = re.sub(
        r'\s+',
        ' ',
        texto
    )

    return texto.strip()


# ============================================================
# 🐱 NUEVO PARSER GATOTV
#
# ESTA ES LA PARTE IMPORTANTE.
#
# En lugar de construir una lista de celdas y luego intentar
# relacionarlas, buscamos directamente CADA <tr>.
#
# Dentro de cada fila buscamos:
#
#   1) las horas <time datetime="HH:MM">
#   2) el bloque tbl_EPG_ProgramsColumn
#   3) el título del enlace
#   4) el texto descriptivo fuera del enlace
#
# La imagen se IGNORA completamente.
#
# Ejemplo real:
#
# <tr>
#   <td>16:14</td>
#   <td>17:49</td>
#   <td><img ...></td>
#   <td class="pelicula">
#       <a ... title="Shrek Tercero">
#           <span>Shrek Tercero</span>
#       </a>
#       Tras la muerte...
#   </td>
# </tr>
#
# Resultado:
#
# inicio = 16:14
# fin = 17:49
# titulo = Shrek Tercero
# descripcion = Tras la muerte...
#
# ============================================================

class GatoTVRowParser(HTMLParser):

    def __init__(self):

        super().__init__(
            convert_charrefs=True
        )

        self.rows = []

        self.in_tr = False

        self.in_time = False

        self.in_program_block = False

        self.in_title_link = False

        self.current_row_html_text = []

        self.current_times = []

        self.current_title = []

        self.current_description = []

        self.current_program_depth = 0

        self.current_title_depth = 0

    def handle_starttag(
        self,
        tag,
        attrs
    ):

        tag = tag.lower()

        attrs_dict = dict(attrs)

        if tag == 'tr':

            if self.in_tr:

                self._cerrar_fila()

            self.in_tr = True

            self.current_times = []

            self.current_title = []

            self.current_description = []

            self.current_program_depth = 0

            self.current_title_depth = 0

        if not self.in_tr:
            return

        if tag == 'time':

            datetime_attr = attrs_dict.get(
                'datetime',
                ''
            ).strip()

            if re.match(
                r'^\d{1,2}:\d{2}$',
                datetime_attr
            ):

                self.current_times.append(
                    datetime_attr
                )

            self.in_time = True

        if tag == 'div':

            class_name = attrs_dict.get(
                'class',
                ''
            )

            if (
                'tbl_EPG_ProgramsColumn'
                in class_name
            ):

                self.in_program_block = True

                self.current_program_depth = 1

        elif self.in_program_block:

            self.current_program_depth += 1

        if (
            self.in_program_block
            and tag == 'a'
        ):

            title_attr = attrs_dict.get(
                'title',
                ''
            ).strip()

            if title_attr:

                self.current_title = [
                    title_attr
                ]

            self.in_title_link = True

            self.current_title_depth = 1

        elif self.in_title_link:

            self.current_title_depth += 1

    def handle_data(
        self,
        data
    ):

        if not self.in_tr:
            return

        texto = limpiar_texto_html(
            data
        )

        if not texto:
            return

        if self.in_title_link:

            # Si ya tenemos title="" del enlace,
            # no necesitamos duplicar el texto del span.
            #
            # Solo lo usamos si el atributo title no existía.

            if not self.current_title:

                self.current_title.append(
                    texto
                )

        elif self.in_program_block:

            self.current_description.append(
                texto
            )

    def handle_endtag(
        self,
        tag
    ):

        tag = tag.lower()

        if tag == 'time':

            self.in_time = False

        if tag == 'a' and self.in_title_link:

            self.in_title_link = False

            self.current_title_depth = 0

        elif (
            self.in_title_link
            and self.current_title_depth > 0
        ):

            self.current_title_depth -= 1

        if (
            tag == 'div'
            and self.in_program_block
        ):

            if self.current_program_depth > 1:

                self.current_program_depth -= 1

            else:

                self.in_program_block = False

                self.current_program_depth = 0

        if tag == 'tr':

            self._cerrar_fila()

    def _cerrar_fila(self):

        if not self.in_tr:
            return

        horas = self.current_times[:]

        titulo = limpiar_texto_html(
            " ".join(
                self.current_title
            )
        )

        descripcion = limpiar_texto_html(
            " ".join(
                self.current_description
            )
        )

        # ----------------------------------------------------
        # Eliminar el título de la descripción si por la
        # estructura HTML quedó repetido.
        # ----------------------------------------------------

        if titulo and descripcion:

            if descripcion.lower().startswith(
                titulo.lower()
            ):

                descripcion = (
                    descripcion[
                        len(titulo):
                    ].strip(
                        " :-"
                    )
                )

        if horas and titulo:

            self.rows.append(
                {
                    'times': horas,
                    'title': titulo,
                    'description': descripcion
                }
            )

        self.in_tr = False

        self.current_times = []

        self.current_title = []

        self.current_description = []

        self.current_program_depth = 0

        self.current_title_depth = 0

        self.in_program_block = False

        self.in_title_link = False


# ============================================================
# 🕐 CONVERTIR HORA DE GATOTV A DATETIME
# ============================================================

def convertir_hora_gatotv(
    hora,
    fecha
):

    if not hora:
        return None

    hora = " ".join(
        hora.strip().split()
    )

    formatos = [
        "%H:%M",
        "%I:%M %p",
        "%I:%M%p",
    ]

    dt_hora = None

    for formato in formatos:

        try:

            dt_hora = datetime.datetime.strptime(
                hora,
                formato
            ).time()

            break

        except ValueError:

            continue

    if dt_hora is None:
        return None

    return datetime.datetime.combine(
        fecha,
        dt_hora,
        tzinfo=ZONA_HORARIA_GATOTV
    )


# ============================================================
# 🐱 EXTRAER PROGRAMACIÓN DE GATOTV
# ============================================================

def extraer_programacion_gatotv(
    url,
    channel_id,
    fecha
):

    print(
        f"    → GatoTV: "
        f"{channel_id} | {fecha}"
    )

    headers = {
        'User-Agent': (
            'Mozilla/5.0 '
            '(Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 '
            '(KHTML, like Gecko) '
            'Chrome/120.0 Safari/537.36'
        ),
        'Accept-Language':
            'es-ES,es;q=0.9,en;q=0.8'
    }

    req = urllib.request.Request(
        url,
        headers=headers
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
            f"       ❌ No se pudo descargar "
            f"GatoTV: {e}"
        )

        return []

    print(
        f"       HTML recibido: "
        f"{len(html):,} caracteres"
    )

    # --------------------------------------------------------
    # Contadores de diagnóstico.
    # --------------------------------------------------------

    total_times = len(
        re.findall(
            r'<time\b',
            html,
            flags=re.IGNORECASE
        )
    )

    total_program_blocks = len(
        re.findall(
            r'tbl_EPG_ProgramsColumn',
            html,
            flags=re.IGNORECASE
        )
    )

    total_tr = len(
        re.findall(
            r'<tr\b',
            html,
            flags=re.IGNORECASE
        )
    )

    print(
        f"       <tr> encontrados: "
        f"{total_tr}"
    )

    print(
        f"       <time> encontrados: "
        f"{total_times}"
    )

    print(
        f"       Bloques "
        f"tbl_EPG_ProgramsColumn: "
        f"{total_program_blocks}"
    )

    # --------------------------------------------------------
    # PARSER
    # --------------------------------------------------------

    parser = GatoTVRowParser()

    try:

        parser.feed(html)

    except Exception as e:

        print(
            f"       ❌ Error leyendo HTML "
            f"de GatoTV: {e}"
        )

        return []

    filas = parser.rows

    print(
        f"       Filas de programación "
        f"reconocidas: {len(filas)}"
    )

    if not filas:

        print(
            "       ⚠️ GatoTV entregó HTML, "
            "pero no se reconocieron filas "
            "con horario + título."
        )

        return []

    # --------------------------------------------------------
    # Mostrar los programas encontrados ANTES de convertirlos.
    #
    # Esto nos permite comprobar que título y horario
    # pertenecen a la misma fila.
    # --------------------------------------------------------

    for indice, fila in enumerate(
        filas,
        start=1
    ):

        horas = fila.get(
            'times',
            []
        )

        titulo = fila.get(
            'title',
            ''
        )

        descripcion = fila.get(
            'description',
            ''
        )

        print(
            f"       🔎 Programa {indice}: "
            f"{titulo}"
        )

        print(
            f"          HORAS: "
            f"{' | '.join(horas)}"
        )

        if descripcion:

            print(
                f"          DESC: "
                f"{descripcion[:180]}"
            )

    programas = []

    # --------------------------------------------------------
    # Crear programas.
    #
    # Cada fila ya trae SUS propias horas.
    # No se mezclan horarios de otras filas.
    # --------------------------------------------------------

    for indice, fila in enumerate(
        filas,
        start=1
    ):

        horas = fila.get(
            'times',
            []
        )

        titulo = fila.get(
            'title',
            ''
        )

        descripcion = fila.get(
            'description',
            ''
        )

        # Necesitamos exactamente al menos dos horarios.

        if len(horas) < 2:

            print(
                f"       ⚠️ Programa {indice} "
                f"ignorado: no tiene dos horarios."
            )

            continue

        hora_inicio = horas[0]

        hora_fin = horas[1]

        if not titulo:

            continue

        # ----------------------------------------------------
        # Limpiar título.
        # ----------------------------------------------------

        titulo = limpiar_texto_html(
            titulo
        )

        # ----------------------------------------------------
        # Limpiar descripción.
        # ----------------------------------------------------

        descripcion = limpiar_texto_html(
            descripcion
        )

        # ----------------------------------------------------
        # Evitar duplicación.
        # ----------------------------------------------------

        if (
            descripcion.lower()
            == titulo.lower()
        ):

            descripcion = ''

        # ----------------------------------------------------
        # Convertir horas.
        # ----------------------------------------------------

        start_local = convertir_hora_gatotv(
            hora_inicio,
            fecha
        )

        stop_local = convertir_hora_gatotv(
            hora_fin,
            fecha
        )

        if not start_local or not stop_local:

            print(
                f"       ⚠️ Programa {indice} "
                f"ignorado por horario inválido."
            )

            continue

        # ----------------------------------------------------
        # Si termina después de medianoche.
        # ----------------------------------------------------

        if stop_local <= start_local:

            stop_local += datetime.timedelta(
                days=1
            )

        # ----------------------------------------------------
        # Convertir a UTC.
        # ----------------------------------------------------

        start_utc = start_local.astimezone(
            datetime.timezone.utc
        )

        stop_utc = stop_local.astimezone(
            datetime.timezone.utc
        )

        # ----------------------------------------------------
        # Desfase exclusivo GatoTV.
        # ----------------------------------------------------

        desfase = DESFASE_GATOTV.get(
            channel_id,
            0
        )

        if desfase != 0:

            diferencia = datetime.timedelta(
                hours=desfase
            )

            start_utc += diferencia

            stop_utc += diferencia

        # ----------------------------------------------------
        # Validación.
        # ----------------------------------------------------

        if stop_utc <= start_utc:

            continue

        duracion = (
            stop_utc - start_utc
        ).total_seconds()

        if duracion > (
            24 * 60 * 60
        ):

            continue

        # ----------------------------------------------------
        # Crear programme.
        # ----------------------------------------------------

        prog = ET.Element(
            'programme',
            {
                'start':
                    start_utc.strftime(
                        "%Y%m%d%H%M%S"
                    ) + " +0000",

                'stop':
                    stop_utc.strftime(
                        "%Y%m%d%H%M%S"
                    ) + " +0000",

                'channel':
                    channel_id
            }
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        title = ET.SubElement(
            prog,
            'title',
            lang='es'
        )

        title.text = titulo

        # ----------------------------------------------------
        # DESCRIPCIÓN
        # ----------------------------------------------------

        if descripcion:

            desc = ET.SubElement(
                prog,
                'desc',
                lang='es'
            )

            desc.text = descripcion

        programas.append(
            (
                prog,
                channel_id,
                start_utc.replace(
                    tzinfo=None
                ),
                stop_utc.replace(
                    tzinfo=None
                )
            )
        )

        if descripcion:

            print(
                f"       ✓ "
                f"{hora_inicio}-{hora_fin} "
                f"{titulo} | DESC: "
                f"{descripcion[:120]}"
            )

        else:

            print(
                f"       ✓ "
                f"{hora_inicio}-{hora_fin} "
                f"{titulo}"
            )

    print(
        f"       ✔ Programas encontrados: "
        f"{len(programas)}"
    )

    return programas


# ============================================================
# 🐱 OBTENER LOS 3 DÍAS DE GATOTV
# ============================================================

def cargar_gatotv(
    programas_lista,
    canales_dict
):

    print("")

    print(
        "3. Cargando programación "
        "desde GatoTV..."
    )

    print("")

    ahora_chile = datetime.datetime.now(
        ZONA_HORARIA_GATOTV
    )

    fecha_base = ahora_chile.date()

    total_programas = 0

    for channel_id, base_url in GATOTV_CANALES.items():

        programas_canal = []

        for dia in range(
            GATOTV_DIAS
        ):

            fecha = (
                fecha_base
                + datetime.timedelta(
                    days=dia
                )
            )

            url = (
                f"{base_url}/"
                f"{fecha.strftime('%Y-%m-%d')}"
            )

            programas = extraer_programacion_gatotv(
                url,
                channel_id,
                fecha
            )

            programas_canal.extend(
                programas
            )

        if not programas_canal:

            print(
                f"    ⚠️ GatoTV no entregó "
                f"programación para "
                f"{channel_id}. "
                f"Se conservarán otras fuentes."
            )

            continue

        # ----------------------------------------------------
        # Crear canal si todavía no existe.
        # ----------------------------------------------------

        if channel_id not in canales_dict:

            ch_elem = ET.Element(
                'channel',
                id=channel_id
            )

            dn_elem = ET.SubElement(
                ch_elem,
                'display-name'
            )

            dn_elem.text = channel_id

            canales_dict[
                channel_id
            ] = ch_elem

        # ----------------------------------------------------
        # GatoTV tiene prioridad sobre las fuentes públicas.
        #
        # Eliminamos únicamente los programas que choquen
        # con los horarios de GatoTV.
        # ----------------------------------------------------

        for (
            _,
            _,
            gatostart,
            gatostop
        ) in programas_canal:

            programas_lista[:] = [
                p
                for p in programas_lista
                if not (
                    p[1] == channel_id
                    and p[2] < gatostop
                    and p[3] > gatostart
                )
            ]

        programas_lista.extend(
            programas_canal
        )

        total_programas += len(
            programas_canal
        )

        print(
            f"    ✔ GatoTV integrado: "
            f"{channel_id} "
            f"({len(programas_canal)} "
            f"programas)"
        )

    print("")

    print(
        f" ✔ GatoTV finalizado. "
        f"Programas incorporados: "
        f"{total_programas}"
    )


# ============================================================
# 🧹 AGREGAR BLOQUE DE RESPALDO
# ============================================================

def agregar_bloque_respaldo(
    canales_dict,
    programas_lista,
    channel_id
):

    ch_name, categoria, titulo_prog, desc_prog = (
        DATOS_RESPALDO.get(
            channel_id,
            (
                channel_id,
                'Variado',
                'Programación General',
                'Transmisión continua.'
            )
        )
    )

    ch_elem = ET.Element(
        'channel',
        id=channel_id
    )

    dn_elem = ET.SubElement(
        ch_elem,
        'display-name'
    )

    dn_elem.text = ch_name

    canales_dict[
        channel_id
    ] = ch_elem

    ahora_utc = datetime.datetime.now(
        datetime.timezone.utc
    ).replace(
        tzinfo=None
    )

    inicio_base = (
        ahora_utc.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
        - datetime.timedelta(
            days=1
        )
    )

    for dia in range(4):

        for bloque in range(8):

            start_dt = (
                inicio_base
                + datetime.timedelta(
                    days=dia,
                    hours=bloque * 3
                )
            )

            stop_dt = (
                start_dt
                + datetime.timedelta(
                    hours=3
                )
            )

            prog = ET.Element(
                'programme',
                start=(
                    start_dt.strftime(
                        "%Y%m%d%H%M%S"
                    )
                    + " +0000"
                ),
                stop=(
                    stop_dt.strftime(
                        "%Y%m%d%H%M%S"
                    )
                    + " +0000"
                ),
                channel=channel_id
            )

            title = ET.SubElement(
                prog,
                'title',
                lang='es'
            )

            title.text = (
                f"{ch_name}: "
                f"{titulo_prog}"
            )

            desc = ET.SubElement(
                prog,
                'desc',
                lang='es'
            )

            desc.text = desc_prog

            category = ET.SubElement(
                prog,
                'category',
                lang='es'
            )

            category.text = categoria

            programas_lista.append(
                (
                    prog,
                    channel_id,
                    start_dt,
                    stop_dt
                )
            )


# ============================================================
# 🚀 PROCESO PRINCIPAL
# ============================================================

try:

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

    print(
        "1. Cargando fuentes públicas..."
    )

    for url in FUENTES_PUBLICAS:

        try:

            guiaroot = descargar_xml(
                url
            )

            for elem in guiaroot:

                if elem.tag == 'channel':

                    ch_id = elem.get(
                        'id'
                    )

                    target_id = MAPEO_IDS.get(
                        ch_id,
                        ch_id
                    )

                    if (
                        target_id in MIS_CANALES
                        and target_id
                        not in canales_dict
                    ):

                        elem.set(
                            'id',
                            target_id
                        )

                        canales_dict[
                            target_id
                        ] = elem

                elif elem.tag == 'programme':

                    ch_id = elem.get(
                        'channel'
                    )

                    target_id = MAPEO_IDS.get(
                        ch_id,
                        ch_id
                    )

                    if target_id in MIS_CANALES:

                        elem.set(
                            'channel',
                            target_id
                        )

                        horas = DESFASE_CANALES.get(
                            target_id,
                            0
                        )

                        start_str, st_dt = (
                            normalizar_a_utc(
                                elem.get(
                                    'start',
                                    ''
                                ),
                                horas
                            )
                        )

                        stop_str, sp_dt = (
                            normalizar_a_utc(
                                elem.get(
                                    'stop',
                                    ''
                                ),
                                horas
                            )
                        )

                        elem.set(
                            'start',
                            start_str
                        )

                        elem.set(
                            'stop',
                            stop_str
                        )

                        if st_dt and sp_dt:

                            programas_lista.append(
                                (
                                    elem,
                                    target_id,
                                    st_dt,
                                    sp_dt
                                )
                            )

            print(
                f" ✔ Cargada guía pública: "
                f"{url}"
            )

        except Exception as e:

            print(
                f" ❌ Error en {url}: {e}"
            )


    # ========================================================
    # 2. GATOTV
    #
    # Se carga DESPUÉS de las fuentes públicas.
    # ========================================================

    cargar_gatotv(
        programas_lista,
        canales_dict
    )


    # ========================================================
    # 3. TU GUÍA PROPIA
    #
    # TU GUIA SIGUE TENIENDO LA MAYOR PRIORIDAD.
    # ========================================================

    print("")

    print(
        "4. Aplicando tu guía propia "
        "(Sobreescribiendo conflictos)..."
    )

    try:

        guiaroot = descargar_xml(
            GUIA_PROPIA
        )

        for elem in guiaroot:

            if elem.tag == 'channel':

                ch_id = elem.get(
                    'id'
                )

                target_id = MAPEO_IDS.get(
                    ch_id,
                    ch_id
                )

                if (
                    target_id in MIS_CANALES
                    and target_id
                    not in canales_dict
                ):

                    elem.set(
                        'id',
                        target_id
                    )

                    canales_dict[
                        target_id
                    ] = elem

            elif elem.tag == 'programme':

                ch_id = elem.get(
                    'channel'
                )

                target_id = MAPEO_IDS.get(
                    ch_id,
                    ch_id
                )

                if target_id in MIS_CANALES:

                    elem.set(
                        'channel',
                        target_id
                    )

                    horas = DESFASE_GUIA_PROPIA.get(
                        target_id,
                        0
                    )

                    start_str, st_dt = (
                        normalizar_a_utc(
                            elem.get(
                                'start',
                                ''
                            ),
                            horas
                        )
                    )

                    stop_str, sp_dt = (
                        normalizar_a_utc(
                            elem.get(
                                'stop',
                                ''
                            ),
                            horas
                        )
                    )

                    elem.set(
                        'start',
                        start_str
                    )

                    elem.set(
                        'stop',
                        stop_str
                    )

                    if st_dt and sp_dt:

                        programas_lista[:] = [
                            p
                            for p in programas_lista
                            if not (
                                p[1] == target_id
                                and p[2] < sp_dt
                                and p[3] > st_dt
                            )
                        ]

                        programas_lista.append(
                            (
                                elem,
                                target_id,
                                st_dt,
                                sp_dt
                            )
                        )

        print(
            f" ✔ Guía propia aplicada "
            f"con éxito: "
            f"{GUIA_PROPIA}"
        )

    except Exception as e:

        print(
            f" ❌ Error cargando tu guía "
            f"propia: {e}"
        )


    # ========================================================
    # 5. RESPALDOS
    # ========================================================

    print("")

    print(
        "5. Verificando respaldos para "
        "canales sin programación..."
    )

    for ch_id in MIS_CANALES:

        tiene_programas = any(
            p[1] == ch_id
            for p in programas_lista
        )

        if (
            ch_id not in canales_dict
            or not tiene_programas
        ):

            agregar_bloque_respaldo(
                canales_dict,
                programas_lista,
                ch_id
            )

            print(
                f" ✔ Respaldo creado para: "
                f"{ch_id}"
            )


    # ========================================================
    # 6. ENSAMBLAJE FINAL
    # ========================================================

    print("")

    print(
        "6. Generando epg_final.xml..."
    )

    for ch_id in sorted(
        canales_dict.keys()
    ):

        root_final.append(
            canales_dict[ch_id]
        )


    # --------------------------------------------------------
    # Orden cronológico.
    # --------------------------------------------------------

    programas_lista.sort(
        key=lambda x: x[2]
    )

    for p in programas_lista:

        root_final.append(
            p[0]
        )


    # ========================================================
    # 7. GUARDAR XML
    # ========================================================

    tree = ET.ElementTree(
        root_final
    )

    ET.indent(
        tree,
        space="  ",
        level=0
    )

    tree.write(
        "epg_final.xml",
        encoding="utf-8",
        xml_declaration=True
    )


    print("")

    print(
        "=========================================="
    )

    print(
        "🎉 ¡PROCESO FINALIZADO CON ÉXITO!"
    )

    print(
        "=========================================="
    )

    print("")

    print(
        "EPG generado correctamente: "
        "epg_final.xml"
    )


except Exception as e:

    print("")

    print(
        "=========================================="
    )

    print(
        "❌ ERROR FATAL"
    )

    print(
        "=========================================="
    )

    print(e)

    print("")

    raise
