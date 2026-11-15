# On-premise and hybrid diagrams

> Read when: the system runs in a customer's own data center or server room, or the on-premise half of a hybrid picture.

Worked example: `examples/onprem_example.py`.

## Nesting

| Kind | Draw for |
|---|---|
| `dc` | the data center or server room (name the owner: "Data center ของโรงพยาบาล") |
| `dmz` | DMZ: reverse proxy, WAF appliance, VPN gateway, mail relay |
| `zone-app` | application zone or VLAN: load balancer, app servers, Kubernetes cluster |
| `zone-data` | data zone: database servers, NAS, object storage, message broker |
| `zone-mgmt` | management zone: bastion, monitoring, directory, CI/CD, backup |
| `cluster` | a Kubernetes or VM cluster inside a zone |
| `rack` | a physical rack, only when rack placement matters (DR, capacity) |
| `site` | another network the users sit in (hospital LAN, branch office) |
| `partner` | a vendor or partner who connects in (support over VPN) |
| `box`, `plain` | a team boundary or a loose column |

Firewalls sit between zones as icons, not as groups: perimeter firewall at the data-center edge, internal firewall between DMZ and the app zone. Lines that cross a zone boundary pass through the firewall icon that guards it.

## Icons

On-premise tiles use a muted palette so they never pass for AWS services:
- network: `firewall router switch lb proxy vpn internet dns`
- compute: `vm server-onprem k8s container device analyzer` (`device` for a medical or IoT device, `analyzer` for a lab instrument)
- data: `db cache nas mq objectstore`
- security: `directory bastion hsm vault`
- operations: `monitor backup-onprem cicd siem`

Generic line icons (`users browser laptop server`) work for people and anything without its own tile.

## Hybrid (on-premise + cloud)

Follow `examples/hybrid_example.py`:
- **Left:** the customer's networks. People and devices in a `site` group (hospital LAN), the customer's servers in a `dc` group beside it.
- **Right:** the cloud account with its own `cloud` > `region` > `vpc` > subnets.
- **Between:** one VPN gateway icon on each side, the on-premise one in the on-premise palette (`vpn`) and the AWS one in the AWS palette (`vgw`), joined by one numbered `flow` for the tunnel (or `dx` for Direct Connect, `tgw` when a Transit Gateway sits in the middle).
- **Users reaching an internal service:** route their line into the on-premise VPN gateway, not straight into AWS, so the picture shows that the traffic rides the tunnel. A public web app behind CloudFront gets its own line that bypasses the tunnel.
- Put the tunnel's facts in Table 1: encryption, which side starts it, which networks it routes. Each side's internal connectors follow its own reference.

## Typical connections (Table 1 wording)

| From → to | How | Auth and limits |
|---|---|---|
| internet user → perimeter firewall → reverse proxy | HTTPS into the DMZ | firewall opens HTTPS only, WAF filters requests |
| staff → internal firewall → load balancer | HTTPS on the hospital network | staff VLAN only |
| reverse proxy → internal firewall → load balancer | HTTPS from the DMZ into the app zone | internal firewall accepts the proxy only |
| app → database | SQL with TLS | app's own DB account, app zone only |
| primary → replica | continuous replication | used for recovery |
| app → directory | LDAPS | read-only service account |
| vendor → VPN → bastion | VPN, then admin access through the bastion only | MFA, sessions recorded |
| servers → monitoring | logs and metrics | agents send outbound only |
| backup server → NAS | nightly database and file backup | backups kept apart from serving machines |

## Sources

- NIST SP 800-41 Rev. 1, Guidelines on Firewalls and Firewall Policy (DMZ and zone layout) — https://csrc.nist.gov/pubs/sp/800/41/r1/final
- Kubernetes icon set — https://github.com/kubernetes/community/tree/master/icons
- AWS Site-to-Site VPN user guide (the usual hybrid link) — https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html
