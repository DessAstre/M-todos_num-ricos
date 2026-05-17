"""Evaluador seguro de expresiones matemáticas.

Sólo permite operadores aritméticos, llamadas a funciones explícitamente
autorizadas y constantes numéricas. No se ejecuta `eval` directo.
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Callable, Mapping


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluar_nodo(nodo, nombres: Mapping[str, object]):
    if isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, (int, float, complex)):
            return nodo.value
        raise ValueError("Sólo se permiten constantes numéricas.")

    if isinstance(nodo, ast.Name):
        if nodo.id in nombres:
            return nombres[nodo.id]
        raise ValueError(f"Nombre no permitido: {nodo.id}")

    if isinstance(nodo, ast.BinOp):
        op = type(nodo.op)
        if op not in _BIN_OPS:
            raise ValueError("Operador binario no permitido.")
        izq = _evaluar_nodo(nodo.left, nombres)
        der = _evaluar_nodo(nodo.right, nombres)
        return _BIN_OPS[op](izq, der)

    if isinstance(nodo, ast.UnaryOp):
        op = type(nodo.op)
        if op not in _UNARY_OPS:
            raise ValueError("Operador unario no permitido.")
        return _UNARY_OPS[op](_evaluar_nodo(nodo.operand, nombres))

    if isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name):
            raise ValueError("Sólo se permiten llamadas directas a funciones autorizadas.")
        nombre = nodo.func.id
        if nombre not in nombres or not callable(nombres[nombre]):
            raise ValueError(f"Función no permitida: {nombre}")
        if nodo.keywords:
            raise ValueError("No se permiten argumentos nombrados.")
        args = [_evaluar_nodo(a, nombres) for a in nodo.args]
        return nombres[nombre](*args)

    raise ValueError("Expresión no permitida.")


def evaluar_expresion(expresion: str, nombres: Mapping[str, object]):
    """Evalúa una expresión matemática a partir de los nombres permitidos."""
    try:
        arbol = ast.parse(expresion, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Expresión inválida: {exc}") from exc
    return _evaluar_nodo(arbol.body, nombres)


def construir_entorno_matematico(extras: dict | None = None) -> dict:
    """Devuelve un diccionario con todas las funciones/constantes del módulo `math`."""
    entorno = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    entorno["abs"] = abs
    if extras:
        entorno.update(extras)
    return entorno
