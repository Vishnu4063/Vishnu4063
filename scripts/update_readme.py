#!/usr/bin/env python3
"""
Update the Daily Motivation section of README.md with a new quote.

This script:
1. Reads the existing README.md
2. Replaces the content between <!-- DAILY_MOTIVATION_START --> and <!-- DAILY_MOTIVATION_END -->
3. Selects a quote based on the current date (deterministic, no external API)
4. Updates the "Last updated" date
5. Writes the modified README back to disk
"""

import json
import os
from datetime import datetime

# Paths - resolve relative to the workspace root (parent of scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.dirname(SCRIPT_DIR)
README_PATH = os.path.join(WORKSPACE_ROOT, "README.md")
QUOTES_PATH = os.path.join(WORKSPACE_ROOT, "quotes.json")


def load_quotes(path):
    """Load quotes from the JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["quotes"]


def select_quote_by_date(quotes):
    """Select a quote based on the current date for deterministic daily variation.

    Uses the date's ordinal (days since 01-01-0001) modulo the number of quotes.
    This ensures:
    - A different quote each day
    - No external API dependency
    - A full cycle through all quotes before repeating
    """
    today = datetime.utcnow().date()
    quote_index = today.toordinal() % len(quotes)
    return quotes[quote_index]


def update_readme(readme_path, quotes_path):
    """Update the Daily Motivation section in README.md."""
    # Load quotes
    quotes = load_quotes(quotes_path)

    # Select quote for today
    today = datetime.utcnow().date()
    selected_quote = select_quote_by_date(quotes)

    # Read current README
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Get the date string for display (UTC)
    date_str = today.strftime("%Y-%m-%d")

    # Build the new Daily Motivation section with markers
    new_section = f"""<!-- DAILY_MOTIVATION_START -->
## 💭 Daily Motivation

> "{selected_quote['quote']}"

_Updated automatically every day. Last updated: {date_str}._
<!-- DAILY_MOTIVATION_END -->"""

    # Find and replace the section between markers
    start_marker = "<!-- DAILY_MOTIVATION_START -->"
    end_marker = "<!-- DAILY_MOTIVATION_END -->"

    start_idx = content.find(start_marker)
    if start_idx == -1:
        # Markers not found - insert after the first ## 💡 section or at a reasonable position
        # Insert before the closing div of the profile section
        insert_pos = content.find('</div>')
        if insert_pos == -1:
            insert_pos = len(content)
        # Insert before the closing div
        new_content = content[:insert_pos] + "\n\n" + new_section + "\n" + content[insert_pos:]
    else:
        # Find the end marker
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            # End marker not found, append at the end
            new_content = content + "\n\n" + new_section
        else:
            # Replace the section between markers (inclusive of markers)
            before = content[:start_idx]
            after = content[end_idx + len(end_marker):]
            new_content = before + "\n\n" + new_section + "\n\n" + after

    # Write updated README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"README updated with quote #{selected_quote['id']}: {selected_quote['quote']}")
    print(f"Last updated: {date_str} (UTC)")


if __name__ == "__main__":
    update_readme(README_PATH, QUOTES_PATH)