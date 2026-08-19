import datetime
import gzip
import urllib.request
import xml.etree.ElementTree as ET

# Dirección directa y estable para la lista de Chile en iptv-epg
URL_EPG_BASE = "https://iptv-epg.com/files/epg/cl.xml"

# Listas de canales con desfase de horario
CANALES_MAS_1h = []  # Lista vacía por ahora
CANALES_MENOS_1h = []  # Lista vacía por ahora


def ajustar_hora(time_str, horas_diferencia):
    """Ajusta la hora en formato XMLTV (YYYYMMDDHHMMSS +0000)"""
    try:
        dt = datetime.datetime.strptime(time_str[:14], "%Y%m%d%H%M%S")
        dt += datetime.timedelta(hours=horas_diferencia)
        return dt.strftime("%Y%m%d%H%M%S") + time_str[14:]
    except Exception:
        return time_str


print(f"Descargando EPG desde: {URL_EPG_BASE}")
try:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    req = urllib.request.Request(URL_EPG_BASE, headers=headers)

    with urllib.request.urlopen(req) as response:
        content = response.read()

    # Si el archivo viene comprimido en formato gzip (.gz)
    if URL_EPG_BASE.endswith(".gz") or content[:2] == b"\x1f\x8b":
        content = gzip.decompress(content)

    root = ET.fromstring(content)

    print("Procesando canales y programas...")
    for programme in root.findall("programme"):
        channel_id = programme.get("channel")

        if channel_id in CANALES_MAS_1h:
            if "start" in programme.attrib:
                programme.set(
                    "start", ajustar_hora(programme.get("start"), 1)
                )
            if "stop" in programme.attrib:
                programme.set("stop", ajustar_hora(programme.get("stop"), 1))

        elif channel_id in CANALES_MENOS_1h:
            if "start" in programme.attrib:
                programme.set(
                    "start", ajustar_hora(programme.get("start"), -1)
                )
            if "stop" in programme.attrib:
                programme.set("stop", ajustar_hora(programme.get("stop"), -1))

    # Crear y guardar el archivo final
    tree = ET.ElementTree(root)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡Archivo epg_final.xml creado exitosamente!")

except Exception as e:
    print(f"Error crítico al procesar la EPG: {e}")
    # Forzar error si no se pudo crear para evitar el fallo en git
    raise e
