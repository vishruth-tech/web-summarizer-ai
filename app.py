from openai import OpenAI
from scraper import fetch_website_contents
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import hashlib
import os
 
load_dotenv()
 
# -----------------------------
# CONFIG
# -----------------------------
MODEL = "openai/gpt-oss-120b"
BASE_URL = "https://api.groq.com/openai/v1"

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")

client = OpenAI(base_url=BASE_URL, api_key=api_key)
 
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
 
# -----------------------------
# PROMPTS
# -----------------------------
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are an expert AI assistant that extracts key insights from web content. "
        "Focus only on meaningful information. Ignore noise like ads, navigation, and repeated text. "
        "Always return clear, structured output."
    )
}
 
# -----------------------------
# UTILS
# -----------------------------
def hash_url(url):
    return hashlib.md5(url.encode()).hexdigest()
 
 
def clean_text(text):
    return text.replace("\n", " ").strip()
 
 
def smart_chunk(text, max_len=800):
    sentences = text.split(". ")
    chunks, current = [], ""
 
    for sentence in sentences:
        if len(current) + len(sentence) < max_len:
            current += sentence + ". "
        else:
            chunks.append(current)
            current = sentence + ". "
 
    if current:
        chunks.append(current)
 
    return chunks
 
 
def call_model(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content
 
 
# -----------------------------
# CACHE
# -----------------------------
def load_cache(url):
    path = os.path.join(CACHE_DIR, hash_url(url))
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None
 
 
def save_cache(url, data):
    path = os.path.join(CACHE_DIR, hash_url(url))
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
 
 
# -----------------------------
# PIPELINE
# -----------------------------
def summarize_chunk(chunk):
    if not chunk.strip():
        return ""
 
    messages = [
        SYSTEM_PROMPT,
        {
            "role": "user",
            "content": f"""
Summarize the following content.
 
Content:
{chunk}
 
Return:
- Key Points
- Important Facts
"""
        }
    ]
 
    return call_model(messages)
 
 
def summarize_parallel(chunks):
    with ThreadPoolExecutor(max_workers=2) as executor:
        return list(executor.map(summarize_chunk, chunks))
 
 
def combine_summaries(summaries):
    valid_summaries = [s for s in summaries if s and len(s.strip()) > 20]
 
    if not valid_summaries:
        return "Failed to generate summaries."
 
    combined_text = "\n\n".join(valid_summaries)
 
    messages = [
        SYSTEM_PROMPT,
        {
            "role": "user",
            "content": f"""
Combine the following summaries into a final structured output.
 
Summaries:
{combined_text}
 
Return:
 
Main Topic:
Key Points:
- ...
Short Summary:
"""
        }
    ]
 
    return call_model(messages)
 
 
def summarize_website(url):
    # Step 1: Cache check
    cached = load_cache(url)
    if cached:
        print("⚡ Using cached result")
        return cached
 
    # Step 2: Fetch website
    print("🌐 Fetching website...")
    try:
        text = fetch_website_contents(url)
    except Exception as e:
        return f"Error fetching website: {e}"
 
    if not text.strip():
        return "No meaningful content extracted."
 
    # Step 3: Clean + limit
    print("🧹 Cleaning content...")
    text = clean_text(text)[:20000]
 
    # Step 4: Chunk
    print("✂️ Splitting into chunks...")
    chunks = smart_chunk(text)
 
    if not chunks:
        return "Failed to split content."
 
    # Step 5: Summarize chunks
    print(f"⚡ Processing {len(chunks)} chunks...")
    summaries = summarize_parallel(chunks)
 
    # Step 6: Combine
    print("🧠 Generating final summary...")
    final_output = combine_summaries(summaries)
 
    # Step 7: Save cache
    save_cache(url, final_output)
 
    return final_output
 
 
# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    url = input("Enter website URL: ").strip()
 
    result = summarize_website(url)
 
    print("\n🔥 FINAL OUTPUT:\n")
    print(result)