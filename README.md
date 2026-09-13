# MiniSearch AI

O aplicație web AI simplă care răspunde la întrebări utilizatorilor folosind informații găsite pe internet.

## 🎯 Caracteristici Principale

- **Căutare Web Inteligentă**: Găsește primele 3 rezultate relevante
- **Extragere Conținut**: Parsează și curață textul util din pagini
- **Sintetizare AI**: Generează răspunsuri concise și informative
- **Interfață Modernă**: Design responsive cu mod dark
- **Securitate**: API keys în variabile de mediu, validări, protecție SSRF
- **Surse Transparente**: Afișează cele 3 surse utilizate cu linkuri

## 📋 Cerințe

- Python 3.9+
- Node.js 16+ (pentru frontend, opțional dacă folosești HTML/JS pur)
- Un API key pentru căutare web (Brave Search, SerpAPI, Bing)
- Un API key pentru LLM (OpenAI, Anthropic, sau local cu Ollama)

## 🚀 Instalare

### 1. Clonează Repositoriul

```bash
git clone https://github.com/adrianus271-afk/minisearch-ai.git
cd minisearch-ai
```

### 2. Configurează Variabilele de Mediu

```bash
cp .env.example .env
```

Editorează `.env` și adaugă cheile tale:

```env
# Căutare web
SEARCH_ENGINE=brave_search
BRAVE_SEARCH_API_KEY=your_key_here

# AI/LLM
AI_MODEL_TYPE=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. Instalează Dependențele Backend

```bash
cd backend
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Pornește Backend-ul

```bash
python main.py
```

Backend va rula pe `http://localhost:8000`

### 5. Deschide Frontend-ul

Deschide în browser:
```
http://localhost:8000/static/index.html
```

## 📚 Cum Funcționează

### Fluxul Aplicației

```
Utilizator introduce întrebare
          ↓
Web Search API (Brave/SerpAPI/Bing)
          ↓
Prelucrează top 3 rezultate
          ↓
Fetch paginile web (cu timeout)
          ↓
Extrage text relevant (elimină ads, meniu, etc.)
          ↓
Trimite informații către LLM (OpenAI/Ollama/Anthropic)
          ↓
LLM sintetizează răspuns
          ↓
Afișează răspuns + cele 3 surse
```

### Selectarea Surselor

1. **Căutare web** - obține top 10 rezultate
2. **Filtrare** - verifică dacă URL-ul este accesibil
3. **Fetch conținut** - descarcă pagina cu timeout de 8 secunde
4. **Validare** - extrage text util (min 200 caractere)
5. **Stop** - când sunt 3 surse valide

Dacă o pagină nu se accesează, trece la următoarea.

## 🔑 API Keys - Unde să le Iei

### Căutare Web

**Brave Search** (Recomandat - gratuit):
- Merge la https://api.search.brave.com
- Sign up gratuit
- Obți API key instant

**SerpAPI** (Alternativ):
- Merge la https://serpapi.com
- 100 request-uri gratuite/lună
- Suportă Google, Bing, Yahoo, etc.

**Bing Search** (Alternativ):
- Merge la https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
- Oferă 1000 query-uri gratuite/lună

### LLM/AI

**OpenAI** (Recomandat):
- Merge la https://platform.openai.com/api-keys
- Înregistrează-te și crează API key
- Plată pe bază de utilizare (ieftin pentru start)

**Anthropic Claude** (Alternativ):
- Merge la https://console.anthropic.com
- Oferă credit inițial

**Ollama Local** (Gratuit):
- Instalează de la https://ollama.ai
- Rulează modele local (no API key needed)
- Comandă: `ollama run llama2`

## 📝 Exemple de Întrebări

```
"Cine a fost Albert Einstein?"
"Cum se face pâinea de casă?"
"Ce este Python și pentru ce se folosește?"
"Istoria Internetului"
"Cum se calculează suprafața unui triunghi?"
```

## ⚙️ Configurare Avansată

### Schimbă Motorul de Căutare

Edit `.env`:
```env
SEARCH_ENGINE=serpapi  # sau brave_search, bing
SERPAPI_API_KEY=your_key
```

### Schimbă Modelul AI

```env
AI_MODEL_TYPE=anthropic  # sau openai, ollama
ANTHROPIC_API_KEY=your_key
```

### Folosește Ollama Local

```env
AI_MODEL_TYPE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Ajustează Limite

```env
MAX_RESULTS_PER_QUERY=5        # Până la 5 surse
REQUEST_TIMEOUT_SECONDS=15     # Timeout mai mare
RATE_LIMIT_REQUESTS_PER_MINUTE=30
```

## 🔒 Securitate

✅ **API keys în `.env`** - Nu în codul git  
✅ **Input validation** - Lungime max, caractere speciale  
✅ **SSRF Protection** - Nu permite localhost/private IPs  
✅ **Request timeout** - Nu bloca thread-urile  
✅ **Rate limiting** - Max 20 req/minut per IP  
✅ **Error handling** - Nu dezvălui stack traces  
✅ **CORS configurabil** - Doar frontend autorizat  

### Fișierul `.env` este ignorat de git

```bash
# Verifică că .env e în .gitignore
cat .gitignore | grep .env
```

## 📁 Structura Proiectului

```
minisearch-ai/
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── config.py               # Configurare din .env
│   ├── search_engine.py        # Modul căutare web
│   ├── content_extractor.py    # Modul extragere text
│   ├── ai_synthesizer.py       # Modul sintetizare AI
│   ├── requirements.txt        # Dependențe Python
│   └── static/
│       ├── index.html          # Frontend
│       ├── style.css           # Stiluri
│       └── script.js           # JavaScript
├── .env.example                # Template variabile
├── .gitignore                  # Ignorare git
└── README.md                   # Acest fișier
```

## 🐛 Limitări Cunoscute

- Răspunsurile sunt limitate la 1000 caractere
- Suportă doar limba engleză și română (depinde de LLM)
- Timeoutul pentru fetch pagini este 8 secunde
- Max 20 request-uri/minut per IP
- Nu parsează conținut dinamic (JavaScript)

## 🆘 Troubleshooting

### "API key invalid"
- Verifică că `.env` e în folderul backend
- Copiază și testează API key din console

### "Cannot connect to search API"
- Verifică conexiunea internet
- Testează API key cu curl:
```bash
curl "https://api.search.brave.com/res/v1/web/search?q=test&count=3" \
  -H "Authorization: Token YOUR_KEY"
```

### "Timeout when fetching page"
- Site-ul poate fi slow sau down
- Aplicația va trece la urmatoarea sursă

### "LLM not responding"
- Verifică API key OpenAI
- Dacă folosești Ollama, asigură-te că e pornit: `ollama serve`

### "CORS error în browser"
- Backend trebuie pornit pe `http://localhost:8000`
- Frontend trebuie pe aceeași origine

## 📞 Support

Pentru probleme:
1. Verifică `.env` este configurat corect
2. Vezi logurile backend-ului
3. Deschide issue pe GitHub

## 📜 Licență

MIT

## 🤝 Contribuții

Pull requests binevenite!

---

**Versiune**: 1.0.0  
**Ultimă actualizare**: septembrie 2024
