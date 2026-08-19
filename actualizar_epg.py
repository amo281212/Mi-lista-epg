import datetime
import xml.etree.ElementTree as ET
import urllib.request
import gzip

# URL de tu lista base de iptv-epg (puedes cambiarla si usas una URL específica)
URL_EPG_BASE = "https://iptv-epg.com/cl.xml"  # Ejemplo base para Chile

# Canales que tienen desfase de +1 hora o -1 hora
# Escribe aquí los IDs de los canales desfasados cuando los tengamos identificados
CANALES_MAS_1h = []  # Ejemplo: ['Espn.cl', 'FoxSports.cl']
CANALES_MENOS_1h = []

def ajustar_hora(time_str, horas_diferencia):
    """Ajusta la hora en formato XMLTV (YYYYMMDDHHMMSS +0000)"""
    try:
        # Tomamos los primeros 14 caracteres (YYYYMMDDHHMMSS)
        dt = datetime.datetime.strptime(time_str[:14], "%Y%m%d%H%M%S")
        dt += datetime.timedelta(hours=horas_diferencia)
        # Reconstruimos la cadena manteniendo el offset original
        return dt.strftime("%Y%m%d%H%M%S") + time_str[14:]
    except Exception:
        return time_str

print("Descargando EPG base...")
try:
    req = urllib.request.Request(
        URL_EPG_BASE, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req) as response:
        content = response.read()

    # Si viene comprimido en .gz lo descomprimimos
    if URL_EPG_BASE.endswith(".gz"):
        content = gzip.decompress(content)

    root = ET.fromstring(content)

    print("Procesando programas y horarios...")
    for programme in root.findall("programme"):
        channel_id = programme.get("channel")

        # Corrección de horario si el canal está en la lista de desfasados
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

    # Guardar el archivo corregido
    tree = ET.ElementTree(root)
    tree.write("epg_final.xml", encoding="utf-8", xml_declaration=True)
    print("¡EPG procesada y guardada con éxito como epg_final.xml!")

except Exception as e:
    print(f"Error procesando la EPG: {e}")
