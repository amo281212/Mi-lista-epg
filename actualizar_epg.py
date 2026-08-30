import datetime
import gzip
import urllib.request
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from zoneinfo import ZoneInfo


# ============================================================
# 🎯 TUS CANALES
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
# 🔄 MAPEO DE IDS
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
# 🌐 FUENTES PÚBLICAS
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
# 📝 TU GUÍA PROPIA
# ============================================================

GUIA_PROPIA = (
    "https://raw.githubusercontent.com/amo281212/"
    "epg_que_actualizo.xml/refs/heads/main/guia.xml"
)


# ============================================================
# 🕒 DESFASES DE LAS FUENTES PÚBLICAS
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
# 🕒 DESFASE DE TU GUÍA PROPIA
# ============================================================

DESFASE_GUIA_PROPIA = {
    'GoldenEdge.cl': -2,
}


# ============================================================
# 🐱 GATOTV
# ============================================================

GATOTV_CANALES = {

    'TVN.cl':
        'https://www.gatotv.com/canal/tvn_chile',

    'Mega.cl':
        'https://www.gatotv.com/canal/mega_chile',

    'Chilevision.cl':
        'https://www.gatotv.com/canal/chilevision',

    'Canal13.cl':
        'https://www.gatotv.com/canal/13_de_chile',

    'AMC.cl':
        'https://www.gatotv.com/canal/amc_mexico',

    'Cinecanal.cl':
        'https://www.gatotv.com/canal/cinecanal_chile',

    'Cinemax.cl':
        'https://www.gatotv.com/canal/cinemax_chile',

    'Golden.cl':
        'https://www.gatotv.com/canal/golden_chile',

    'GoldenEdge.cl':
        'https://www.gatotv.com/canal/golden_edge',

    'HBO.cl':
        'https://www.gatotv.com/canal/hbo_chile',

    'HBO2.cl':
        'https://www.gatotv.com/canal/hbo_2_latinoamerica',

    'HBOFamily.cl':
        'https://www.gatotv.com/canal/hbo_family_latinoamerica',

    'HBOPop.cl':
        'https://www.gatotv.com/canal/hbo_pop',

    'HBOXtreme.cl':
        'https://www.gatotv.com/canal/hbo_xtreme',

    'ENTChannel.cl':
        'https://www.gatotv.com/canal/ent_channel',

    'SONYMOVIES.uy':
        'https://www.gatotv.com/canal/sony_movies_chile',

    'Sony.cl':
        'https://www.gatotv.com/canal/sony_centro',

    'Space.cl':
        'https://www.gatotv.com/canal/space_chile',

    'StudioUniversal.ar':
        'https://www.gatotv.com/canal/studio_universal_panregional',

    'TNT.cl':
        'https://www.gatotv.com/canal/tnt_chile',

    'TNTSeries.cl':
        'https://www.gatotv.com/canal/tnt_series',

    'StarChannel.cl':
        'https://www.gatotv.com/canal/star_channel_chile',

    'UniversalTV.cl':
        'https://www.gatotv.com/canal/universal_tv_panregional',

    'WarnerChannel.cl':
        'https://www.gatotv.com/canal/warner_tv_chile',

    'USANetwork.bo':
        'https://www.gatotv.com/canal/usa_network_chile',

    'AXN.cl':
        'https://www.gatotv.com/canal/axn_chile',

    'AE.cl':
        'https://www.gatotv.com/canal/a_y_e_chile',

    'FX.cl':
        'https://www.gatotv.com/canal/fx_chile',

    'FilmAndArts.cl':
        'https://www.gatotv.com/canal/film_and_arts',

    'ComedyCentral.cl':
        'https://www.gatotv.com/canal/comedy_central_bolivia',

    'E_Entertainment.cl':
        'https://www.gatotv.com/canal/e_entertainment_television_chile',

    'ESPN.cl':
        'https://www.gatotv.com/canal/espn_chile',

    'ESPN2.cl':
        'https://www.gatotv.com/canal/espn_2_colombia',

    'ESPN3.cl':
        'https://www.gatotv.com/canal/espn_3_chile',

    'ESPN4.cl':
        'https://www.gatotv.com/canal/espn_4_sur',

    'ESPN5.cl':
        'https://www.gatotv.com/canal/espn_5_chile',

    'ESPN6.cl':
        'https://www.gatotv.com/canal/espn_6_chile',

    'ESPN7.cl':
        'https://www.gatotv.com/canal/espn_7_chile',

    'DIRECTVSports.cl':
        'https://www.gatotv.com/canal/directv_sports_chile',

    'TNTSportsPremium.cl':
        'https://www.gatotv.com/canal/tnt_sports_premium_chile',

    'TyCSports.cl':
        'https://www.gatotv.com/canal/tyc_sports',

    'CartoonNetwork.cl':
        'https://www.gatotv.com/canal/cartoon_network_chile',

    'DiscoveryKids.cl':
        'https://www.gatotv.com/canal/discovery_kids_chile',

    'DisneyChannel.cl':
        'https://www.gatotv.com/canal/disney_channel_chile',

    'DisneyJunior.cl':
        'https://www.gatotv.com/canal/disney_junior_chile',

    'NickJr.bo':
        'https://www.gatotv.com/canal/nick_junior_latinoamerica',

    'Nick.cl':
        'https://www.gatotv.com/canal/nickelodeon_chile',

    'Tooncast.cl':
        'https://www.gatotv.com/canal/tooncast',

    'AnimalPlanet.cl':
        'https://www.gatotv.com/canal/animal_planet_chile',

    'Discovery.cl':
        'https://www.gatotv.com/canal/discovery_channel_chile',

    'DiscoveryScience.cl':
        'https://www.gatotv.com/canal/discovery_science_latinoamerica',

    'DiscoveryTheater.cl':
        'https://www.gatotv.com/canal/discovery_theater_latinoamerica',

    'DiscoveryTurbo.cl':
        'https://www.gatotv.com/canal/discovery_turbo_latinoamerica',

    'DiscoveryWorld.cl':
        'https://www.gatotv.com/canal/discovery_world_latinoamerica',

    'ElGourmet.cl':
        'https://www.gatotv.com/canal/elgourmet',

    'FOODNETWORK.uy':
        'https://www.gatotv.com/canal/food_network_latinoamerica',

    'HGTV.ar':
        'https://www.gatotv.com/canal/hgtv_latinoamerica',

    'DiscoveryHomeAndHealth.cl':
        'https://www.gatotv.com/canal/discovery_home_and_health_chile',

    'History.cl':
        'https://www.gatotv.com/canal/history_chile',

    'History2.cl1':
        'https://www.gatotv.com/canal/history_2_chile',

    'InvestigationDiscovery.cl':
        'https://www.gatotv.com/canal/investigation_discovery_panregional',

    'NationalGeographic.cl':
        'https://www.gatotv.com/canal/national_geographic_chile',

    'LasEstrellas.cl':
        'https://www.gatotv.com/canal/las_estrellas_chile',

    'PASIONES.uy':
        'https://www.gatotv.com/canal/pasiones_latinoamerica',

    'TelemundoInternacional.ar':
        'https://www.gatotv.com/canal/telemundo_chile',

    'TLNovelas.cl':
        'https://www.gatotv.com/canal/tlnovelas_chile',

    'EnlaceTBN.cl':
        'https://www.gatotv.com/canal/enlace',

    'CNNChile.cl':
        'https://www.gatotv.com/canal/cnn_chile',

    'CHVNoticias.cl':
        'https://www.gatotv.com/canal/chv_noticias',

    'T13Noticias.cl':
        'https://www.gatotv.com/canal/t13',

    '24Horas.cl':
        'https://www.gatotv.com/canal/24_horas_chile',
}


# ============================================================
# ⚙️ CONFIGURACIÓN GATOTV
# ============================================================

GATOTV_DIAS = 3

ZONA_CHILE = ZoneInfo(
    "America/Santiago"
)


# ============================================================
# 🔧 NORMALIZAR A UTC
# ============================================================

def normalizar_utc(
    time_str,
    horas_desfase=0
):

    if (
        not time_str
        or len(time_str.strip()) < 14
    ):

        return time_str, None

    try:

        clean = time_str.strip()

        dt_part = clean[:14]

        tz_part = clean[14:].strip()

        dt = datetime.datetime.strptime(
            dt_part,
            "%Y%m%d%H%M%S"
        )

        if (
            tz_part
            and tz_part[0] in "+-"
        ):

            signo = (
                1
                if tz_part[0] == "+"
                else -1
            )

            horas = int(
                tz_part[1:3]
            )

            minutos = 0

            if len(tz_part) >= 5:

                minutos = int(
                    tz_part[3:5]
                )

            offset = datetime.timedelta(
                hours=signo * horas,
                minutes=signo * minutos
            )

            dt -= offset

        if horas_desfase:

            dt += datetime.timedelta(
                hours=horas_desfase
            )

        resultado = (
            dt.strftime(
                "%Y%m%d%H%M%S"
            )
            + " +0000"
        )

        return resultado, dt

    except Exception:

        return time_str, None


# ============================================================
# 🌐 DESCARGAR XML
# ============================================================

def descargar_xml(url):

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(
        req,
        timeout=30
    ) as response:

        contenido = response.read()

    if (
        contenido[:2] == b"\x1f\x8b"
        or url.endswith(".gz")
    ):

        contenido = gzip.decompress(
            contenido
        )

    return ET.fromstring(
        contenido
    )


# ============================================================
# 🧹 LIMPIAR TEXTO
# ============================================================

def limpiar(texto):

    if not texto:
        return ""

    return re.sub(
        r"\s+",
        " ",
        texto
    ).strip()


# ============================================================
# 🐱 PARSER DE GATOTV
#
# IMPORTANTE:
#
# GatoTV organiza la programación en filas:
#
# HORA INICIO | HORA FIN | PROGRAMA
#
# No dependemos de que exista <a>.
# ============================================================

class GatoParser(
    HTMLParser
):

    def __init__(self):

        super().__init__(
            convert_charrefs=True
        )

        self.rows = []

        self.en_tr = False

        self.en_celda = False

        self.fila = []

        self.celda = []

    def handle_starttag(
        self,
        tag,
        attrs
    ):

        tag = tag.lower()

        if tag == "tr":

            self.en_tr = True

            self.fila = []

        elif (
            self.en_tr
            and tag in (
                "td",
                "th"
            )
        ):

            self.en_celda = True

            self.celda = []

    def handle_data(
        self,
        data
    ):

        if not self.en_celda:
            return

        texto = limpiar(
            data
        )

        if texto:

            self.celda.append(
                texto
            )

    def handle_endtag(
        self,
        tag
    ):

        tag = tag.lower()

        if (
            tag in (
                "td",
                "th"
            )
            and self.en_celda
        ):

            texto = limpiar(
                " ".join(
                    self.celda
                )
            )

            self.fila.append(
                texto
            )

            self.celda = []

            self.en_celda = False

        elif (
            tag == "tr"
            and self.en_tr
        ):

            if self.fila:

                self.rows.append(
                    self.fila
                )

            self.fila = []

            self.en_tr = False


# ============================================================
# 🕐 PARSEAR HORA
# ============================================================

def parsear_hora(
    texto
):

    texto = limpiar(
        texto
    )

    formatos = [
        "%H:%M",
        "%I:%M %p",
        "%I:%M%p"
    ]

    for formato in formatos:

        try:

            return datetime.datetime.strptime(
                texto,
                formato
            ).time()

        except ValueError:

            pass

    return None


# ============================================================
# 🐱 EXTRAER PROGRAMACIÓN DE GATOTV
# ============================================================

def extraer_gatotv(
    base_url,
    channel_id,
    fecha
):

    url = (
        base_url
        + "/"
        + fecha.strftime(
            "%Y-%m-%d"
        )
    )

    print(
        f"      → {channel_id} "
        f"{fecha}"
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36",

            "Accept":
                "text/html,"
                "application/xhtml+xml",

            "Accept-Language":
                "es-CL,es;q=0.9,en;q=0.8"
        }
    )

    try:

        with urllib.request.urlopen(
            req,
            timeout=30
        ) as response:

            html = response.read().decode(
                "utf-8",
                errors="replace"
            )

    except Exception as e:

        print(
            f"         ❌ Error: {e}"
        )

        return []

    parser = GatoParser()

    try:

        parser.feed(
            html
        )

    except Exception as e:

        print(
            f"         ❌ Error parser: {e}"
        )

        return []

    resultados = []

    for fila in parser.rows:

        if len(fila) < 3:
            continue

        inicio_txt = limpiar(
            fila[0]
        )

        fin_txt = limpiar(
            fila[1]
        )

        titulo = limpiar(
            fila[2]
        )

        # ----------------------------------------------------
        # Validar horas
        # ----------------------------------------------------

        if not re.match(
            r"^\d{1,2}:\d{2}(?:\s*[AP]M)?$",
            inicio_txt,
            re.IGNORECASE
        ):

            continue

        if not re.match(
            r"^\d{1,2}:\d{2}(?:\s*[AP]M)?$",
            fin_txt,
            re.IGNORECASE
        ):

            continue

        if not titulo:
            continue

        hora_inicio = parsear_hora(
            inicio_txt
        )

        hora_fin = parsear_hora(
            fin_txt
        )

        if (
            hora_inicio is None
            or hora_fin is None
        ):

            continue

        # ----------------------------------------------------
        # Crear horario local Chile
        # ----------------------------------------------------

        inicio_local = datetime.datetime.combine(
            fecha,
            hora_inicio,
            tzinfo=ZONA_CHILE
        )

        fin_local = datetime.datetime.combine(
            fecha,
            hora_fin,
            tzinfo=ZONA_CHILE
        )

        # Cruza medianoche.

        if fin_local <= inicio_local:

            fin_local += datetime.timedelta(
                days=1
            )

        # ----------------------------------------------------
        # Convertir UTC
        # ----------------------------------------------------

        inicio_utc = inicio_local.astimezone(
            datetime.timezone.utc
        )

        fin_utc = fin_local.astimezone(
            datetime.timezone.utc
        )

        # ----------------------------------------------------
        # Desfase GatoTV
        # ----------------------------------------------------

        desfase = DESFASE_GATOTV.get(
            channel_id,
            0
        )

        if desfase:

            delta = datetime.timedelta(
                hours=desfase
            )

            inicio_utc += delta

            fin_utc += delta

        # ----------------------------------------------------
        # Validaciones
        # ----------------------------------------------------

        if fin_utc <= inicio_utc:
            continue

        duracion = (
            fin_utc - inicio_utc
        ).total_seconds()

        if duracion > 86400:
            continue

        # ----------------------------------------------------
        # Crear XMLTV
        # ----------------------------------------------------

        programa = ET.Element(
            "programme",
            {
                "start":
                    inicio_utc.strftime(
                        "%Y%m%d%H%M%S"
                    )
                    + " +0000",

                "stop":
                    fin_utc.strftime(
                        "%Y%m%d%H%M%S"
                    )
                    + " +0000",

                "channel":
                    channel_id
            }
        )

        title = ET.SubElement(
            programa,
            "title",
            {
                "lang": "es"
            }
        )

        title.text = titulo

        resultados.append(
            (
                programa,
                channel_id,
                inicio_utc.replace(
                    tzinfo=None
                ),
                fin_utc.replace(
                    tzinfo=None
                )
            )
        )

        print(
            f"         "
            f"{inicio_txt} - "
            f"{fin_txt} → "
            f"{titulo}"
        )

    print(
        f"         ✔ "
        f"{len(resultados)} programas"
    )

    return resultados


# ============================================================
# 🐱 CARGAR GATOTV
# ============================================================

def cargar_gatotv(
    programas,
    canales
):

    print("")
    print(
        "3. OBTENIENDO PROGRAMACIÓN REAL "
        "DE GATOTV"
    )
    print("")

    fecha_base = datetime.datetime.now(
        ZONA_CHILE
    ).date()

    total = 0

    for (
        channel_id,
        base_url
    ) in GATOTV_CANALES.items():

        canal_programas = []

        for dia in range(
            GATOTV_DIAS
        ):

            fecha = (
                fecha_base
                + datetime.timedelta(
                    days=dia
                )
            )

            datos = extraer_gatotv(
                base_url,
                channel_id,
                fecha
            )

            canal_programas.extend(
                datos
            )

        if not canal_programas:

            print(
                f"   ⚠️ "
                f"GatoTV sin datos: "
                f"{channel_id}"
            )

            continue

        # ----------------------------------------------------
        # GATOTV TIENE PRIORIDAD
        #
        # Eliminamos cualquier programa anterior
        # que se cruce con un programa real de GatoTV.
        # ----------------------------------------------------

        for (
            _,
            _,
            inicio,
            fin
        ) in canal_programas:

            programas[:] = [
                p
                for p in programas
                if not (
                    p[1] == channel_id
                    and p[2] < fin
                    and p[3] > inicio
                )
            ]

        programas.extend(
            canal_programas
        )

        total += len(
            canal_programas
        )

        print(
            f"   ✔ {channel_id}: "
            f"{len(canal_programas)} "
            f"programas reales"
        )

    print("")
    print(
        f"✔ GATOTV: "
        f"{total} programas incorporados"
    )


# ============================================================
# 🚀 PROCESO PRINCIPAL
# ============================================================

try:

    root_final = ET.Element(
        "tv",
        {
            "generator-info-name":
                "CustomEPGGenerator",

            "generator-info-url":
                "https://github.com"
        }
    )

    canales = {}

    programas = []


    # ========================================================
    # 1. FUENTES PÚBLICAS
    # ========================================================

    print(
        "1. Cargando fuentes públicas..."
    )

    for url in FUENTES_PUBLICAS:

        try:

            raiz = descargar_xml(
                url
            )

            for elem in raiz:

                if elem.tag == "channel":

                    ch_id = elem.get(
                        "id"
                    )

                    target = MAPEO_IDS.get(
                        ch_id,
                        ch_id
                    )

                    if (
                        target in MIS_CANALES
                        and target not in canales
                    ):

                        elem.set(
                            "id",
                            target
                        )

                        canales[
                            target
                        ] = elem

                elif elem.tag == "programme":

                    ch_id = elem.get(
                        "channel"
                    )

                    target = MAPEO_IDS.get(
                        ch_id,
                        ch_id
                    )

                    if target not in MIS_CANALES:
                        continue

                    elem.set(
                        "channel",
                        target
                    )

                    desfase = DESFASE_CANALES.get(
                        target,
                        0
                    )

                    start_str, start_dt = (
                        normalizar_utc(
                            elem.get(
                                "start",
                                ""
                            ),
                            desfase
                        )
                    )

                    stop_str, stop_dt = (
                        normalizar_utc(
                            elem.get(
                                "stop",
                                ""
                            ),
                            desfase
                        )
                    )

                    elem.set(
                        "start",
                        start_str
                    )

                    elem.set(
                        "stop",
                        stop_str
                    )

                    if (
                        start_dt
                        and stop_dt
                    ):

                        programas.append(
                            (
                                elem,
                                target,
                                start_dt,
                                stop_dt
                            )
                        )

            print(
                f" ✔ Fuente cargada: "
                f"{url}"
            )

        except Exception as e:

            print(
                f" ❌ Error en fuente: "
                f"{url}"
            )

            print(
                f"    {e}"
            )


    # ========================================================
    # 2. GATOTV
    # ========================================================

    cargar_gatotv(
        programas,
        canales
    )


    # ========================================================
    # 3. GUÍA PROPIA
    # ========================================================

    print("")
    print(
        "4. Aplicando guía propia..."
    )

    try:

        raiz = descargar_xml(
            GUIA_PROPIA
        )

        for elem in raiz:

            if elem.tag == "channel":

                ch_id = elem.get(
                    "id"
                )

                target = MAPEO_IDS.get(
                    ch_id,
                    ch_id
                )

                if (
                    target in MIS_CANALES
                    and target not in canales
                ):

                    elem.set(
                        "id",
                        target
                    )

                    canales[
                        target
                    ] = elem

            elif elem.tag == "programme":

                ch_id = elem.get(
                    "channel"
                )

                target = MAPEO_IDS.get(
                    ch_id,
                    ch_id
                )

                if target not in MIS_CANALES:
                    continue

                elem.set(
                    "channel",
                    target
                )

                desfase = DESFASE_GUIA_PROPIA.get(
                    target,
                    0
                )

                start_str, start_dt = (
                    normalizar_utc(
                        elem.get(
                            "start",
                            ""
                        ),
                        desfase
                    )
                )

                stop_str, stop_dt = (
                    normalizar_utc(
                        elem.get(
                            "stop",
                            ""
                        ),
                        desfase
                    )
                )

                elem.set(
                    "start",
                    start_str
                )

                elem.set(
                    "stop",
                    stop_str
                )

                if (
                    start_dt
                    and stop_dt
                ):

                    programas[:] = [
                        p
                        for p in programas
                        if not (
                            p[1] == target
                            and p[2] < stop_dt
                            and p[3] > start_dt
                        )
                    ]

                    programas.append(
                        (
                            elem,
                            target,
                            start_dt,
                            stop_dt
                        )
                    )

        print(
            " ✔ Guía propia aplicada"
        )

    except Exception as e:

        print(
            f" ❌ Error guía propia: "
            f"{e}"
        )


    # ========================================================
    # 4. CREAR CANALES FALTANTES
    #
    # SOLO crea el encabezado <channel>.
    #
    # NO crea programación falsa.
    # ========================================================

    for ch_id in MIS_CANALES:

        if ch_id not in canales:

            canal = ET.Element(
                "channel",
                {
                    "id": ch_id
                }
            )

            nombre = ET.SubElement(
                canal,
                "display-name"
            )

            nombre.text = ch_id

            canales[
                ch_id
            ] = canal


    # ========================================================
    # 5. ELIMINAR PROGRAMAS DUPLICADOS
    # ========================================================

    programas_unicos = {}

    for (
        elem,
        channel_id,
        start,
        stop
    ) in programas:

        clave = (
            channel_id,
            start,
            stop
        )

        programas_unicos[
            clave
        ] = (
            elem,
            channel_id,
            start,
            stop
        )

    programas = list(
        programas_unicos.values()
    )


    # ========================================================
    # 6. ORDENAR PROGRAMACIÓN
    # ========================================================

    programas.sort(
        key=lambda x: (
            x[1],
            x[2]
        )
    )


    # ========================================================
    # 7. ENSAMBLAJE FINAL
    # ========================================================

    print("")
    print(
        "5. Generando epg_final.xml..."
    )

    for ch_id in sorted(
        canales.keys()
    ):

        root_final.append(
            canales[
                ch_id
            ]
        )

    for (
        elem,
        channel_id,
        start,
        stop
    ) in programas:

        root_final.append(
            elem
        )


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


    # ========================================================
    # 🎉 FINAL
    # ========================================================

    print("")
    print(
        "=========================================="
    )

    print(
        "🎉 EPG GENERADO CORRECTAMENTE"
    )

    print(
        "=========================================="
    )

    print("")

    print(
        "Archivo: epg_final.xml"
    )

    print(
        f"Programas totales: "
        f"{len(programas)}"
    )

    print("")


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

    print("")

    print(
        repr(e)
    )

    print("")

    raise
