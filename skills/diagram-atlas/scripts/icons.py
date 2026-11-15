"""AWS-style service icons (category colour tile + white glyph), drawn by hand as SVG symbols."""

GRAD = {
    "compute": ("#C8511B", "#FF9900"),
    "database": ("#2E27AD", "#527FFF"),
    "storage": ("#1B660F", "#6CAE3E"),
    "network": ("#4D27A8", "#A166FF"),
    "security": ("#BD0816", "#FF5252"),
    "mgmt": ("#B0084D", "#FF4F8B"),
    "integration": ("#B0084D", "#FF4F8B"),
}

W = 'fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'

GLYPH = {
    "ec2": ("compute", f'<g {W}><rect x="15" y="15" width="18" height="18"/><rect x="20" y="20" width="8" height="8"/>'
            '<path d="M19 9v6M24 9v6M29 9v6M19 33v6M24 33v6M29 33v6M9 19h6M9 24h6M9 29h6M33 19h6M33 24h6M33 29h6"/></g>'),
    "aurora": ("database", f'<g {W}><ellipse cx="24" cy="14" rx="11" ry="4"/><path d="M13 14v20c0 2.2 4.9 4 11 4s11-1.8 11-4V14"/>'
               '<path d="M13 21c0 2.2 4.9 4 11 4s11-1.8 11-4M13 28c0 2.2 4.9 4 11 4s11-1.8 11-4"/></g>'),
    "efs": ("storage", f'<g {W}><path d="M10 16h10l3 3h15v17H10z"/><path d="M15 24h18M15 29h18"/></g>'),
    "s3": ("storage", f'<g {W}><ellipse cx="24" cy="13" rx="13" ry="4"/><path d="M11 13l4 23c.5 2 4.2 3 9 3s8.5-1 9-3l4-23"/></g>'),
    "alb": ("network", f'<g {W}><circle cx="15" cy="24" r="6"/><path d="M21 24h8M20 21l9-7M20 27l9 7"/>'
            '<circle cx="33" cy="13" r="3"/><circle cx="33" cy="24" r="3"/><circle cx="33" cy="35" r="3"/></g>'),
    "waf": ("security", f'<g {W}><rect x="10" y="12" width="28" height="24"/><path d="M10 20h28M10 28h28M18 12v8M30 12v8M24 20v8M16 28v8M32 28v8"/></g>'),
    "secrets": ("security", f'<g {W}><circle cx="17" cy="24" r="7"/><path d="M24 24h15M33 24v6M37 24v4"/></g>'),
    "identity": ("security", f'<g {W}><circle cx="20" cy="17" r="5"/><path d="M11 35c0-6 4-10 9-10s9 4 9 10"/><path d="M30 26l3 3 6-6"/></g>'),
    "cloudwatch": ("mgmt", f'<g {W}><circle cx="21" cy="21" r="10"/><path d="M28 28l9 9"/><path d="M15 23l4-4 3 3 5-5"/></g>'),
    "ssm": ("mgmt", f'<g {W}><rect x="9" y="12" width="30" height="24" rx="2"/><path d="M14 20l5 4-5 4M22 29h8"/></g>'),
    "backup": ("storage", f'<g {W}><path d="M35 19a12 12 0 1 0 1 9"/><path d="M36 12v8h-8"/><rect x="19" y="20" width="9" height="9"/></g>'),
    "sns": ("integration", f'<g {W}><circle cx="17" cy="24" r="4"/><path d="M22 24h14M21 20l13-8M21 28l13 8"/><path d="M33 9l3 3-3 3M33 33l3 3-3 3M33 21l3 3-3 3"/></g>'),
    "ses": ("integration", f'<g {W}><rect x="9" y="14" width="30" height="21" rx="1"/><path d="M9 15l15 11 15-11"/></g>'),
    "nat": ("network", f'<g {W}><circle cx="24" cy="24" r="13"/><path d="M15 24h18M28 19l5 5-5 5"/></g>'),
    "igw": ("network", f'<g {W}><path d="M14 38V14a10 10 0 0 1 20 0v24"/><path d="M24 20v14M19 29l5 5 5-5"/></g>'),
    "vpcep": ("network", f'<g {W}><rect x="11" y="11" width="26" height="26" rx="3"/><path d="M18 24h12M25 19l5 5-5 5"/></g>'),
    "acm": ("security", f'<g {W}><rect x="10" y="11" width="28" height="20" rx="1"/><path d="M15 18h12M15 23h8"/><circle cx="31" cy="31" r="5"/><path d="M28 35l-1 5 4-2 4 2-1-5"/></g>'),
    "kms": ("security", f'<g {W}><rect x="13" y="22" width="22" height="16" rx="2"/><path d="M17 22v-5a7 7 0 0 1 14 0v5"/><path d="M24 28v4"/></g>'),
    "flowlogs": ("network", f'<g {W}><path d="M10 16h20M10 24h28M10 32h20"/><path d="M33 12l4 4-4 4M33 28l4 4-4 4"/></g>'),
}


def symbols():
    out = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>']
    for cat, (a, b) in GRAD.items():
        out.append(f'<linearGradient id="g-{cat}" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
    for name, (cat, glyph) in GLYPH.items():
        out.append(f'<symbol id="i-{name}" viewBox="0 0 48 48"><rect width="48" height="48" fill="url(#g-{cat})"/>{glyph}</symbol>')
    # generic (non-AWS) icons: grey line style, like the general-icon set used in draw.io AWS diagrams
    G = 'fill="none" stroke="#232F3E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    out += [
        f'<symbol id="i-user" viewBox="0 0 48 48"><g {G}><circle cx="24" cy="15" r="7"/><path d="M10 40c0-8 6-14 14-14s14 6 14 14z"/></g></symbol>',
        f'<symbol id="i-users" viewBox="0 0 48 48"><g {G}><circle cx="18" cy="16" r="6"/><path d="M6 38c0-7 5-12 12-12s12 5 12 12z"/><circle cx="32" cy="14" r="5"/><path d="M31 24c6 0 11 4 11 11h-9"/></g></symbol>',
        f'<symbol id="i-mobile" viewBox="0 0 48 48"><g {G}><rect x="14" y="5" width="20" height="38" rx="3"/><path d="M21 37h6M14 11h20M14 32h20"/></g></symbol>',
        f'<symbol id="i-laptop" viewBox="0 0 48 48"><g {G}><rect x="10" y="10" width="28" height="19" rx="1"/><path d="M5 35h38l-3-6H8z"/></g></symbol>',
        f'<symbol id="i-browser" viewBox="0 0 48 48"><g {G}><rect x="6" y="9" width="36" height="30" rx="2"/><path d="M6 16h36"/><circle cx="11" cy="12.5" r=".8"/><circle cx="14" cy="12.5" r=".8"/></g></symbol>',
        f'<symbol id="i-dev" viewBox="0 0 48 48"><g {G}><rect x="6" y="8" width="36" height="24" rx="2"/><path d="M18 16l-5 4 5 4M30 16l5 4-5 4M26 14l-4 12M16 40h16M24 32v8"/></g></symbol>',
        f'<symbol id="i-git" viewBox="0 0 48 48"><rect width="48" height="48" fill="#30343C"/><g fill="none" stroke="#fff" stroke-width="2"><circle cx="16" cy="12" r="3.5"/><circle cx="16" cy="36" r="3.5"/><circle cx="32" cy="20" r="3.5"/><path d="M16 15.5v17M32 23.5c0 6-16 4-16 9"/></g></symbol>',
        f'<symbol id="i-server" viewBox="0 0 48 48"><g {G}><rect x="10" y="8" width="28" height="10" rx="1"/><rect x="10" y="20" width="28" height="10" rx="1"/><rect x="10" y="32" width="28" height="10" rx="1"/><path d="M15 13h2M15 25h2M15 37h2"/></g></symbol>',
        f'<symbol id="i-mail" viewBox="0 0 48 48"><g {G}><rect x="7" y="12" width="34" height="24" rx="1"/><path d="M7 13l17 12 17-12"/></g></symbol>',
        f'<symbol id="i-doc" viewBox="0 0 48 48"><g {G}><path d="M12 6h17l8 8v28H12z"/><path d="M29 6v8h8M17 22h14M17 28h14M17 34h9"/></g></symbol>',
        f'<symbol id="i-lock" viewBox="0 0 48 48"><g {G}><rect x="12" y="22" width="24" height="18" rx="2"/><path d="M17 22v-6a7 7 0 0 1 14 0v6"/></g></symbol>',
        '<symbol id="i-cloudflare" viewBox="0 0 64 40"><path d="M14 34h40a9 9 0 0 0 1-18 13 13 0 0 0-25-4 9 9 0 0 0-13 7A8 8 0 0 0 14 34z" fill="#F38020"/><path d="M47 34h9a6 6 0 0 0-2-11 8 8 0 0 0-7 3z" fill="#FBAD41"/></symbol>',
        # group tags (AWS diagram group icons)
        '<symbol id="t-cloud" viewBox="0 0 24 24"><rect width="24" height="24" fill="#232F3E"/><path d="M6 16h11a3 3 0 0 0 0-6 4.5 4.5 0 0 0-8.5-1A3.5 3.5 0 0 0 6 16z" fill="none" stroke="#fff" stroke-width="1.4"/></symbol>',
        '<symbol id="t-region" viewBox="0 0 24 24"><rect width="24" height="24" fill="#00A4A6"/><path d="M7 19V5M7 6h10l-2 3 2 3H7" fill="none" stroke="#fff" stroke-width="1.4"/></symbol>',
        '<symbol id="t-vpc" viewBox="0 0 24 24"><rect width="24" height="24" fill="#8C4FFF"/><path d="M6 15h11a3 3 0 0 0 0-6 4.5 4.5 0 0 0-8.5-1A3.5 3.5 0 0 0 6 15z" fill="none" stroke="#fff" stroke-width="1.3"/><rect x="9.5" y="14" width="5" height="4" fill="#fff"/></symbol>',
        '<symbol id="t-pub" viewBox="0 0 24 24"><rect width="24" height="24" fill="#7AA116"/><rect x="7" y="11" width="10" height="8" rx="1" fill="none" stroke="#fff" stroke-width="1.4"/><path d="M9 11V8a3 3 0 0 1 6 0" fill="none" stroke="#fff" stroke-width="1.4"/></symbol>',
        '<symbol id="t-priv" viewBox="0 0 24 24"><rect width="24" height="24" fill="#00A4A6"/><rect x="7" y="11" width="10" height="8" rx="1" fill="none" stroke="#fff" stroke-width="1.4"/><path d="M9 11V8a3 3 0 0 1 6 0v3" fill="none" stroke="#fff" stroke-width="1.4"/></symbol>',
        '<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#232F3E"/></marker>',
        '<marker id="arr-r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#BD0816"/></marker>',
        '<marker id="arr-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#147EBA"/></marker>',
    ]
    out.append("</defs></svg>")
    return "\n".join(out)
