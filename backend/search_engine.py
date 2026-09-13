import httpx
import logging
from typing import List, Dict, Optional
from config import settings
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SearchResult:
    """Model pentru rezultatul căutării"""
    def __init__(self, title: str, url: str, snippet: str):
        self.title = title
        self.url = url
        self.snippet = snippet
    
    def to_dict(self):
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet
        }

class SearchEngine:
    """Interfață pentru motoare de căutare web"""
    
    def __init__(self):
        self.engine = settings.SEARCH_ENGINE
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Caută pe internet și returnează rezultatele
        """
        if self.engine == "brave_search":
            return await self._brave_search(query, num_results)
        elif self.engine == "serpapi":
            return await self._serpapi_search(query, num_results)
        elif self.engine == "bing":
            return await self._bing_search(query, num_results)
        else:
            raise ValueError(f"Motor de căutare necunoscut: {self.engine}")
    
    async def _brave_search(self, query: str, num_results: int) -> List[SearchResult]:
        """Căutare folosind Brave Search API"""
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Authorization": f"Token {settings.BRAVE_SEARCH_API_KEY}"
        }
        params = {
            "q": query,
            "count": num_results
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for result in data.get("web", []):
                results.append(SearchResult(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("description", "")
                ))
            
            logger.info(f"Brave Search: {len(results)} rezultate pentru '{query}'")
            return results
        
        except httpx.HTTPError as e:
            logger.error(f"Eroare Brave Search: {str(e)}")
            return []
    
    async def _serpapi_search(self, query: str, num_results: int) -> List[SearchResult]:
        """Căutare folosind SerpAPI"""
        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": settings.SERPAPI_API_KEY,
            "num": num_results,
            "engine": "google"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for result in data.get("organic_results", []):
                results.append(SearchResult(
                    title=result.get("title", ""),
                    url=result.get("link", ""),
                    snippet=result.get("snippet", "")
                ))
            
            logger.info(f"SerpAPI: {len(results)} rezultate pentru '{query}'")
            return results
        
        except httpx.HTTPError as e:
            logger.error(f"Eroare SerpAPI: {str(e)}")
            return []
    
    async def _bing_search(self, query: str, num_results: int) -> List[SearchResult]:
        """Căutare folosind Bing Search API"""
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            "Ocp-Apim-Subscription-Key": settings.BING_SEARCH_API_KEY
        }
        params = {
            "q": query,
            "count": num_results
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            for result in data.get("webPages", {}).get("value", []):
                results.append(SearchResult(
                    title=result.get("name", ""),
                    url=result.get("url", ""),
                    snippet=result.get("snippet", "")
                ))
            
            logger.info(f"Bing Search: {len(results)} rezultate pentru '{query}'")
            return results
        
        except httpx.HTTPError as e:
            logger.error(f"Eroare Bing Search: {str(e)}")
            return []

def is_safe_url(url: str) -> bool:
    """
    Verifică dacă URL-ul este sigur pentru acces (protecție SSRF)
    Nu permite localhost, IPs private, file://, etc.
    """
    try:
        parsed = urlparse(url)
        
        # Verifică schema
        if parsed.scheme not in ["http", "https"]:
            return False
        
        # Verifică host-ul
        hostname = parsed.hostname or ""
        hostname_lower = hostname.lower()
        
        # Interzice localhost și variante
        if hostname_lower in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:
            return False
        
        # Interzice IP-uri private (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
        if hostname_lower.startswith(("192.168.", "10.", "172.")):
            return False
        
        # Interzice IP-uri link-local (169.254.x.x)
        if hostname_lower.startswith("169.254."):
            return False
        
        return True
    
    except Exception:
        return False

async def get_top_results(query: str, max_results: int = 3) -> List[SearchResult]:
    """
    Obține top N rezultate sigure din căutare
    """
    search_engine = SearchEngine()
    all_results = await search_engine.search(query, num_results=10)
    
    # Filtrează doar URL-urile sigure
    safe_results = [
        result for result in all_results 
        if is_safe_url(result.url)
    ]
    
    # Returnează primele max_results
    return safe_results[:max_results]

if __name__ == "__main__":
    import asyncio
    
    async def test():
        results = await get_top_results("Albert Einstein", max_results=3)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Snippet: {result.snippet[:100]}...")
    
    asyncio.run(test())
