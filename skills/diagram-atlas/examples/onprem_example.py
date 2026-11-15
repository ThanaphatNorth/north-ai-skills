"""Worked example (on-premise): a hospital web system in its own data center.
DMZ with reverse proxy and VPN, internal firewall, app zone with a Kubernetes cluster, data zone with a primary and
replica database and NAS, management zone (bastion, monitoring, directory, CI/CD, backup).
Copy this file, keep the structure, redraw the coordinates for your system.
Run:  python3 onprem_example.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from archkit import badge, flow, group, icon, icon_l, icon_r, label, lines, render, svg  # noqa: E402


def topology():
    b = []
    # containers: data center > zones; people and partners outside
    b += [group(215, 15, 1035, 790, "dc", "Data center ของโรงพยาบาล (on-premise)"),
          group(300, 48, 650, 132, "dmz", ""), label(940, 172, "DMZ", "end", fill="#A2410F"),
          group(300, 270, 650, 290, "zone-app", ""), label(940, 552, "App zone", "end", fill="#1E5F8A"),
          group(320, 360, 400, 180, "cluster", ""), label(330, 532, "Kubernetes cluster", "start", 11.5, "#326CE5"),
          group(300, 590, 650, 200, "zone-data", ""), label(940, 782, "Data zone", "end", fill="#2E3FA0"),
          group(978, 48, 252, 520, "zone-mgmt", "Management zone"),
          group(10, 200, 190, 120, "partner", "Vendor"),
          group(10, 370, 190, 150, "site", "Hospital LAN")]

    # connectors first, numbered; the tables under the figure explain each number
    b += [flow([(92, 110), (233, 110)], 1, (160, 110), "web"),
          flow([(277, 120), (418, 120)], 1, (350, 120), "web"),
          flow([(122, 440), (208, 440), (208, 225), (418, 225)], 2, (208, 345), "web"),
          flow([(440, 142), (440, 203)], 3, (440, 160), "web"),
          flow([(440, 247), (440, 298)], 3, (440, 272), "web"),
          flow([(440, 340), (440, 408)], 4, (440, 374), "web"),
          flow([(462, 430), (578, 430)], 5, (520, 430)),
          flow([(600, 492), (600, 575), (440, 575), (440, 636)], 6, (520, 575)),
          flow([(462, 660), (618, 660)], 7, (540, 660), "sync"),
          flow([(622, 430), (700, 430), (700, 310), (988, 310)], 8, (840, 310)),
          flow([(92, 250), (150, 250), (150, 134), (233, 134)], 9, (150, 192), "ops"),
          flow([(255, 98), (255, 80), (800, 80), (800, 98)], 9, (620, 80), "ops"),
          flow([(822, 120), (988, 120)], 9, (900, 120), "ops"),
          flow([(680, 360), (680, 240), (960, 240), (960, 210), (988, 210)], 10, (820, 240), "ops"),
          flow([(988, 410), (722, 410)], 11, (860, 410)),
          flow([(986, 510), (965, 510), (965, 660), (882, 660)], 12, (965, 590))]

    # people and partners
    b += [icon_l(70, 110, "browser", ["ผู้ใช้ภายนอก", "ผ่าน internet"], 42, 11.5),
          icon_l(70, 250, "laptop", ["ทีม support", "ของ vendor"], 40, 11),
          icon_l(70, 440, "users", ["เจ้าหน้าที่", "ในโรงพยาบาล"], 42, 11.5)]
    # edge and DMZ
    b += [icon(255, 120, "firewall", 44), lines(255, 160, ["Firewall", "ขอบเครือข่าย"], 11, "middle", None, True),
          icon(440, 120, "proxy", 44), lines(468, 116, ["Reverse proxy + WAF", "TLS จบที่นี่"], 11, "start", None, True),
          icon(800, 120, "vpn", 44), lines(800, 158, ["VPN gateway", "เฉพาะ vendor"], 11, "middle", None, True),
          icon(440, 225, "firewall", 40), lines(466, 229, ["Firewall ภายใน"], 11, "start", None, True)]
    # app zone
    b += [icon(440, 320, "lb", 40), lines(466, 316, ["Load balancer", "ภายใน"], 11, "start", None, True),
          icon_l(440, 430, "container", ["web", "frontend pod"], 44, 11),
          icon_l(600, 430, "container", ["api", "backend pod"], 44, 11)]
    # data zone
    b += [icon_l(440, 660, "db", ["Database", "primary"], 44, 11),
          icon_l(640, 660, "db", ["Database", "replica"], 44, 11),
          icon_l(860, 660, "nas", ["NAS", "ไฟล์ · ข้อมูลสำรอง"], 44, 11)]
    # management zone
    mg = [(110, "bastion", ["Bastion host", "ทางเข้าดูแลระบบ"]), (210, "monitor", ["Monitoring", "log · metric · alert"]),
          (310, "directory", ["Active Directory", "บัญชีเจ้าหน้าที่"]), (410, "cicd", ["CI/CD + registry", "build · deploy"]),
          (510, "backup-onprem", ["Backup server", "สำรองทุกคืน"])]
    b += [icon_r(1005, y, n, lab, 34, 11) for y, n, lab in mg]
    return svg(1260, 820, "".join(b))


TALKS = [
    ("1", "ผู้ใช้ภายนอก → Firewall → Reverse proxy", "HTTPS จาก internet เข้า DMZ", "firewall เปิดเฉพาะ HTTPS · WAF กรอง request ก่อนเข้าระบบ"),
    ("2", "เจ้าหน้าที่ → Firewall ภายใน → Load balancer", "HTTPS ภายในเครือข่ายโรงพยาบาล", "รับเฉพาะ VLAN ของเจ้าหน้าที่"),
    ("3", "Reverse proxy → Firewall ภายใน → Load balancer", "HTTPS จาก DMZ เข้า App zone", "firewall ภายในรับจาก reverse proxy เท่านั้น"),
    ("4", "Load balancer → web", "HTTP ผ่าน ingress ของ cluster", "health check ก่อนส่ง request"),
    ("5", "web → api", "REST ภายใน cluster", "token ของผู้ใช้ส่งต่อใน header"),
    ("6", "api → Database primary", "SQL พร้อม TLS", "บัญชีฐานข้อมูลเฉพาะของ api · รับจาก App zone เท่านั้น"),
    ("7", "Database primary → replica", "replication ต่อเนื่อง", "ใช้กู้ระบบเมื่อ primary ขัดข้อง"),
    ("8", "api → Active Directory", "LDAPS ตรวจบัญชีเจ้าหน้าที่", "service account แบบอ่านอย่างเดียว"),
    ("9", "vendor → Firewall → VPN → Bastion", "VPN แล้วเข้าระบบผ่าน bastion เท่านั้น", "VPN พร้อม MFA · ทุก session ถูกบันทึก"),
    ("10", "Kubernetes cluster → Monitoring", "ส่ง log และ metric", "agent ส่งออกทางเดียว"),
    ("11", "CI/CD → Kubernetes cluster", "deploy image จาก registry ภายใน", "service account ของ pipeline"),
    ("12", "Backup server → NAS", "สำรองฐานข้อมูลจาก replica และไฟล์ทุกคืน", "เก็บข้อมูลสำรองแยกจากเครื่องที่ให้บริการ"),
]

DEPLOY = [
    ("web, api", "container บน Kubernetes cluster ใน App zone", "ทีมพัฒนา"),
    ("Database", "primary และ replica บน VM คนละเครื่องใน Data zone", "ทีม infra"),
    ("Reverse proxy + WAF, VPN gateway", "appliance หรือ VM ใน DMZ", "ทีม network"),
    ("Firewall, Load balancer", "อุปกรณ์เครือข่ายของ data center", "ทีม network"),
    ("Bastion, Monitoring, Active Directory, CI/CD, Backup", "VM ใน Management zone", "ทีม infra"),
]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    render(os.path.join(out, "onprem-example"), "ระบบของโรงพยาบาล: component และการเชื่อมต่อ (on-premise)",
           "ตัวอย่างระบบที่ติดตั้งใน data center ของโรงพยาบาลเอง แบ่ง DMZ, App, Data และ Management zone",
           topology(), TALKS, DEPLOY)
