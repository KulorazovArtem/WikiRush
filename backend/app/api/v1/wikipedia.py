"""
Endpoints для работы с Wikipedia API
"""
from fastapi import APIRouter, HTTPException, status

from app.services.wikipedia_service import wikipedia_service

router = APIRouter()


@router.get("/article/{title}/summary")
async def get_article_summary(title: str):
    """Получить краткое описание статьи"""
    article_info = await wikipedia_service.get_article_info(title)

    if not article_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Статья '{title}' не найдена"
        )

    return {
        "title": article_info.get("title", title),
        "extract": article_info.get("extract", ""),
        "page_id": article_info.get("pageid"),
    }


@router.get("/article/{title}/links")
async def get_article_links(title: str, limit: int = 50):
    """Получить список ссылок из статьи"""
    links = await wikipedia_service.get_article_links(title, limit=limit)

    if not links:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Статья '{title}' не найдена или не содержит ссылок",
        )

    return {"title": title, "links": links, "total": len(links)}


@router.get("/search")
async def search_articles(query: str, limit: int = 10):
    """Поиск статей по запросу"""
    results = await wikipedia_service.search_articles(query, limit=limit)

    return {
        "query": query,
        "results": [
            {
                "title": result.get("title"),
                "snippet": result.get("snippet", ""),
                "page_id": result.get("pageid"),
            }
            for result in results
        ],
        "total": len(results),
    }
