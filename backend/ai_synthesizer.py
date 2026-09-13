import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

class AISynthesizer:
    """Sintetizează informații folosind LLM"""
    
    def __init__(self):
        self.model_type = settings.AI_MODEL_TYPE
    
    async def synthesize(self, question: str, sources_content: dict) -> Optional[str]:
        """
        Sintetizează un răspuns bazat pe conținutul surselor
        
        Args:
            question: Întrebarea utilizatorului
            sources_content: Dict cu {url: text} pentru fiecare sursă
        
        Returns:
            Răspunsul generat de LLM sau None dacă eșuează
        """
        if self.model_type == "openai":
            return await self._synthesize_openai(question, sources_content)
        elif self.model_type == "anthropic":
            return await self._synthesize_anthropic(question, sources_content)
        elif self.model_type == "ollama":
            return await self._synthesize_ollama(question, sources_content)
        else:
            logger.error(f"Model tip necunoscut: {self.model_type}")
            return None
    
    async def _synthesize_openai(self, question: str, sources_content: dict) -> Optional[str]:
        """Sintetizare cu OpenAI API"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Construiește prompt-ul
            sources_text = "\n\n---\n\n".join([
                f"Sursa: {url}\nConținut: {text[:1000]}"
                for url, text in sources_content.items()
            ])
            
            prompt = f"""Analizează următoarele informații din surse web și răspunde la întrebare.

ÎNTREBARE: {question}

SURSE:
{sources_text}

INSTRUCȚIUNI:
1. Răspunde direct și concis la întrebare
2. Folosește informații din sursele de mai sus
3. Nu inventa informații
4. Limitează răspunsul la 500-800 cuvinte
5. Dacă sursele nu oferă suficiente informații, spune-o

RĂSPUNS:"""
            
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Ești un asistent AI care sintetizează informații din web. Răspunde în limba română dacă întrebarea e în română."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content.strip()
            logger.info(f"OpenAI: Răspuns generat ({len(answer)} caractere)")
            return answer
        
        except Exception as e:
            logger.error(f"Eroare OpenAI: {str(e)}")
            return None
    
    async def _synthesize_anthropic(self, question: str, sources_content: dict) -> Optional[str]:
        """Sintetizare cu Anthropic Claude API"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            
            # Construiește prompt-ul
            sources_text = "\n\n---\n\n".join([
                f"Sursa: {url}\nConținut: {text[:1000]}"
                for url, text in sources_content.items()
            ])
            
            prompt = f"""Analizează următoarele informații din surse web și răspunde la întrebare.

ÎNTREBARE: {question}

SURSE:
{sources_text}

INSTRUCȚIUNI:
1. Răspunde direct și concis la întrebare
2. Folosește informații din sursele de mai sus
3. Nu inventa informații
4. Limitează răspunsul la 500-800 cuvinte
5. Dacă sursele nu oferă suficiente informații, spune-o

RĂSPUNS:"""
            
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            answer = response.content[0].text.strip()
            logger.info(f"Claude: Răspuns generat ({len(answer)} caractere)")
            return answer
        
        except Exception as e:
            logger.error(f"Eroare Anthropic: {str(e)}")
            return None
    
    async def _synthesize_ollama(self, question: str, sources_content: dict) -> Optional[str]:
        """Sintetizare cu Ollama (local LLM)"""
        try:
            import httpx
            
            # Construiește prompt-ul
            sources_text = "\n\n---\n\n".join([
                f"Sursa: {url}\nConținut: {text[:1000]}"
                for url, text in sources_content.items()
            ])
            
            prompt = f"""Analizează următoarele informații din surse web și răspunde la întrebare.

ÎNTREBARE: {question}

SURSE:
{sources_text}

INSTRUCȚIUNI:
1. Răspunde direct și concis la întrebare
2. Folosește informații din sursele de mai sus
3. Nu inventa informații
4. Limitează răspunsul la 500-800 cuvinte
5. Dacă sursele nu oferă suficiente informații, spune-o

RĂSPUNS:"""
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                answer = data.get("response", "").strip()
                logger.info(f"Ollama: Răspuns generat ({len(answer)} caractere)")
                return answer
        
        except Exception as e:
            logger.error(f"Eroare Ollama: {str(e)}")
            return None

async def generate_answer(question: str, sources_content: dict) -> Optional[str]:
    """Wrapper funcție pentru generarea răspunsului"""
    synthesizer = AISynthesizer()
    return await synthesizer.synthesize(question, sources_content)

if __name__ == "__main__":
    import asyncio
    
    async def test():
        question = "Cine a fost Albert Einstein?"
        sources = {
            "https://example.com/1": "Albert Einstein a fost un fizician german...",
            "https://example.com/2": "Einstein a dezvoltat teoria relativității...",
        }
        
        answer = await generate_answer(question, sources)
        if answer:
            print("Răspuns generat:")
            print(answer)
        else:
            print("Nu s-a putut genera răspunsul")
    
    asyncio.run(test())
