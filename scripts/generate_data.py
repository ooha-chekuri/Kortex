"""
Generate synthetic corporate data: SOP PDFs and IT support tickets.
Creates realistic mock enterprise data for RAG training.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from reportlab.lib import pagesizes
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import ParagraphStyle


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = DATA_DIR = BASE_DIR / "data" / "synthetic"
OUTPUT_DIR = DATA_DIR / "sops"


SOP_TEMPLATES = [
    {
        "title": "VPN Setup and Configuration",
        "category": "Network",
        "content": """# VPN Setup and Configuration Standard Operating Procedure

## Purpose
This SOP establishes the standard procedure for configuring and managing VPN access for employees working remotely.

## Scope
Applies to all employees requiring remote access to company network resources.

## Procedure

### 1. VPN Client Installation
1.1. Download the VPN client from the IT portal
1.2. Install the client on your workstation
1.3. Restart the computer after installation

### 2. VPN Configuration
2.1. Open the VPN client application
2.2. Enter the server address: vpn.company.internal
2.3. Enter your corporate credentials
2.4. Select the appropriate server region

### 3. Authentication
3.1. Enable two-factor authentication
3.2. Register your mobile device for MFA
3.3. Complete the authentication test connection

### 4. Troubleshooting
- If connection fails, check your internet connection
- Verify credentials are not expired
- Contact IT support if issues persist

## Related Documents
- Security Policy v2.1
- Remote Work Guidelines
- MFA Setup SOP
""",
    },
    {
        "title": "Password Reset Procedure",
        "category": "Security",
        "content": """# Password Reset Procedure

## Purpose
Standard procedure for resetting expired or forgotten passwords.

## Scope
All employees with corporate account credentials.

## Procedure

### 1. Self-Service Reset
1.1. Navigate to the password reset portal
1.3. Enter your username
1.4. Complete security challenge questions
1.5. Set new password following complexity requirements

### 2. IT-Assisted Reset
2.1. Contact IT Help Desk at ext. 4357
2.2. Verify identity with security questions
2.3. Receive temporary password
2.4. Change password on first login

## Password Requirements
- Minimum 12 characters
- Must include uppercase, lowercase, numbers, symbols
- Cannot reuse last 10 passwords
- Expires every 90 days

## Troubleshooting
- Account locked after 5 failed attempts
- Contact IT for immediate unlock
""",
    },
    {
        "title": "Email Configuration Guide",
        "category": "Communication",
        "content": """# Email Configuration Guide

## Purpose
Configure corporate email on various devices and clients.

## Scope
All employees using corporate email.

## Desktop Client Setup

### Outlook for Windows
1. Open Outlook
2. Go to File > Add Account
3. Enter email address
4. Click Connect
5. Authenticate with SSO

### Outlook for Mac
1. Open Outlook
2. Choose Account
3. Enter email credentials
4. Configure automatic setup

## Mobile Setup

### iPhone
1. Settings > Mail > Accounts
2. Add Account > Microsoft Exchange
3. Enter email and description
4. Sign in with corporate credentials

### Android
1. Open Gmail app
2. Add account
3. Select Exchange
4. Enter corporate email

## Troubleshooting
- Sync failures: Check network connection
- Authentication errors: Clear credentials and re-add
- Missing emails: Check server filters
""",
    },
    {
        "title": "Database Backup and Recovery",
        "category": "Database",
        "content": """# Database Backup and Recovery SOP

## Purpose
Ensure regular backups and recovery procedures for production databases.

## Scope
DBAs and infrastructure team members.

## Backup Schedule

### Full Backup
- Daily at 02:00 UTC
- Retention: 30 days

### Incremental Backup
- Every 4 hours
- Retention: 7 days

### Transaction Logs
- Every 15 minutes
- Retention: 48 hours

## Recovery Procedures

### Point-in-Time Recovery
1. Identify recovery point
2. Stop all database connections
3. Restore from last full backup
4. Apply transaction logs
5. Verify data integrity

### Emergency Recovery
1. Contact on-call DBA
2. Assess failure scope
3. Execute recovery plan
4. Verify application connectivity

## Testing
- Monthly recovery drill
- Quarterly full disaster recovery test
- Document results in compliance portal
""",
    },
    {
        "title": "Kubernetes Cluster Management",
        "category": "Infrastructure",
        "content": """# Kubernetes Cluster Management

## Purpose
Manage and monitor Kubernetes production clusters.

## Scope
Platform and DevOps engineers.

## Cluster Access

### Access Requirements
- Corporate VPN connection
- Kubernetes RBAC permissions
- kubectl installed locally

### Authentication
1. Request cluster access via IT ticket
2. Receive kubeconfig file
3. Place in ~/.kube/config
4. Test with: kubectl get nodes

## Common Operations

### Deployment
kubectl apply -f deployment.yaml
kubectl rollout status deployment/<name>

### Scaling
kubectl scale deployment/<name> --replicas=3

### Troubleshooting
- Check pod status: kubectl get pods
- View logs: kubectl logs <pod>
- Describe: kubectl describe pod <pod>

## Monitoring
- Prometheus for metrics
- Grafana dashboards
- PagerDuty alerts
""",
    },
    {
        "title": "Kafka Topic Management",
        "category": "Data",
        "content": """# Kafka Topic Management

## Purpose
Create, configure, and manage Kafka topics for message streaming.

## Scope
Developers and data engineers.

## Creating Topics

### CLI Command
 kafka-topics.sh --create \\
  --topic <topic-name> \\
  --partitions 3 \\
  --replication-factor 3 \\
  --bootstrap-servers <brokers>

## Topic Configuration

### Retention Settings
- retention.ms: 604800000 (7 days)
- cleanup.policy: delete
- compression.type: producer

### Partition Strategy
- Use key-based partitioning for ordered messages
- Use random partitioning for unordered

## Monitoring
- Lag metrics in Kafka Manager
- Consumer group offset tracking
- Topic size alerts

## Troubleshooting
- Producer errors: Check serialization
- Consumer lag: Scale consumers
- Broker issues: Check cluster health
""",
    },
    {
        "title": "API Gateway Configuration",
        "category": "Integration",
        "content": """# API Gateway Configuration

## Purpose
Configure and manage the central API Gateway for all microservices.

## Scope
API developers and platform engineers.

## Adding New APIs

### Step 1: Register Service
1. Create service definition in config repo
2. Define routes and endpoints
3. Configure authentication rules
4. Submit for approval

### Step 2: Deploy Configuration
kubectl apply -f api-definition.yaml

### Step 3: Testing
- Use Postman collection
- Verify authentication
- Check rate limiting

## Rate Limiting
- Default: 1000 requests/minute
- Premium: 10000 requests/minute
- Enterprise: Custom SLA

## Authentication
- API Keys for service-to-service
- OAuth 2.0 for user-facing APIs
- JWT validation for all requests
""",
    },
    {
        "title": "Incident Response Procedure",
        "category": "Operations",
        "content": """# Incident Response Procedure

## Purpose
Standardize response to production incidents and outages.

## Scope
All IT operations team members.

## Severity Levels

### SEV1 - Critical
- Complete service outage
- Customer impact
- Response time: 15 minutes

### SEV2 - High
- Major functionality impacted
- Workaround available
- Response time: 1 hour

### SEV3 - Medium
- Minor functionality affected
- Low customer impact
- Response time: 4 hours

## Response Steps

### 1. Detection
- Automated monitoring alerts
- Customer reports
- Team discovery

### 2. Assessment
- Determine severity
- Identify root cause
- Assess impact

### 3. Communication
- Create incident channel
- Update status page
- Notify stakeholders

### 4. Resolution
- Execute fix
- Verify resolution
- Document incident

### 5. Post-Mortem
- Root cause analysis
- Action items
- Process improvements
""",
    },
    {
        "title": "Code Deployment Pipeline",
        "category": "Development",
        "content": """# Code Deployment Pipeline

## Purpose
Standard deployment process for all applications.

## Scope
All development teams.

## Pipeline Stages

### 1. Build
- Unit tests pass
- Code linting passes
- Security scanning passes

### 2. Test
- Integration tests
- Performance benchmarks
- E2E tests

### 3. Staging Deploy
- Automated deployment
- Smoke tests
- Manual QA approval

### 4. Production Deploy
- Blue-green or canary
- Monitor metrics
- Rollback if needed

## Rollback Procedure
1. Identify issue
2. Execute rollback command
3. Verify successful
4. Document in incident

## Deployment Windows
- Standard: Tuesday-Thursday 10am-4pm
- Emergency: Any time with approval
""",
    },
    {
        "title": "Security Patch Management",
        "category": "Security",
        "content": """# Security Patch Management

## Purpose
Manage security patches for all systems and applications.

## Scope
Infrastructure and security teams.

## Patch Classification

### Critical Patches
- Zero-day vulnerabilities
- Must apply within 24-48 hours
- Requires emergency change request

### High Priority
- Severe but not critical
- Apply within 7 days
- Standard change process

### Medium Priority
- Moderate risk
- Apply during regular maintenance
- Monthly patch window

## Process

### 1. Assessment
- Review patch details
- Assess applicability
- Test in staging

### 2. Scheduling
- Plan maintenance window
- Schedule rollback
- Notify stakeholders

### 3. Deployment
- Apply to staging first
- Verify functionality
- Apply to production

### 4. Verification
- Monitor systems
- Check logs
- Confirm patch applied
""",
    },
    {
        "title": "User Account Provisioning",
        "category": "Identity",
        "content": """# User Account Provisioning

## Purpose
Standard procedure for creating and managing user accounts.

## Scope
HR and IT teams.

## New Employee Setup

### 1. HR Request
- Receive onboarding ticket
- Verify employee details
- Determine required access

### 2. Account Creation
- Create Active Directory account
- Set up email
- Configure groups

### 3. Application Access
- Grant required permissions
- Configure MFA
- Distribute credentials

### 4. Equipment
- Laptop setup
- Monitor and peripherals
- Security token

## Account Modifications
- Role changes
- Department transfers
- Access escalations

## Account Termination
- Disable on last day
- Revoke access
- Archive mailbox
- Return equipment
""",
    },
    {
        "title": "Monitoring and Alerting Setup",
        "category": "Operations",
        "content": """# Monitoring and Alerting Setup

## Purpose
Configure monitoring for applications and infrastructure.

## Scope
DevOps and platform teams.

## Monitoring Stack

### Metrics
- Prometheus for collection
- Grafana for visualization
- Custom dashboards

### Logging
- ELK stack for logs
- Application logs
- Infrastructure logs

### Tracing
- Jaeger for distributed tracing
- Request tracing
- Performance analysis

## Alert Configuration

### Steps
1. Identify key metrics
2. Define thresholds
3. Create alert rules
4. Configure notification channels
5. Test alerts

### Alert Channels
- PagerDuty for critical
- Slack for warnings
- Email for informational

## On-Call Procedures
- Rotating on-call schedule
- Escalation paths
- Response time targets
""",
    },
    {
        "title": "Load Balancer Configuration",
        "category": "Network",
        "content": """# Load Balancer Configuration

## Purpose
Configure and manage load balancers for high availability.

## Scope
Network and infrastructure teams.

## Configuration Steps

### 1. Backend Pool
- Define backend servers
- Health check configuration
- Session persistence settings

### 2. Listener Setup
- Protocol (HTTP/HTTPS/TCP)
- Port configuration
- SSL certificate

### 3. Health Checks
- URL path: /health
- Interval: 10 seconds
- Timeout: 5 seconds
- Unhealthy threshold: 3

### 4. SSL/TLS
- Certificate upload
- Cipher configuration
- Redirect HTTP to HTTPS

## Common Issues
- Backend server down: Check health
- SSL errors: Verify certificate
- High latency: Check backend response
""",
    },
    {
        "title": "Docker Container Management",
        "category": "Development",
        "content": """# Docker Container Management

## Purpose
Standard procedures for managing Docker containers.

## Scope
Developers and DevOps engineers.

## Building Images

### Dockerfile Best Practices
- Use official base images
- Minimize layers
- Use .dockerignore
- Set proper working directory

### Build Command
docker build -t <image>:<tag> .

## Running Containers

### Basic Run
docker run -d -p 8080:80 <image>

### With Environment
docker run -d \\
  -e ENV_VAR=value \\
  -v volume:/data \\
  <image>

## Management Commands

### List Containers
docker ps -a

### View Logs
docker logs -f <container>

### Execute Command
docker exec -it <container> bash

### Stop/Remove
docker stop <container>
docker rm <container>

## Troubleshooting
- Check logs for errors
- Inspect with docker inspect
- Monitor resource usage
""",
    },
    {
        "title": "SSL Certificate Management",
        "category": "Security",
        "content": """# SSL Certificate Management

## Purpose
Manage SSL/TLS certificates for all services.

## Scope
Infrastructure and security teams.

## Certificate Types

### Domain Validation
- Single domain
- Validation via email/DNS
- Validity: 1 year

### Organization Validation
- Verified organization
- Higher trust level
- Validity: 1-2 years

### Extended Validation
- Green bar in browser
- Highest trust
- Validity: 1-2 years

## Obtaining Certificates

### Via CA
1. Generate CSR
2. Submit to CA
3. Complete validation
4. Install certificate

### Via Let's Encrypt
1. Use certbot tool
2. Automatic validation
3. Auto-renewal enabled

## Installation

### Apache
SSLCertificateFile /path/to/cert.crt
SSLCertificateKeyFile /path/to/key.key

### Nginx
ssl_certificate /path/to/cert.crt;
ssl_certificate_key /path/to/key.key;

## Renewal Process
- Start 30 days before expiry
- Test in staging
- Deploy to production
- Update monitoring
""",
    },
    {
        "title": "Disaster Recovery Plan",
        "category": "Operations",
        "content": """# Disaster Recovery Plan

## Purpose
Ensure business continuity during catastrophic events.

## Scope
IT leadership and operations teams.

## Recovery Objectives

### RTO - Recovery Time Objective
- Critical: 4 hours
- Important: 24 hours
- Standard: 72 hours

### RPO - Recovery Point Objective
- Critical: 15 minutes
- Important: 1 hour
- Standard: 24 hours

## Disaster Scenarios

### Data Center Failure
- Failover to secondary DC
- DNS switch
- Verify functionality

### Ransomware
- Isolate affected systems
- Restore from backups
- Investigate origin

### Natural Disaster
- Remote failover
- Employee remote work
- Communication plan

## Testing Schedule
- Monthly: Backup restoration
- Quarterly: Full DR drill
- Annual: Executive review
""",
    },
    {
        "title": "Log Management and Analysis",
        "category": "Operations",
        "content": """# Log Management and Analysis

## Purpose
Standardize log collection, storage, and analysis.

## Scope
All development and operations teams.

## Log Collection

### Application Logs
- Level: INFO, WARN, ERROR
- Format: JSON
- Include correlation IDs

### Infrastructure Logs
- System logs
- Security logs
- Network logs

### Access Logs
- HTTP requests
- Authentication
- File access

## Log Storage

### Short-term (30 days)
- Hot storage
- Full searchable
- Real-time analysis

### Long-term (1 year)
- Archive storage
- Cost-optimized
- Manual retrieval

## Analysis Tools

### Search
- Kibana for ELK
- CloudWatch for AWS
- Built-in dashboards

### Alerting
- Anomaly detection
- Pattern matching
- Threshold alerts

## Retention
- Application: 1 year
- Security: 3 years
- Compliance: 7 years
""",
    },
    {
        "title": "Network Firewall Rules",
        "category": "Network",
        "content": """# Network Firewall Rules

## Purpose
Manage firewall rules for network security.

## Scope
Network and security teams.

## Rule Structure

### Required Fields
- Source IP/CIDR
- Destination IP/CIDR
- Protocol
- Port
- Action: Allow/Deny

## Common Rules

### Inbound HTTP/HTTPS
- Source: Any
- Dest: Web server
- Port: 80, 443
- Action: Allow

### SSH Access
- Source: VPN IP range
- Dest: Any server
- Port: 22
- Action: Allow

### Database Access
- Source: App servers
- Dest: Database
- Port: 5432, 3306
- Action: Allow

## Rule Management

### Adding Rules
1. Submit change request
2. Security review
3. Test in staging
4. Deploy to production

### Removing Rules
1. Verify no dependencies
2. Monitor for issues
3. Remove after 30 days
4. Document removal

## Audit
- Quarterly rule review
- Remove unused rules
- Document business need
""",
    },
    {
        "title": "Backup Verification Procedure",
        "category": "Storage",
        "content": """# Backup Verification Procedure

## Purpose
Verify backup integrity and recoverability.

## Scope
DBAs and infrastructure teams.

## Verification Schedule

### Daily
- Backup completion check
- Size validation
- Error log review

### Weekly
- Random restore test
- Restore time measurement

### Monthly
- Full restore drill
- Recovery team drill

## Verification Steps

### 1. Pre-restore Check
- Verify backup exists
- Check disk space
- Notify stakeholders

### 2. Restore Process
- Restore to test environment
- Verify file integrity
- Check data consistency

### 3. Post-restore
- Compare to production
- Document discrepancies
- Clean up test environment

## Documentation
- Verify date
- Who performed
- Results
- Action items
""",
    },
    {
        "title": "Software License Management",
        "category": "Compliance",
        "content": """# Software License Management

## Purpose
Track and manage software licenses for compliance.

## Scope
Procurement and IT teams.

## License Types

### Perpetual
- One-time purchase
- Own the license
- May have annual maintenance

### Subscription
- Time-based access
- Regular payments
- May have usage limits

### Open Source
- No license cost
- Must follow license terms
- No support guarantee

## Management Process

### Procurement
1. Identify need
2. Evaluate options
3. Get quotes
4. Approve budget
5. Purchase

### Tracking
- License inventory
- Usage monitoring
- Renewal tracking
- Cost allocation

## Compliance
- Audit ready
- Usage reports
- Renewal alerts
- Decommission process
""",
    },
    {
        "title": "Access Control Review",
        "category": "Security",
        "content": """# Access Control Review

## Purpose
Regularly review and audit system access rights.

## Scope
Security and IT managers.

## Review Schedule

### Quarterly
- Privileged access
- Administrative accounts
- Service accounts

### Annually
- All access rights
- Department review
- Role changes

## Review Process

### 1. Generate Report
- Export access list
- Cross-reference HR data
- Identify issues

### 2. Manager Review
- Verify business need
- Approve/deny access
- Document reasons

### 3. Remediation
- Remove unnecessary access
- Escalate issues
- Document changes

### 4. Reporting
- Compliance report
- Exception list
- Action items
""",
    },
    {
        "title": "Change Management Process",
        "category": "Operations",
        "content": """# Change Management Process

## Purpose
Standardize infrastructure and application changes.

## Scope
All IT teams.

## Change Types

### Standard
- Regular maintenance
- Low risk
- Pre-approved

### Normal
- Application changes
- Standard change process
- CAB for high impact

### Emergency
- Incident response
- Security patches
- Expedited approval

## Process

### 1. Request
- Fill out change form
- Describe change
- Risk assessment
- Rollback plan

### 2. Review
- Manager approval
- Technical review
- Security review
- CAB for big changes

### 3. Implementation
- Schedule window
- Implement change
- Monitor metrics

### 4. Closure
- Verify success
- Update documentation
- Close change ticket
""",
    },
    {
        "title": "Performance Tuning Guide",
        "category": "Optimization",
        "content": """# Performance Tuning Guide

## Purpose
Optimize system and application performance.

## Scope
Developers and performance engineers.

## Monitoring Areas

### Metrics
- CPU utilization
- Memory usage
- Disk I/O
- Network I/O
- Application latency

### Tools
- Top/htop for system
- VisualVM for Java
- Python profilers
- Database explain plans

## Optimization Steps

### 1. Identify Bottleneck
- Profile application
- Analyze metrics
- Identify hot spots

### 2. Analyze
- Review code
- Check queries
- Review configuration

### 3. Optimize
- Code improvements
- Caching
- Database indexing
- Resource scaling

### 4. Verify
- Re-run benchmarks
- Compare metrics
- Monitor in production

## Common Issues
- N+1 queries
- Missing indexes
- Unoptimized loops
- Memory leaks
""",
    },
    {
        "title": "Cloud Resource Management",
        "category": "Cloud",
        "content": """# Cloud Resource Management

## Purpose
Manage cloud resources efficiently and cost-effectively.

## Scope
Cloud and DevOps engineers.

## Resource Tagging

### Required Tags
- Environment: prod/staging/dev
- Cost Center
- Owner
- Application

### Optional Tags
- Compliance
- Backup requirements
- Criticality

## Cost Optimization

### Compute
- Right-size instances
- Use spot/preemptible
- Auto-scaling

### Storage
- Move to cheaper tiers
- Delete unused
- Lifecycle policies

### Networking
- Use VPC endpoints
- CDN for static
- Transfer caching

## Resource Review
- Monthly unused resource report
- Cost analysis
- Right-sizing recommendations
""",
    },
    {
        "title": "Data Retention Policy",
        "category": "Compliance",
        "content": """# Data Retention Policy

## Purpose
Define requirements for data retention and disposal.

## Scope
Legal, compliance, and IT teams.

## Retention Periods

### Transaction Data
- 7 years for financial
- 3 years for operational

### Logs
- 1 year for application
- 3 years for security
- 7 years for compliance

### Personal Data
- Until account deletion
- Max 3 years inactive
- GDPR compliance

## Disposal Process

### 1. Identify
- Find data due for deletion
- Verify legal requirement
- Check for litigation hold

### 2. Delete
- Remove from production
- Remove from backups
- Verify deletion

### 3. Document
- Record destruction
- Certificate of disposal
- Update inventory
""",
    },
    {
        "title": "Multi-Factor Authentication Setup",
        "category": "Security",
        "content": """# Multi-Factor Authentication Setup

## Purpose
Enable and manage multi-factor authentication.

## Scope
All employees with system access.

## MFA Methods

### Authenticator App
- Google Authenticator
- Microsoft Authenticator
- Authy

### SMS
- Phone number verification
- Less secure
- Backup only

### Hardware Token
- YubiKey
- RSA token
- Highest security

## Setup Steps

### 1. Enable MFA
1. Navigate to security settings
2. Select MFA method
3. Verify identity

### 2. Register Device
1. Scan QR code
2. Enter verification code
3. Save backup codes

### 3. Verify
1. Test authentication
2. Verify MFA works
3. Store backup codes

## Backup Access
- Save backup codes securely
- Register backup phone
- Contact IT if locked out
""",
    },
]


TICKET_CATEGORIES = [
    "Network",
    "Hardware",
    "Software",
    "Security",
    "Email",
    "Database",
    "VPN",
    "Authentication",
    "Cloud",
    "Application",
]

TICKET_TEMPLATES = [
    {
        "title": "VPN Connection Timeout",
        "description": "Unable to connect to corporate VPN. Connection times out after 30 seconds.",
        "category": "VPN",
        "resolution": "Updated VPN client to latest version. Reset network settings. Connection restored.",
    },
    {
        "title": "Email Not Syncing",
        "description": "Outlook not receiving new emails. Can send but not receive.",
        "category": "Email",
        "resolution": "Cleared Outlook cache. Reconfigured account. Emails flowing again.",
    },
    {
        "title": "Password Expired",
        "description": "Cannot log in. Password has expired and system won't let me change it.",
        "category": "Security",
        "resolution": "Reset password via self-service. Verified login works.",
    },
    {
        "title": "Database Connection Failed",
        "description": "Application cannot connect to production database.",
        "category": "Database",
        "resolution": "Firewall rule added. Connection string corrected. DB accessible.",
    },
    {
        "title": "Slow Network Performance",
        "description": "Network is extremely slow. Downloads taking hours.",
        "category": "Network",
        "resolution": "Found malware on endpoint. Removed. Network restored.",
    },
    {
        "title": "SSO Login Loop",
        "description": "SSO authentication redirects in a loop. Cannot access any application.",
        "category": "Authentication",
        "resolution": "Cleared browser cache. Regenerated SSO token. Works now.",
    },
    {
        "title": "Kubernetes Pod Crash",
        "description": "Pod in CrashLoopBackOff. Logs show memory error.",
        "category": "Cloud",
        "resolution": "Increased memory limit. Pod running stable.",
    },
    {
        "title": "SSL Certificate Error",
        "description": "Browser shows certificate error on internal site.",
        "category": "Security",
        "resolution": "Updated certificate. Added to trust store.",
    },
    {
        "title": "File Share Access Denied",
        "description": "Cannot access shared drive. Permission denied error.",
        "category": "Network",
        "resolution": "Added user to correct AD group. Access restored.",
    },
    {
        "title": "Printer Not Found",
        "description": "Cannot find network printer from my computer.",
        "category": "Hardware",
        "resolution": "Reinstalled printer driver. Printer now visible.",
    },
]


def generate_sop_pdfs(output_dir: Path) -> dict[str, Any]:
    """Generate SOP PDF files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {"sops_created": 0, "sops": []}

    for sop in SOP_TEMPLATES:
        filename = f"{sop['title'].lower().replace(' ', '_')}.pdf"
        filepath = output_dir / filename

        try:
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=pagesizes.letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )

            story = []
            story.append(
                Paragraph(
                    sop["title"],
                    ParagraphStyle(
                        "Title", fontSize=18, spaceAfter=20, keepWithNext=True
                    ),
                )
            )
            story.append(
                Paragraph(
                    f"<i>Category: {sop['category']}</i>",
                    ParagraphStyle("Category", fontSize=10, textColor="gray"),
                )
            )
            story.append(Spacer(1, 20))

            for line in sop["content"].split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("# "):
                    story.append(
                        Paragraph(
                            line[2:],
                            ParagraphStyle(
                                "H1",
                                fontSize=14,
                                spaceBefore=15,
                                spaceAfter=10,
                                keepWithNext=True,
                            ),
                        )
                    )
                elif line.startswith("## "):
                    story.append(
                        Paragraph(
                            line[3:],
                            ParagraphStyle(
                                "H2", fontSize=12, spaceBefore=12, spaceAfter=8
                            ),
                        )
                    )
                elif line.startswith("### "):
                    story.append(
                        Paragraph(
                            line[4:],
                            ParagraphStyle(
                                "H3", fontSize=11, spaceBefore=8, spaceAfter=6
                            ),
                        )
                    )
                elif line.startswith("- "):
                    story.append(
                        Paragraph(
                            line,
                            ParagraphStyle(
                                "Bullet", fontSize=10, spaceAfter=3, leftIndent=20
                            ),
                        )
                    )
                else:
                    story.append(
                        Paragraph(
                            line, ParagraphStyle("Body", fontSize=10, spaceAfter=4)
                        )
                    )

            doc.build(story)
            results["sops"].append(
                {"title": sop["title"], "file": filename, "category": sop["category"]}
            )
            results["sops_created"] += 1
            print(f"Created SOP: {sop['title']}")

        except Exception as e:
            print(f"Failed to create SOP {sop['title']}: {e}")

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


def generate_tickets_csv(output_path: Path, num_tickets: int = 250) -> dict[str, Any]:
    """Generate synthetic IT support tickets CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ticket_id = 1000
    tickets = []

    for i in range(num_tickets):
        template = random.choice(TICKET_TEMPLATES)
        category = random.choice(TICKET_CATEGORIES)

        days_ago = random.randint(1, 180)
        created_date = datetime.now() - timedelta(days=days_ago)

        ticket = {
            "ticket_id": f"TICKET-{ticket_id:05d}",
            "title": template["title"],
            "description": template["description"],
            "category": category,
            "status": random.choice(["resolved", "resolved", "resolved", "closed"]),
            "priority": random.choice(["low", "medium", "high", "critical"]),
            "created_at": created_date.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": (
                created_date + timedelta(hours=random.randint(1, 48))
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "resolution": template["resolution"],
            "assigned_team": random.choice(
                [
                    "Network Team",
                    "Help Desk",
                    "Security Team",
                    "Database Team",
                    "Cloud Team",
                ]
            ),
            "user_department": random.choice(
                ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]
            ),
        }
        tickets.append(ticket)
        ticket_id += 1

    import pandas as pd

    df = pd.DataFrame(tickets)
    df.to_csv(output_path, index=False)

    return {"tickets_created": len(tickets), "file": str(output_path)}


def generate_all() -> dict[str, Any]:
    """Generate all synthetic data."""
    results = {}

    print("Generating SOP PDFs...")
    results["sops"] = generate_sop_pdfs(OUTPUT_DIR)

    print("\nGenerating IT Support Tickets...")
    csv_path = DATA_DIR / "tickets.csv"
    results["tickets"] = generate_tickets_csv(csv_path)

    return results


if __name__ == "__main__":
    print(json.dumps(generate_all(), indent=2))
