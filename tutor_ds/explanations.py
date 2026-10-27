from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

from tutor_ds.catalog import DEFECTS
from tutor_ds.models import Detection, Finding


def _join_es(items: Sequence[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} y {items[-1]}"


def _format_d1(context: Mapping[str, Any]) -> str:
    if context["scope_kind"] == "función":
        return (
            f"La función `{context['scope']}` mezcla cálculo de negocio "
            f"(`{context['calculation']}`) con E/S (`{context['io']}`)."
        )
    return (
        f"El módulo mezcla cálculo de negocio (`{context['calculation']}`) "
        f"con E/S (`{context['io']}`)."
    )


def _format_d2(context: Mapping[str, Any]) -> str:
    count = context["count"]
    lines = context["lines"]
    occurrence = "vez" if count == 1 else "veces"
    line_word = "línea" if len(lines) == 1 else "líneas"
    line_list = ", ".join(str(line) for line in lines)
    return (
        f"Número mágico `{context['value']}`: aparece {count} {occurrence} "
        f"en {context['usage']} ({line_word} {line_list})."
    )


def _format_d3(context: Mapping[str, Any]) -> str:
    line_list = ", ".join(str(line) for line in context["lines"])
    return (
        f"Se repite un bloque equivalente de {context['nodes']} nodos en "
        f"{context['count']} lugares (líneas {line_list}): `{context['snippet']}`."
    )


def _format_d4(context: Mapping[str, Any]) -> str:
    return (
        f"Script largo sin funciones: {context['statements']} sentencias a nivel "
        "superior y ninguna definición de función o clase."
    )


def _format_d5(context: Mapping[str, Any]) -> str:
    values = context["values"]
    shown = ", ".join(f"`{value}`" for value in values[:4])
    if len(values) > 4:
        shown += ", …"
    return (
        f"Condicional encadenado: {context['branches']} ramas comparan "
        f"`{context['variable']}` con los valores {shown}."
    )


def _format_d6(context: Mapping[str, Any]) -> str:
    functions = _join_es([f"`{name}`" for name in context["functions"]])
    params = ", ".join(f"`{name}`" for name in context["params"])
    return (
        f"Datos que viajan juntos: las funciones {functions} "
        f"repiten los parámetros {params}."
    )


_FORMATTERS: dict[str, Callable[[Mapping[str, Any]], str]] = {
    "D1": _format_d1,
    "D2": _format_d2,
    "D3": _format_d3,
    "D4": _format_d4,
    "D5": _format_d5,
    "D6": _format_d6,
}

_EVIDENCE: dict[str, Callable[[Mapping[str, Any]], str]] = {
    "D1": lambda context: str(context["calculation"]),
    "D2": lambda context: str(context["value"]),
    "D3": lambda context: str(context["snippet"]),
    "D4": lambda context: f"{context['statements']} sentencias",
    "D5": lambda context: str(context["variable"]),
    "D6": lambda context: ", ".join(context["params"]),
}


def build_findings(detections: Iterable[Detection]) -> tuple[Finding, ...]:
    findings = []
    for detection in detections:
        spec = DEFECTS[detection.code]
        context = detection.context
        findings.append(
            Finding(
                code=detection.code,
                defect=spec.name,
                message=_FORMATTERS[detection.code](context),
                remedy=spec.remedy,
                line=detection.line,
                column=detection.column,
                severity=(
                    detection.severity
                    if detection.severity is not None
                    else spec.severity
                ),
                paradigms=spec.paradigms,
                evidence=_EVIDENCE[detection.code](context),
            )
        )
    return tuple(sorted(findings, key=lambda finding: (finding.line, finding.code)))
