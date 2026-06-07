import requests
from config.settings import SERPAPI_KEY


class SearchService:
    def __init__(self):
        self.api_key = SERPAPI_KEY

    def search(self, query: str) -> str:
        """Search the web using SerpAPI"""
        try:
            response = requests.get(
                "https://serpapi.com/search",
                params={
                    "q": query,
                    "api_key": self.api_key,
                    "num": 3
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                # Get organic results
                for result in data.get("organic_results", [])[:3]:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    results.append(f"• {title}: {snippet}")

                if results:
                    return "\n".join(results)
                return "No results found"
            else:
                print(f"❌ Search failed: {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error searching: {e}")
            return None