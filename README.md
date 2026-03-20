# 🌐 Web Summarizer AI

A local LLM-powered pipeline that scrapes a website, processes the content, and returns a clean structured summary — running entirely on your own machine via Ollama.

---

## 🚀 Overview

Most LLM demos just send a short prompt and print a response. This project solves a real engineering problem: **what do you do when the content is too large to fit in a single LLM call?**

The pipeline handles this with chunking, parallel inference, and a two-stage summarization strategy — patterns used in production LLM systems.

---

## 🧠 How It Works

```
URL entered
   ↓
Cache check → if already summarized, return instantly
   ↓
Scrape webpage → strip HTML tags, scripts, nav, footer
   ↓
Clean text → remove newlines, limit to 4000 chars
   ↓
Smart chunking → split into ~800 char sentence-aware pieces
   ↓
Parallel LLM calls → summarize each chunk (2 at a time)
   ↓
Combine summaries → one final structured LLM call
   ↓
Save to cache → skip all this next time
   ↓
Print final output
```

---

## ⚙️ Key Engineering Decisions

**Chunking** — LLMs have context limits. Feeding a full webpage in one shot either fails or produces poor output. Splitting into ~800 character chunks keeps each call focused and within limits.

**Two-stage summarization** — Each chunk gets its own summary first, then all summaries are combined in a final call. This is the map-reduce pattern applied to LLM inference.

**Parallel execution** — Chunks are summarized 2 at a time using `ThreadPoolExecutor` instead of sequentially. Cuts inference time roughly in half for multi-chunk pages.

**Caching** — Results are saved to disk using the URL's MD5 hash as the filename. Re-running on the same URL returns instantly without touching the LLM. Delete the `cache/` folder to force a fresh run.

**Smart scraping** — BeautifulSoup strips not just `<script>` and `<style>` tags but also `<nav>`, `<footer>`, and `<header>` elements. This prevents the LLM from summarizing navigation menus, reference lists, and external link sections as if they were real content.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Ollama + llama3.2 | Local LLM inference |
| OpenAI SDK | API client (pointed at Ollama) |
| BeautifulSoup4 | HTML parsing and cleaning |
| ThreadPoolExecutor | Parallel LLM calls |
| hashlib + os | File-based caching |

---

## ▶️ Setup

Make sure you have [Ollama](https://ollama.com) installed and running with llama3.2 pulled:

```bash
ollama pull llama3.2
ollama serve
```

Then install dependencies:

```bash
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

---

## ▶️ Run

```bash
python app.py
```

You will be prompted to enter a URL:

```
Enter website URL: https://en.wikipedia.org/wiki/Machine_learning
```

---

## 📌 Example Output

Input URL: `https://en.wikipedia.org/wiki/Machine_learning`

```
**Main Topic:** Machine Learning

**Key Points:**
1. Machine learning paradigms: supervised, unsupervised, semi-supervised, self-supervised, reinforcement learning
2. Supervised learning types: classification, regression, decision trees, random forest, SVM, neural networks
3. Deep learning architectures: CNN, RNN, LSTM, GAN, diffusion models
4. Real-world applications: bioinformatics, finance, healthcare, NLP, image recognition
5. Key limitations: explainability, overfitting, data bias

**Short Summary:**
Machine learning is the study of algorithms that improve automatically through experience.
It encompasses many paradigms and has broad applications across industry and research.
```

---

## 💡 What This Project Demonstrates

- Designing a multi-step LLM pipeline from scratch
- Solving the context limit problem with chunking
- Applying map-reduce thinking to LLM inference
- Performance optimization with parallel execution
- Caching strategies to avoid redundant LLM calls
- Prompt engineering for structured, consistent output
- Cleaning noisy web data before it reaches the model

---

## 🔮 Future Improvements

- Crawl multiple pages from the same domain
- Semantic chunking (split by meaning, not character count)
- RAG-based Q&A on top of scraped content
- Streamlit UI for a proper interface
- Configurable model and chunk size via CLI flags

---

## 📌 Notes

- This project runs fully locally — no OpenAI API key needed
- The OpenAI SDK is used purely as a client pointed at Ollama's OpenAI-compatible endpoint
- Caching is URL-based; delete the `cache/` folder to force a fresh fetch

---

## 👨‍💻 Author

Vishruth — built as part of learning practical LLM engineering.
Third project in a series exploring real-world LLM application patterns.