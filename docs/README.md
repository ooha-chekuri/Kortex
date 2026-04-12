Place technical PDFs in this folder before running `POST /ingest`.

Suggested demo files:
- Kafka documentation PDF
- Kubernetes documentation PDF
- Docker or FastAPI PDF

If an official PDF is not available, generate one from the website:

```powershell
.\scripts\save-web-docs.ps1 -Urls "https://kubernetes.io/docs/concepts/workloads/pods/"
```

You can pass multiple URLs:

```powershell
.\scripts\save-web-docs.ps1 -Urls `
  "https://kafka.apache.org/documentation/" `
  "https://fastapi.tiangolo.com/tutorial/first-steps/"
```

After PDFs are saved here, run `POST /ingest` again.
