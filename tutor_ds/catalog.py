from tutor_ds.models import DefectSpec, Paradigm, Severity


DEFECTS: dict[str, DefectSpec] = {
    "D1": DefectSpec(
        code="D1",
        name="Lógica de negocio mezclada con entrada/salida",
        remedy=(
            "Extrae el cálculo a una función pura que reciba datos y devuelva "
            "el resultado; deja `input()` y `print()` en una capa de interfaz "
            "aparte."
        ),
        paradigms=(Paradigm.MODULAR,),
        severity=Severity.ALTA,
    ),
    "D2": DefectSpec(
        code="D2",
        name="Números mágicos",
        remedy=(
            "Sustituye el literal por una constante con nombre (`IVA = 0.19`) "
            "o un parámetro de configuración."
        ),
        paradigms=(Paradigm.FUNCIONAL, Paradigm.OO),
        severity=Severity.MEDIA,
    ),
    "D3": DefectSpec(
        code="D3",
        name="Duplicación de código",
        remedy="Extrae el bloque repetido a una función y llámala desde los dos lugares.",
        paradigms=(Paradigm.FUNCIONAL,),
        severity=Severity.MEDIA,
    ),
    "D4": DefectSpec(
        code="D4",
        name="Script largo sin funciones",
        remedy=(
            "Divide el script en funciones con una responsabilidad clara y un "
            "bloque `main()` que orqueste."
        ),
        paradigms=(Paradigm.FUNCIONAL, Paradigm.MODULAR),
        severity=Severity.ALTA,
    ),
    "D5": DefectSpec(
        code="D5",
        name="Condicional encadenado por tipo",
        remedy=(
            "Reemplaza la cadena por polimorfismo (una clase por tipo) o por "
            "una tabla de reglas."
        ),
        paradigms=(Paradigm.OO, Paradigm.MODULAR),
        severity=Severity.ALTA,
    ),
    "D6": DefectSpec(
        code="D6",
        name="Datos que viajan juntos",
        remedy=(
            "Agrupa los datos que viajan juntos en una clase o `dataclass` y "
            "pasa un solo objeto."
        ),
        paradigms=(Paradigm.OO,),
        severity=Severity.MEDIA,
    ),
}
