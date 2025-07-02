# utils/__init__.py
"""Init utils package & apply global patches."""

from importlib import import_module
import_module("utils.httpx_proxy_patch")   # noqa: F401