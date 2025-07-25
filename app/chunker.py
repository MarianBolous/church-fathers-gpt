
import pdfplumber, re, pandas as pd
from pathlib import Path
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

RAW_DIR = Path("../raw_docs")
OUT_DIR = Path("../processed_chunks")

FATHER_PATTERN = re.compile(r"(CLEMENT|IGNATIUS|POLYCARP|JUSTIN MARTYR|IRENAEUS)", re.IGNORECASE)
CHAPTER_PATTERN = re.compile(r"CHAPTER\s+(\d+)\s*(.*)", re.IGNORECASE)

SUMMARY_PROMPT = """
You are an Orthodox theological assistant. Summarize the following Church Father quote
in 2-3 sentences. Keep it faithful to Orthodox patristic teaching, avoid modern reinterpretation,
and keep the tone pastoral and accurate.

Quote:
\"\"\"{quote}\"\"\"
"""

TOPIC_PROMPT = """
You are a classifier tagging theological themes. Read the following quote and list 3-5 key topics 
as single words or short phrases (e.g., repentance, humility, fasting).

Quote:
\"\"\"{quote}\"\"\"
"""

BIBLE_PROMPT = """
Suggest 1-3 Bible references (Book Chapter:Verse) that directly relate to the following Church Father quote. 
Only use Orthodox canonical books. Return as a comma-separated list without commentary.

Quote:
\"\"\"{quote}\"\"\"
"""

def summarize_quote(quote):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a careful Orthodox theologian summarizing patristic texts."},
                      {"role": "user", "content": SUMMARY_PROMPT.format(quote=quote)}]
        )
        return r.choices[0].message.content.strip()
    except:
        return ""

def detect_topics(quote):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a theological classifier."},
                      {"role": "user", "content": TOPIC_PROMPT.format(quote=quote)}]
        )
        return [t.strip().lower() for t in r.choices[0].message.content.split(",")]
    except:
        return []

def detect_bible_refs(quote):
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are an Orthodox theologian linking Patristic sayings to Scripture."},
                      {"role": "user", "content": BIBLE_PROMPT.format(quote=quote)}]
        )
        return [ref.strip() for ref in r.choices[0].message.content.split(",")]
    except:
        return []

def extract_chunks(file_path):
    chunks = []
    current_father = "Unknown"
    current_chapter = "Unknown"
    current_chapter_title = ""
    all_topics = set()

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            for line in lines:
                father_match = FATHER_PATTERN.search(line)
                if father_match:
                    current_father = father_match.group(1).title()

                chapter_match = CHAPTER_PATTERN.search(line)
                if chapter_match:
                    current_chapter = chapter_match.group(1)
                    current_chapter_title = chapter_match.group(2).strip()

                if len(line.strip()) > 50:
                    quote = line.strip()
                    summary = summarize_quote(quote)
                    topics = detect_topics(quote)
                    bible_refs = detect_bible_refs(quote)
                    all_topics.update(topics)
                    chunks.append({
                        "quote": quote,
                        "father": current_father,
                        "source": f"{file_path.stem} - Chapter {current_chapter}",
                        "chapter_title": current_chapter_title,
                        "topics": topics,
                        "summary": summary,
                        "bible_refs": bible_refs
                    })
    return chunks, all_topics

def main():
    all_chunks = []
    master_topics = set()

    for file in RAW_DIR.glob("*.pdf"):
        print(f"Processing {file.name}...")
        chunks, topics = extract_chunks(file)
        all_chunks.extend(chunks)
        master_topics.update(topics)

    df = pd.DataFrame(all_chunks)
    OUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUT_DIR/"chunks_with_bible.csv", index=False)

    topics_df = pd.DataFrame(sorted(master_topics), columns=["topic"])
    topics_df.to_csv(OUT_DIR/"master_topics.csv", index=False)

    print(f"✅ Processed {len(all_chunks)} chunks.")
    print(f"✅ Found {len(master_topics)} unique topics.")

if __name__ == "__main__":
    main()
