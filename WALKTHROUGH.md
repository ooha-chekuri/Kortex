# Kortex User Walkthrough

Welcome to the **Kortex Enterprise Knowledge Copilot**. This guide explains how to use the clean, intuitive interface to search your enterprise data.

## Step 1: Manage the Knowledge Base (Admin)
Before asking questions, ensure Kortex has data to search.
1.  **Sidebar**: Open the collapsible sidebar on the left.
2.  **Upload Knowledge**: Use the "📁 UPLOAD KNOWLEDGE" expander to drag and drop your PDFs, Markdown files, or TXT documents. They will be saved to the `/docs` directory.
3.  **Sync**: Click the "🔄 SYNC KNOWLEDGE BASE" button. Kortex will:
    - Redact PII (Emails, IPs, Phones).
    - Chunk and embed the text.
    - Build FAISS vector indices for semantic search.
4.  **Confirmation**: A success message will show the number of documents and tickets indexed.

## Step 2: Ask a Question
1.  **Search Bar**: Type your question into the central input field (e.g., *"How do I resolve Kafka consumer lag?"*).
2.  **Submit**: Click the **"ASK KORTEX"** button.

## Step 3: Observe Reasoning
Once submitted, you will see a status panel showing the multi-agent collaboration:
- **Triage**: Categorizing your query.
- **Retrieval**: Finding relevant documents and tickets.
- **Synthesis**: Writing the final answer.
- **Validator**: Auditing for accuracy.

## Step 4: Review Results
The results area is divided into two panels:
- **🧠 AGENT ACTIVITY (Left)**: Detailed logs of what each agent did.
- **📄 GROUNDED RESPONSE (Right)**:
  - **Answer**: The final synthesized response.
  - **Sources**: Direct citations of the documents or tickets used.
  - **Confidence**: A metric score (0-100%) showing how reliable the answer is.

## Step 5: Handling Uncertainties
If Kortex is unsure (Confidence < 50%), an **Escalation Banner** will appear at the bottom, suggesting redirection to a human engineer.

---
*Built for Hackathon Demo Excellence*
