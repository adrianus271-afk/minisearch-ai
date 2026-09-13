import httpx
import logging
from typing import Optional
from bs4 import BeautifulSoup
from config import settings
import re

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Extrage și curață conținutul din pagini HTML"""
    
    def __init__(self):
        self.timeout = settings.PAGE_FETCH_TIMEOUT_SECONDS
        self.max_size = settings.MAX_PAGE_SIZE_MB * 1024 * 1024
    
    async def fetch_and_extract(self, url: str) -> Optional[str]:
        """
        Descarcă pagina și extrage textul relevant
        Returnează textul curățat sau None dacă nu reușește
        """
        try:
            html = await self._fetch_page(url)
            if not html:
                return None
            
            text = self._extract_text(html)
            if not text or len(text) < 200:
                logger.warning(f"Text prea scurt de la {url}: {len(text)} caractere")
                return None
            
            return text
        
        except Exception as e:
            logger.error(f"Eroare la extragerea din {url}: {str(e)}")
            return None
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Descarcă pagina HTML cu timeout și validări"""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                limits=httpx.Limits(max_connections=5)
            ) as client:
                # Headers obișnuiți ca să evităm blocajele
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                # Verifică dimensiunea răspunsului
                if len(response.content) > self.max_size:
                    logger.warning(f"Pagina {url} e prea mare: {len(response.content)} bytes")
                    return None
                
                return response.text
        
        except httpx.TimeoutException:
            logger.warning(f"Timeout la {url}")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code} la {url}")
            return None
        except Exception as e:
            logger.error(f"Eroare la fetch {url}: {str(e)}")
            return None
    
    def _extract_text(self, html: str) -> str:
        """
        Extrage textul util din HTML
        Elimină: scripts, styles, ads, navigation, etc.
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Elimină elementele inutile
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'noscript']):
                element.decompose()
            
            # Elimină comentarii
            for comment in soup.find_all(string=lambda text: isinstance(text, str)):
                if text.strip().startswith('<!--') and text.strip().endswith('-->'):
                    comment.extract()
            
            # Extrage textul din main content areas prioritar
            main_content = None
            
            # Încearcă să găsească main content
            for selector in ['main', 'article', '[role="main"]', '.content', '.post-content']:
                element = soup.select_one(selector)
                if element:
                    main_content = element
                    break
            
            # Dacă nu găsește main, folosește body
            if not main_content:
                main_content = soup.find('body') or soup
            
            # Extrage textul
            text = main_content.get_text(separator=' ', strip=True)
            
            # Curață whitespace excesiv
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Elimină liniiile prea scurte care par să fie din UI
            lines = [line.strip() for line in text.split('.') if len(line.strip()) > 20]
            text = '. '.join(lines)
            
            # Limitează la primii 3000 caractere (pentru eficiență AI)
            text = text[:3000]
            
            logger.info(f"Extras {len(text)} caractere")
            return text
        
        except Exception as e:
            logger.error(f"Eroare la parsarea HTML: {str(e)}")
            return ""
    
    def extract_text_from_html(self, html: str) -> str:
        """Wrapper public pentru extragere text"""
        return self._extract_text(html)

async def extract_from_urls(urls: list) -> dict:
    """
    Extrage conținut din mai multe URL-uri
    Returnează dict cu URL ca key și textul extras ca value
    """
    extractor = ContentExtractor()
    results = {}
    
    for url in urls:
        logger.info(f"Extrag din: {url}")
        text = await extractor.fetch_and_extract(url)
        if text:
            results[url] = text
            logger.info(f"✓ Extras cu succes din {url}")
        else:
            logger.warning(f"✗ Nu s-a putut extrage din {url}")
    
    return results

if __name__ == "__main__":
    import asyncio
    
    async def test():
        extractor = ContentExtractor()
        url = "https://en.wikipedia.org/wiki/Albert_Einstein"
        text = await extractor.fetch_and_extract(url)
        if text:
            print(f"Extras {len(text)} caractere:")
            print(text[:500])
        else:
            print("Nu s-a putut extrage")
    
    asyncio.run(test())
