# Kortex OS: User Walkthrough

Welcome to the **Kortex Operating System**. This guide will walk you through the end-to-end flow of using the Copilot.

## Step 1: Initialize the Knowledge Base
Before querying, you need data.
1. Go to the **UPLOAD_KNOWLEDGE** section in the right sidebar.
2. Drag and drop your PDFs, Markdown, or TXT files.
3. Click **SYNC_KNOWLEDGE**. The system will chunk your documents, redact PII (Emails, Phones, IPs), generate embeddings, and build the FAISS indices.
4. Verify the success message (e.g., `OK: 5 DOCS / 28 TIX`).

## Step 2: Enter a Query
1. Locate the **INPUT** field in the central panel.
2. Type your question (e.g., *"How do I configure Kafka partitions?"*).
3. (Optional) Check the sidebar to ensure you are in the correct **TRIAGE.ENV** context.

## Step 3: Investigate
1. Click the **INVESTIGATE** button in the top-right **ACTIONS** box.
2. Observe the **RUNNING_AGENTS...** status panel. You will see real-time updates as the system:
   - **TRIAGE**: Identifies whether to look at docs or tickets.
   - **RETRIEVAL**: Searches the vector database.
   - **SYNTHESIS**: Drafts the answer.
   - **VALIDATOR**: Checks for accuracy and computes a confidence score.

## Step 4: Review the Synthesis
Once the pipeline is complete:
1. Read the **RESPONSE_SYNTHESIS** in the central ledger.
2. Check the **SOURCES_MAPPING** at the bottom of the ledger to see exactly which documents or tickets were used.
3. Look at the **AI_CONFIDENCE** stat box. 
   - **> 75%**: Highly reliable.
   - **50% - 75%**: Use with caution.
   - **< 50%**: Trigger an **ESCALATION** (The system will warn you if it's not confident).

## Step 5: Reset
If you want to start a new investigation, simply click **DISCARD** in the Actions panel to clear the session state and start fresh.

---
**System Note**: Always ensure your local LLM (Ollama) or OpenAI API key is configured in your `.env` file for the synthesis agent to function.
