# AWS diagrams

> Read when: the system runs on AWS, or the AWS half of a hybrid picture.

Worked example: `examples/aws_example.py`.

## Nesting

`group(x, y, w, h, kind, label)` kinds, outside → in:

| Kind | Draw for |
|---|---|
| `cloud` | the AWS account ("AWS Cloud (บัญชี production)") |
| `region` | the region; a service in another region (SES elsewhere) gets its own small `region` box inside `cloud` |
| `vpc` | the VPC; say "2 Availability Zone" in its label instead of drawing every task twice |
| `pub` | public subnet: ALB, NAT gateway |
| `priv` | private subnets: App (ECS, EC2, EKS) and Data (Aurora, RDS, ElastiCache) |
| `plain` | dashed grey column for regional services |
| `box` | a team or service boundary inside a subnet, or the external-services box |

Draw two `az()` columns only when the picture is about availability (DR, failover). For "what talks to what", one logical copy of each service plus "≥ 1 task per AZ" in the label reads better.

## Icons

AWS-style tiles: `ec2 ecs ecr eks lambda aurora rds elasticache vectordb s3 efs cloudfront apigw route53 alb nat igw vpcep vgw tgw dx waf secrets kms acm identity cloudwatch ssm backup sns sqs ses flowlogs`.
Generic line icons: `user users browser laptop mobile dev git server mail doc lock`; edge: `cloudflare`.
`vgw` is the AWS end of a site-to-site VPN, `tgw` a Transit Gateway, `dx` Direct Connect. Add a missing service from your drawing script: `import icons` (it sits beside `archkit.py`) and call `icons.GLYPH.update({"name": ("network", "<g ...>...</g>")})` with an AWS category (`compute database storage network security mgmt integration`) and white strokes on a 48 × 48 grid. Leave the skill folder untouched.

## Typical connections (Table 1 wording)

| From → to | How | Auth and limits |
|---|---|---|
| user → CloudFront | HTTPS for static files and API calls | access token in Authorization header, refresh token in an HttpOnly cookie |
| CloudFront → S3 | static files | bucket private, read through CloudFront only |
| CloudFront → ALB | HTTPS | ALB accepts CloudFront only |
| ALB → service | HTTP inside the VPC | security group from the ALB only |
| service → Aurora/RDS | SQL | password from Secrets Manager, security group from that service only |
| service → service (internal ALB) | HTTP inside the VPC, JSON, SSE for streams | service token header |
| service → internet (LLM, SaaS) | HTTPS through NAT gateway | API key |
| service → SQS → worker | send, then long-poll | IAM role of the task |
| every task → Secrets Manager, ECR, CloudWatch | secrets at task start, image pull, logs and metrics | IAM role of the task |

## Sources

- AWS Architecture Icons — https://aws.amazon.com/architecture/icons/
- Amazon VPC user guide, subnets — https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html
- Amazon ECS developer guide, task networking — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-networking.html
