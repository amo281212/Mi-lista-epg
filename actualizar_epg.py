import datetime
import gzip
import urllib.request
import html
import xml.etree.ElementTree as ET
import re


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
    'HBO.Plus.cl',
    'StudioUniversal.ar',
    'SONYMOVIES.uy',
    'Sony.cl',
    'UniversalCinema.cl',
    'Space.cl',
    'TNT.cl',
    'FX.cl',
    'WarnerChannel.cl',
    'StarChannel.cl',
    'UniversalTV.cl',
    'AXN.cl',
    'AE.cl',
    'UniversalCrime.cl',
    'TNTSeries.cl',
    'DramasCoreanos.cl',
    'DramasCoreanosTeen.cl',
    'USANetwork.bo',
    'DIRECTVSports.cl',
    'ESPN.cl',
    'ESPN2.cl',
    'ESPN3.cl',
    'ESPN4.cl',
    'ESPN5.cl',
    'ESPN6.cl',
    'ESPN7.cl',
    'ESPNPremium.cl',
    'TNTSportsPremium.cl',
    'TNTSports.cl',
    'TyCSports.cl',
    'ComedyCentral.cl',
    'E_Entertainment.cl',
    'DiscoveryHomeAndHealth.cl',
    'HGTV.ar',
    'ElGourmet.cl',
    'FOODNETWORK.uy',
    'History.cl',
    'History2.cl1',
    'InvestigationDiscovery.cl',
    'NationalGeographic.cl',
    'AnimalPlanet.cl',
    'Discovery.cl',
    'DiscoveryScience.cl',
    'DiscoveryTheater.cl',
    'DiscoveryTurbo.cl',
    'DiscoveryWorld.cl',
    'CartoonNetwork.cl',
    'DiscoveryKids.cl',
    'DisneyChannel.cl',
    'DisneyJunior.cl',
    'NickJr.bo',
    'Nick.cl',
    'Tooncast.cl',
    'LasEstrellas.cl',
    'PASIONES.uy',
    'TelemundoInternacional.ar',
    'TNTNovelas.cl',
    'TLNovelas.cl',
    'EnlaceTBN.cl',
    'LaRed.cl',
    'NTV.cl',
    'CNNChile.cl',
    'CHVNoticias.cl',
    'T13Noticias.cl',
    '24Horas.cl',
}


# ============================================================
# 🔄 MAPEO COMPLETO
#
# Aquí puedes seguir agregando todos los IDs diferentes
# que encuentres en las fuentes públicas o en tu guía.
#
# IMPORTANTE:
# Este mapeo NO depende de la fuente.
# Solo sirve para convertir el ID encontrado
# al ID limpio que usas en MIS_CANALES.
# ============================================================

MAPEO_IDS = {
    '0104': 'TVN.cl',
    '0105': 'Mega.cl',
    '0106': 'Chilevision.cl',
    '0107': 'Canal13.cl',
    '1836': 'AMC.cl',
    '0846': 'Cinecanal.cl',
    '1840': 'Cinemax.cl',
    '1821': 'Golden.cl',
    '0823': 'GoldenEdge.cl',
    '2813': 'HBO.cl',
    '1814': 'HBO2.cl',
    '0816': 'HBOFamily.cl',
    '0819': 'HBOPop.cl',
    '0820': 'HBOXtreme.cl',
    '0815': 'HBO.Plus.cl',
    '2834': 'StudioUniversal.ar',
    '0810': 'SONYMOVIES.uy',
    '2810': 'Sony.cl',
    '1841': 'UniversalCinema.cl',
    '0829': 'Space.cl',
    '2805': 'TNT.cl',
    '0811': 'FX.cl',
    '0832': 'WarnerChannel.cl',
    '3801': 'StarChannel.cl',
    '1804': 'UniversalTV.cl',
    '1847': 'AXN.cl',
    '0808': 'AE.cl',
    '0842': 'UniversalCrime.cl',
    '0833': 'TNTSeries.cl',
    '6185a9a88b2ce30007de5128': 'DramasCoreanos.cl',
    '6661d5424b10960008599fa3': 'DramasCoreanosTeen.cl',
    '0809': 'USANetwork.bo',
    '0411': 'ESPN.cl',
    '0412': 'ESPN2.cl',
    '2413': 'ESPN3.cl',
    '0414': 'ESPN4.cl',
    '0415': 'ESPN5.cl',
    '0416': 'ESPN6.cl',
    '0417': 'ESPN7.cl',
    '0418': 'ESPNPremium.cl',
    '0401': 'TNTSportsPremium.cl',
    '0403': 'TNTSports.cl',
    '1409': 'TyCSports.cl',
    '0812': 'ComedyCentral.cl',
    '0606': 'E_Entertainment.cl',
    '0601': 'DiscoveryHomeAndHealth.cl',
    '0610': 'ElGourmet.cl',
    '0706': 'History.cl',
    '0707': 'History2.cl1',
    '0604': 'InvestigationDiscovery.cl',
    '0702': 'NationalGeographic.cl',
    '0705': 'AnimalPlanet.cl',
    '0701': 'Discovery.cl',
    '0703': 'DiscoveryScience.cl',
    '0704': 'DiscoveryTheater.cl',
    '0602': 'DiscoveryTurbo.cl',
    '0607': 'DiscoveryWorld.cl',
    '0305': 'CartoonNetwork.cl',
    '0323': 'DiscoveryKids.cl',
    '0304': 'DisneyChannel.cl',
    '0311': 'DisneyJunior.cl',
    '0307': 'NickJr.bo',
    '0303': 'Nick.cl',
    '0308': 'Tooncast.cl',
    '0837': 'LasEstrellas.cl',
    '0613': 'PASIONES.uy',
    '0615': 'TelemundoInternacional.ar',
    '0835': 'TNTNovelas.cl',
    '0611': 'TLNovelas.cl',
    '0623': 'EnlaceTBN.cl',
    '0102': 'LaRed.cl',
    '0202': 'CNNChile.cl',
    'Canal.24.Horas.(Chile).cl': '24Horas.cl',
}


# ============================================================
# 🌐 FUENTES PÚBLICAS DISPONIBLES
#
# Puedes agregar o quitar enlaces de esta lista.
#
# OJO:
# Esta lista solo contiene las fuentes disponibles.
# La elección de qué fuente usa cada canal se hace
# más abajo en FUENTE_POR_CANAL.
# ============================================================

FUENTES_PUBLICAS = [
    "https://iptv-epg.org/files/epg-cl.xml",
    "https://iptv-epg.org/files/epg-ar.xml",
    "https://iptv-epg.org/files/epg-ec.xml",
    "https://iptv-epg.org/files/epg-co.xml",
    "https://iptv-epg.org/files/epg-uy.xml",
    "https://iptv-epg.org/files/epg-bo.xml",
    "https://epg.lat/files/cl.xml.gz",
    "https://epg.lat/files/mx.xml.gz",
    "https://epg.lat/files/uy.xml.gz",
    "https://epg.lat/files/cr.xml.gz",
    "https://epg.lat/files/co.xml.gz",
    "https://epg.lat/files/ar.xml.gz",
    "https://raw.githubusercontent.com/siulemorales-arch/latam-sports-epg/refs/heads/main/epg.xml",
    "https://github.com/matthuisman/i.mjh.nz/raw/master/PlutoTV/mx.xml.gz",
    "https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml",
]


# ============================================================
# 🎯 FUENTE EPG ELEGIDA PARA CADA CANAL
#
# ============================================================
#
# AQUÍ ES DONDE VAS A TRABAJAR.
#
# Cada canal puede tener UN SOLO enlace.
#
# Ejemplo:
#
# 'HBO.cl': 'https://epg.lat/files/mx.xml.gz',
#
# Eso significa:
#
# HBO.cl
#   ↓
# SOLO se buscará en epg.lat/files/mx.xml.gz
#
# Si otro de los XML públicos también tiene HBO,
# NO se utilizará.
#
# ------------------------------------------------------------
#
# Si todavía no sabes qué fuente usar para un canal,
# puedes dejarlo como None temporalmente.
#
# Ejemplo:
#
# 'HBO.cl': None,
#
# Con None, ese canal podrá buscarse en todas las
# fuentes públicas disponibles.
#
# PERO cuando ya tengas elegido el enlace,
# reemplaza None por el enlace.
#
# ============================================================

FUENTE_POR_CANAL = {

    'TVN.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Mega.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Chilevision.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Canal13.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'AMC.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Cinecanal.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Cinemax.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Golden.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'GoldenEdge.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'HBO.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'HBO2.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'HBOFamily.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'HBOPop.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'HBOXtreme.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'HBO.Plus.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'StudioUniversal.ar': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'SONYMOVIES.uy': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Sony.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'UniversalCinema.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Space.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TNT.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'FX.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'WarnerChannel.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'StarChannel.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'UniversalTV.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'AXN.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'AE.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'UniversalCrime.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TNTSeries.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DramasCoreanos.cl': 'https://github.com/matthuisman/i.mjh.nz/raw/master/PlutoTV/mx.xml.gz',
    'DramasCoreanosTeen.cl': 'https://github.com/matthuisman/i.mjh.nz/raw/master/PlutoTV/mx.xml.gz',
    'USANetwork.bo': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ComedyCentral.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'E_Entertainment.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DiscoveryHomeAndHealth.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DIRECTVSports.cl': None,
    'ESPN.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ESPN2.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ESPN3.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ESPN4.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ESPN5.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ESPN6.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ESPN7.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'ESPNPremium.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TNTSportsPremium.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TNTSports.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TyCSports.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DiscoveryHomeAndHealth.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'HGTV.ar': None,
    'ElGourmet.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'FOODNETWORK.uy': None,
    'History.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'History2.cl1': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'InvestigationDiscovery.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'NationalGeographic.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'AnimalPlanet.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Discovery.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DiscoveryScience.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DiscoveryTheater.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DiscoveryTurbo.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DiscoveryWorld.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'CartoonNetwork.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DiscoveryKids.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DisneyChannel.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'DisneyJunior.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'NickJr.bo': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Nick.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'Tooncast.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'LasEstrellas.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'PASIONES.uy': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TelemundoInternacional.ar': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TNTNovelas.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'TLNovelas.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'EnlaceTBN.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'LaRed.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    'NTV.cl': None,
    'CNNChile.cl': 'https://raw.githubusercontent.com/Puticastillo/EPGCL/refs/heads/main/smithers/guia-de-programacion.xml',
    '24Horas.cl': None,
}


# ============================================================
# 🌐 CANALES QUE SÍ PUEDEN USAR FUENTES PÚBLICAS
# ============================================================

CANALES_FUENTES_PUBLICAS = {
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
    'HBO.Plus.cl',
    'StudioUniversal.ar',
    'SONYMOVIES.uy',
    'Sony.cl',
    'UniversalCinema.cl',
    'Space.cl',
    'TNT.cl',
    'FX.cl',
    'WarnerChannel.cl',
    'StarChannel.cl',
    'UniversalTV.cl',
    'AXN.cl',
    'AE.cl',
    'UniversalCrime.cl',
    'TNTSeries.cl',
    'DramasCoreanos.cl',
    'DramasCoreanosTeen.cl',
    'USANetwork.bo',
    'DIRECTVSports.cl',
    'ESPN.cl',
    'ESPN2.cl',
    'ESPN3.cl',
    'ESPN4.cl',
    'ESPN5.cl',
    'ESPN6.cl',
    'ESPN7.cl',
    'ESPNPremium.cl',
    'TNTSportsPremium.cl',
    'TNTSports.cl',
    'TyCSports.cl',
    'ComedyCentral.cl',
    'E_Entertainment.cl',
    'DiscoveryHomeAndHealth.cl',
    'HGTV.ar',
    'ElGourmet.cl',
    'FOODNETWORK.uy',
    'History.cl',
    'History2.cl1',
    'InvestigationDiscovery.cl',
    'NationalGeographic.cl',
    'AnimalPlanet.cl',
    'Discovery.cl',
    'DiscoveryScience.cl',
    'DiscoveryTheater.cl',
    'DiscoveryTurbo.cl',
    'DiscoveryWorld.cl',
    'CartoonNetwork.cl',
    'DiscoveryKids.cl',
    'DisneyChannel.cl',
    'DisneyJunior.cl',
    'NickJr.bo',
    'Nick.cl',
    'Tooncast.cl',
    'LasEstrellas.cl',
    'PASIONES.uy',
    'TelemundoInternacional.ar',
    'TNTNovelas.cl',
    'TLNovelas.cl',
    'EnlaceTBN.cl',
    'LaRed.cl',
    'NTV.cl',
    'CNNChile.cl',
    '24Horas.cl',
}


# ============================================================
# 📝 TU GUÍA MANUAL
#
# Esta fuente tiene prioridad sobre las fuentes públicas.
# ============================================================

GUIA_PROPIA = "https://raw.githubusercontent.com/amo281212/epg_que_actualizo.xml/refs/heads/main/guia.xml"

# ============================================================
# 🕒 DESFASES PARA LAS FUENTES PÚBLICAS
#
# Estos desfases SOLO afectan a las fuentes públicas.
# ============================================================

DESFASE_CANALES = {
    'TVN.cl': 0,
    'Mega.cl': 0,
    'Chilevision.cl': 0,
    'Canal13.cl': 0,
    'AMC.cl': -3,
    'Cinecanal.cl': 0,
    'Cinemax.cl': -1,
    'Golden.cl': -1,
    'GoldenEdge.cl': 1,
    'HBO.cl': 0,
    'HBO2.cl': 0,
    'HBOFamily.cl': 0,
    'HBOPop.cl': 0,
    'HBOXtreme.cl': 0,
    'HBO.Plus.cl': 0,
    'SONYMOVIES.uy': 3,
    'Sony.cl': -1,
    'Space.cl': 0,
    'StudioUniversal.ar': -2,
    'TNT.cl': 1,
    'TNTSeries.cl': 0,
    'StarChannel.cl': 1,
    'UniversalTV.cl': 0,
    'UniversalCinema.cl': -3,
    'UniversalCrime.cl': 2,
    'WarnerChannel.cl': 0,
    'FX.cl': -3,
    'AXN.cl': 0,
    'AE.cl': 0,
    'DramasCoreanos.cl': 0,
    'DramasCoreanosTeen.cl': 0,
    'USANetwork.bo': 0,
    'DIRECTVSports.cl': -1,
    'ESPN.cl': 0,
    'ESPN2.cl': 2,
    'ESPN3.cl': 0,
    'ESPN4.cl': 0,
    'ESPN5.cl': 0,
    'ESPN6.cl': 0,
    'ESPN7.cl': 0,
    'ESPNPremium.cl': 0,
    'TyCSports.cl': 0,
    'ComedyCentral.cl': 0,
    'E_Entertainment.cl': 0,
    'DiscoveryHomeAndHealth.cl': 0,
    'HGTV.ar': 0,
    'ElGourmet.cl': 0,
    'FOODNETWORK.uy': 0,
    'History.cl': 0,
    'History2.cl1': 0,
    'InvestigationDiscovery.cl': 0,
    'NationalGeographic.cl': 0,
    'AnimalPlanet.cl': 0,
    'Discovery.cl': 0,
    'DiscoveryScience.cl': 0,
    'DiscoveryTheater.cl': 0,
    'DiscoveryTurbo.cl': 0,
    'DiscoveryWorld.cl': 0,
    'CartoonNetwork.cl': 0,
    'DiscoveryKids.cl': 0,
    'DisneyChannel.cl': 0,
    'DisneyJunior.cl': 0,
    'NickJr.bo': 0,
    'Nick.cl': 0,
    'Tooncast.cl': 0,
    'LasEstrellas.cl': 0,
    'PASIONES.uy': 0,
    'TelemundoInternacional.ar': 0,
    'TNTNovelas.cl': 1,
    'TLNovelas.cl': 0,
    'EnlaceTBN.cl': 0,
    'LaRed.cl': 0,
    'CNNChile.cl': 0,
    '24Horas.cl': 0,
}


# ============================================================
# 🕒 DESFASES EXCLUSIVOS PARA TU GUÍA PROPIA
#
# Estos desfases SOLO afectan a tu guia.xml.
# ============================================================

DESFASE_GUIA_PROPIA = {
    # 'GoldenEdge.cl': -2,
}


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
        'Programación Chilevisión',
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

def normalizar_a_utc(
    time_str,
    horas_desfase=0
):

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

    ahora_utc = datetime.datetime.utcnow()

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
    #
    # IMPORTANTE:
    #
    # Cada canal que tenga una URL definida en
    # FUENTE_POR_CANAL SOLO puede recibir programas
    # desde ESA URL.
    #
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
                        target_id
                        not in CANALES_FUENTES_PUBLICAS
                    ):
                        continue

                    fuente_asignada = FUENTE_POR_CANAL.get(
                        target_id
                    )

                    # Si el canal tiene una fuente específica,
                    # ignoramos completamente cualquier otra.
                    if (
                        fuente_asignada is not None
                        and fuente_asignada != url
                    ):
                        continue

                    if target_id not in canales_dict:

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

                    if (
                        target_id
                        not in CANALES_FUENTES_PUBLICAS
                    ):
                        continue

                    fuente_asignada = FUENTE_POR_CANAL.get(
                        target_id
                    )

                    # 🔒 AQUÍ ESTÁ EL CAMBIO IMPORTANTE:
                    #
                    # Si HBO.cl tiene asignado un XML,
                    # ningún otro XML puede aportar programas
                    # para HBO.cl.

                    if (
                        fuente_asignada is not None
                        and fuente_asignada != url
                    ):
                        continue

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
    # 2. TU GUÍA PROPIA
    #
    # La guía propia se aplica DESPUÉS de las fuentes
    # públicas y elimina cualquier programa que choque
    # con ella.
    # ========================================================

    print("")

    print(
        "2. Aplicando tu guía propia "
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
    # 3. RESPALDOS
    # ========================================================

    print("")

    print(
        "3. Verificando respaldos para "
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

    programas_lista.sort(
        key=lambda x: x[2]
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
