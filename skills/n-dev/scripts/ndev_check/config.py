"""The repo's `.ndev.toml`: budgets, excludes and layer rules for the structure check.

`from_dict` is pure; `load` is the only function that reads a file. Unknown keys and wrong types are errors,
so a typo never silently falls back to a default. The file is always parsed with `tomlsubset`, so it means
the same thing on every Python version."""
from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from . import tomlsubset
from .fileio import read_regular_file
from .model import Budgets, Layer

DEFAULT_NAME = ".ndev.toml"
_BUDGET_KEYS = {name.replace("_", "-"): name for name in Budgets.__dataclass_fields__}
_TOP_KEYS = ("budgets", "check", "layers", "profile")
_LAYER_KEYS = ("paths", "imports", "may-import")


class ConfigError(ValueError):
    """The config file is missing where one was named, unreadable, not the TOML subset, or says something
    the check does not know (an unknown key, a wrong type, an undeclared layer)."""


@dataclass(frozen=True)
class Config:
    """What a `.ndev.toml` says, validated; the empty Config stands for "no file"."""
    path: Optional[str] = None                               # repo-relative path of the file read, or None
    budgets: Dict[str, int] = field(default_factory=dict)    # Budgets field name -> value
    exclude: Tuple[str, ...] = ()
    layers: Tuple[Layer, ...] = ()

    def apply(self, defaults: Budgets, flags: Mapping[str, Optional[int]]) -> Budgets:
        """Defaults, overridden by the file, overridden by the flags that were given (None = not given)."""
        given = {k: v for k, v in flags.items() if v is not None}
        return replace(defaults, **{**self.budgets, **given})


def load(root: str, path: Optional[str]) -> Config:
    """Read `path` (or `.ndev.toml` at the root when None). A missing default file means no config; a file
    that is there but cannot be read or parsed is a ConfigError naming it, never a silent default."""
    rel = path or DEFAULT_NAME
    full = rel if os.path.isabs(rel) else os.path.join(root, rel)
    try:
        data = read_regular_file(full)
    except FileNotFoundError:
        if path:
            raise ConfigError("config file %s not found" % rel) from None
        if os.path.islink(full):
            raise ConfigError("config file %s is a symlink to a missing file" % rel) from None
        return Config()
    except OSError as e:  # a directory, no permission, a FIFO
        raise ConfigError("cannot read config file %s: %s" % (rel, e.strerror or e)) from None
    try:
        return replace(from_dict(tomlsubset.loads(_decode(data))), path=rel)
    except (tomlsubset.TomlError, ConfigError) as e:
        raise ConfigError("%s: %s" % (rel, e)) from None


def _decode(data: bytes) -> str:
    """The file's text with newlines as text mode reads them; bytes that are not UTF-8 name their line."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ConfigError("line %d: not valid UTF-8" % (data.count(b"\n", 0, e.start) + 1)) from None
    return text.replace("\r\n", "\n").replace("\r", "\n")


def from_dict(data: Mapping[str, Any]) -> Config:
    """The Config a parsed document describes (its `path` left unset). ConfigError on any key, type or
    layer name the check does not know."""
    _only(data, _TOP_KEYS, "the top level")
    check = _table(data, "check")
    _only(check, ("exclude",), "[check]")
    _only(_table(data, "profile"), ("path",), "[profile]")
    return Config(None, _budgets(_table(data, "budgets")), _strings(check.get("exclude", []), "[check] exclude"),
                  _layers(_table(data, "layers")))


def _budgets(table: Mapping[str, Any]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key, value in table.items():
        if key not in _BUDGET_KEYS:
            raise ConfigError("[budgets] has no key %r (known: %s)" % (key, ", ".join(sorted(_BUDGET_KEYS))))
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ConfigError("[budgets] %s must be a whole number >= 0" % key)
        out[_BUDGET_KEYS[key]] = value
    return out


def _layers(table: Mapping[str, Any]) -> Tuple[Layer, ...]:
    """The declared layers in file order. Every may-import name must be a declared layer."""
    layers = []
    for name, spec in table.items():
        where = "[layers.%s]" % name
        if not isinstance(spec, dict):
            raise ConfigError("%s must be a table" % where)
        _only(spec, _LAYER_KEYS, where)
        paths = _strings(spec.get("paths", []), where + " paths")
        if not paths:
            raise ConfigError("%s needs at least one entry in paths" % where)
        layers.append(Layer(name, paths, _strings(spec.get("imports", []), where + " imports"),
                            _strings(spec.get("may-import", []), where + " may-import")))
    names = {layer.name for layer in layers}
    for layer in layers:
        unknown = [n for n in layer.may_import if n not in names]
        if unknown:
            raise ConfigError("[layers.%s] may-import names unknown layer(s): %s" % (layer.name, ", ".join(unknown)))
    return tuple(layers)


def _table(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    """The table under `key`; {} when the document has none."""
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ConfigError("[%s] must be a table" % key)
    return value


def _strings(value: Any, where: str) -> Tuple[str, ...]:
    """The value as a tuple, once it is known to be an array of strings."""
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ConfigError("%s must be an array of strings" % where)
    return tuple(value)


def _only(data: Mapping[str, Any], allowed: Iterable[str], where: str) -> None:
    """Raise ConfigError when `data` holds a key that is not in `allowed`."""
    unknown = sorted(set(data) - set(allowed))
    if unknown:
        raise ConfigError("%s has unknown key(s): %s (known: %s)" % (where, ", ".join(unknown), ", ".join(allowed)))
