import re
import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from datetime import datetime
from core.extractors import Extractor
from core.id_creator import FileIDGenerator
import shutil
from tkinter import messagebox

class FileProcessor:
    def __init__(self, app):
        self.app = app
        self.file_path = None
        self.stop_words = set(ENGLISH_STOP_WORDS)
        self.model = SentenceTransformer("paraphrase-MiniLM-L6-v2")  # Shared model
        self.keyword_model = KeyBERT(model=self.model)  # Reuse model
        self.extractor = Extractor()  # Integrate the Extractor class

    def process_file(self, file_path):
        """
        Only read and return file content without analysis.
        """
        self.file_path = file_path
        return self.read_file_content(file_path)

    def read_file_content(self, file_path):
        """
        Use the Extractor class to read file content based on extension.
        """
        try:
            extractor_func = self.extractor.get_extractor_by_extension(file_path)
            if extractor_func:
                content = extractor_func(file_path)
                return content
            else:
                ext = os.path.splitext(file_path)[1].lower()
                return f"[Preview not available for {ext} files]"
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")


    def remove_stopwords(self, text):
        print(">>> Removing stopwords...")
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in self.stop_words]
        return " ".join(filtered_words)

    def extract_keywords(self, text, top_k=10): 
        print(">>> Extracting keywords using Transformer (KeyBERT)...")
        keywords = self.keyword_model.extract_keywords(
            text, top_n=top_k, stop_words='english', use_maxsum=True
        )
        top_keywords = [kw[0] for kw in keywords]
        print(f">>> Extracted {len(top_keywords)} keywords: {top_keywords}")
        return top_keywords

    def calculate_cosine_similarity(self, vector1, vector2):
        return cosine_similarity([vector1], [vector2])[0][0]

    def create_folder_structure(self, root_dir, topic, parent=None):
        if parent:
            parent_dir = os.path.join(root_dir, parent)
            os.makedirs(parent_dir, exist_ok=True)
            topic_dir = os.path.join(parent_dir, topic)
        else:
            topic_dir = os.path.join(root_dir, topic)
        os.makedirs(topic_dir, exist_ok=True)
        return topic_dir

    def analyze_text(self, text):
        try:
            print(">>> Analyzing text...")
            clean_text = self.remove_stopwords(text)
            keywords = self.extract_keywords(clean_text, top_k=10)
            if not keywords:
                raise ValueError("No keywords extracted from the content")
            # Lấy embedding cho tất cả 10 keywords
            keyword_embeddings = [self.model.encode(kw) for kw in keywords]
            return {
                "keywords": keywords,
                "embeddings": keyword_embeddings,
            }
        except Exception as e:
            print(f"❌ Error analyzing text: {e}")
            return {
                "keywords": [],
                "embeddings": [],
            }

    def analyze_content(self, json_data, root_dir, keyword_embeddings, keywords, input_file_path):
        print(">>> Matching keywords with topics (including children)...")
        best_match = None  # (topic_name, parent_name, is_child, keyword, similarity)
        highest_similarity = 0.0

        for topic in json_data:
            parent_name = topic.get("name", "Unnamed")
            parent_vector = topic.get("embedding_vector")
            children = topic.get("children", [])

            # So sánh với topic cha
            if parent_vector is not None:
                parent_vector = np.array(parent_vector)
                for kw, emb in zip(keywords, keyword_embeddings):
                    if len(parent_vector) == len(emb):
                        similarity = self.calculate_cosine_similarity(emb, parent_vector)
                        print(f"Parent '{parent_name}' vs keyword '{kw}' similarity: {similarity:.2f}")
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            best_match = (parent_name, None, False, kw, similarity)

            # So sánh với topic con
            for child in children:
                if not isinstance(child, dict):
                    continue
                child_name = child.get("name")
                child_vector = child.get("embedding_vector")
                if not child_name or not child_vector:
                    continue
                child_vector = np.array(child_vector)
                for kw, emb in zip(keywords, keyword_embeddings):
                    if len(child_vector) == len(emb):
                        similarity = self.calculate_cosine_similarity(emb, child_vector)
                        print(f"Child '{child_name}' vs keyword '{kw}' similarity: {similarity:.2f}")
                        if similarity > highest_similarity:
                            highest_similarity = similarity
                            best_match = (child_name, parent_name, True, kw, similarity)

        if best_match and highest_similarity > 0.7:
            topic_name, parent_name, is_child, keyword, similarity = best_match
            print(f"✅ Best match: '{topic_name}' (similarity: {similarity:.2f})")
            if input_file_path:
                folder_path = self.create_folder_structure(root_dir, topic_name, parent_name if is_child else None)
                created_time = datetime.now().isoformat()
                file_id = FileIDGenerator(created_time).get_file_id()
                # Cập nhật metadata
                new_entry = {
                    "file_id": file_id,
                    "embedding": keyword_embeddings[keywords.index(keyword)].tolist(),
                    "keyword": keyword
                }
                json_file_path = os.path.join(root_dir, "node.json")
                try:
                    if os.path.exists(json_file_path):
                        with open(json_file_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    else:
                        metadata = []
                    metadata.append(new_entry)
                    with open(json_file_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=4)
                    print(f"✅ Metadata updated at {json_file_path}")
                    # Check if destination file already exists
                    dest_file_path = os.path.join(folder_path, os.path.basename(input_file_path))
                    if os.path.exists(dest_file_path):
                        # Add a timestamp to the filename to avoid conflict
                        name, ext = os.path.splitext(os.path.basename(input_file_path))
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest_file_path = os.path.join(folder_path, f"{name}_{ts}{ext}")
                    
                    shutil.move(input_file_path, dest_file_path)
                    print(f"✅ Moved file to '{dest_file_path}'")
                    messagebox.showinfo("Topic Matched", f"Đã gán chủ đề: {topic_name}\nFile đã được di chuyển!")
                except Exception as e:
                    print(f"❌ File move or metadata update failed: {e}")
                    raise e # Re-raise to let the app handle it if needed

            return {
                "topic_name": topic_name,
                "similarity": float(similarity),
                "keyword": keyword,
                "moved": bool(input_file_path)
            }
        else:
            print("✖ No match found with sufficient similarity.")
            return None

    def show_analysis(self, stats):
        """
        Hiển thị kết quả phân tích lên analysis_text.
        """
        self.app.analysis_text.delete("1.0", "end")
        if not stats:
            self.app.analysis_text.insert("1.0", "No analysis available.")
            return
        lines = []
        if "keywords" in stats:
            lines.append("Keywords: " + ", ".join(stats["keywords"]))
        if "matched_topic" in stats and stats["matched_topic"]:
            mt = stats["matched_topic"]
            lines.append(f"Matched Topic: {mt.get('topic_name', '')} (Similarity: {mt.get('similarity', 0):.2f})")
            lines.append(f"Keyword: {mt.get('keyword', '')}")
        self.app.analysis_text.insert("1.0", "\n".join(lines))
             