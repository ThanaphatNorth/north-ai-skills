"""Worked example (hybrid): a hospital lab system. Analyzers and staff on the hospital LAN, an interface server
and the HIS in the hospital data center, the API and database on AWS, joined by a site-to-site VPN.
Drawn by a fresh agent from a one-paragraph request; inferred facts are marked (assumed) in the tables.
It also shows how to add an icon the kit lacks, from the drawing script, without editing the skill.
Run:  python3 hybrid_example.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import icons  # noqa: E402
from archkit import W, badge, flow, group, icon, icon_l, icon_r, label, lines, render, svg  # noqa: E402,F401

# an icon the kit does not ship: add it here, from the drawing script (category + white strokes on a 48 x 48 grid).
# "lab-rack" is only a demonstration and is not drawn below.
icons.GLYPH.update({
    "lab-rack": ("op-compute", f'<g {W}><rect x="10" y="10" width="28" height="28" rx="2"/><path d="M17 16v16M24 16v16M31 16v16"/></g>'),
})

SITE_C, DC_C = "#2E7D32", "#232F3E"


def topology():
    b = []
    # containers
    b += [group(10, 60, 195, 360, "site", "LAN โรงพยาบาล"),
          group(225, 160, 320, 440, "dc", "Data center ของโรงพยาบาล"),
          group(600, 20, 650, 690, "cloud", "AWS Cloud"),
          group(620, 170, 617, 525, "region", "AWS region"),
          group(640, 205, 390, 475, "vpc", "VPC"),
          group(720, 235, 295, 255, "priv", ""), label(1005, 255, "Private subnet (App)", "end", fill="#007A7C"),
          group(720, 505, 295, 160, "priv", ""), label(1005, 655, "Private subnet (Data)", "end", fill="#007A7C"),
          group(1050, 205, 175, 150, "plain", "บริการระดับ Region", 11.5)]

    # connectors first, icons and labels on top
    b += [flow([(127, 330), (308, 330)], 1, (166, 330), "data"),                               # analyzer -> interface (HL7)
          flow([(352, 330), (455, 330), (455, 380), (483, 380)], 2, (400, 330), "data"),       # interface -> VPN gw
          flow([(527, 390), (658, 390)], 3, (572, 390), "web"),                                # site-to-site VPN
          flow([(702, 390), (773, 390)], 4, (745, 390), "web"),                                # VGW -> ALB internal
          flow([(817, 390), (878, 390)], 5, (847, 390), "web"),                                # ALB -> API
          flow([(900, 412), (900, 568)], 6, (900, 455), "data"),                               # API -> Aurora
          flow([(352, 520), (435, 520), (435, 402), (483, 402)], 7, (395, 520), "data"),       # HIS -> VPN gw (pull)
          flow([(127, 108), (678, 108)], 8, (420, 108), "web"),                                # users -> CloudFront
          flow([(722, 108), (1040, 108), (1040, 275), (1120, 275)], 9, (880, 108), "static"),  # CloudFront -> S3
          flow([(127, 132), (505, 132), (505, 368)], 10, (505, 250), "web")]                   # users -> VPN gw (API calls)

    # hospital LAN
    b += [icon_l(105, 120, "users", ["แพทย์ · เจ้าหน้าที่", "ใช้เว็บผ่าน browser"], 42, 11),
          icon_l(105, 330, "analyzer", ["เครื่องวิเคราะห์แล็บ", "analyzer"], 44, 11)]
    # hospital data center
    b += [icon_l(330, 330, "vm", ["Interface server", "VM · รับผล HL7"], 44, 11),
          icon_l(330, 520, "server-onprem", ["HIS", "ของโรงพยาบาล"], 44, 11),
          icon(505, 390, "vpn", 44), lines(505, 430, ["VPN gateway", "ของโรงพยาบาล"], 11, "middle", None, True)]
    # AWS edge
    b += [icon(700, 108, "cloudfront", 44), lines(700, 146, ["CloudFront", "เว็บของแพทย์"], 11, "middle", None, True)]
    # VPC
    b += [icon(680, 390, "vgw", 40), lines(680, 426, ["VPN gateway", "ฝั่ง AWS"], 11, "middle", None, True),
          icon(795, 390, "alb", 40), lines(795, 426, ["ALB internal"], 11, "middle", None, True),
          icon_r(900, 390, "ecs", ["API", "ECS Fargate"], 44, 11),
          icon(900, 590, "aurora", 44), lines(870, 586, ["Aurora PostgreSQL", "ฐานข้อมูลผลแล็บ"], 11, "end", None, True)]
    # regional services
    b += [icon_l(1137, 275, "s3", ["Amazon S3", "ไฟล์เว็บของแพทย์"], 34, 11)]
    return svg(1260, 725, "".join(b))


TALKS = [
    ("1", "เครื่องวิเคราะห์แล็บ → Interface server", "ส่งผลตรวจเป็นข้อความ HL7 ใน LAN โรงพยาบาล (MLLP บน TCP: assumed)",
     "จำกัดด้วยเครือข่ายภายใน (assumed)"),
    ("2", "Interface server → API", "HTTPS ส่งผลที่แปลงแล้วขึ้น AWS ผ่าน VPN (รูปแบบ JSON: assumed)",
     "token ของ service (assumed)"),
    ("3", "VPN gateway ของโรงพยาบาล ↔ VPN gateway ฝั่ง AWS", "site-to-site VPN เข้ารหัส IPsec (assumed) ส่งต่อทราฟฟิกระหว่างเครือข่ายโรงพยาบาลกับ VPC",
     "ฝั่งที่เริ่มเชื่อมต่อและช่วง network ที่ route ยังไม่ได้ระบุ"),
    ("4", "VPN gateway ฝั่ง AWS → ALB internal", "request จากเครือข่ายโรงพยาบาลเข้า VPC", "ALB ไม่เปิด internet รับจากช่วง network ของโรงพยาบาลเท่านั้น (assumed)"),
    ("5", "ALB internal → API", "HTTP ภายใน VPC", "security group รับจาก ALB เท่านั้น (assumed)"),
    ("6", "API → Aurora PostgreSQL", "SQL", "บัญชีฐานข้อมูลของ API · รับจาก API เท่านั้น (assumed)"),
    ("7", "HIS → API", "HTTPS ผ่าน VPN เส้นเดียวกัน HIS เป็นฝั่งดึงผลแล็บ", "token ของ service (assumed)"),
    ("8", "แพทย์ → CloudFront", "HTTPS โหลดไฟล์เว็บของแพทย์ ออก internet ของโรงพยาบาล (assumed)", "ไฟล์ static เปิดให้โหลดได้ ข้อมูลผู้ป่วยไม่อยู่ในไฟล์"),
    ("9", "CloudFront → S3", "ดึงไฟล์ static ของเว็บแพทย์", "bucket ไม่เปิด public อ่านผ่าน CloudFront เท่านั้น (assumed)"),
    ("10", "เว็บของแพทย์ → API", "HTTPS จาก browser ใน LAN ผ่าน VPN ไปที่ ALB internal (assumed: ALB เป็น internal จึงเรียกจาก internet ไม่ได้)",
     "ผู้ใช้ login ก่อนเรียก API (assumed)"),
]

DEPLOY = [
    ("เครื่องวิเคราะห์แล็บ", "อุปกรณ์ใน LAN ของโรงพยาบาล", "ห้องแล็บ (assumed)"),
    ("Interface server", "VM ใน data center ของโรงพยาบาล", "ทีม IT โรงพยาบาล (assumed)"),
    ("HIS", "ระบบ on-premise ของโรงพยาบาล วางใน data center เดียวกัน (assumed)", "ทีม IT โรงพยาบาล (assumed)"),
    ("VPN gateway ของโรงพยาบาล", "firewall หรือ VPN appliance ที่ขอบ data center (assumed)", "ทีม network โรงพยาบาล (assumed)"),
    ("VPN gateway ฝั่ง AWS", "virtual private gateway หรือ transit gateway ต่อกับ VPC (assumed)", "ทีมระบบ LIS (assumed)"),
    ("API", "container บน ECS Fargate ใน private subnet หลัง ALB internal", "ทีมระบบ LIS (assumed)"),
    ("Aurora PostgreSQL", "cluster ใน private subnet (Data)", "ทีมระบบ LIS (assumed)"),
    ("เว็บของแพทย์", "ไฟล์ static บน S3 ส่งผ่าน CloudFront", "ทีมระบบ LIS (assumed)"),
]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    render(os.path.join(out, "hybrid-example"), "ระบบ LIS แบบ hybrid: component และการเชื่อมต่อ",
           "เครื่องวิเคราะห์แล็บ, interface server และ HIS อยู่ที่โรงพยาบาล ส่วน API, ฐานข้อมูล และเว็บของแพทย์อยู่บน AWS "
           "สองฝั่งคุยกันผ่าน site-to-site VPN เส้นเดียว",
           topology(), TALKS, DEPLOY)
