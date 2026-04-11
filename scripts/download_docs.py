"""
Download scripts for public IT documentation.
Downloads text content from official documentation sites.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "public_docs"
OUTPUT_DIR = DATA_DIR / "text"


class DocDownloader(ABC):
    """Base class for documentation downloader."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.output_dir = OUTPUT_DIR / name.lower()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def get_urls(self) -> list[tuple[str, str]]:
        """Return list of (title, url) tuples."""
        pass

    def download_page(self, url: str) -> str | None:
        """Download a single page and extract text."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()

            # Get main content
            main = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_=re.compile(r"content|main|article"))
            )
            if main:
                text = main.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text.strip()
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return None

    def download_all(self) -> dict[str, Any]:
        """Download all pages."""
        results = {"docs_indexed": 0, "pages": []}
        urls = self.get_urls()

        for title, url in urls:
            print(f"Downloading {self.name}: {title}...")
            text = self.download_page(url)
            if text and len(text) > 100:
                filename = self._sanitize_filename(title) + ".txt"
                filepath = self.output_dir / filename
                filepath.write_text(text, encoding="utf-8")
                results["pages"].append({"title": title, "file": str(filename)})
                results["docs_indexed"] += 1

        # Save manifest
        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        return results

    def _sanitize_filename(self, title: str) -> str:
        """Convert title to safe filename."""
        title = re.sub(r"[^\w\s-]", "", title)
        title = re.sub(r"\s+", "_", title)
        return title[:100]


class KafkaDownloader(DocDownloader):
    """Download Apache Kafka documentation."""

    def get_urls(self) -> list[tuple[str, str]]:
        return [
            ("Kafka Quick Start", "https://kafka.apache.org/documentation/#quickstart"),
            (
                "Kafka Architecture",
                "https://kafka.apache.org/documentation/#architecture",
            ),
            ("Kafka API", "https://kafka.apache.org/documentation/#api"),
            (
                "Kafka Configuration",
                "https://kafka.apache.org/documentation/#configuration",
            ),
            ("Kafka Security", "https://kafka.apache.org/documentation/#security"),
            ("Kafka Monitoring", "https://kafka.apache.org/documentation/#monitoring"),
            ("Kafka Operations", "https://kafka.apache.org/documentation/#operations"),
        ]


class KubernetesDownloader(DocDownloader):
    """Download Kubernetes documentation."""

    def get_urls(self) -> list[tuple[str, str]]:
        return [
            ("Kubernetes Quick Start", "https://kubernetes.io/docs/setup/"),
            ("Kubernetes Concepts", "https://kubernetes.io/docs/concepts/"),
            ("Kubernetes Tasks", "https://kubernetes.io/docs/tasks/"),
            ("Kubernetes Tutorials", "https://kubernetes.io/docs/tutorials/"),
            ("Kubernetes Reference", "https://kubernetes.io/docs/reference/"),
            (
                "Kubernetes API",
                "https://kubernetes.io/docs/reference/generated/kubernetes-api/",
            ),
        ]


class DockerDownloader(DocDownloader):
    """Download Docker documentation."""

    def get_urls(self) -> list[tuple[str, str]]:
        return [
            ("Docker Get Started", "https://docs.docker.com/get-started/"),
            ("Docker Guides", "https://docs.docker.com/guides/"),
            ("Docker Manual", "https://docs.docker.com/manuals/"),
            ("Docker Reference", "https://docs.docker.com/reference/"),
            ("Docker Components", "https://docs.docker.com/components/"),
        ]


def run_all_downloads() -> dict[str, Any]:
    """Download all documentation."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = {}
    for downloader in [
        KafkaDownloader("kafka"),
        KubernetesDownloader("kubernetes"),
        DockerDownloader("docker"),
    ]:
        print(f"\n{'=' * 60}")
        print(f"Starting {downloader.name} download...")
        results[downloader.name] = downloader.download_all()
        print(
            f"Completed {downloader.name}: {results[downloader.name]['docs_indexed']} pages"
        )

    return results


if __name__ == "__main__":
    print(json.dumps(run_all_downloads(), indent=2))
