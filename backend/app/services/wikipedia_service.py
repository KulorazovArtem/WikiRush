"""
Сервис для работы с Wikipedia API
"""
import asyncio
from typing import Any

import httpx

from app.core.config import settings


class WikipediaService:
    """Сервис для работы с Wikipedia"""
    
    def __init__(self):
        self.api_url = settings.WIKIPEDIA_API_URL
        self.timeout = httpx.Timeout(10.0)
        self._rate_limiter = asyncio.Semaphore(settings.WIKIPEDIA_RATE_LIMIT)
    
    async def _make_request(self, params: dict[str, Any]) -> dict[str, Any]:
        """Выполнение запроса к Wikipedia API с rate limiting"""
        async with self._rate_limiter:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.api_url, params=params)
                response.raise_for_status()
                return response.json()
    
    async def get_article_info(self, title: str) -> dict[str, Any] | None:
        """Получение информации о статье"""
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "info|extracts",
            "exintro": True,
            "explaintext": True,
        }
        
        try:
            data = await self._make_request(params)
            pages = data.get("query", {}).get("pages", {})
            
            # Получаем первую (и единственную) страницу
            page = next(iter(pages.values()), None)
            
            if page and "missing" not in page:
                return page
            
            return None
        except Exception as e:
            print(f"Error fetching article info: {e}")
            return None
    
    async def get_article_links(self, title: str, limit: int = 500) -> list[str]:
        """Получение списка ссылок из статьи"""
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "links",
            "pllimit": min(limit, 500),  # Max 500 per request
            "plnamespace": 0,  # Only main namespace
        }
        
        try:
            data = await self._make_request(params)
            pages = data.get("query", {}).get("pages", {})
            
            page = next(iter(pages.values()), None)
            
            if page and "links" in page:
                return [link["title"] for link in page["links"]]
            
            return []
        except Exception as e:
            print(f"Error fetching article links: {e}")
            return []
    
    async def search_articles(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Поиск статей по запросу"""
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": min(limit, 50),
        }
        
        try:
            data = await self._make_request(params)
            results = data.get("query", {}).get("search", [])
            return results
        except Exception as e:
            print(f"Error searching articles: {e}")
            return []
    
    async def get_random_article(self) -> str | None:
        """Получение случайной статьи"""
        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnnamespace": 0,
            "rnlimit": 1,
        }
        
        try:
            data = await self._make_request(params)
            random_pages = data.get("query", {}).get("random", [])
            
            if random_pages:
                return random_pages[0]["title"]
            
            return None
        except Exception as e:
            print(f"Error getting random article: {e}")
            return None
    
    async def validate_article_exists(self, title: str) -> bool:
        """Проверка существования статьи"""
        article = await self.get_article_info(title)
        return article is not None
    
    async def is_link_valid(self, from_article: str, to_article: str) -> bool:
        """Проверка существования ссылки между статьями"""
        links = await self.get_article_links(from_article)
        return to_article in links
    
    async def get_shortest_path_length(
        self, 
        start: str, 
        target: str, 
        max_depth: int = 6
    ) -> int | None:
        """
        Приблизительная оценка длины кратчайшего пути (BFS)
        Возвращает None если путь не найден
        """
        if start == target:
            return 0
        
        visited = {start}
        queue = [(start, 0)]
        
        while queue and len(visited) < 1000:  # Ограничение для производительности
            current, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            links = await self.get_article_links(current, limit=100)
            
            for link in links:
                if link == target:
                    return depth + 1
                
                if link not in visited:
                    visited.add(link)
                    queue.append((link, depth + 1))
        
        return None


# Singleton instance
wikipedia_service = WikipediaService()
