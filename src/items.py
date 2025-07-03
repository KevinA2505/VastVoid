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
    Item("oro", "materia_prima", 4.0, 50, "Metal precioso, muy valorado."),
    Item("plata", "materia_prima", 3.8, 30, "Metal precioso, buen conductor."),
    Item("aluminio", "materia_prima", 1.0, 4, "Metal ligero y resistente a la corrosión."),
    Item("diamante", "materia_prima", 0.1, 100, "El mineral más duro y valioso."),
    Item("cuarzo", "materia_prima", 1.0, 7, "Cristal común usado en electrónica."),
    Item("grafeno", "materia_prima", 0.05, 70, "Material bidimensional extremadamente resistente."),
    Item("platino", "materia_prima", 4.5, 60, "Metal noble, muy raro y resistente."),
    Item("cobalto", "materia_prima", 2.5, 18, "Metal ferromagnético, usado en aleaciones."),
    Item("tungsteno", "materia_prima", 3.2, 22, "Metal con alto punto de fusión."),
    Item("neodimio", "materia_prima", 1.7, 28, "Elemento de tierras raras para imanes potentes."),
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
    Item("hidrogeno liquido", "combustible", 0.3, 15, "Combustible criogénico para cohetes."),
    Item("helio-3", "combustible", 0.05, 80, "Isótopo ligero para fusión nuclear."),
    Item("plutonio", "combustible", 2.0, 90, "Elemento radiactivo para energía nuclear."),
    Item("biocombustible", "combustible", 1.5, 12, "Combustible ecológico de origen orgánico."),
    Item("metano", "combustible", 0.7, 8, "Gas natural, combustible común."),
    Item("cristal de energia", "combustible", 0.4, 60, "Cristal que emite energía constante."),
    Item("combustible de fusion", "combustible", 0.9, 75, "Mezcla avanzada para reactores de fusión."),
    Item("carbon", "combustible", 2.5, 3, "Combustible fósil sólido."),
    Item("petroleo crudo", "combustible", 1.8, 7, "Combustible fósil sin refinar."),
    Item("vapor condensado", "combustible", 0.6, 18, "Vapor de alta presión, fuente de energía."),
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
    Item("ojo de gorgon", "objeto_raro", 0.8, 120, "Reliquia que petrifica al contacto."),
    Item("gema de alma", "objeto_raro", 0.2, 150, "Gema que contiene una esencia vital."),
    Item("pluma de fenix", "objeto_raro", 0.1, 110, "Pluma que otorga resurrección."),
    Item("mapa estelar antiguo", "objeto_raro", 0.5, 95, "Mapa que muestra rutas galácticas ocultas."),
    Item("huevo de dragon", "objeto_raro", 5.0, 200, "Un huevo de una criatura mítica."),
    Item("arena del tiempo", "objeto_raro", 0.1, 130, "Arena que manipula el flujo temporal."),
    Item("lagrima de sirena", "objeto_raro", 0.05, 105, "Lágrima que cura cualquier enfermedad."),
    Item("corazon de estrella", "objeto_raro", 3.0, 180, "Núcleo de una estrella en miniatura."),
    Item("espejo de los deseos", "objeto_raro", 1.0, 140, "Espejo que muestra los deseos más profundos."),
    Item("flor eterea", "objeto_raro", 0.02, 160, "Una flor que solo crece en dimensiones alternativas."),
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
    Item("disco de navegacion", "artefacto", 0.6, 65, "Dispositivo para trazar rutas espaciales."),
    Item("generador de escudo", "artefacto", 2.0, 85, "Crea un campo de fuerza protector."),
    Item("traductor universal", "artefacto", 0.3, 70, "Permite entender cualquier idioma."),
    Item("globo terraqueo holografico", "artefacto", 1.2, 90, "Proyecta mapas interactivos del universo."),
    Item("reloj de bolsillo temporal", "artefacto", 0.1, 100, "Permite breves saltos en el tiempo."),
    Item("anillo de levitacion", "artefacto", 0.05, 80, "Anillo que permite al portador flotar."),
    Item("matriz de teletransporte", "artefacto", 4.0, 120, "Dispositivo para reubicación instantánea."),
    Item("modulador de voz", "artefacto", 0.2, 35, "Cambia la voz del usuario."),
    Item("brazalete de fuerza", "artefacto", 0.7, 60, "Aumenta la fuerza física del portador."),
    Item("proyector de camuflaje", "artefacto", 1.5, 95, "Genera un campo de invisibilidad."),
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
    Item("arco de energia", "arma", 1.5, 45, "Arco que dispara flechas de energía."),
    Item("lanzallamas", "arma", 4.0, 55, "Arroja un chorro de fuego."),
    Item("mina de proximidad", "arma", 0.8, 20, "Explosivo que detona al acercarse un enemigo."),
    Item("cuchillo de combate", "arma", 0.7, 10, "Arma blanca básica."),
    Item("lanzamisiles", "arma", 8.0, 150, "Arma pesada que dispara misiles explosivos."),
    Item("blaster sónico", "arma", 1.0, 40, "Arma que aturde con ondas de sonido."),
    Item("escopeta de iones", "arma", 3.5, 70, "Dispara una ráfaga de iones paralizantes."),
    Item("flagelador de partículas", "arma", 6.0, 110, "Arma devastadora que desintegra molecularmente."),
    Item("hacha de batalla", "arma", 2.8, 25, "Hacha pesada para combate cuerpo a cuerpo."),
    Item("cerbatana toxica", "arma", 0.4, 12, "Dispara dardos con veneno paralizante."),
    Item("laser de rafaga", "arma", 4.0, 70, "Haz continuo de alta energia de tres segundos."),
    Item("mina temporizada", "arma", 1.0, 20, "Explosivo que detona tras unos segundos."),
    Item("dron asistente", "arma", 2.0, 120, "Pequena nave que orbita y dispara."),
    Item("misil hiperguiado", "arma", 3.5, 90, "Proyectil pesado con guiado extremo."),
    Item("arma generica", "arma", 1.0, 20, "Arma básica de poco poder."),
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
    Item("llave inglesa", "herramienta", 0.8, 8, "Para ajustar tuercas y pernos."),
    Item("soldador", "herramienta", 1.5, 20, "Para unir metales."),
    Item("escáner de minerales", "herramienta", 0.6, 50, "Detecta depósitos de minerales cercanos."),
    Item("analizador de datos", "herramienta", 0.4, 35, "Decodifica información compleja."),
    Item("cable de anclaje", "herramienta", 2.5, 18, "Permite asegurar objetos pesados."),
    Item("multipico", "herramienta", 1.2, 28, "Herramienta versátil para minería y excavación."),
    Item("bateria portatil", "herramienta", 1.0, 15, "Fuente de energía para dispositivos."),
    Item("botiquin de primeros auxilios", "herramienta", 0.9, 22, "Contiene vendajes y medicinas básicas."),
    Item("dispensador de agua", "herramienta", 0.5, 10, "Provee agua potable purificada."),
    Item("comunicador interestelar", "herramienta", 0.7, 60, "Permite la comunicación a través de grandes distancias."),
]

# --- Vehiculos ----------------------------------------------------------
VEHICULOS: List[Item] = [
    Item("boat", "vehiculo", 8.0, 20, "Pequeña embarcación algo quemada pero útil."),
]

# Organize items by type for easy lookup
ITEMS_BY_TYPE: Dict[str, List[Item]] = {
    "materia_prima": MATERIA_PRIMA,
    "combustible": COMBUSTIBLES,
    "objeto_raro": OBJETOS_RAROS,
    "artefacto": ARTEFACTOS,
    "arma": ARMAS,
    "herramienta": HERRAMIENTAS,
    "vehiculo": VEHICULOS,
}

# Flatten list with all items
ITEMS: List[Item] = [item for group in ITEMS_BY_TYPE.values() for item in group]

# List of item names for backwards compatibility
ITEM_NAMES: List[str] = [item.nombre for item in ITEMS]