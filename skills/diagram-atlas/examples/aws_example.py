"""Worked example (AWS): a fictional web platform with an AI service on ECS Fargate, numbered connectors and both tables.
Copy this file, keep the structure, redraw the coordinates for your system.
Run:  python3 aws_example.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from archkit import BLUE, MUTED, PINK, T, badge, group, icon, icon_l, icon_r, lines, path, render, svg  # noqa: E402

def note(x, y, text, anchor="start", fill=MUTED):
    return T(x, y, text, 11, anchor, "normal", fill)


def topology():
    b = []
    # containers
    b += [group(215, 15, 1035, 800, "cloud", "AWS Cloud (บัญชี production)"),
          group(240, 48, 1000, 757, "region", "AWS region"),
          group(262, 82, 700, 713, "vpc", "VPC · ทุก service รันอย่างน้อย 1 task ต่อ AZ ใน 2 Availability Zone"),
          group(280, 112, 665, 96, "pub", ""), group(280, 224, 665, 396, "priv", ""), group(280, 636, 665, 146, "priv", ""),
          T(935, 128, "Public subnet", 12.5, "end", fill="#4C7A0B"),
          T(935, 244, "Private subnet (App)", 12.5, "end", fill="#007A7C"),
          T(935, 772, "Private subnet (Data)", 12.5, "end", fill="#007A7C"),
          group(296, 256, 224, 300, "box", "", 11.5), T(304, 272, "ทีม web", 11.5),
          group(660, 256, 270, 300, "box", "", 11.5), T(668, 272, "ทีม AI", 11.5),
          group(978, 90, 250, 700, "plain", "บริการระดับ Region", 11.5),
          group(10, 560, 190, 120, "box", "บริการภายนอก", 11.5)]

    # connectors first so icons and labels sit on top
    b += [path([(92, 100), (120, 100), (120, 150), (151, 150)]),                       # 1 user-web user
          path([(92, 240), (120, 240), (120, 170), (151, 170)]),                       # 1 admin user
          path([(175, 138), (175, 40), (970, 40), (970, 140), (986, 140)], BLUE, "5 4"),        # 2 static files
          path([(197, 160), (386, 160)]),                                              # 3 CloudFront -> ALB
          path([(408, 182), (408, 306)]),                                              # 4 ALB -> api
          path([(408, 392), (408, 676)]),                                              # 5 api -> MySQL
          path([(430, 318), (548, 318), (548, 216), (970, 216), (970, 232), (986, 232)]),                      # 6 api -> SES
          path([(430, 332), (573, 332)], marker=None), path([(607, 332), (711, 332)]),  # 7 api -> ALB int -> ai-api
          path([(735, 308), (735, 190), (800, 190), (800, 177)]),                      # 8 ai-api -> NAT
          path([(262, 620), (202, 620)], MUTED, "3 3"),                                # 8 NAT -> internet -> LLM
          path([(735, 392), (735, 676)]),                                              # 9 ai-api -> pgvector
          path([(757, 320), (945, 320), (945, 452), (981, 452)]),                      # 10 ai-api -> SQS
          path([(981, 468), (884, 468)]),                                              # 10 SQS -> ingest
          path([(860, 522), (860, 700), (759, 700)]),                                  # 11 ingest -> pgvector
          path([(986, 550), (972, 550), (972, 710), (986, 710)], PINK, "5 4", None), path([(972, 600), (947, 600)], PINK, "5 4")]                                 # 12 shared services -> tasks

    # users and edge (outside AWS)
    b += [icon_l(70, 100, "browser", ["ผู้ใช้งาน", "user-web (React)"], 42, 11.5),
          icon_l(70, 240, "browser", ["Admin องค์กร", "admin-web (React)"], 42, 11.5),
          icon(175, 160, "cloudfront", 44), lines(175, 200, ["CloudFront", "+ AWS WAF"], 11.5, "middle", None, True)]
    # public subnet
    b += [icon(408, 160, "alb", 40), lines(436, 156, ["ALB (public)", "รับจาก CloudFront เท่านั้น"], 11, "start", None, True),
          icon_r(800, 160, "nat", ["NAT gateway"], 30, 11)]
    # app subnet
    b += [icon_l(408, 330, "ecs", ["api", "NestJS · ECS Fargate"], 44, 11),
          icon(590, 332, "alb", 34), lines(590, 372, ["ALB internal", "api → ai-api เท่านั้น"], 11, "middle", None, True),
          icon_l(735, 330, "ecs", ["ai-api", "guard · RAG · model"], 44, 11),
          icon_l(860, 460, "ecs", ["ingest worker", "URL · PDF · OCR"], 44, 11)]
    # data subnet
    b += [icon(408, 700, "aurora", 44), lines(436, 696, ["Aurora MySQL", "writer + reader · ทีม web"], 11, "start", None, True),
          icon(735, 700, "vectordb", 44), lines(705, 696, ["Aurora PostgreSQL", "pgvector · ทีม AI"], 11, "end", None, True)]
    # regional services
    svc = [(140, "s3", ["Amazon S3", "ไฟล์ static ของสองแอป"]), (232, "ses", ["Amazon SES", "อีเมลเชิญ · รีเซ็ตรหัสผ่าน"]),
           (460, "sqs", ["Amazon SQS", "คิวงาน ingest"]), (550, "secrets", ["Secrets Manager", "+ KMS · secret ทุกตัว"]),
           (630, "ecr", ["Amazon ECR", "image ของทุก service"]), (710, "cloudwatch", ["CloudWatch", "log · metric · alarm"])]
    b += [icon_r(1005, y, n, lab, 34, 11) for y, n, lab in svc]
    # outside AWS
    b += [icon_r(40, 618, "server", ["LLM providers", "OpenAI · Gemini", "Anthropic"], 30, 10.5),
          note(192, 672, "ออกผ่าน NAT gateway", "end")]

    # numbered badges: the table under the figure says how each pair talks
    b += [badge(120, 125, 1), badge(120, 205, 1), badge(600, 40, 2), badge(300, 160, 3), badge(408, 244, 4),
          badge(408, 588, 5), badge(860, 216, 6), badge(660, 332, 7), badge(735, 250, 8), badge(231, 620, 8),
          badge(735, 588, 9), badge(945, 386, 10), badge(930, 468, 10), badge(860, 588, 11), badge(972, 660, 12)]
    return svg(1260, 830, "".join(b))


TALKS = [
    ("1", "ผู้ใช้ → CloudFront", "HTTPS ทั้งไฟล์หน้าเว็บและ request ของ api",
     "access token (JWT 15 นาที) ใน header Authorization · refresh token ใน cookie HttpOnly, Secure, SameSite=Strict"),
    ("2", "CloudFront → S3", "ดึงไฟล์ static ของ user-web และ admin-web", "bucket ไม่เปิด public อ่านได้ผ่าน CloudFront เท่านั้น"),
    ("3", "CloudFront → ALB (public)", "HTTPS ส่งต่อ request ของ api", "ALB รับเฉพาะ request จาก CloudFront"),
    ("4", "ALB → api", "HTTP ภายใน VPC", "security group รับจาก ALB เท่านั้น · api ตรวจ JWT, role และ tenant ทุก request"),
    ("5", "api → Aurora MySQL", "SQL ผ่าน TypeORM", "รหัสผ่านจาก Secrets Manager · ฐานข้อมูลรับจาก task ของ api เท่านั้น"),
    ("6", "api → Amazon SES", "SMTP ส่งอีเมลเชิญและลิงก์ตั้งรหัสผ่านใหม่", "credential จาก Secrets Manager"),
    ("7", "api → ALB internal → ai-api", "HTTP ภายใน VPC · JSON ไปที่ /v1/* · แชทตอบกลับเป็น SSE",
     "header header service token · ai-api ไม่ได้รับ token ของผู้ใช้"),
    ("8", "ai-api → LLM providers", "HTTPS ออก internet ผ่าน NAT gateway", "key ของ provider ที่ api ส่งมาใน header หรือ key ของ ai-service เอง"),
    ("9", "ai-api → Aurora PostgreSQL", "SQL ค้นเอกสารด้วย pgvector (RAG)", "ฐานข้อมูลรับจาก task ของ ai-service เท่านั้น"),
    ("10", "ai-api → SQS → ingest worker", "ai-api ส่งงาน ingest เข้าคิว แล้ว worker ดึงไปทำ", "IAM role ของ task"),
    ("11", "ingest worker → Aurora PostgreSQL", "SQL เขียน vector ของเอกสาร", "รหัสผ่านจาก Secrets Manager"),
    ("12", "ECS task ทุกตัว → Secrets Manager, ECR, CloudWatch", "รับ secret ตอนเริ่ม task · ดึง image · ส่ง log และ metric",
     "IAM role ของ task · ไม่มี secret อยู่ใน code หรือ image"),
]

DEPLOY = [
    ("user-web", "ไฟล์ static บน S3 ส่งผ่าน CloudFront", "web"),
    ("admin-web", "ไฟล์ static บน S3 ส่งผ่าน CloudFront คนละ domain กับ user-web", "web"),
    ("api", "container บน ECS Fargate ใน Private subnet (App) image เก็บใน ECR", "web"),
    ("ai-api", "container บน ECS Fargate หลัง ALB internal", "DS"),
    ("ingest worker", "container บน ECS Fargate รับงานจาก SQS", "DS"),
    ("Aurora MySQL", "cluster writer และ reader ใน Private subnet (Data)", "web"),
    ("Aurora PostgreSQL", "cluster พร้อม pgvector ใน Private subnet (Data)", "DS"),
    ("CloudFront, WAF, ALB, NAT, SQS, SES, Secrets Manager, ECR, CloudWatch",
     "บริการของ AWS สร้างด้วย Terraform", "web (DS ส่ง PR ส่วนของตัวเอง)"),
]



if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    render(os.path.join(out, "aws-example"), "ตัวอย่างระบบเว็บและ AI service: component และการเชื่อมต่อ",
           "ระบบ production บน AWS region ระบบสมมติสำหรับใช้เป็นตัวอย่าง",
           topology(), TALKS, DEPLOY)
