import json
import re
import os
from collections import defaultdict, Counter

# File paths
FILE_PATH = "../../data/annotations/annotations.json"
OUTPUT_DIR = "../../data/results"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "keyword_analysis_results.txt")

# Comprehensive list of English stop words to ignore in our text mining
STOP_WORDS = {
    "the", "to", "and", "a", "of", "in", "that", "for", "was", "is", "on", 
    "with", "as", "by", "an", "this", "it", "from", "or", "were", "their", 
    "they", "are", "be", "at", "not", "have", "has", "had", "which", "due", 
    "system", "ai", "algorithm", "algorithmic", "subject", "subjects", 
    "resulted", "resulting", "caused", "leading", "led", "based", "its", 
    "because", "who", "them", "these", "those", "when", "where", "how", "what",
    "an", "out", "into", "through", "about", "over", "after", "before", "more",
    "between", "under", "system's", "did", "could", "would", "should", "all",
    "can", "will", "may", "might", "must", "been", "being", "do", "does", "any",
    "doing", "but", "if", "than", "then", "there", "their", "theirs", "we",
    "us", "our", "ours", "you", "your", "yours", "he", "him", "his", "she",
    "her", "hers", "i", "me", "my", "mine", "only", "also", "such", "other"
}

def clean_text(text):
    """Removes punctuation, makes lowercase, and splits into words."""
    if not text:
        return []
    # Remove non-alphabetic characters and convert to lowercase (keep words of 3+ letters)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    # Filter out stop words
    return [w for w in words if w not in STOP_WORDS]

def main():
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found at {FILE_PATH}")
        return

    # Dictionary to hold all words for each category
    category_words = defaultdict(list)
    total_processed = 0

    # Process the dataset
    for incident in data:
        for subject in incident.get("subjects", []):
            markers = subject.get("identity_markers", {})
            
            for cat_name, cat_data in markers.items():
                if cat_data.get("DirectScore") == "Yes":
                    total_processed += 1
                    clean_cat = cat_name.lower().replace("_", " ").strip()
                    
                    # Extract the specific harm text
                    harm_text = cat_data.get("MarkerHarm", "")
                    
                    # Clean and tokenize the text
                    words = clean_text(harm_text)
                    category_words[clean_cat].extend(words)

    # Write the results to a file in the data/results folder
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("============================================================\n")
        out.write(" 📝 TEXT MINING: THE VOCABULARY OF OPPRESSION\n")
        out.write("============================================================\n\n")

        for category in sorted(category_words.keys()):
            words = category_words[category]
            if not words:
                continue
                
            word_counts = Counter(words)
            # Only process categories with enough data points to be meaningful (e.g., > 20 words total)
            if sum(word_counts.values()) > 20: 
                out.write(f"📂 CATEGORY: {category.upper()}\n")
                out.write("-" * 40 + "\n")
                # Get top 10 most common words
                for word, count in word_counts.most_common(10):
                    out.write(f"   • {word.ljust(15)} ({count} times)\n")
                out.write("\n")

    print(f"✅ Done! Text Mining complete. Processed {total_processed} harm descriptions.")
    print(f"📄 Your keyword report has been saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    main()