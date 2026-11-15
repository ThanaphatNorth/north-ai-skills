# Layout rules

> Read when: placing anything on a diagram, before the first render, and again when lint reports a line through text or a picture looks crowded.

Diagrams are SVG placed by coordinates on a viewBox about 1260 × 800 to 830. Text stays at 11 px or more (about 7 pt printed on landscape A4).

## Reading order

- **Left, outside everything:** people (browser, users, laptop, mobile) and partners (vendor box). Group people by where they sit (internet, hospital LAN as a `site` group).
- **Edge:** CDN or perimeter firewall, between the people and the big container.
- **The big container:** `cloud` > `region` > `vpc` > subnets (AWS), or `dc` > zones (on-premise).
- **Right column:** regional or shared services (S3, SES, Secrets Manager, ECR, CloudWatch) or the management zone (bastion, monitoring, directory, CI/CD, backup).
- **Outside, bottom-left:** external services (LLM providers, payment gateway, SMS) in a `box` group, reached through NAT with a dotted line.

Keep the main user path on one straight horizontal line (user → edge → load balancer). Data stores go at the bottom, in their own subnet or zone.

## Connectors

- Orthogonal only: give `flow()` points that change x or y, never both.
- One badge per connector story; two lines of the same story (chat user and admin user to the CDN) share a number.
- Kinds: `web` and `data` look the same on purpose (solid ink; the name only documents what travels, the table says how), `static` dashed blue (CDN to static files), `sync` dashed green (replication), `ops` dashed pink (admin access, logs, monitoring), `out` dotted grey (to the internet through NAT).
- Enter icons from the side when a label sits under the icon; enter from above when the label sits to the right.
- Route through gaps: between team boxes, between zones, between the VPC edge and the right column. Leave at least 12 px between parallel lines and 16 px between lines leaving the same icon edge.
- A shared service used by every task (secrets, image registry, logs) gets one bracket line from the column to the app subnet edge, not one line per service.
- A line must not run along a box border. Move it 6 to 8 px off.

## Labels (where lines go wrong)

These caused every rejected round so far:
- **Subnet and zone names:** make the group with an empty label (`group(..., "priv", "")`) and place the name with `label()` at the top-right or bottom-right corner, wherever no line passes. The group's top-left tag icon stays.
- **Team or boundary boxes:** keep the title short ("ทีม web", "ทีม AI") so vertical lines entering the box clear it. Put repo names in Table 2.
- **Label next to a vertical line:** put it on the side the line does not cross, and never under an icon whose connector leaves downward.
- **Label beside an icon:** icon labels sit under the icon (`icon_l`) or to its right (`icon_r`); for a database at the bottom, put the label left (`lines(..., "end")`) when a line arrives from the right.
- **Badges:** place on a straight segment, at least 24 px from a corner and from other badges, never on a border crossing.

## Tables

- **Table 1, what talks to what:** `#`, from → to, how they connect (protocol, direction, format such as JSON or SSE), authentication and limits (token, service token, security group, who may connect). Ports, IPs and hostnames stay out.
- **Table 2, deployed as:** component, deployed as (container on ECS Fargate, static files on S3 behind CloudFront, VM in the app zone, appliance in the DMZ), owner team.

Write Thai the way an engineer explains their own system: short, direct, no Thai term followed by its English twin in brackets, no "X เป็นผู้...".

## Sources

- How the figures in hand-drawn architecture documents are laid out, and the rounds a user rejected while drawing a real system topology in November 2026: subnet labels crossed by lines, long team titles, a line running along a box border.
- AWS Architecture Icons, guidance on groups and connectors — https://aws.amazon.com/architecture/icons/
