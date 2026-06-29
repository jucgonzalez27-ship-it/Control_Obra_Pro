"""Creación y consultas principales del modelo de datos V0.1."""

from pathlib import Path
from contextlib import closing, contextmanager
import sqlite3

RUTA_DB_PREDETERMINADA = Path(__file__).resolve().parent.parent / "obra_v01.db"

PARTIDAS = (
    "Tabiquería",
    "Yeso / enlucido",
    "Preparación base",
    "Pavimento",
    "Porcelanato muro",
    "Porcelanato piso",
    "Fragüe",
    "Pintura",
    "Cornisa",
    "Ventanas",
    "Puerta",
    "Muro",
    "Cielo",
    "Muebles",
    "Vanitorio",
    "Grifería",
    "Tina",
    "Receptáculo",
    "Mampara",
    "Artefactos",
    "Extractor de aire",
    "Instalaciones",
    "Equipamiento",
    "Limpieza final",
)

TIPOS_PROBLEMA = (
    ("Falta material", 1),
    ("Falta mano de obra", 0),
    ("Observación grave", 1),
    ("Retrabajo pendiente", 1),
    ("Instalación incompleta", 1),
    ("No funciona", 1),
    ("Otro", 0),
)

RECINTOS = (
    "Living comedor",
    "Sala estar",
    "Logia",
    "Dormitorio principal",
    "Dormitorio 1",
    "Dormitorio 2",
    "Baño principal",
    "Baño 1",
    "Baño 2",
    "Walking closet",
    "Terraza principal",
    "Terraza 1",
)

ETAPAS_DEPARTAMENTO = (
    "obra_gruesa",
    "tabiqueria",
    "yeso_enlucidos",
    "pavimentos",
    "pintura",
    "muebles_artefactos",
    "terminacion_fina",
    "preentrega",
    "entregado",
)

ESTADOS_OPERATIVOS = (
    "sin_revisar",
    "en_proceso",
    "observado",
    "bloqueado",
    "liberable",
    "verificado",
)

ESPECIALIDAD_PREDETERMINADA = "Terminaciones Generales"

ESPECIALIDADES_V1 = (
    "Pintura",
    "CerÃ¡micos",
    "Piso Flotante",
    "Guardapolvos",
    "Cornisas y Junquillos",
    "Puertas",
    "Muebles",
    "Cubiertas",
    "Vidrios y Barandas",
    "Electricidad",
    "Sanitario",
    "ClimatizaciÃ³n",
    "Limpieza",
    ESPECIALIDAD_PREDETERMINADA,
)

ESPECIALIDAD_POR_PARTIDA = {
    "TabiquerÃ­a": ESPECIALIDAD_PREDETERMINADA,
    "Tabique": ESPECIALIDAD_PREDETERMINADA,
    "Yeso / enlucido": "Pintura",
    "Empaste": "Pintura",
    "Enlucido": "Pintura",
    "Aparejo": "Pintura",
    "PreparaciÃ³n base": "Pintura",
    "Primera mano de pintura": "Pintura",
    "Mano final de pintura": "Pintura",
    "Pintura": "Pintura",
    "Muro": "Pintura",
    "Cielo": "Pintura",
    "Textura": "Pintura",
    "Textura terraza": "Pintura",
    "CerÃ¡mico muro": "CerÃ¡micos",
    "CerÃ¡mico piso": "CerÃ¡micos",
    "CerÃ¡mica muro": "CerÃ¡micos",
    "CerÃ¡mica piso": "CerÃ¡micos",
    "Piso cerÃ¡mico": "CerÃ¡micos",
    "Porcelanato muro": "CerÃ¡micos",
    "Porcelanato piso": "CerÃ¡micos",
    "FragÃ¼e": "CerÃ¡micos",
    "FragÃ¼e muro": "CerÃ¡micos",
    "FragÃ¼e piso": "CerÃ¡micos",
    "Piso flotante": "Piso Flotante",
    "Pavimento": "Piso Flotante",
    "Guardapolvo": "Guardapolvos",
    "Guardapolvo cerÃ¡mico": "CerÃ¡micos",
    "Cornisa": "Cornisas y Junquillos",
    "Junquillo": "Cornisas y Junquillos",
    "Puerta": "Puertas",
    "Puertas": "Puertas",
    "Cerradura": "Puertas",
    "Mueble base": "Muebles",
    "Mueble aÃ©reo": "Muebles",
    "Muebles": "Muebles",
    "Closet": "Muebles",
    "Estante": "Muebles",
    "Vanitorio mueble": "Muebles",
    "Cubierta": "Cubiertas",
    "Ventanas": "Vidrios y Barandas",
    "Baranda vidriada": "Vidrios y Barandas",
    "Espejo": "Vidrios y Barandas",
    "Equipamiento elÃ©ctrico": "Electricidad",
    "Componentes elÃ©ctricos": "Electricidad",
    "Instalaciones elÃ©ctricas": "Electricidad",
    "Instalaciones": "Electricidad",
    "Equipamiento": ESPECIALIDAD_PREDETERMINADA,
    "Lavaplatos": "Sanitario",
    "GriferÃ­a": "Sanitario",
    "Artefactos": "Sanitario",
    "WC": "Sanitario",
    "Vanitorio": "Sanitario",
    "Tina": "Sanitario",
    "Receptáculo": "Sanitario",
    "ReceptÃ¡culo": "Sanitario",
    "Mampara": "Sanitario",
    "Mampara": "Sanitario",
    "Accesorios": ESPECIALIDAD_PREDETERMINADA,
    "Extractor de aire": "Electricidad",
    "Cocina": ESPECIALIDAD_PREDETERMINADA,
    "Encimera": ESPECIALIDAD_PREDETERMINADA,
    "Horno": ESPECIALIDAD_PREDETERMINADA,
    "Campana": ESPECIALIDAD_PREDETERMINADA,
    "Radiador": "ClimatizaciÃ³n",
    "Caldera": "ClimatizaciÃ³n",
    "Limpieza final": "Limpieza",
    "Limpieza": "Limpieza",
}

DEPENDENCIA_TODAS_PRINCIPALES = "__todas_principales__"

DEPENDENCIAS_CRITICAS_V1 = (
    ("Cocina", "Tabique", "Canalizaciones elÃ©ctricas", 1, "Canalizaciones ejecutadas que correspondan al recinto"),
    ("Cocina", "Tabique", "Canalizaciones sanitarias", 1, "Canalizaciones ejecutadas que correspondan al recinto"),
    ("Cocina", "Tabique", "Canalizaciones climatizaciÃ³n", 1, "Canalizaciones ejecutadas que correspondan al recinto"),
    ("Cocina", "TabiquerÃ­a", "Canalizaciones elÃ©ctricas", 1, "Canalizaciones ejecutadas que correspondan al recinto"),
    ("Cocina", "TabiquerÃ­a", "Canalizaciones sanitarias", 1, "Canalizaciones ejecutadas que correspondan al recinto"),
    ("Cocina", "TabiquerÃ­a", "Canalizaciones climatizaciÃ³n", 1, "Canalizaciones ejecutadas que correspondan al recinto"),
    ("Cocina", "Empaste", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Empaste", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Aparejo", "Empaste", 1, "Empaste terminado"),
    ("Cocina", "Primera mano de pintura", "Aparejo", 1, "Aparejo terminado"),
    ("Cocina", "Mano final de pintura", "Primera mano de pintura", 1, "Primera mano terminada"),
    ("Cocina", "CerÃ¡mica muro", "Tabique", 1, "TabiquerÃ­a terminada o muro terminado"),
    ("Cocina", "CerÃ¡mica muro", "Muro", 1, "TabiquerÃ­a terminada o muro terminado"),
    ("Cocina", "CerÃ¡mico muro", "Tabique", 1, "TabiquerÃ­a terminada o muro terminado"),
    ("Cocina", "CerÃ¡mico muro", "Muro", 1, "TabiquerÃ­a terminada o muro terminado"),
    ("Cocina", "FragÃ¼e muro", "CerÃ¡mica muro", 1, "CerÃ¡mico muro instalado"),
    ("Cocina", "FragÃ¼e muro", "CerÃ¡mico muro", 1, "CerÃ¡mico muro instalado"),
    ("Cocina", "FragÃ¼e piso", "CerÃ¡mica piso", 1, "CerÃ¡mico piso instalado"),
    ("Cocina", "FragÃ¼e piso", "CerÃ¡mico piso", 1, "CerÃ¡mico piso instalado"),
    ("Cocina", "Guardapolvo cerÃ¡mico", "CerÃ¡mica piso", 1, "CerÃ¡mico piso instalado"),
    ("Cocina", "Guardapolvo cerÃ¡mico", "CerÃ¡mico piso", 1, "CerÃ¡mico piso instalado"),
    ("Cocina", "Mueble base", "CerÃ¡mica piso", 1, "CerÃ¡mico piso instalado"),
    ("Cocina", "Mueble base", "CerÃ¡mico piso", 1, "CerÃ¡mico piso instalado"),
    ("Cocina", "Mueble aÃ©reo", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Cocina", "Estante", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Cocina", "Cubierta", "Mueble base", 1, "Mueble base instalado"),
    ("Cocina", "Lavaplatos", "Cubierta", 1, "Cubierta instalada"),
    ("Cocina", "GriferÃ­a", "Lavaplatos", 1, "Lavaplatos instalado"),
    ("Cocina", "Encimera", "Mueble base", 1, "Mueble instalado"),
    ("Cocina", "Cocina", "Mueble base", 1, "Mueble instalado"),
    ("Cocina", "Horno", "Mueble base", 1, "Mueble instalado"),
    ("Cocina", "Campana", "Mueble base", 1, "Mueble instalado"),
    ("Cocina", "Radiador", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Radiador", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Caldera", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Cocina", "Componentes elÃ©ctricos", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Componentes elÃ©ctricos", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Equipamiento elÃ©ctrico", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Equipamiento elÃ©ctrico", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Cocina", "Placas elÃ©ctricas", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Cocina", "Puerta", "Marco", 1, "Marco instalado previamente"),
    ("Cocina", "Cerradura", "Puerta", 1, "Puerta instalada"),
    ("Cocina", "Cornisa", "Empaste", 1, "Empaste terminado"),
    ("Cocina", "Limpieza final", DEPENDENCIA_TODAS_PRINCIPALES, 1, "Todas las partidas principales terminadas"),
    ("Living - Comedor", "Tabique", "Canalizaciones elÃ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Living - Comedor", "Tabique", "Canalizaciones climatizaciÃ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Living - Comedor", "TabiquerÃ­a", "Canalizaciones elÃ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Living - Comedor", "TabiquerÃ­a", "Canalizaciones climatizaciÃ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Living - Comedor", "Empaste", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Empaste", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Guardapolvo", "Empaste", 1, "Empaste terminado"),
    ("Living - Comedor", "Cornisa", "Empaste", 1, "Empaste terminado"),
    ("Living - Comedor", "Aparejo", "Empaste", 1, "Empaste terminado"),
    ("Living - Comedor", "Primera mano de pintura", "Aparejo", 1, "Aparejo terminado"),
    ("Living - Comedor", "Mano final de pintura", "Primera mano de pintura", 1, "Primera mano terminada"),
    ("Living - Comedor", "Junquillo", "Piso flotante", 1, "Piso flotante instalado"),
    ("Living - Comedor", "Radiador", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Radiador", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Componentes elÃ©ctricos", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Componentes elÃ©ctricos", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Equipamiento elÃ©ctrico", "Tabique", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Equipamiento elÃ©ctrico", "TabiquerÃ­a", 1, "TabiquerÃ­a terminada"),
    ("Living - Comedor", "Placas elÃ©ctricas", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Living - Comedor", "Puerta", "Marco", 1, "Marco instalado previamente"),
    ("Living - Comedor", "Cerradura", "Puerta", 1, "Puerta instalada"),
    ("Living - Comedor", "Limpieza final", DEPENDENCIA_TODAS_PRINCIPALES, 1, "Todas las partidas principales terminadas"),
    ("Dormitorio", "Tabique", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio", "Tabique", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio", "TabiquerÃƒÂ­a", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio", "TabiquerÃƒÂ­a", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio", "Empaste", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Empaste", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Guardapolvo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio", "Cornisa", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio", "Aparejo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio", "Primera mano de pintura", "Aparejo", 1, "Aparejo terminado"),
    ("Dormitorio", "Mano final de pintura", "Primera mano de pintura", 1, "Primera mano terminada"),
    ("Dormitorio", "Junquillo", "Piso flotante", 1, "Piso flotante instalado"),
    ("Dormitorio", "Radiador", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Radiador", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Componentes elÃƒÂ©ctricos", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Componentes elÃƒÂ©ctricos", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Equipamiento elÃƒÂ©ctrico", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Equipamiento elÃƒÂ©ctrico", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio", "Placas elÃƒÂ©ctricas", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Dormitorio", "Puerta", "Marco", 1, "Marco instalado previamente"),
    ("Dormitorio", "Cerradura", "Puerta", 1, "Puerta instalada"),
    ("Dormitorio", "Limpieza final", DEPENDENCIA_TODAS_PRINCIPALES, 1, "Todas las partidas principales terminadas"),
    ("Dormitorio Principal", "Tabique", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio Principal", "Tabique", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio Principal", "TabiquerÃƒÂ­a", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio Principal", "TabiquerÃƒÂ­a", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio Principal", "Empaste", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Empaste", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Guardapolvo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio Principal", "Cornisa", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio Principal", "Aparejo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio Principal", "Primera mano de pintura", "Aparejo", 1, "Aparejo terminado"),
    ("Dormitorio Principal", "Mano final de pintura", "Primera mano de pintura", 1, "Primera mano terminada"),
    ("Dormitorio Principal", "Junquillo", "Piso flotante", 1, "Piso flotante instalado"),
    ("Dormitorio Principal", "Radiador", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Radiador", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Componentes elÃƒÂ©ctricos", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Componentes elÃƒÂ©ctricos", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Equipamiento elÃƒÂ©ctrico", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Equipamiento elÃƒÂ©ctrico", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio Principal", "Placas elÃƒÂ©ctricas", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Dormitorio Principal", "Puerta", "Marco", 1, "Marco instalado previamente"),
    ("Dormitorio Principal", "Cerradura", "Puerta", 1, "Puerta instalada"),
    ("Dormitorio Principal", "Limpieza final", DEPENDENCIA_TODAS_PRINCIPALES, 1, "Todas las partidas principales terminadas"),
    ("Dormitorio 1", "Tabique", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 1", "Tabique", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 1", "TabiquerÃƒÂ­a", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 1", "TabiquerÃƒÂ­a", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 1", "Empaste", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Empaste", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Guardapolvo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio 1", "Cornisa", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio 1", "Aparejo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio 1", "Primera mano de pintura", "Aparejo", 1, "Aparejo terminado"),
    ("Dormitorio 1", "Mano final de pintura", "Primera mano de pintura", 1, "Primera mano terminada"),
    ("Dormitorio 1", "Junquillo", "Piso flotante", 1, "Piso flotante instalado"),
    ("Dormitorio 1", "Radiador", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Radiador", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Componentes elÃƒÂ©ctricos", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Componentes elÃƒÂ©ctricos", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Equipamiento elÃƒÂ©ctrico", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Equipamiento elÃƒÂ©ctrico", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 1", "Placas elÃƒÂ©ctricas", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Dormitorio 1", "Puerta", "Marco", 1, "Marco instalado previamente"),
    ("Dormitorio 1", "Cerradura", "Puerta", 1, "Puerta instalada"),
    ("Dormitorio 1", "Limpieza final", DEPENDENCIA_TODAS_PRINCIPALES, 1, "Todas las partidas principales terminadas"),
    ("Dormitorio 2", "Tabique", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 2", "Tabique", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 2", "TabiquerÃƒÂ­a", "Canalizaciones elÃƒÂ©ctricas", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 2", "TabiquerÃƒÂ­a", "Canalizaciones climatizaciÃƒÂ³n", 1, "Canalizaciones ejecutadas que correspondan"),
    ("Dormitorio 2", "Empaste", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Empaste", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Guardapolvo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio 2", "Cornisa", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio 2", "Aparejo", "Empaste", 1, "Empaste terminado"),
    ("Dormitorio 2", "Primera mano de pintura", "Aparejo", 1, "Aparejo terminado"),
    ("Dormitorio 2", "Mano final de pintura", "Primera mano de pintura", 1, "Primera mano terminada"),
    ("Dormitorio 2", "Junquillo", "Piso flotante", 1, "Piso flotante instalado"),
    ("Dormitorio 2", "Radiador", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Radiador", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Componentes elÃƒÂ©ctricos", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Componentes elÃƒÂ©ctricos", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Equipamiento elÃƒÂ©ctrico", "Tabique", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Equipamiento elÃƒÂ©ctrico", "TabiquerÃƒÂ­a", 1, "TabiquerÃƒÂ­a terminada"),
    ("Dormitorio 2", "Placas elÃƒÂ©ctricas", "Mano final de pintura", 1, "Mano final pintura terminada"),
    ("Dormitorio 2", "Puerta", "Marco", 1, "Marco instalado previamente"),
    ("Dormitorio 2", "Cerradura", "Puerta", 1, "Puerta instalada"),
    ("Dormitorio 2", "Limpieza final", DEPENDENCIA_TODAS_PRINCIPALES, 1, "Todas las partidas principales terminadas"),
    ("Baño Principal", "Mampara", "Receptáculo", 1, "Receptáculo instalado"),
    ("Baño Principal", "Extractor de aire", "Fragüe muro", 1, "Fragüe muro terminado"),
    ("Baño Principal", "Espejo", "Fragüe muro", 1, "Fragüe muro terminado"),
    ("Baño 1", "Extractor de aire", "Fragüe muro", 1, "Fragüe muro terminado"),
    ("Baño 1", "Espejo", "Fragüe muro", 1, "Fragüe muro terminado"),
)


def conectar(ruta_db: str | Path = RUTA_DB_PREDETERMINADA) -> sqlite3.Connection:
    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


@contextmanager
def sesion(ruta_db: str | Path = RUTA_DB_PREDETERMINADA):
    """Abre una transacción y garantiza el cierre de la conexión."""
    with closing(conectar(ruta_db)) as conexion:
        with conexion:
            yield conexion


def crear_esquema(conexion: sqlite3.Connection) -> None:
    conexion.executescript(
        """
        CREATE TABLE IF NOT EXISTS obras (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            activa INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS torres (
            id INTEGER PRIMARY KEY,
            obra_id INTEGER NOT NULL REFERENCES obras(id),
            nombre TEXT NOT NULL,
            UNIQUE (obra_id, nombre)
        );

        CREATE TABLE IF NOT EXISTS tipologias (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS departamentos (
            id INTEGER PRIMARY KEY,
            torre_id INTEGER NOT NULL REFERENCES torres(id),
            piso INTEGER NOT NULL,
            numero TEXT NOT NULL,
            tipologia_id INTEGER REFERENCES tipologias(id),
            etapa_actual TEXT NOT NULL DEFAULT 'obra_gruesa',
            estado_operativo TEXT NOT NULL DEFAULT 'sin_revisar',
            fecha_objetivo_preentrega TEXT,
            fecha_objetivo_entrega TEXT,
            fecha_ultima_revision TEXT,
            UNIQUE (torre_id, numero)
        );

        CREATE TABLE IF NOT EXISTS tipologia_recinto (
            id INTEGER PRIMARY KEY,
            tipologia_id INTEGER NOT NULL REFERENCES tipologias(id)
                ON DELETE CASCADE,
            nombre_recinto TEXT NOT NULL,
            orden INTEGER NOT NULL DEFAULT 0,
            UNIQUE (tipologia_id, nombre_recinto)
        );

        CREATE TABLE IF NOT EXISTS recinto_partida (
            id INTEGER PRIMARY KEY,
            tipologia_recinto_id INTEGER NOT NULL
                REFERENCES tipologia_recinto(id) ON DELETE CASCADE,
            partida_id INTEGER NOT NULL REFERENCES partidas(id),
            orden INTEGER NOT NULL DEFAULT 0,
            peso_avance INTEGER NOT NULL DEFAULT 1,
            obligatoria INTEGER NOT NULL DEFAULT 1
                CHECK (obligatoria IN (0, 1)),
            UNIQUE (tipologia_recinto_id, partida_id)
        );

        CREATE TABLE IF NOT EXISTS dependencias_criticas_partida (
            id INTEGER PRIMARY KEY,
            recinto TEXT NOT NULL,
            partida TEXT NOT NULL,
            dependencia TEXT NOT NULL,
            grupo INTEGER NOT NULL DEFAULT 1,
            tipo_condicion TEXT NOT NULL DEFAULT 'AND'
                CHECK (tipo_condicion IN ('AND', 'OR')),
            descripcion TEXT NOT NULL,
            activa INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1)),
            UNIQUE (recinto, partida, dependencia, grupo)
        );

        CREATE TABLE IF NOT EXISTS estado_partida_departamento (
            id INTEGER PRIMARY KEY,
            departamento_id INTEGER NOT NULL REFERENCES departamentos(id)
                ON DELETE CASCADE,
            recinto_partida_id INTEGER NOT NULL REFERENCES recinto_partida(id)
                ON DELETE CASCADE,
            estado TEXT NOT NULL DEFAULT 'no_iniciada'
                CHECK (estado IN (
                    'no_iniciada', 'en_proceso', 'terminada',
                    'observada', 'bloqueada', 'verificada', 'no_aplica'
                )),
            actualizado_por_usuario_id INTEGER REFERENCES usuarios(id),
            fecha_ultima_actualizacion TEXT,
            UNIQUE (departamento_id, recinto_partida_id)
        );

        CREATE TABLE IF NOT EXISTS historial_partida_departamento (
            id INTEGER PRIMARY KEY,
            estado_partida_id INTEGER NOT NULL
                REFERENCES estado_partida_departamento(id) ON DELETE CASCADE,
            departamento_id INTEGER NOT NULL REFERENCES departamentos(id),
            recinto_partida_id INTEGER NOT NULL REFERENCES recinto_partida(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            estado_anterior TEXT,
            estado_nuevo TEXT NOT NULL,
            comentario TEXT,
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS restricciones_avance (
            id INTEGER PRIMARY KEY,
            estado_partida_id INTEGER NOT NULL UNIQUE
                REFERENCES estado_partida_departamento(id) ON DELETE CASCADE,
            causa TEXT NOT NULL CHECK (length(trim(causa)) > 0),
            responsable_id INTEGER NOT NULL REFERENCES responsables(id),
            fecha_compromiso TEXT NOT NULL
                CHECK (
                    date(fecha_compromiso) IS NOT NULL
                    AND date(fecha_compromiso) = fecha_compromiso
                ),
            comentario TEXT,
            estado TEXT NOT NULL DEFAULT 'activa'
                CHECK (estado IN ('activa', 'cerrada')),
            fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            fecha_cierre TEXT
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (
                rol IN ('Administrador', 'Supervisor', 'Solo lectura')
            ),
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS responsables (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            empresa TEXT,
            cargo TEXT,
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS partidas (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            especialidad TEXT NOT NULL DEFAULT 'Terminaciones Generales'
        );

        CREATE TABLE IF NOT EXISTS tipos_problema (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE,
            bloquea_por_defecto INTEGER NOT NULL CHECK (bloquea_por_defecto IN (0, 1))
        );

        CREATE TABLE IF NOT EXISTS recintos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS problemas_madre (
            id INTEGER PRIMARY KEY,
            titulo TEXT NOT NULL CHECK (length(trim(titulo)) > 0),
            partida_id INTEGER NOT NULL REFERENCES partidas(id),
            tipo_problema_id INTEGER NOT NULL REFERENCES tipos_problema(id),
            responsable_id INTEGER NOT NULL REFERENCES responsables(id),
            creado_por_usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS restricciones (
            id INTEGER PRIMARY KEY,
            problema_madre_id INTEGER NOT NULL REFERENCES problemas_madre(id),
            departamento_id INTEGER NOT NULL REFERENCES departamentos(id),
            recinto_id INTEGER NOT NULL REFERENCES recintos(id),
            estado TEXT NOT NULL DEFAULT 'Abierto'
                CHECK (estado IN ('Abierto', 'En gestión', 'Resuelto', 'Verificado')),
            fecha_deteccion TEXT NOT NULL
                CHECK (
                    date(fecha_deteccion) IS NOT NULL
                    AND date(fecha_deteccion) = fecha_deteccion
                ),
            fecha_compromiso TEXT NOT NULL
                CHECK (
                    date(fecha_compromiso) IS NOT NULL
                    AND date(fecha_compromiso) = fecha_compromiso
                ),
            comentario_corto TEXT NOT NULL
                CHECK (length(trim(comentario_corto)) > 0),
            requiere_retrabajo INTEGER NOT NULL DEFAULT 0
                CHECK (requiere_retrabajo IN (0, 1)),
            afecta_funcionalidad INTEGER NOT NULL DEFAULT 0
                CHECK (afecta_funcionalidad IN (0, 1)),
            bloquea_entrega INTEGER NOT NULL CHECK (bloquea_entrega IN (0, 1)),
            verificado_por_usuario_id INTEGER REFERENCES usuarios(id),
            fecha_verificacion TEXT
                CHECK (
                    fecha_verificacion IS NULL
                    OR datetime(fecha_verificacion) IS NOT NULL
                ),
            UNIQUE (problema_madre_id, departamento_id, recinto_id),
            CHECK (
                (estado = 'Verificado'
                    AND verificado_por_usuario_id IS NOT NULL
                    AND fecha_verificacion IS NOT NULL)
                OR
                (estado <> 'Verificado'
                    AND verificado_por_usuario_id IS NULL
                    AND fecha_verificacion IS NULL)
            )
        );

        CREATE TABLE IF NOT EXISTS acciones (
            id INTEGER PRIMARY KEY,
            restriccion_id INTEGER NOT NULL REFERENCES restricciones(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            comentario TEXT NOT NULL CHECK (length(trim(comentario)) > 0),
            estado_resultante TEXT NOT NULL
                CHECK (estado_resultante IN (
                    'Abierto', 'En gestión', 'Resuelto', 'Verificado'
                ))
        );

        CREATE TABLE IF NOT EXISTS liberaciones_departamento (
            id INTEGER PRIMARY KEY,
            departamento_id INTEGER NOT NULL REFERENCES departamentos(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            comentario TEXT NOT NULL CHECK (length(trim(comentario)) > 0)
        );

        CREATE TRIGGER IF NOT EXISTS validar_bloqueo_restriccion_insert
        BEFORE INSERT ON restricciones
        BEGIN
            SELECT CASE WHEN NEW.bloquea_entrega <> (
                SELECT CASE
                    WHEN bloquea_por_defecto = 1
                         OR NEW.requiere_retrabajo = 1
                         OR NEW.afecta_funcionalidad = 1
                    THEN 1 ELSE 0
                END
                FROM tipos_problema
                WHERE id = (
                    SELECT tipo_problema_id
                    FROM problemas_madre
                    WHERE id = NEW.problema_madre_id
                )
            )
            THEN RAISE(ABORT, 'bloquea_entrega no coincide con las reglas')
            END;
        END;

        CREATE TRIGGER IF NOT EXISTS validar_bloqueo_restriccion_update
        BEFORE UPDATE OF problema_madre_id, requiere_retrabajo,
                         afecta_funcionalidad, bloquea_entrega
        ON restricciones
        BEGIN
            SELECT CASE WHEN NEW.bloquea_entrega <> (
                SELECT CASE
                    WHEN bloquea_por_defecto = 1
                         OR NEW.requiere_retrabajo = 1
                         OR NEW.afecta_funcionalidad = 1
                    THEN 1 ELSE 0
                END
                FROM tipos_problema
                WHERE id = (
                    SELECT tipo_problema_id
                    FROM problemas_madre
                    WHERE id = NEW.problema_madre_id
                )
            )
            THEN RAISE(ABORT, 'bloquea_entrega no coincide con las reglas')
            END;
        END;

        CREATE TRIGGER IF NOT EXISTS recalcular_bloqueo_al_cambiar_tipo
        AFTER UPDATE OF tipo_problema_id ON problemas_madre
        BEGIN
            UPDATE restricciones
            SET bloquea_entrega = CASE
                WHEN (
                    SELECT bloquea_por_defecto
                    FROM tipos_problema
                    WHERE id = NEW.tipo_problema_id
                ) = 1
                OR requiere_retrabajo = 1
                OR afecta_funcionalidad = 1
                THEN 1 ELSE 0
            END
            WHERE problema_madre_id = NEW.id;
        END;

        CREATE TRIGGER IF NOT EXISTS validar_verificador_insert
        BEFORE INSERT ON restricciones
        WHEN NEW.estado = 'Verificado'
        BEGIN
            SELECT CASE WHEN (
                SELECT rol FROM usuarios WHERE id = NEW.verificado_por_usuario_id
            ) <> 'Administrador'
            THEN RAISE(ABORT, 'solo un administrador puede verificar')
            END;
        END;

        CREATE TRIGGER IF NOT EXISTS validar_verificador_update
        BEFORE UPDATE OF estado, verificado_por_usuario_id ON restricciones
        WHEN NEW.estado = 'Verificado'
        BEGIN
            SELECT CASE WHEN (
                SELECT rol FROM usuarios WHERE id = NEW.verificado_por_usuario_id
            ) <> 'Administrador'
            THEN RAISE(ABORT, 'solo un administrador puede verificar')
            END;
        END;

        CREATE VIEW IF NOT EXISTS v_restricciones_detalle AS
        SELECT
            r.id AS restriccion_id,
            pm.id AS problema_madre_id,
            pm.titulo,
            o.nombre AS obra,
            t.nombre AS torre,
            d.piso,
            d.numero AS departamento,
            rec.nombre AS recinto,
            p.nombre AS partida,
            tp.nombre AS tipo_problema,
            resp.nombre AS responsable,
            r.estado,
            r.fecha_deteccion,
            r.fecha_compromiso,
            r.comentario_corto,
            r.requiere_retrabajo,
            r.afecta_funcionalidad,
            r.bloquea_entrega
        FROM restricciones r
        JOIN problemas_madre pm ON pm.id = r.problema_madre_id
        JOIN departamentos d ON d.id = r.departamento_id
        JOIN torres t ON t.id = d.torre_id
        JOIN obras o ON o.id = t.obra_id
        JOIN recintos rec ON rec.id = r.recinto_id
        JOIN partidas p ON p.id = pm.partida_id
        JOIN tipos_problema tp ON tp.id = pm.tipo_problema_id
        JOIN responsables resp ON resp.id = pm.responsable_id;

        CREATE VIEW IF NOT EXISTS v_estado_departamentos AS
        SELECT
            d.id AS departamento_id,
            o.nombre AS obra,
            t.nombre AS torre,
            d.piso,
            d.numero AS departamento,
            CASE
                WHEN EXISTS (
                    SELECT 1 FROM restricciones r
                    WHERE r.departamento_id = d.id
                      AND r.estado <> 'Verificado'
                      AND r.bloquea_entrega = 1
                ) THEN 'Bloqueado'
                WHEN EXISTS (
                    SELECT 1 FROM restricciones r
                    WHERE r.departamento_id = d.id
                      AND r.estado <> 'Verificado'
                ) THEN 'Observado no bloqueante'
                ELSE 'Liberable'
            END AS estado,
            (
                SELECT COUNT(*) FROM restricciones r
                WHERE r.departamento_id = d.id
                  AND r.estado <> 'Verificado'
            ) AS pendientes_activos
        FROM departamentos d
        JOIN torres t ON t.id = d.torre_id
        JOIN obras o ON o.id = t.obra_id;

        CREATE VIEW IF NOT EXISTS v_estado_problemas_madre AS
        SELECT
            pm.id AS problema_madre_id,
            pm.titulo,
            CASE
                WHEN COUNT(r.id) = 0 THEN 'Sin departamentos'
                WHEN SUM(CASE WHEN r.estado <> 'Verificado' THEN 1 ELSE 0 END) = 0
                    THEN 'Verificado'
                WHEN SUM(CASE WHEN r.estado = 'Abierto' THEN 1 ELSE 0 END) > 0
                    THEN 'Abierto'
                WHEN SUM(CASE WHEN r.estado = 'En gestión' THEN 1 ELSE 0 END) > 0
                    THEN 'En gestión'
                ELSE 'Resuelto'
            END AS estado,
            COUNT(r.id) AS departamentos_afectados,
            SUM(CASE WHEN r.estado <> 'Verificado' THEN 1 ELSE 0 END)
                AS pendientes_activos
        FROM problemas_madre pm
        LEFT JOIN restricciones r ON r.problema_madre_id = pm.id
        GROUP BY pm.id, pm.titulo;
        """
    )
    migrar_estado_partida_v01(conexion)
    migrar_recinto_partida_v01(conexion)
    migrar_departamentos_v01(conexion)
    migrar_usuarios_roles_v01(conexion)
    reparar_referencias_tablas_renombradas_v01(conexion)
    reparar_triggers_usuarios_v01(conexion)
    migrar_partidas_especialidad_v1(conexion)
    migrar_dependencias_criticas_v1(conexion)
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS liberaciones_departamento (
            id INTEGER PRIMARY KEY,
            departamento_id INTEGER NOT NULL REFERENCES departamentos(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            comentario TEXT NOT NULL CHECK (length(trim(comentario)) > 0)
        )
        """
    )


def _columnas_tabla(
    conexion: sqlite3.Connection,
    tabla: str,
) -> set[str]:
    return {
        fila["name"]
        for fila in conexion.execute(f"PRAGMA table_info({tabla})").fetchall()
    }


def _sql_tabla(conexion: sqlite3.Connection, tabla: str) -> str:
    fila = conexion.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (tabla,),
    ).fetchone()
    return fila["sql"] if fila and fila["sql"] else ""


def migrar_estado_partida_v01(conexion: sqlite3.Connection) -> None:
    """Actualiza estados de partida e historial en bases existentes."""
    sql = _sql_tabla(conexion, "estado_partida_departamento")
    if "observada" not in sql:
        conexion.executescript(
            """
            PRAGMA foreign_keys = OFF;

            ALTER TABLE estado_partida_departamento
            RENAME TO estado_partida_departamento_anterior;

            CREATE TABLE estado_partida_departamento (
                id INTEGER PRIMARY KEY,
                departamento_id INTEGER NOT NULL REFERENCES departamentos(id)
                    ON DELETE CASCADE,
                recinto_partida_id INTEGER NOT NULL REFERENCES recinto_partida(id)
                    ON DELETE CASCADE,
                estado TEXT NOT NULL DEFAULT 'no_iniciada'
                    CHECK (estado IN (
                        'no_iniciada', 'en_proceso', 'terminada',
                        'observada', 'bloqueada', 'verificada', 'no_aplica'
                    )),
                actualizado_por_usuario_id INTEGER REFERENCES usuarios(id),
                fecha_ultima_actualizacion TEXT,
                UNIQUE (departamento_id, recinto_partida_id)
            );

            INSERT INTO estado_partida_departamento (
                id,
                departamento_id,
                recinto_partida_id,
                estado,
                actualizado_por_usuario_id,
                fecha_ultima_actualizacion
            )
            SELECT
                id,
                departamento_id,
                recinto_partida_id,
                estado,
                actualizado_por_usuario_id,
                fecha_ultima_actualizacion
            FROM estado_partida_departamento_anterior;

            DROP TABLE estado_partida_departamento_anterior;

            PRAGMA foreign_keys = ON;
            """
        )

    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS historial_partida_departamento (
            id INTEGER PRIMARY KEY,
            estado_partida_id INTEGER NOT NULL
                REFERENCES estado_partida_departamento(id) ON DELETE CASCADE,
            departamento_id INTEGER NOT NULL REFERENCES departamentos(id),
            recinto_partida_id INTEGER NOT NULL REFERENCES recinto_partida(id),
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            estado_anterior TEXT,
            estado_nuevo TEXT NOT NULL,
            comentario TEXT,
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def migrar_departamentos_v01(conexion: sqlite3.Connection) -> None:
    """Añade campos operativos a bases creadas antes del nuevo flujo."""
    columnas = _columnas_tabla(conexion, "departamentos")
    nuevas_columnas = {
        "tipologia_id": "INTEGER REFERENCES tipologias(id)",
        "etapa_actual": "TEXT NOT NULL DEFAULT 'obra_gruesa'",
        "estado_operativo": "TEXT NOT NULL DEFAULT 'sin_revisar'",
        "fecha_objetivo_preentrega": "TEXT",
        "fecha_objetivo_entrega": "TEXT",
        "fecha_ultima_revision": "TEXT",
    }
    for nombre, definicion in nuevas_columnas.items():
        if nombre not in columnas:
            conexion.execute(
                f"ALTER TABLE departamentos ADD COLUMN {nombre} {definicion}"
            )


def migrar_recinto_partida_v01(conexion: sqlite3.Connection) -> None:
    """Añade peso de avance a checklists ya creados."""
    columnas = _columnas_tabla(conexion, "recinto_partida")
    if "peso_avance" not in columnas:
        conexion.execute(
            "ALTER TABLE recinto_partida ADD COLUMN peso_avance INTEGER NOT NULL DEFAULT 1"
        )
    if "obligatoria" in columnas:
        conexion.execute("UPDATE recinto_partida SET obligatoria = 1")


def migrar_usuarios_roles_v01(conexion: sqlite3.Connection) -> None:
    """Permite el rol Solo lectura en bases creadas antes del sprint V1."""
    sql = _sql_tabla(conexion, "usuarios")
    if "Solo lectura" in sql:
        return

    conexion.executescript(
        """
        PRAGMA foreign_keys = OFF;

        ALTER TABLE usuarios RENAME TO usuarios_anterior;

        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (
                rol IN ('Administrador', 'Supervisor', 'Solo lectura')
            ),
            activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
        );

        INSERT INTO usuarios (id, nombre, rol, activo)
        SELECT id, nombre, rol, activo
        FROM usuarios_anterior;

        DROP TABLE usuarios_anterior;

        PRAGMA foreign_keys = ON;
        """
    )


def reparar_triggers_usuarios_v01(conexion: sqlite3.Connection) -> None:
    """Recrea triggers que SQLite pudo reescribir hacia usuarios_anterior."""
    triggers = {
        "validar_verificador_insert": """
            CREATE TRIGGER IF NOT EXISTS validar_verificador_insert
            BEFORE INSERT ON restricciones
            WHEN NEW.estado = 'Verificado'
            BEGIN
                SELECT CASE WHEN (
                    SELECT rol FROM usuarios WHERE id = NEW.verificado_por_usuario_id
                ) <> 'Administrador'
                THEN RAISE(ABORT, 'solo un administrador puede verificar')
                END;
            END
        """,
        "validar_verificador_update": """
            CREATE TRIGGER IF NOT EXISTS validar_verificador_update
            BEFORE UPDATE OF estado, verificado_por_usuario_id ON restricciones
            WHEN NEW.estado = 'Verificado'
            BEGIN
                SELECT CASE WHEN (
                    SELECT rol FROM usuarios WHERE id = NEW.verificado_por_usuario_id
                ) <> 'Administrador'
                THEN RAISE(ABORT, 'solo un administrador puede verificar')
                END;
            END
        """,
    }

    for nombre, sql_creacion in triggers.items():
        fila = conexion.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'trigger'
              AND name = ?
            """,
            (nombre,),
        ).fetchone()
        if fila and fila["sql"] and "usuarios_anterior" in fila["sql"]:
            conexion.execute(f"DROP TRIGGER {nombre}")
        conexion.execute(sql_creacion)


def reparar_referencias_tablas_renombradas_v01(
    conexion: sqlite3.Connection,
) -> None:
    """Corrige FKs reescritas por SQLite hacia tablas temporales de migracion."""
    referencias_antiguas = conexion.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE sql LIKE '%usuarios_anterior%'
           OR sql LIKE '%estado_partida_departamento_anterior%'
        """
    ).fetchone()[0]
    if referencias_antiguas == 0:
        return

    version = conexion.execute("PRAGMA schema_version").fetchone()[0]
    conexion.execute("PRAGMA writable_schema = ON")
    conexion.execute(
        """
        UPDATE sqlite_master
        SET sql = replace(
            replace(
                replace(
                    replace(
                        sql,
                        'REFERENCES "usuarios_anterior"(id)',
                        'REFERENCES usuarios(id)'
                    ),
                    'REFERENCES usuarios_anterior(id)',
                    'REFERENCES usuarios(id)'
                ),
                'REFERENCES "estado_partida_departamento_anterior"(id)',
                'REFERENCES estado_partida_departamento(id)'
            ),
            'REFERENCES estado_partida_departamento_anterior(id)',
            'REFERENCES estado_partida_departamento(id)'
        )
        WHERE sql LIKE '%usuarios_anterior%'
           OR sql LIKE '%estado_partida_departamento_anterior%'
        """
    )
    conexion.execute("PRAGMA writable_schema = OFF")
    conexion.execute(f"PRAGMA schema_version = {version + 1}")


def migrar_partidas_especialidad_v1(conexion: sqlite3.Connection) -> None:
    """Agrega y mantiene la especialidad principal por partida."""
    columnas = _columnas_tabla(conexion, "partidas")
    if "especialidad" not in columnas:
        conexion.execute(
            """
            ALTER TABLE partidas
            ADD COLUMN especialidad TEXT NOT NULL DEFAULT 'Terminaciones Generales'
            """
        )
    aplicar_especialidades_partidas(conexion)


def aplicar_especialidades_partidas(conexion: sqlite3.Connection) -> None:
    """Actualiza las partidas existentes con el mapeo funcional V1."""
    filas = conexion.execute("SELECT id, nombre FROM partidas").fetchall()
    for fila in filas:
        especialidad = ESPECIALIDAD_POR_PARTIDA.get(
            fila["nombre"],
            ESPECIALIDAD_PREDETERMINADA,
        )
        conexion.execute(
            "UPDATE partidas SET especialidad = ? WHERE id = ?",
            (especialidad, fila["id"]),
        )


def migrar_dependencias_criticas_v1(conexion: sqlite3.Connection) -> None:
    """Crea y carga la matriz configurable de dependencias criticas V1."""
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS dependencias_criticas_partida (
            id INTEGER PRIMARY KEY,
            recinto TEXT NOT NULL,
            partida TEXT NOT NULL,
            dependencia TEXT NOT NULL,
            grupo INTEGER NOT NULL DEFAULT 1,
            tipo_condicion TEXT NOT NULL DEFAULT 'AND'
                CHECK (tipo_condicion IN ('AND', 'OR')),
            descripcion TEXT NOT NULL,
            activa INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1)),
            UNIQUE (recinto, partida, dependencia, grupo)
        )
        """
    )
    columnas = {
        fila["name"]
        for fila in conexion.execute(
            "PRAGMA table_info(dependencias_criticas_partida)"
        ).fetchall()
    }
    if "tipo_condicion" not in columnas:
        conexion.execute(
            """
            ALTER TABLE dependencias_criticas_partida
            ADD COLUMN tipo_condicion TEXT NOT NULL DEFAULT 'AND'
            CHECK (tipo_condicion IN ('AND', 'OR'))
            """
        )
    conexion.executemany(
        """
        INSERT INTO dependencias_criticas_partida (
            recinto,
            partida,
            dependencia,
            grupo,
            descripcion
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (recinto, partida, dependencia, grupo)
        DO NOTHING
        """,
        DEPENDENCIAS_CRITICAS_V1,
    )


def cargar_catalogos(conexion: sqlite3.Connection) -> None:
    conexion.executemany(
        "INSERT OR IGNORE INTO partidas (nombre) VALUES (?)",
        ((nombre,) for nombre in PARTIDAS),
    )
    aplicar_especialidades_partidas(conexion)
    conexion.executemany(
        """
        INSERT OR IGNORE INTO tipos_problema (nombre, bloquea_por_defecto)
        VALUES (?, ?)
        """,
        TIPOS_PROBLEMA,
    )
    conexion.executemany(
        "INSERT OR IGNORE INTO recintos (nombre) VALUES (?)",
        ((nombre,) for nombre in RECINTOS),
    )
    consolidar_partida_duplicada(conexion, "Puertas", "Puerta")


def consolidar_partida_duplicada(
    conexion: sqlite3.Connection,
    nombre_duplicado: str,
    nombre_canonico: str,
) -> None:
    """Fusiona una variante antigua del nombre sin perder relaciones."""
    duplicada = conexion.execute(
        "SELECT id FROM partidas WHERE nombre = ?",
        (nombre_duplicado,),
    ).fetchone()
    canonica = conexion.execute(
        "SELECT id FROM partidas WHERE nombre = ?",
        (nombre_canonico,),
    ).fetchone()
    if duplicada is None or canonica is None:
        return

    conexion.execute(
        """
        DELETE FROM recinto_partida
        WHERE partida_id = ?
          AND tipologia_recinto_id IN (
              SELECT tipologia_recinto_id
              FROM recinto_partida
              WHERE partida_id = ?
          )
        """,
        (duplicada["id"], canonica["id"]),
    )
    conexion.execute(
        "UPDATE recinto_partida SET partida_id = ? WHERE partida_id = ?",
        (canonica["id"], duplicada["id"]),
    )
    conexion.execute(
        "UPDATE problemas_madre SET partida_id = ? WHERE partida_id = ?",
        (canonica["id"], duplicada["id"]),
    )
    conexion.execute(
        "DELETE FROM partidas WHERE id = ?",
        (duplicada["id"],),
    )


def inicializar_base(ruta_db: str | Path = RUTA_DB_PREDETERMINADA) -> Path:
    ruta = Path(ruta_db)
    with sesion(ruta) as conexion:
        crear_esquema(conexion)
        cargar_catalogos(conexion)
    return ruta
