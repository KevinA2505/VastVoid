"""Definitions of all in game items with simple properties."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Item:
    """Small container for item data."""

    nombre: str
    tipo: str
    peso: float
    valor: int
    descripcion: str


# --- Materias primas -------------------------------------------------------
MATERIA_PRIMA: List[Item] = [
    Item("hierro", "materia_prima", 3.0, 5, "Metal común para construcción."),
    Item("cobre", "materia_prima", 2.0, 8, "Buen conductor eléctrico."),
    Item(
        "silicio",
        "materia_prima",
        1.5,
        6,
        "Mineral utilizado en componentes electrónicos.",
    ),
    Item("titanio", "materia_prima", 3.5, 15, "Metal muy resistente y ligero."),
    Item("litio", "materia_prima", 0.5, 12, "Elemento clave para baterías."),
]

# --- Combustibles ----------------------------------------------------------
COMBUSTIBLES: List[Item] = [
    Item("gasolina", "combustible", 1.0, 10, "Combustible fósil refinado."),
    Item(
        "materia oscura",
        "combustible",
        0.2,
        50,
        "Fuente de energía extremadamente poderosa.",
    ),
    Item(
        "combustible ionico",
        "combustible",
        0.8,
        20,
        "Gas ionizado para motores espaciales.",
    ),
    Item("antimateria", "combustible", 0.1, 100, "La energía más potente."),
    Item(
        "deuterio",
        "combustible",
        1.2,
        25,
        "Isótopo de hidrógeno para reactores.",
    ),
]

# --- Objetos raros ---------------------------------------------------------
OBJETOS_RAROS: List[Item] = [
    Item(
        "cristal quantico",
        "objeto_raro",
        0.3,
        80,
        "Cristal capaz de alterar la realidad.",
    ),
    Item(
        "fragmento de meteorito",
        "objeto_raro",
        2.5,
        30,
        "Roca espacial de origen desconocido.",
    ),
    Item(
        "calavera cristal",
        "objeto_raro",
        1.0,
        70,
        "Artefacto antiguo de culturas perdidas.",
    ),
    Item(
        "reliquia antigua",
        "objeto_raro",
        1.5,
        60,
        "Objeto venerado por civilizaciones pasadas.",
    ),
    Item(
        "cubo misterioso",
        "objeto_raro",
        0.7,
        90,
        "Dispositivo de función desconocida.",
    ),
]

# --- Artefactos ------------------------------------------------------------
ARTEFACTOS: List[Item] = [
    Item(
        "amuleto de poder",
        "artefacto",
        0.2,
        40,
        "Se dice que otorga fuerza a su portador.",
    ),
    Item("antiguo chip", "artefacto", 0.1, 50, "Tecnología olvidada."),
    Item(
        "esfera luminosa",
        "artefacto",
        0.4,
        55,
        "Esfera que emite luz inagotable.",
    ),
    Item(
        "libro prohibido",
        "artefacto",
        1.0,
        75,
        "Contiene conocimientos peligrosos.",
    ),
    Item(
        "estatua alienigena",
        "artefacto",
        3.0,
        45,
        "Representación de un dios extraterrestre.",
    ),
]

# --- Armas -----------------------------------------------------------------
ARMAS: List[Item] = [
    Item(
        "pistola laser",
        "arma",
        1.2,
        35,
        "Arma de mano que dispara pulsos de energía.",
    ),
    Item(
        "rifle de plasma",
        "arma",
        3.0,
        60,
        "Dispara proyectiles supercalientes.",
    ),
    Item("cañon gauss", "arma", 5.0, 80, "Lanza proyectiles a gran velocidad."),
    Item(
        "espada de energia",
        "arma",
        2.5,
        50,
        "Hoja de energía pura.",
    ),
    Item("granada", "arma", 0.5, 15, "Explosivo portátil de un solo uso."),
]

# --- Herramientas ----------------------------------------------------------
HERRAMIENTAS: List[Item] = [
    Item("martillo", "herramienta", 1.0, 10, "Básico para construcción."),
    Item("destornillador", "herramienta", 0.3, 5, "Para tornillos y ajustes."),
    Item("taladro", "herramienta", 2.0, 25, "Perfora casi cualquier superficie."),
    Item(
        "cortador laser",
        "herramienta",
        1.8,
        45,
        "Herramienta de corte de alta precisión.",
    ),
    Item(
        "kit de reparaciones",
        "herramienta",
        3.0,
        30,
        "Conjunto para arreglos rápidos.",
    ),
]

# Organize items by type for easy lookup
ITEMS_BY_TYPE: Dict[str, List[Item]] = {
    "materia_prima": MATERIA_PRIMA,
    "combustible": COMBUSTIBLES,
    "objeto_raro": OBJETOS_RAROS,
    "artefacto": ARTEFACTOS,
    "arma": ARMAS,
    "herramienta": HERRAMIENTAS,
}

# Flatten list with all items
ITEMS: List[Item] = [item for group in ITEMS_BY_TYPE.values() for item in group]

# List of item names for backwards compatibility
ITEM_NAMES: List[str] = [item.nombre for item in ITEMS]
