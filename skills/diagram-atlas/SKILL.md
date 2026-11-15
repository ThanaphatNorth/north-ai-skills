---
name: diagram-atlas
description: Draw real-looking architecture and deployment-topology diagrams, the kind an engineer draws in draw.io for an architecture document, with cloud or data-center icons, nested network groups (AWS cloud, region, VPC, subnets, or on-premise data center, DMZ, app, data and management zones, racks, Kubernetes clusters), numbered connectors, and tables saying what talks to what, how, and how each component is deployed. Outputs an HTML page (figure plus tables) and a PNG. Supports AWS, on-premise and hybrid setups. Use this whenever someone wants to draw, visualise or explain a system's architecture, infrastructure, deployment, network or components and how they connect, for example "วาด diagram", "วาด architecture", "deploy component ยังไง", "อะไรคุยกับอะไร", "แผนผังระบบ", "on-premise diagram", "infra diagram", "topology", even if they don't say "diagram". Prefer it over animated or step-by-step explainers for architecture pictures.
---

# Diagram Atlas

Architecture and deployment-topology diagrams for AWS, on-premise and hybrid systems. `SKILL.md` holds the process; the layout rules and platform catalogs live in `references/`, worked examples in `examples/`, and the drawing kit in `scripts/`. Reply in the user's language.

The goal is a picture that looks like a real architecture figure: the reader sees where each component runs and who talks to whom, then reads the tables for how. People reject anything that looks like a slide animation or a toy flowchart, so draw it the way an engineer lays out draw.io: every box placed by hand on a grid, real service icons, nested network groups.

## 1. Pin down what to draw

"Deploy diagram" has two readings: the **runtime topology** (where each component runs, what connects to what) and the **CI/CD pipeline**. They are different pictures. Unless the request clearly says pipeline, release or CI/CD, draw the topology, and if it could be either, ask one question naming both before drawing.

Also settle, from the request or the code (ask only for what you cannot find):
- **Platform:** AWS, on-premise, or hybrid. Read `references/aws.md` or `references/onprem.md`; for hybrid read both, then the hybrid section of `references/onprem.md`.
- **Scope:** which components, which environment (usually production), and whether other teams' systems appear as one box or in detail.
- **Language** of labels and tables (`lang="th"` or `"en"`).

## 2. Gather facts before placing anything

Every box and line must be true. Read the sources: infrastructure code (Terraform, Helm, compose), the app's env/config (what it connects to), Dockerfiles (ports, base image), the architecture doc if one exists. Read the branch that production runs (`git show origin/develop:path` without checking out).

Write down, for each component: where it runs (deployed as), who owns it, and each connection: protocol, direction, authentication. A fact that is planned rather than built, or that you inferred, gets said so in the table ("แผน", "assumed"). Leave out WAF, encryption, rate limits and the like unless a source shows them. Never draw secrets, IPs, account IDs or hostnames.

## 3. Lay it out

Copy the closest worked example and redraw it for this system, keeping its structure:
- `examples/aws_example.py`: web apps on S3 + CloudFront, API and AI service on ECS Fargate, Aurora, SQS, SES.
- `examples/onprem_example.py`: hospital data center with DMZ, firewalls, Kubernetes cluster, primary/replica DB, NAS, management zone, vendor VPN.
- `examples/hybrid_example.py`: hospital LAN and data center on the left, AWS on the right, one site-to-site VPN between them; also shows how to add an icon the kit lacks.

`examples/aws-example.png`, `examples/onprem-example.png` and `examples/hybrid-example.png` show the finished look to aim for; open the one that matches before you start.

Read `references/layout.md` first: it holds the placement rules that keep lines out of labels, learned from real rejections. The short version:
- Outside → in: people and partners on the left, then the edge, then the cloud/data-center box with zones inside, shared or regional services in a column on the right.
- Number every connector with a badge; the number is the row in the "what talks to what" table. Labels on lines stay out of the picture.
- Put zone and subnet names where no line passes (usually top-right or bottom-right), and keep team-box titles short.

`scripts/archkit.py` gives you `group()` for containers, `icon`/`icon_l`/`icon_r` for components, `flow(points, n, at, kind)` for numbered connectors, `label()` for free text, and `render()` for output. `flow()` is `path()` plus `badge()` in one call; the AWS example still uses the two separately, which draws the same thing. Icon and group names are listed in the platform references. When an icon is missing, add it from your drawing script with `icons.GLYPH.update({"name": (category, svg)})` (see the hybrid example) rather than editing the skill.

## 4. Render, lint, look

```bash
python3 my_diagram.py <out_dir>
```

`render(out_base, title, lead, fig, talks, deploy, lang)` writes `<out_base>.html` (figure + Table 1 "what talks to what, how" + Table 2 "deployed as") and `<out_base>.png`, then prints lint hits: connector segments estimated to run through text, badges on top of each other, and arrowheads hidden under an icon. It cannot see a label crossing a box border or a line running along one, so the look below still matters. Fix every hit or confirm by eye that it is a false alarm.

Then open the PNG and look at it yourself, zooming where the picture is dense. Check: lines through text, labels outside their box, an arrowhead hidden under an icon, a line running along a box border, badges on top of each other, text clipped at the edge. Expect two or three rounds of nudging coordinates. Never hand over a diagram you have not looked at.

Before writing into the user's folders, check the target path (`test -e`); `render()` overwrites. Keep the drawing script beside the output (for example `<project>/.doc_src/diagrams/`) so the figure can be regenerated; scratchpads get wiped.

## 5. Hand over

Give the HTML and PNG paths as links with their absolute paths, say which facts were planned or assumed, and name anything in the picture the user did not state. Offer the next useful step in one line (an English version, a second environment, a hybrid view).

For a figure inside a formal document (Architecture, DR Plan), draw it here and place the SVG or PNG in that document.
