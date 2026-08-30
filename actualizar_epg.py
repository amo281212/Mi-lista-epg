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

            sign = 1 if tz_part[0] == '+' else -1

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
# 🐱 PARSER HTML DE GATOTV
#
# No usamos BeautifulSoup ni ninguna librería externa.
# Python estándar se encarga de leer las filas de la tabla.
# ============================================================

class GatoTVParser(HTMLParser):

    def __init__(self):

        super().__init__(
            convert_charrefs=True
        )

        self.rows = []

        self.in_tr = False
        self.in_td = False
        self.in_th = False
        self.in_a = False

        self.current_row = []
        self.current_cell = []

        self.current_anchor = []
        self.anchor_text = None

    def handle_starttag(
        self,
        tag,
        attrs
    ):

        tag = tag.lower()

        if tag == 'tr':

            self.in_tr = True
            self.current_row = []

        elif (
            self.in_tr
            and tag in ('td', 'th')
        ):

            self.in_td = tag == 'td'
            self.in_th = tag == 'th'

            self.current_cell = []
            self.current_anchor = []
            self.anchor_text = None

        elif (
            (self.in_td or self.in_th)
            and tag == 'a'
        ):

            self.in_a = True
            self.current_anchor = []

    def handle_data(self, data):

        if not (
            self.in_td
            or self.in_th
        ):

            return

        texto = data.strip()

        if not texto:
            return

        self.current_cell.append(
            texto
        )

        if self.in_a:

            self.current_anchor.append(
                texto
            )

    def handle_endtag(self, tag):

        tag = tag.lower()

        if tag == 'a' and self.in_a:

            self.in_a = False

            self.anchor_text = (
                " ".join(
                    self.current_anchor
                ).strip()
            )

        elif (
            tag in ('td', 'th')
            and (
                self.in_td
                or self.in_th
            )
        ):

            texto = " ".join(
                self.current_cell
            ).strip()

            # ====================================================
            # 🔧 CAMBIO:
            #
            # Conservamos TODO el contenido de la celda.
            # Así no perdemos información adicional de GatoTV.
            # ====================================================

            self.current_row.append(
                texto
            )

            self.in_td = False
            self.in_th = False

            self.current_cell = []
            self.current_anchor = []
            self.anchor_text = None

        elif (
            tag == 'tr'
            and self.in_tr
        ):

            if self.current_row:

                self.rows.append(
                    self.current_row
                )

            self.current_row = []
            self.in_tr = False


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
# 🐱 EXTRAER PROGRAMACIÓN DE UNA PÁGINA GATOTV
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
        'Accept-Language': (
            'es-ES,es;q=0.9,en;q=0.8'
        )
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

    parser = GatoTVParser()

    try:

        parser.feed(html)

    except Exception as e:

        print(
            f"       ❌ Error leyendo HTML "
            f"de GatoTV: {e}"
        )

        return []

    programas = []

    for row in parser.rows:

        if len(row) < 3:
            continue

        hora_inicio = row[0].strip()
        hora_fin = row[1].strip()
        titulo_completo = row[2].strip()

        # Las filas reales de programación
        # comienzan con una hora.
        if not re.match(
            r'^\d{1,2}:\d{2}',
            hora_inicio
        ):

            continue

        if not re.match(
            r'^\d{1,2}:\d{2}',
            hora_fin
        ):

            continue

        if not titulo_completo:
            continue

        # ====================================================
        # 🔧 SEPARAR TÍTULO Y TEXTO ADICIONAL
        #
        # GatoTV puede colocar dentro de la misma celda:
        #
        #   Título
        #   Episodio / número / descripción
        #
        # El primer bloque se conserva como título y el resto
        # pasa a la descripción.
        # ====================================================

        partes_titulo = [
            parte.strip()
            for parte in re.split(
                r'\n+',
                titulo_completo
            )
            if parte.strip()
        ]

        if len(partes_titulo) > 1:

            titulo = partes_titulo[0]

            descripcion = " ".join(
                partes_titulo[1:]
            ).strip()

        else:

            titulo = titulo_completo
            descripcion = ""

            partes_extra = [
                parte.strip()
                for parte in re.split(
                    r'\s{2,}|\t+',
                    titulo_completo
                )
                if parte.strip()
            ]

            if len(partes_extra) > 1:

                titulo = partes_extra[0]

                descripcion = " ".join(
                    partes_extra[1:]
                ).strip()

        if not titulo:
            continue

        start_local = convertir_hora_gatotv(
            hora_inicio,
            fecha
        )

        stop_local = convertir_hora_gatotv(
            hora_fin,
            fecha
        )

        if not start_local or not stop_local:
            continue

        # Si termina después de medianoche,
        # la hora final pertenece al día siguiente.
        if stop_local <= start_local:

            stop_local += datetime.timedelta(
                days=1
            )

        # Convertimos a UTC.
        start_utc = start_local.astimezone(
            datetime.timezone.utc
        )

        stop_utc = stop_local.astimezone(
            datetime.timezone.utc
        )

        # Aplicar desfase EXCLUSIVO de GatoTV.
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

        # Evitar programas absurdos o dañados.
        if stop_utc <= start_utc:
            continue

        if (
            stop_utc - start_utc
        ).total_seconds() > 24 * 60 * 60:

            continue

        prog = ET.Element(
            'programme',
            {
                'start': (
                    start_utc.strftime(
                        "%Y%m%d%H%M%S"
                    )
                    + " +0000"
                ),
                'stop': (
                    stop_utc.strftime(
                        "%Y%m%d%H%M%S"
                    )
                    + " +0000"
                ),
                'channel': channel_id
            }
        )

        title = ET.SubElement(
            prog,
            'title',
            lang='es'
        )

        title.text = titulo

        # ====================================================
        # 🔧 NUEVO:
        #
        # La información adicional de GatoTV queda en <desc>.
        # ====================================================

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

    print(
        f"       ✔ Programas encontrados: "
        f"{len(programas)}"
    )

    return programas


# ============================================================
# 🔥 GATOTV TIENE PRIORIDAD ABSOLUTA
#
# Esta función elimina los programas de otras fuentes que
# se crucen con un programa REAL de GatoTV.
#
# NO crea respaldos.
# NO inventa programación.
#
# Si otra fuente tiene:
#
# 05:30 ───────────── 06:30
#
# y GatoTV tiene:
#
# 05:00 ─────── 06:00
#
# el resultado será:
#
# 05:00 ─────── 06:00  GatoTV
# 06:00 ─────── 06:30  programa anterior
#
# De esta manera nunca quedan dos programas ocupando
# exactamente el mismo horario.
# ============================================================

def aplicar_gatotv_con_prioridad(
    programas_lista,
    programas_gatotv
):

    for gato_prog, channel_id, gato_start, gato_stop in programas_gatotv:

        nueva_lista = []

        for prog, ch_id, start, stop in programas_lista:

            # Si es otro canal, no tocamos nada.
            if ch_id != channel_id:

                nueva_lista.append(
                    (
                        prog,
                        ch_id,
                        start,
                        stop
                    )
                )

                continue

            # Si no existe solapamiento, conservamos el programa.
            if (
                stop <= gato_start
                or start >= gato_stop
            ):

                nueva_lista.append(
                    (
                        prog,
                        ch_id,
                        start,
                        stop
                    )
                )

                continue

            # ====================================================
            # 🔧 EXISTE SOLAPAMIENTO.
            #
            # GatoTV gana.
            #
            # Pero si el programa anterior sobresale por alguno
            # de los extremos, conservamos únicamente la parte
            # que NO pisa a GatoTV.
            # ====================================================

            # Parte anterior al inicio de GatoTV.
            if start < gato_start:

                parte_izquierda = copiar_programa_con_horario(
                    prog,
                    start,
                    min(stop, gato_start)
                )

                if parte_izquierda is not None:

                    nueva_lista.append(
                        (
                            parte_izquierda,
                            ch_id,
                            start,
                            min(stop, gato_start)
                        )
                    )

            # Parte posterior al final de GatoTV.
            if stop > gato_stop:

                parte_derecha = copiar_programa_con_horario(
                    prog,
                    max(start, gato_stop),
                    stop
                )

                if parte_derecha is not None:

                    nueva_lista.append(
                        (
                            parte_derecha,
                            ch_id,
                            max(start, gato_stop),
                            stop
                        )
                    )

        # Agregamos finalmente el programa real de GatoTV.
        nueva_lista.append(
            (
                gato_prog,
                channel_id,
                gato_start,
                gato_stop
            )
        )

        programas_lista[:] = nueva_lista


# ============================================================
# ✂️ COPIAR UN PROGRAMA CONSERVANDO SU INFORMACIÓN
#
# Se utiliza únicamente cuando un programa de otra fuente
# sobresale por fuera del horario de GatoTV.
#
# Así no perdemos una parte válida que no estaba cubierta
# por GatoTV.
# ============================================================

def copiar_programa_con_horario(
    original,
    nuevo_start,
    nuevo_stop
):

    if nuevo_stop <= nuevo_start:
        return None

    nuevo = ET.fromstring(
        ET.tostring(
            original,
            encoding='unicode'
        )
    )

    nuevo.set(
        'start',
        nuevo_start.strftime(
            "%Y%m%d%H%M%S"
        ) + " +0000"
    )

    nuevo.set(
        'stop',
        nuevo_stop.strftime(
            "%Y%m%d%H%M%S"
        ) + " +0000"
    )

    return nuevo


# ============================================================
# 🐱 OBTENER LOS 3 DÍAS DE GATOTV
# ============================================================

def cargar_gatotv(
    programas_lista,
    canales_dict
):

    print("")
    print(
        "3. Cargando programación desde GatoTV..."
    )
    print("")

    # Usamos la fecha de Chile,
    # no la fecha UTC del servidor de GitHub.
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
                f"programación para {channel_id}."
            )

            continue

        # Si el canal no existía todavía,
        # creamos su elemento.
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

        # ====================================================
        # 🔥 GATOTV TIENE PRIORIDAD MÁXIMA.
        #
        # Aquí ya NO simplemente agregamos GatoTV al XML.
        #
        # Primero eliminamos/reducimos los programas anteriores
        # que estén ocupando los mismos horarios.
        # ====================================================

        aplicar_gatotv_con_prioridad(
            programas_lista,
            programas_canal
        )

        total_programas += len(
            programas_canal
        )

        print(
            f"    ✔ GatoTV integrado con "
            f"PRIORIDAD MÁXIMA: "
            f"{channel_id} "
            f"({len(programas_canal)} programas)"
        )

    print("")

    print(
        f" ✔ GatoTV finalizado. "
        f"Programas incorporados: "
        f"{total_programas}"
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
                        and target_id not in canales_dict
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

                        start_str, st_dt = normalizar_a_utc(
                            elem.get(
                                'start',
                                ''
                            ),
                            horas
                        )

                        stop_str, sp_dt = normalizar_a_utc(
                            elem.get(
                                'stop',
                                ''
                            ),
                            horas
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
                f" ❌ Error en {url}: "
                f"{e}"
            )


    # ========================================================
    # 2. TU GUÍA PROPIA
    #
    # Esta fuente se aplica antes de GatoTV.
    #
    # GatoTV tendrá la última palabra cuando sus horarios
    # se superpongan con esta guía.
    # ========================================================

    print("")

    print(
        "2. Aplicando tu guía propia..."
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
                    and target_id not in canales_dict
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

                    start_str, st_dt = normalizar_a_utc(
                        elem.get(
                            'start',
                            ''
                        ),
                        horas
                    )

                    stop_str, sp_dt = normalizar_a_utc(
                        elem.get(
                            'stop',
                            ''
                        ),
                        horas
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

                        # La guía propia reemplaza los
                        # conflictos que ya existían.
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
            f" ✔ Guía propia aplicada con éxito: "
            f"{GUIA_PROPIA}"
        )

    except Exception as e:

        print(
            f" ❌ Error cargando tu guía propia: "
            f"{e}"
        )


    # ========================================================
    # 3. GATOTV
    #
    # 🔥 IMPORTANTE:
    #
    # GatoTV se ejecuta DESPUÉS de todas las demás fuentes.
    #
    # Por lo tanto, si GatoTV dice que HBO tiene un programa
    # de 05:00 a 06:00, cualquier programa de otra fuente que
    # ocupe ese horario será eliminado de ese tramo.
    #
    # NO se crea ningún respaldo.
    # ========================================================

    cargar_gatotv(
        programas_lista,
        canales_dict
    )


    # ========================================================
    # 4. ENSAMBLAJE FINAL
    # ========================================================

    print("")

    print(
        "4. Generando epg_final.xml..."
    )

    for ch_id in sorted(
        canales_dict.keys()
    ):

        root_final.append(
            canales_dict[ch_id]
        )


    # Orden cronológico de todos los programas.
    programas_lista.sort(
        key=lambda x: (
            x[1],
            x[2]
        )
    )

    for p in programas_lista:

        root_final.append(
            p[0]
        )


    # ========================================================
    # 5. GUARDAR XML
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
