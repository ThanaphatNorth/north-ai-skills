"""Icon glyphs and group tags that archkit adds to the kit. Pure SVG data, one glyph per line,
so this file is excluded from the line-width budget (see .ndev.toml)."""
import icons

W = icons.W

icons.GRAD.update({
    # on-premise palette: muted, so a reader never mistakes an appliance for an AWS service
    "op-net": ("#1E4E79", "#3A7BBF"),
    "op-compute": ("#37474F", "#6B7F8E"),
    "op-data": ("#1F3A93", "#4A6FD1"),
    "op-sec": ("#8E1B1B", "#C94A3A"),
    "op-ops": ("#5B3A8C", "#8A63C2"),
})

icons.GLYPH.update({
    # AWS extras
    "ecs": ("compute", f'<g {W}><rect x="9" y="17" width="13" height="12"/><rect x="26" y="17" width="13" height="12"/>'
            '<rect x="17.5" y="32" width="13" height="8"/><path d="M13 12h22"/></g>'),
    "ecr": ("compute", f'<g {W}><rect x="12" y="12" width="24" height="20" rx="1"/><path d="M12 19h24M18 32v5h12v-5"/></g>'),
    "lambda": ("compute", f'<g {W}><path d="M14 38h6l6-13 6 13h4M17 10h6l13 28"/></g>'),
    "eks": ("compute", f'<g {W}><path d="M24 8l13 7v18l-13 7-13-7V15z"/><path d="M20 18v12M20 24l7-6M20 24l7 6"/></g>'),
    "cloudfront": ("network", f'<g {W}><circle cx="24" cy="24" r="13"/><path d="M11 24h26M24 11c-6 5-6 21 0 26M24 11c6 5 6 21 0 26"/></g>'),
    "apigw": ("network", f'<g {W}><path d="M14 10v28M34 10v28"/><path d="M19 24h10M25 20l4 4-4 4"/></g>'),
    "route53": ("network", f'<g {W}><circle cx="24" cy="24" r="13"/><path d="M17 30c2-8 4-12 7-12s5 4 7 12"/></g>'),
    "vgw": ("network", f'<g {W}><path d="M24 8l12 5v9c0 8-5 14-12 18-7-4-12-10-12-18v-9z"/><path d="M18 24h12M25 20l4 4-4 4"/></g>'),
    "tgw": ("network", f'<g {W}><circle cx="24" cy="24" r="5"/><circle cx="11" cy="13" r="3"/><circle cx="37" cy="13" r="3"/>'
            '<circle cx="11" cy="35" r="3"/><circle cx="37" cy="35" r="3"/><path d="M14 15l6 6M34 15l-6 6M14 33l6-6M34 33l-6-6"/></g>'),
    "dx": ("network", f'<g {W}><path d="M8 24h32"/><path d="M14 18l-6 6 6 6M34 18l6 6-6 6"/><rect x="19" y="19" width="10" height="10"/></g>'),
    "sqs": ("integration", f'<g {W}><rect x="8" y="17" width="32" height="14" rx="2"/><path d="M15 17v14M21 17v14M27 17v14M33 17v14"/></g>'),
    "rds": ("database", f'<g {W}><ellipse cx="24" cy="14" rx="11" ry="4"/><path d="M13 14v20c0 2.2 4.9 4 11 4s11-1.8 11-4V14"/></g>'),
    "elasticache": ("database", f'<g {W}><rect x="11" y="13" width="26" height="22" rx="2"/><path d="M16 19h16M16 24h16M16 29h10"/></g>'),
    "vectordb": ("database", f'<g {W}><ellipse cx="24" cy="14" rx="11" ry="4"/><path d="M13 14v20c0 2.2 4.9 4 11 4s11-1.8 11-4V14"/></g>'
                 '<g fill="#fff"><circle cx="19" cy="24" r="1.8"/><circle cx="27" cy="29" r="1.8"/><circle cx="29" cy="21" r="1.8"/></g>'),
    # on-premise
    "firewall": ("op-sec", f'<g {W}><rect x="9" y="12" width="30" height="24"/><path d="M9 20h30M9 28h30M17 12v8M29 12v8M23 20v8M15 28v8M31 28v8"/></g>'),
    "router": ("op-net", f'<g {W}><circle cx="24" cy="24" r="12"/><path d="M18 20h12M26 16l4 4-4 4M30 28H18M22 24l-4 4 4 4"/></g>'),
    "switch": ("op-net", f'<g {W}><rect x="8" y="16" width="32" height="16" rx="2"/><path d="M14 21h20M30 18l4 3-4 3M34 27H14M18 24l-4 3 4 3"/></g>'),
    "lb": ("op-net", f'<g {W}><circle cx="15" cy="24" r="6"/><path d="M21 24h8M20 21l9-7M20 27l9 7"/>'
           '<circle cx="33" cy="13" r="3"/><circle cx="33" cy="24" r="3"/><circle cx="33" cy="35" r="3"/></g>'),
    "proxy": ("op-net", f'<g {W}><rect x="10" y="14" width="28" height="20" rx="2"/><path d="M4 24h6M38 24h6M17 21h14M17 27h14"/></g>'),
    "vpn": ("op-net", f'<g {W}><path d="M24 8l12 5v9c0 8-5 14-12 18-7-4-12-10-12-18v-9z"/><path d="M19 24l4 4 7-8"/></g>'),
    "internet": ("op-net", f'<g {W}><circle cx="24" cy="24" r="13"/><path d="M11 24h26M24 11c-6 5-6 21 0 26M24 11c6 5 6 21 0 26"/></g>'),
    "dns": ("op-net", f'<g {W}><rect x="10" y="12" width="28" height="24" rx="2"/><path d="M15 20h18M15 26h12M15 31h8"/></g>'),
    "vm": ("op-compute", f'<g {W}><rect x="9" y="11" width="30" height="20" rx="1"/><path d="M15 37h18M24 31v6M15 17h8M15 22h12"/></g>'),
    "server-onprem": ("op-compute", f'<g {W}><rect x="11" y="8" width="26" height="9" rx="1"/><rect x="11" y="20" width="26" height="9" rx="1"/>'
                      '<rect x="11" y="32" width="26" height="9" rx="1"/><path d="M15 12.5h2M15 24.5h2M15 36.5h2"/></g>'),
    "k8s": ("op-compute", f'<g {W}><path d="M24 7l14 7 3 15-10 12H17L7 29l3-15z"/><circle cx="24" cy="25" r="4"/>'
            '<path d="M24 14v7M24 29v7M14 20l6 3M28 27l6 3M14 30l6-3M28 23l6-3"/></g>'),
    "container": ("op-compute", f'<g {W}><path d="M24 9l13 7v16l-13 7-13-7V16z"/><path d="M11 16l13 7 13-7M24 23v16"/></g>'),
    "device": ("op-compute", f'<g {W}><rect x="9" y="12" width="30" height="20" rx="2"/><path d="M14 38h20M24 32v6"/><circle cx="32" cy="22" r="3"/><path d="M14 18h10M14 23h8"/></g>'),
    "analyzer": ("op-compute", f'<g {W}><rect x="8" y="20" width="32" height="18" rx="2"/><path d="M15 20V9M21 20V9M27 20V9"/>'
                 '<path d="M13 9h4M19 9h4M25 9h4M31 26h5M31 31h5"/><rect x="12" y="25" width="15" height="8"/></g>'),
    "db": ("op-data", f'<g {W}><ellipse cx="24" cy="13" rx="12" ry="4"/><path d="M12 13v22c0 2.2 5.4 4 12 4s12-1.8 12-4V13"/>'
           '<path d="M12 24c0 2.2 5.4 4 12 4s12-1.8 12-4"/></g>'),
    "cache": ("op-data", f'<g {W}><rect x="10" y="13" width="28" height="22" rx="2"/><path d="M24 17l-5 8h10l-5 8"/></g>'),
    "nas": ("op-data", f'<g {W}><rect x="10" y="9" width="28" height="30" rx="2"/><path d="M15 16h18M15 22h18M15 28h18"/><circle cx="32" cy="34" r="1.2"/></g>'),
    "mq": ("op-data", f'<g {W}><rect x="8" y="17" width="32" height="14" rx="2"/><path d="M15 17v14M21 17v14M27 17v14M33 17v14"/></g>'),
    "objectstore": ("op-data", f'<g {W}><ellipse cx="24" cy="13" rx="13" ry="4"/><path d="M11 13l4 23c.5 2 4.2 3 9 3s8.5-1 9-3l4-23"/></g>'),
    "directory": ("op-sec", f'<g {W}><circle cx="20" cy="17" r="5"/><path d="M11 35c0-6 4-10 9-10s9 4 9 10"/><path d="M31 15h7M31 21h7M31 27h5"/></g>'),
    "bastion": ("op-sec", f'<g {W}><rect x="9" y="12" width="30" height="24" rx="2"/><path d="M14 20l5 4-5 4M22 29h8"/></g>'),
    "hsm": ("op-sec", f'<g {W}><rect x="13" y="22" width="22" height="16" rx="2"/><path d="M17 22v-5a7 7 0 0 1 14 0v5"/><path d="M24 28v4"/></g>'),
    "vault": ("op-sec", f'<g {W}><circle cx="17" cy="24" r="7"/><path d="M24 24h15M33 24v6M37 24v4"/></g>'),
    "monitor": ("op-ops", f'<g {W}><circle cx="21" cy="21" r="10"/><path d="M28 28l9 9"/><path d="M15 23l4-4 3 3 5-5"/></g>'),
    "backup-onprem": ("op-ops", f'<g {W}><path d="M35 19a12 12 0 1 0 1 9"/><path d="M36 12v8h-8"/><rect x="19" y="20" width="9" height="9"/></g>'),
    "cicd": ("op-ops", f'<g {W}><path d="M10 24a8 8 0 0 1 14-5l4 5 4 5a8 8 0 1 0 0-10l-4 5-4 5a8 8 0 0 1-14-5z"/></g>'),
    "siem": ("op-ops", f'<g {W}><path d="M10 34h28M14 34V24M21 34V16M28 34V20M35 34V12"/></g>'),
})

# group tags for on-premise containers (24x24, same shape as the AWS group tags)
TAGS = {
    "t-dc": ("#232F3E", '<path d="M6 19V8l6-3 6 3v11M9 11h2M13 11h2M9 14h2M13 14h2M10 19v-3h4v3" fill="none" stroke="#fff" stroke-width="1.3"/>'),
    "t-dmz": ("#C8511B", '<path d="M12 5l6 3v5c0 3.5-2.5 6-6 7-3.5-1-6-3.5-6-7V8z" fill="none" stroke="#fff" stroke-width="1.4"/>'),
    "t-zone": ("#1E6F9F", '<rect x="6" y="7" width="12" height="10" rx="1" fill="none" stroke="#fff" stroke-width="1.4"/><path d="M9 11h6M9 14h4" stroke="#fff" stroke-width="1.2"/>'),
    "t-data": ("#2E3FA0", '<ellipse cx="12" cy="8" rx="5" ry="2" fill="none" stroke="#fff" stroke-width="1.3"/><path d="M7 8v8c0 1.1 2.2 2 5 2s5-.9 5-2V8" fill="none" stroke="#fff" stroke-width="1.3"/>'),
    "t-mgmt": ("#5B3A8C", '<circle cx="12" cy="12" r="4" fill="none" stroke="#fff" stroke-width="1.4"/><path d="M12 5v3M12 16v3M5 12h3M16 12h3" stroke="#fff" stroke-width="1.4"/>'),
    "t-rack": ("#455A64", '<rect x="7" y="5" width="10" height="14" fill="none" stroke="#fff" stroke-width="1.3"/><path d="M9 9h6M9 12h6M9 15h6" stroke="#fff" stroke-width="1.2"/>'),
    "t-cluster": ("#326CE5", '<path d="M12 5l6 3 1.5 7-4.5 5h-6L4.5 15 6 8z" fill="none" stroke="#fff" stroke-width="1.3"/><circle cx="12" cy="12" r="2" fill="#fff"/>'),
    "t-site": ("#2E7D32", '<path d="M5 18V10l7-5 7 5v8M10 18v-4h4v4" fill="none" stroke="#fff" stroke-width="1.4"/>'),
    "t-partner": ("#6D4C41", '<circle cx="9" cy="10" r="2.5" fill="none" stroke="#fff" stroke-width="1.3"/><circle cx="15" cy="10" r="2.5" fill="none" stroke="#fff" stroke-width="1.3"/><path d="M5 18c0-3 2-5 4-5s4 2 4 5M11 18c0-3 2-5 4-5s4 2 4 5" fill="none" stroke="#fff" stroke-width="1.2"/>'),
}
