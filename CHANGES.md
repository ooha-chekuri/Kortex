# Kortex Project Changes Log

## 2026-04-10

### UI Improvements (app.py)
- **Refactored Response Synthesis Display**
  - Added confidence-based color coding (green/yellow/red)
  - Shows ANSWER/ESCALATE decision badge
  - Clean response display without trace info
- **Added Structured Source Cards**
  - Shows source type (DOC/TICKET)
  - Displays relevance score percentage
  - Shows preview snippet from source
  - Improved source citation layout

### Demo Data Generation

#### Corporate SOPs (demo/inputs/docs/)
Created 30 comprehensive SOP documents:

**IT Operations (6):**
- Network_Security_SOP.txt
- VPN_Access_Policy.txt
- Password_Policy.txt
- Remote_Access_SOP.txt
- Incident_Response_SOP.txt
- Backup_Recovery_SOP.txt

**DevOps (6):**
- Kubernetes_Onboarding.txt
- Docker_Standards.txt
- CI_CD_Pipeline_Guide.txt
- Container_Orchestration.txt
- Helm_Chart_Guidelines.txt
- K8s_Troubleshooting.txt

**Data & API (6):**
- FastAPI_Guidelines.txt
- Kafka_Deployment_Guide.txt
- API_Rate_Limits.txt
- Data_Privacy_Policy.txt
- API_Versioning_SOP.txt
- Webhook_Configuration.txt

**Security (6):**
- Access_Control_SOP.txt
- PII_Handling_Guidelines.txt
- Security_Audit_Procedure.txt
- Vulnerability_Management.txt
- Encryption_Standards.txt
- Security_Incident_Response.txt

**HR/IT Setup (6):**
- New_Employee_IT_Setup.txt
- Device_Policy.txt
- Software_Installation_Guide.txt
- Email_Configuration.txt
- VPN_Setup_Guide.txt
- Remote_Work_Policy.txt

#### IT Support Tickets (demo/inputs/tickets/)
- Generated 300 realistic IT support tickets (tickets.csv)
- Categories: Access & Authentication, Hardware/Software, Network & Connectivity, Application Issues, Infrastructure, General Inquiries
- Priority distribution: P1 (73), P2 (137), P3 (90)
- Includes resolution text and tags

#### Knowledge Base Q&A (demo/inputs/docs/)
- Created 40 IT domain Q&A pairs (knowledge_base.json)
- Source attribution mapping to SOPs
- Covers common IT operations questions

---

## Previous Updates
- Initial project setup with multi-agent architecture
- Streamlit UI with agent visualizer
- FAISS vector database integration
- Agent orchestration (Triage, Retrieval, Synthesis, Validator)

