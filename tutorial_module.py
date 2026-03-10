# ============================================================================
# FILE: tutorial_module.py
# PURPOSE: Returns sewing tutorial links for given techniques.
#          Uses YouTube search URLs — swap for YouTube Data API v3 for
#          production use (requires a free Google API key + quota).
# ============================================================================

from typing import List, Dict, Any
import urllib.parse


def find_youtube_tutorials(techniques: List[str]) -> List[Dict[str, Any]]:
    """
    Returns YouTube search links for each sewing technique.

    In production, replace the URL construction below with calls to the
    YouTube Data API v3 (videos.list / search.list) to get real video
    titles, thumbnails, and verified links.
    """
    if not techniques:
        return [
            {
                "title": "Basic Sewing Techniques for Beginners",
                "link": "https://www.youtube.com/results?search_query=basic+sewing+techniques",
            }
        ]

    results = []
    for technique in techniques[:3]:          # Limit to 3 tutorials
        query = urllib.parse.quote_plus(f"sewing tutorial {technique}")
        results.append(
            {
                "title": f"How to: {technique.replace('_', ' ').title()}",
                "link": f"https://www.youtube.com/results?search_query={query}",
            }
        )

    return results
