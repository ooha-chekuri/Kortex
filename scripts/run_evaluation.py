"""
Evaluation script for Kortex RAG pipeline.
Calculates Precision@K, Recall@K, MRR, and generates a performance report.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.core.orchestrator import Orchestrator
from backend.services.evaluation import evaluate_query


def run_full_evaluation():
    dataset_path = Path("tests/evaluation_dataset.json")
    if not dataset_path.exists():
        print("Evaluation dataset not found at tests/evaluation_dataset.json")
        return

    with open(dataset_path, "r") as f:
        dataset = json.load(f)

    orchestrator = Orchestrator()
    results = []
    
    print(f"Starting evaluation of {len(dataset)} queries...")
    
    for entry in dataset:
        query = entry["query"]
        ground_truth = entry["ground_truth"]
        
        print(f"Evaluating query: {query}")
        
        # Run orchestrator
        response = orchestrator.run(query)
        
        # Extract retrieved docs/tickets from response
        retrieved = response.get("contexts", [])
        
        # Calculate metrics
        metrics = evaluate_query(query, retrieved, ground_truth)
        
        results.append({
            "query": query,
            "metrics": metrics,
            "status": response.get("status"),
            "confidence": response.get("confidence", 0)
        })

    # Aggregate metrics
    avg_metrics = {}
    if results:
        metric_keys = results[0]["metrics"].keys()
        for key in metric_keys:
            avg_metrics[key] = sum(r["metrics"][key] for r in results) / len(results)

    # Generate Report
    report_path = Path("evaluation_report.md")
    with open(report_path, "w") as f:
        f.write("# Kortex RAG Performance Report\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary Metrics\n")
        f.write("| Metric | Score |\n")
        f.write("| --- | --- |\n")
        for key, value in avg_metrics.items():
            f.write(f"| {key.upper()} | {value:.4f} |\n")
        
        f.write("\n## Detailed Results\n")
        f.write("| Query | Precision@3 | Recall@3 | Confidence | Status |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        for r in results:
            f.write(f"| {r['query']} | {r['metrics']['precision_at_3']:.2f} | {r['metrics']['recall_at_3']:.2f} | {r['confidence']:.2f} | {r['status']} |\n")

    print(f"Evaluation complete. Report generated at {report_path}")


if __name__ == "__main__":
    run_full_evaluation()
