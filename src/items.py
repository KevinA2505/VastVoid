from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class Rarity(Enum):
    """Possible rarities for items."""

    COMUN = "comun"
    POCO_COMUN = "poco_comun"
    RARO = "raro"
    EPICO = "epico"


@dataclass
class Item:
    """Small container for item data."""

    nombre: str
    tipo: str
    peso: float
    valor: int
    descripcion: str
    rareza: Rarity


# --- Materias primas -------------------------------------------------------
MATERIA_PRIMA: List[Item] = [
    Item("hierro", "materia_prima", 3.0, 5, "Metal común para construcción.", Rarity.COMUN),
    Item("cobre", "materia_prima", 2.0, 8, "Buen conductor eléctrico.", Rarity.COMUN),
    Item(
        "silicio",
        "materia_prima",
        1.5,
        6,
        "Mineral utilizado en componentes electrónicos.",
        Rarity.COMUN,
    ),
    Item("titanio", "materia_prima", 3.5, 15, "Metal muy resistente y ligero.", Rarity.POCO_COMUN),
    Item("litio", "materia_prima", 0.5, 12, "Elemento clave para baterías.", Rarity.POCO_COMUN),
    Item("oro", "materia_prima", 4.0, 50, "Metal precioso, muy valorado.", Rarity.RARO),
    Item("plata", "materia_prima", 3.8, 30, "Metal precioso, buen conductor.", Rarity.POCO_COMUN),
    Item("aluminio", "materia_prima", 1.0, 4, "Metal ligero y resistente a la corrosión.", Rarity.COMUN),
    Item("diamante", "materia_prima", 0.1, 100, "El mineral más duro y valioso.", Rarity.EPICO),
    Item("cuarzo", "materia_prima", 1.0, 7, "Cristal común usado en electrónica.", Rarity.COMUN),
    Item(
        "grafeno",
        "materia_prima",
        0.05,
        70,
        "Material bidimensional extremadamente resistente.",
        Rarity.RARO,
    ),
    Item("platino", "materia_prima", 4.5, 60, "Metal noble, muy raro y resistente.", Rarity.RARO),
    Item("cobalto", "materia_prima", 2.5, 18, "Metal ferromagnético, usado en aleaciones.", Rarity.POCO_COMUN),
    Item("tungsteno", "materia_prima", 3.2, 22, "Metal con alto punto de fusión.", Rarity.POCO_COMUN),
    Item("neodimio", "materia_prima", 1.7, 28, "Elemento de tierras raras para imanes potentes.", Rarity.RARO),
    Item("iridio", "materia_prima", 2.0, 40, "Metal denso usado en catalizadores.", Rarity.RARO),
    Item("magnesio", "materia_prima", 1.2, 6, "Metal ligero de reactividad moderada.", Rarity.COMUN),
    Item("uranio", "materia_prima", 3.8, 55, "Elemento radiactivo de alto valor.", Rarity.RARO),
    Item("rubidio", "materia_prima", 1.0, 20, "Metal alcalino de baja abundancia.", Rarity.POCO_COMUN),
    Item("perla negra", "materia_prima", 0.2, 75, "Gema oscura de gran valor.", Rarity.RARO),
    Item("obsidiana", "materia_prima", 1.5, 10, "Vidrio volcánico oscuro.", Rarity.COMUN),
    Item("permafrost", "materia_prima", 1.0, 12, "Hielo eterno, útil en experimentos.", Rarity.POCO_COMUN),
    Item("mercurio", "materia_prima", 2.0, 18, "Metal líquido tóxico.", Rarity.POCO_COMUN),
    Item("palladium", "materia_prima", 2.5, 45, "Metal precioso resistente a la corrosión.", Rarity.RARO),
    Item("berilio", "materia_prima", 2.0, 30, "Metal ligero de alta rigidez.", Rarity.POCO_COMUN),
    Item("zinc", "materia_prima", 2.0, 8, "Metal común usado en aleaciones.", Rarity.COMUN),
    Item("niquel", "materia_prima", 2.0, 12, "Metal común resistente a la corrosión.", Rarity.COMUN),
    Item("zafiro", "materia_prima", 0.1, 80, "Piedra preciosa azul.", Rarity.RARO),
    Item("esmeralda", "materia_prima", 0.1, 70, "Piedra preciosa verde.", Rarity.RARO),
    Item("rubi", "materia_prima", 0.1, 75, "Piedra preciosa roja.", Rarity.RARO),
    Item("kryptonita", "materia_prima", 1.5, 90, "Mineral ficticio de poder extremo.", Rarity.EPICO),
    Item("adamantita", "materia_prima", 3.0, 85, "Metal mítico casi indestructible.", Rarity.EPICO),
    Item("cromo", "materia_prima", 1.5, 15, "Metal brillante, resistente a la oxidación.", Rarity.COMUN),
    Item("vanadio", "materia_prima", 1.8, 25, "Metal de alta resistencia.", Rarity.POCO_COMUN),
    Item("molibdeno", "materia_prima", 2.0, 35, "Metal con alto punto de fusión.", Rarity.POCO_COMUN),
    Item("lingote de hierro", "materia_prima", 2.5, 12, "Barra de hierro purificado.", Rarity.COMUN),
    Item("placa de titanio", "materia_prima", 3.0, 25, "Lamina resistente de titanio procesado.", Rarity.POCO_COMUN),
]

# --- Combustibles ----------------------------------------------------------
COMBUSTIBLES: List[Item] = [
    Item("gasolina", "combustible", 1.0, 10, "Combustible fósil refinado.", Rarity.COMUN),
    Item(
        "materia oscura",
        "combustible",
        0.2,
        50,
        "Fuente de energía extremadamente poderosa.",
        Rarity.EPICO,
    ),
    Item(
        "combustible ionico",
        "combustible",
        0.8,
        20,
        "Gas ionizado para motores espaciales.",
        Rarity.POCO_COMUN,
    ),
    Item("antimateria", "combustible", 0.1, 100, "La energía más potente.", Rarity.EPICO),
    Item(
        "deuterio",
        "combustible",
        1.2,
        25,
        "Isótopo de hidrógeno para reactores.",
        Rarity.POCO_COMUN,
    ),
    Item("hidrogeno liquido", "combustible", 0.3, 15, "Combustible criogénico para cohetes.", Rarity.COMUN),
    Item("helio-3", "combustible", 0.05, 80, "Isótopo ligero para fusión nuclear.", Rarity.RARO),
    Item("plutonio", "combustible", 2.0, 90, "Elemento radiactivo para energía nuclear.", Rarity.RARO),
    Item("biocombustible", "combustible", 1.5, 12, "Combustible ecológico de origen orgánico.", Rarity.COMUN),
    Item("metano", "combustible", 0.7, 8, "Gas natural, combustible común.", Rarity.COMUN),
    Item("cristal de energia", "combustible", 0.4, 60, "Cristal que emite energía constante.", Rarity.RARO),
    Item("combustible de fusion", "combustible", 0.9, 75, "Mezcla avanzada para reactores de fusión.", Rarity.RARO),
    Item("carbon", "combustible", 2.5, 3, "Combustible fósil sólido.", Rarity.COMUN),
    Item("petroleo crudo", "combustible", 1.8, 7, "Combustible fósil sin refinar.", Rarity.COMUN),
    Item("vapor condensado", "combustible", 0.6, 18, "Vapor de alta presión, fuente de energía.", Rarity.POCO_COMUN),
    Item("hidrazina", "combustible", 1.0, 40, "Combustible de cohetes altamente reactivo.", Rarity.POCO_COMUN),
    Item("etanol", "combustible", 0.8, 6, "Combustible orgánico común.", Rarity.COMUN),
    Item("cristal energizado", "combustible", 0.3, 65, "Cristal cargado que libera energía.", Rarity.RARO),
    Item("aceite vegetal", "combustible", 1.2, 5, "Combustible alternativo sencillo.", Rarity.COMUN),
    Item("gas de lunas", "combustible", 0.7, 30, "Mezcla de gases recolectada de lunas distantes.", Rarity.POCO_COMUN),
    Item("nitrometano", "combustible", 0.9, 25, "Combustible para motores de alto rendimiento.", Rarity.POCO_COMUN),
    Item("fusion gel", "combustible", 0.2, 85, "Gel energético para reactores de fusión.", Rarity.RARO),
    Item("turboplasma", "combustible", 0.4, 95, "Plasma estabilizado para armamento.", Rarity.EPICO),
    Item("oxigeno liquido", "combustible", 1.1, 14, "Agente oxidante criogénico.", Rarity.POCO_COMUN),
    Item("particulas exoticas", "combustible", 0.05, 120, "Fuente de energía inestable.", Rarity.EPICO),
]

# --- Objetos raros ---------------------------------------------------------
OBJETOS_RAROS: List[Item] = [
    Item(
        "cristal quantico",
        "objeto_raro",
        0.3,
        80,
        "Cristal capaz de alterar la realidad.",
        Rarity.EPICO,
    ),
    Item(
        "fragmento de meteorito",
        "objeto_raro",
        2.5,
        30,
        "Roca espacial de origen desconocido.",
        Rarity.RARO,
    ),
    Item(
        "calavera cristal",
        "objeto_raro",
        1.0,
        70,
        "Artefacto antiguo de culturas perdidas.",
        Rarity.RARO,
    ),
    Item(
        "reliquia antigua",
        "objeto_raro",
        1.5,
        60,
        "Objeto venerado por civilizaciones pasadas.",
        Rarity.RARO,
    ),
    Item(
        "cubo misterioso",
        "objeto_raro",
        0.7,
        90,
        "Dispositivo de función desconocida.",
        Rarity.EPICO,
    ),
    Item("ojo de gorgon", "objeto_raro", 0.8, 120, "Reliquia que petrifica al contacto.", Rarity.EPICO),
    Item("gema de alma", "objeto_raro", 0.2, 150, "Gema que contiene una esencia vital.", Rarity.EPICO),
    Item("pluma de fenix", "objeto_raro", 0.1, 110, "Pluma que otorga resurrección.", Rarity.EPICO),
    Item("mapa estelar antiguo", "objeto_raro", 0.5, 95, "Mapa que muestra rutas galácticas ocultas.", Rarity.RARO),
    Item("huevo de dragon", "objeto_raro", 5.0, 200, "Un huevo de una criatura mítica.", Rarity.EPICO),
    Item("arena del tiempo", "objeto_raro", 0.1, 130, "Arena que manipula el flujo temporal.", Rarity.EPICO),
    Item("lagrima de sirena", "objeto_raro", 0.05, 105, "Lágrima que cura cualquier enfermedad.", Rarity.EPICO),
    Item("corazon de estrella", "objeto_raro", 3.0, 180, "Núcleo de una estrella en miniatura.", Rarity.EPICO),
    Item("espejo de los deseos", "objeto_raro", 1.0, 140, "Espejo que muestra los deseos más profundos.", Rarity.EPICO),
    Item("flor eterea", "objeto_raro", 0.02, 160, "Una flor que solo crece en dimensiones alternativas.", Rarity.EPICO),
    Item("reliquia galactica", "objeto_raro", 1.0, 100, "Tesoro ancestral de civilizaciones estelares.", Rarity.RARO),
    Item("anillo cosmico", "objeto_raro", 0.1, 130, "Joya que refleja las estrellas.", Rarity.EPICO),
    Item("piedra de la eternidad", "objeto_raro", 0.5, 150, "Roca que detiene el envejecimiento.", Rarity.EPICO),
    Item("cuerno de unicornio", "objeto_raro", 0.7, 140, "Símbolo de pureza y poder curativo.", Rarity.RARO),
    Item("hoja fantasma", "objeto_raro", 0.3, 120, "Arma etérea que atraviesa la materia.", Rarity.EPICO),
    Item("fragmento del vacio", "objeto_raro", 0.2, 160, "Trozo de oscuridad absoluta.", Rarity.EPICO),
    Item("mascara perdida", "objeto_raro", 1.2, 90, "Máscara ritual con poderes ocultos.", Rarity.RARO),
    Item("orbe del caos", "objeto_raro", 0.6, 155, "Esfera impredecible de energía.", Rarity.EPICO),
    Item("llave dimensional", "objeto_raro", 0.3, 110, "Abre portales a lugares extraños.", Rarity.RARO),
    Item("cristal armonico", "objeto_raro", 0.4, 115, "Resuena con melodías del universo.", Rarity.RARO),
]

# --- Artefactos ------------------------------------------------------------
ARTEFACTOS: List[Item] = [
    Item(
        "amuleto de poder",
        "artefacto",
        0.2,
        40,
        "Se dice que otorga fuerza a su portador.",
        Rarity.RARO,
    ),
    Item("antiguo chip", "artefacto", 0.1, 50, "Tecnología olvidada.", Rarity.RARO),
    Item(
        "esfera luminosa",
        "artefacto",
        0.4,
        55,
        "Esfera que emite luz inagotable.",
        Rarity.RARO,
    ),
    Item(
        "libro prohibido",
        "artefacto",
        1.0,
        75,
        "Contiene conocimientos peligrosos.",
        Rarity.EPICO,
    ),
    Item(
        "estatua alienigena",
        "artefacto",
        3.0,
        45,
        "Representación de un dios extraterrestre.",
        Rarity.RARO,
    ),
    Item("disco de navegacion", "artefacto", 0.6, 65, "Dispositivo para trazar rutas espaciales.", Rarity.POCO_COMUN),
    Item("generador de escudo", "artefacto", 2.0, 85, "Crea un campo de fuerza protector.", Rarity.RARO),
    Item("traductor universal", "artefacto", 0.3, 70, "Permite entender cualquier idioma.", Rarity.POCO_COMUN),
    Item("globo terraqueo holografico", "artefacto", 1.2, 90, "Proyecta mapas interactivos del universo.", Rarity.RARO),
    Item("reloj de bolsillo temporal", "artefacto", 0.1, 100, "Permite breves saltos en el tiempo.", Rarity.EPICO),
    Item("anillo de levitacion", "artefacto", 0.05, 80, "Anillo que permite al portador flotar.", Rarity.RARO),
    Item("matriz de teletransporte", "artefacto", 4.0, 120, "Dispositivo para reubicación instantánea.", Rarity.EPICO),
    Item("modulador de voz", "artefacto", 0.2, 35, "Cambia la voz del usuario.", Rarity.COMUN),
    Item("brazalete de fuerza", "artefacto", 0.7, 60, "Aumenta la fuerza física del portador.", Rarity.RARO),
    Item("proyector de camuflaje", "artefacto", 1.5, 95, "Genera un campo de invisibilidad.", Rarity.EPICO),
    Item("simbolo ancestral", "artefacto", 0.3, 50, "Representa la sabiduría de los ancestros.", Rarity.POCO_COMUN),
    Item("estatuilla sagrada", "artefacto", 1.4, 70, "Figurilla venerada por culturas remotas.", Rarity.RARO),
    Item("medallon estelar", "artefacto", 0.2, 90, "Vincula a su portador con las constelaciones.", Rarity.RARO),
    Item("reloj infinito", "artefacto", 0.6, 130, "Marca el tiempo de universos paralelos.", Rarity.EPICO),
    Item("tomo arcano", "artefacto", 1.1, 95, "Libro lleno de hechizos olvidados.", Rarity.RARO),
]

# --- Armas -----------------------------------------------------------------
ARMAS: List[Item] = [
    Item(
        "pistola laser",
        "arma",
        1.2,
        35,
        "Arma de mano que dispara pulsos de energía.",
        Rarity.COMUN,
    ),
    Item(
        "rifle de plasma",
        "arma",
        3.0,
        60,
        "Dispara proyectiles supercalientes.",
        Rarity.POCO_COMUN,
    ),
    Item("cañon gauss", "arma", 5.0, 80, "Lanza proyectiles a gran velocidad.", Rarity.RARO),
    Item(
        "espada de energia",
        "arma",
        2.5,
        50,
        "Hoja de energía pura.",
        Rarity.POCO_COMUN,
    ),
    Item("granada", "arma", 0.5, 15, "Explosivo portátil de un solo uso.", Rarity.COMUN),
    Item("arco de energia", "arma", 1.5, 45, "Arco que dispara flechas de energía.", Rarity.POCO_COMUN),
    Item("lanzallamas", "arma", 4.0, 55, "Arroja un chorro de fuego.", Rarity.POCO_COMUN),
    Item("mina de proximidad", "arma", 0.8, 20, "Explosivo que detona al acercarse al objetivo.", Rarity.POCO_COMUN),
    Item("cuchillo de combate", "arma", 0.7, 10, "Arma blanca básica.", Rarity.COMUN),
    Item("lanzamisiles", "arma", 8.0, 150, "Arma pesada que dispara misiles explosivos.", Rarity.RARO),
    Item("blaster sónico", "arma", 1.0, 40, "Arma que aturde con ondas de sonido.", Rarity.POCO_COMUN),
    Item("escopeta de iones", "arma", 3.5, 70, "Dispara una ráfaga de iones paralizantes.", Rarity.POCO_COMUN),
    Item("flagelador de partículas", "arma", 6.0, 110, "Arma devastadora que desintegra molecularmente.", Rarity.EPICO),
    Item("hacha de batalla", "arma", 2.8, 25, "Hacha pesada para combate cuerpo a cuerpo.", Rarity.COMUN),
    Item("cerbatana toxica", "arma", 0.4, 12, "Dispara dardos con veneno paralizante.", Rarity.COMUN),
    Item("laser de rafaga", "arma", 4.0, 70, "Haz continuo de alta energia de tres segundos.", Rarity.POCO_COMUN),
    Item("mina temporizada", "arma", 1.0, 20, "Explosivo que detona tras unos segundos.", Rarity.COMUN),
    Item("dron asistente", "arma", 2.0, 120, "Pequena nave que orbita y dispara.", Rarity.RARO),
    Item("misil hiperguiado", "arma", 3.5, 90, "Proyectil pesado con guiado extremo.", Rarity.RARO),
    Item("arma generica", "arma", 1.0, 20, "Arma básica de poco poder.", Rarity.COMUN),
    Item("arco gravitatorio", "arma", 1.3, 60, "Arco que utiliza la gravedad para lanzar proyectiles.", Rarity.RARO),
    Item("pistola electrica", "arma", 1.1, 25, "Arma que descarga electricidad paralizante.", Rarity.POCO_COMUN),
    Item("martillo de choque", "arma", 3.0, 50, "Arma pesada que libera pulsos eléctricos.", Rarity.POCO_COMUN),
    Item("rifle antimateria", "arma", 4.5, 140, "Desintegra a los enemigos con antimateria.", Rarity.EPICO),
    Item("shuriken de plasma", "arma", 0.2, 35, "Arrojadizas de energía concentrada.", Rarity.POCO_COMUN),
    Item("lanzador de redes", "arma", 2.2, 30, "Dispara redes para capturar objetivos.", Rarity.COMUN),
    Item("cañon de gravitones", "arma", 6.0, 120, "Manipula la gravedad para aplastar.", Rarity.RARO),
    Item("sable magnetico", "arma", 2.0, 55, "Espada que se extiende con magnetismo.", Rarity.POCO_COMUN),
    Item("baston psiquico", "arma", 1.5, 85, "Canaliza energía mental en ataques.", Rarity.RARO),
    Item("daga espectral", "arma", 0.3, 45, "Arma ligera que penetra armaduras.", Rarity.POCO_COMUN),
]

# --- Herramientas ----------------------------------------------------------
HERRAMIENTAS: List[Item] = [
    Item("martillo", "herramienta", 1.0, 10, "Básico para construcción.", Rarity.COMUN),
    Item("destornillador", "herramienta", 0.3, 5, "Para tornillos y ajustes.", Rarity.COMUN),
    Item("taladro", "herramienta", 2.0, 25, "Perfora casi cualquier superficie.", Rarity.POCO_COMUN),
    Item(
        "cortador laser",
        "herramienta",
        1.8,
        45,
        "Herramienta de corte de alta precisión.",
        Rarity.POCO_COMUN,
    ),
    Item(
        "kit de reparaciones",
        "herramienta",
        3.0,
        30,
        "Conjunto para arreglos rápidos.",
        Rarity.COMUN,
    ),
    Item("llave inglesa", "herramienta", 0.8, 8, "Para ajustar tuercas y pernos.", Rarity.COMUN),
    Item("soldador", "herramienta", 1.5, 20, "Para unir metales.", Rarity.COMUN),
    Item("escáner de minerales", "herramienta", 0.6, 50, "Detecta depósitos de minerales cercanos.", Rarity.RARO),
    Item("analizador de datos", "herramienta", 0.4, 35, "Decodifica información compleja.", Rarity.POCO_COMUN),
    Item("cable de anclaje", "herramienta", 2.5, 18, "Permite asegurar objetos pesados.", Rarity.COMUN),
    Item("multipico", "herramienta", 1.2, 28, "Herramienta versátil para minería y excavación.", Rarity.POCO_COMUN),
    Item("bateria portatil", "herramienta", 1.0, 15, "Fuente de energía para dispositivos.", Rarity.COMUN),
    Item("botiquin de primeros auxilios", "herramienta", 0.9, 22, "Contiene vendajes y medicinas básicas.", Rarity.COMUN),
    Item("dispensador de agua", "herramienta", 0.5, 10, "Provee agua potable purificada.", Rarity.COMUN),
    Item("comunicador interestelar", "herramienta", 0.7, 60, "Permite la comunicación a través de grandes distancias.", Rarity.RARO),
    Item("impresora 3d", "herramienta", 1.5, 75, "Crea objetos a partir de planos digitales.", Rarity.RARO),
    Item("nanoensamblador", "herramienta", 2.0, 90, "Construye estructuras a nivel molecular.", Rarity.EPICO),
    Item("pico laser", "herramienta", 1.3, 40, "Excava usando un rayo concentrado.", Rarity.POCO_COMUN),
    Item("maletin medico avanzado", "herramienta", 1.0, 55, "Contiene equipo de emergencia de alta tecnología.", Rarity.POCO_COMUN),
    Item("sensor climatico", "herramienta", 0.5, 20, "Predice cambios atmosféricos.", Rarity.COMUN),
    Item("torno portatil", "herramienta", 2.2, 32, "Herramienta para dar forma a piezas.", Rarity.COMUN),
    Item("gafas de vision termica", "herramienta", 0.2, 30, "Permiten ver fuentes de calor.", Rarity.POCO_COMUN),
    Item("guantes de fuerza", "herramienta", 0.8, 45, "Multiplican la fuerza de las manos.", Rarity.RARO),
]

# --- Piezas de nave -------------------------------------------------------
PIEZAS_NAVE: List[Item] = [
    Item("motor basico", "pieza_nave", 5.0, 50, "Motor espacial de bajo rendimiento.", Rarity.COMUN),
    Item("motor avanzado", "pieza_nave", 6.0, 120, "Motor eficiente de alta potencia.", Rarity.RARO),
    Item("casco ligero", "pieza_nave", 4.0, 40, "Estructura externa simple.", Rarity.COMUN),
    Item("casco reforzado", "pieza_nave", 5.5, 90, "Blindaje mejorado para mayor resistencia.", Rarity.POCO_COMUN),
    Item("cabina estandar", "pieza_nave", 3.0, 60, "Modulo básico para la tripulación.", Rarity.COMUN),
    Item("cabina de lujo", "pieza_nave", 3.5, 150, "Espaciosa y confortable para largas travesías.", Rarity.RARO),
]

# --- Vehiculos ----------------------------------------------------------
VEHICULOS: List[Item] = [
    Item("boat", "vehiculo", 8.0, 20, "Pequeña embarcación algo quemada pero útil.", Rarity.COMUN),
    Item("buggy lunar", "vehiculo", 6.0, 250, "Vehículo para explorar superficies lunares.", Rarity.POCO_COMUN),
    Item("moto antigravitatoria", "vehiculo", 3.5, 320, "Moto que flota sin ruedas.", Rarity.RARO),
    Item("submarino ligero", "vehiculo", 10.0, 300, "Submarino para exploraciones oceánicas.", Rarity.RARO),
]

# Organize items by type for easy lookup
ITEMS_BY_TYPE: Dict[str, List[Item]] = {
    "materia_prima": MATERIA_PRIMA,
    "combustible": COMBUSTIBLES,
    "objeto_raro": OBJETOS_RAROS,
    "artefacto": ARTEFACTOS,
    "arma": ARMAS,
    "herramienta": HERRAMIENTAS,
    "pieza_nave": PIEZAS_NAVE,
    "vehiculo": VEHICULOS,
}

# Flatten list with all items
ITEMS: List[Item] = [item for group in ITEMS_BY_TYPE.values() for item in group]

# Fast lookup table by item name
ITEMS_BY_NAME: Dict[str, Item] = {item.nombre: item for item in ITEMS}


def get_item(name: str) -> Item:
    """Return the :class:`Item` matching ``name``."""
    return ITEMS_BY_NAME[name]

# List of item names for backwards compatibility
ITEM_NAMES: List[str] = list(ITEMS_BY_NAME.keys())
