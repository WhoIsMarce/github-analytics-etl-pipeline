from datetime import datetime


def normalize_issue(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "number": raw["number"],
        "title": raw["title"],
        "state": raw["state"],
        "is_pull_request": "pull_request" in raw,
        "created_at": raw["created_at"],
        "closed_at": raw.get("closed_at"),
        "comments": raw["comments"],
        "author": raw["user"]["login"] if raw.get("user") else None,
    }
    
def time_to_close_hours(row: dict):
    if not row["closed_at"]:
        return None
    created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    closed = datetime.fromisoformat(row["closed_at"].replace("Z", "+00:00"))
    return round((closed - created).total_seconds() / 3600, 2)