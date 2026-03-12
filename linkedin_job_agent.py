#!/usr/bin/env python3
"""LinkedIn-style Job Agent.

This script discovers software engineering job links, stores them in
`job_links.txt`, and generates a short markdown summary in `report.md`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import urllib.error
import urllib.parse
import urllib.request


JOB_LINKS_FILE = Path("job_links.txt")
REPORT_FILE = Path("report.md")


@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    url: str


def fetch_remote_jobs(query: str = "python developer") -> list[JobPosting]:
    """Fetch jobs from Remote OK API and map them into a simple structure.

    The script emulates a "LinkedIn job agent" workflow while relying on a
    public API for reliable local execution.
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://remoteok.com/api?tags={encoded_query}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; JobAgent/1.0)",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    jobs: list[JobPosting] = []
    for item in payload:
        if not isinstance(item, dict) or "position" not in item:
            continue
        jobs.append(
            JobPosting(
                title=item.get("position", "Unknown title"),
                company=item.get("company", "Unknown company"),
                location=item.get("location", "Remote"),
                url=item.get("url", ""),
            )
        )

    return jobs[:10]


def fallback_jobs() -> list[JobPosting]:
    """Provide deterministic sample data when network calls fail."""
    return [
        JobPosting(
            title="Python Backend Engineer",
            company="Example Labs",
            location="Remote",
            url="https://www.linkedin.com/jobs/view/0000000001/",
        ),
        JobPosting(
            title="Machine Learning Engineer",
            company="DataNova",
            location="San Francisco, CA",
            url="https://www.linkedin.com/jobs/view/0000000002/",
        ),
        JobPosting(
            title="Full Stack Developer",
            company="CloudOrbit",
            location="New York, NY",
            url="https://www.linkedin.com/jobs/view/0000000003/",
        ),
    ]


def write_outputs(jobs: list[JobPosting], source: str) -> None:
    links = [job.url for job in jobs if job.url]
    JOB_LINKS_FILE.write_text("\n".join(links) + "\n", encoding="utf-8")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# LinkedIn Job Agent Report",
        "",
        f"Generated: {timestamp}",
        f"Source: {source}",
        f"Jobs collected: {len(jobs)}",
        "",
        "## Top job matches",
    ]

    for i, job in enumerate(jobs, start=1):
        lines.append(f"{i}. **{job.title}** — {job.company} ({job.location})")
        lines.append(f"   - Link: {job.url}")

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    try:
        jobs = fetch_remote_jobs()
        source = "remoteok.com api"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        jobs = fallback_jobs()
        source = "local fallback sample data"

    write_outputs(jobs, source)

    print(f"Wrote {len(jobs)} links to {JOB_LINKS_FILE}")
    print(f"Generated report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
