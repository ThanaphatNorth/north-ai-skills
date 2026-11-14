"""Checks a and b: the plugin manifest against the marketplace file and against the agent files on disk."""
from __future__ import annotations

import glob
import os
from typing import List

from .model import MANIFEST, PLUGIN, PLUGIN_NAME, Finding, error, load_json

MARKETPLACE = ".claude-plugin/marketplace.json"


def check_versions(repo: str) -> List[Finding]:
    """An error when the plugin's version in the marketplace file differs from its own manifest's."""
    market, manifest = load_json(repo, MARKETPLACE), load_json(repo, MANIFEST)
    if market is None or manifest is None:
        return [error("version", "cannot read %s as JSON" % rel)
                for rel, data in ((MARKETPLACE, market), (MANIFEST, manifest)) if data is None]
    listed = [p for p in market.get("plugins", []) if isinstance(p, dict) and p.get("name") == PLUGIN_NAME]
    if not listed:
        return [error("version", "%s has no plugin named %s" % (MARKETPLACE, PLUGIN_NAME))]
    ours, theirs = listed[0].get("version"), manifest.get("version")
    if ours != theirs:
        return [error("version", "%s says %s, %s says %s" % (MARKETPLACE, ours, MANIFEST, theirs))]
    return []


def check_agents_registered(repo: str) -> List[Finding]:
    """Errors where the manifest's agents array and the plugin's agents/*.md files differ either way."""
    manifest = load_json(repo, MANIFEST)
    if manifest is None:
        return [error("agents", "cannot read %s as JSON" % MANIFEST)]
    out = []
    entries = manifest.get("agents")
    if not isinstance(entries, list):
        out.append(error("agents", "%s has no agents array" % MANIFEST))
        entries = []
    registered = {os.path.normpath(str(e)): str(e) for e in entries}
    on_disk = sorted("agents/" + os.path.basename(p)
                     for p in glob.glob(os.path.join(repo, PLUGIN, "agents", "*.md")))
    for rel in on_disk:
        if rel not in registered:
            out.append(error("agents", "%s/%s is not in plugin.json's agents array, "
                                       "so the plugin does not load it" % (PLUGIN, rel)))
    for norm in sorted(registered):
        if norm not in on_disk:
            out.append(error("agents", "plugin.json registers %s, which does not exist" % registered[norm]))
    return out
