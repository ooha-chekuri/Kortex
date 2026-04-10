import pandas as pd
import random
from pathlib import Path

def generate_mock_data():
    # 1. Create Directories
    Path("demo/inputs/docs").mkdir(parents=True, exist_ok=True)
    Path("demo/inputs/tickets").mkdir(parents=True, exist_ok=True)
    
    # 2. Generate Mock SOPs (Option C)
    sops = [
        ("Network Security SOP", "All employees must use VPN. Passwords rotate every 90 days. Multi-factor authentication is mandatory for all production access."),
        ("Kafka Deployment Guide", "Kafka brokers should be deployed across multiple zones. Min.insync.replicas should be set to 2 for high availability. Use SASL_SSL for secure communication."),
        ("Kubernetes Onboarding", "Developers must use Helm for deployments. Resource limits (CPU/Memory) are required for every container. Use namespaces for environment isolation."),
        ("Data Privacy Policy", "PII data must be encrypted at rest and in transit. Access to production databases requires approval from the DPO. Log all access attempts."),
        ("Incident Response SOP", "Severity 1 incidents require a bridge call within 15 minutes. Root cause analysis (RCA) must be published within 48 hours of resolution.")
    ]
    
    for title, content in sops:
        with open(f"demo/inputs/docs/{title.replace(' ', '_')}.txt", "w") as f:
            f.write(content)
            
    # 3. Generate 200 Mock Tickets (Option C)
    categories = ["Kafka", "Kubernetes", "Auth", "Docker", "Database", "Network"]
    resolutions = [
        "Restarted the service and cleared cache.",
        "Updated the configuration file and redeployed.",
        "Increased resource limits and added replicas.",
        "Fixed a syntax error in the environment variables.",
        "Rotated the secret and updated the application.",
        "Cleared disk space and adjusted retention policy."
    ]
    
    tickets = []
    for i in range(1001, 1201):
        cat = random.choice(categories)
        tickets.append({
            "ticket_id": f"INC-{i}",
            "title": f"Issue with {cat} in production",
            "description": f"The user reported a failure in the {cat} module during peak hours.",
            "resolution": random.choice(resolutions),
            "category": cat
        })
        
    df = pd.DataFrame(tickets)
    df.to_csv("demo/inputs/tickets/sample_tickets_expanded.csv", index=False)
    # Also update the main data folder
    df.to_csv("src/data/sample_tickets.csv", index=False)
    
    print(f"Generated {len(sops)} SOPs and {len(tickets)} tickets.")

if __name__ == "__main__":
    generate_mock_data()
