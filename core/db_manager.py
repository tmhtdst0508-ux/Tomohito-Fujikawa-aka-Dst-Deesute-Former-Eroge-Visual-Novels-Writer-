"""
Database Manager for KENZEN SeaArt Helper v5.0.0
Handles SQLite tags.db operations, category loading, tag retrieval, and search.
"""

import os
import sqlite3
from typing import List, Dict, Tuple, Optional, Any


from .path_utils import get_resource_path


class DBManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.db_path = get_resource_path("tags.db")
        else:
            self.db_path = db_path

        self._categories_cache: List[Dict] = []
        self._tags_by_category_cache: Dict[int, List[Dict]] = {}
        self._jp_to_en_map: Dict[str, str] = {}
        self._en_to_jp_map: Dict[str, str] = {}
        self._tag_to_category_order: Dict[str, int] = {}
        
        # Verify database health before loading
        is_healthy, _ = self.verify_database_health()
        if is_healthy:
            self.load_all_data()

    def verify_database_health(self) -> Tuple[bool, str]:
        """
        Performs 3-tier integrity checks on SQLite database:
        1. File existence and size (> 1KB)
        2. SQLite PRAGMA integrity_check == 'ok'
        3. Essential tables ('categories', 'tags') and non-zero rows exist.
        Returns (is_healthy: bool, detail_message: str).
        """
        # 1. Existence and size check (prevents sqlite3.connect from creating a 0-byte fake DB)
        if not os.path.exists(self.db_path):
            return False, "データベースファイルが見つかりません (File not found)"
        
        try:
            if os.path.getsize(self.db_path) < 1024:
                return False, "データベースファイルが空、またはサイズが小さすぎます (Empty or incomplete file)"
        except Exception as e:
            return False, f"ファイルアクセスエラー (File access error: {e})"

        # 2. SQLite integrity check
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check;")
            res = cur.fetchone()
            if not res or res[0] != "ok":
                return False, f"データベース内部の破損を検知しました (Integrity check failed: {res[0] if res else 'Unknown'})"

            # 3. Essential tables & records check
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cur.fetchall()]
            if "categories" not in tables or "tags" not in tables:
                return False, "必要なテーブル（categories, tags）が見つかりません (Missing required tables)"

            cur.execute("SELECT count(*) FROM tags;")
            tag_count = cur.fetchone()[0]
            if tag_count == 0:
                return False, "タグ辞書データが0件です (No tag records found in database)"

        except Exception as e:
            return False, f"データベース接続・検証エラー (Database error: {e})"
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        return True, "OK"

    def enforce_valid_database_or_exit(self):
        """Checks database health. If invalid, shows a critical dialog and terminates the process immediately."""
        is_healthy, detail = self.verify_database_health()
        if is_healthy:
            return

        import sys
        from PySide6.QtWidgets import QApplication, QMessageBox

        app = QApplication.instance() or QApplication(sys.argv)
        msg = (
            "【⚠️ 辞書データベースの異常 / Database Error】\n\n"
            "タグ辞書データベース（tags.db）が見つからないか、破損しています。\n"
            "The tag dictionary database (tags.db) was not found or is corrupted.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"【詳細 / Detail】\n{detail}\n\n"
            "【対処方法 / Solution】\n"
            "本ツールのフォルダ（EXEと同じ場所）に、正常な 'tags.db' を\n"
            "配置してから、再度起動してください。\n"
            "Please place a valid 'tags.db' file in the application folder.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Path: {os.path.abspath(self.db_path)}"
        )

        box = QMessageBox()
        box.setIcon(QMessageBox.Critical)
        box.setWindowTitle("データベースエラー / Database Error")
        box.setText(msg)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()

        sys.exit(1)

    def get_connection(self) -> sqlite3.Connection:
        # Edge-case Guard 1: Timeout and WAL/busy_timeout for concurrent DB access (e.g. DB Browser)
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.row_factory = sqlite3.Row
        return conn

    def load_all_data(self):
        """Loads and caches all categories, tags, and mapping dictionaries."""
        if not os.path.exists(self.db_path):
            print(f"[DBManager] Warning: Database file not found at {self.db_path}")
            return

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Load Categories
                cursor.execute("SELECT id, category_order, category_name FROM categories ORDER BY category_order ASC")
                cats = cursor.fetchall()
                self._categories_cache = [dict(row) for row in cats]

                # Check if 'note' column exists
                cursor.execute("PRAGMA table_info(tags)")
                cols = [c["name"] for c in cursor.fetchall()]
                has_note = "note" in cols

                if has_note:
                    cursor.execute("SELECT id, category_id, category_name, label_ja, prompt_en, note FROM tags ORDER BY prompt_en COLLATE NOCASE ASC")
                else:
                    cursor.execute("SELECT id, category_id, category_name, label_ja, prompt_en FROM tags ORDER BY prompt_en COLLATE NOCASE ASC")
                
                tags = cursor.fetchall()
                
                self._tags_by_category_cache.clear()
                self._jp_to_en_map.clear()
                self._en_to_jp_map.clear()
                self._tag_to_category_order.clear()

                cat_order_map = {c["id"]: c["category_order"] for c in self._categories_cache}

                for t in tags:
                    tag_dict = dict(t)
                    if "note" not in tag_dict or tag_dict["note"] is None:
                        tag_dict["note"] = ""

                    cid = tag_dict["category_id"]
                    if cid not in self._tags_by_category_cache:
                        self._tags_by_category_cache[cid] = []
                    self._tags_by_category_cache[cid].append(tag_dict)

                    ja = tag_dict.get("label_ja", "").strip()
                    en = tag_dict.get("prompt_en", "").strip()

                    if ja and en:
                        self._jp_to_en_map[ja] = en
                        self._en_to_jp_map[en.lower()] = ja

                    # Record category order for sorting prompt tags
                    order = cat_order_map.get(cid, 999)
                    if order == 0:
                        order = 990 # Category 0 (particles/prepositions) sorted toward the end, not top
                    if en:
                        for token in en.split(","):
                            clean_tok = token.strip().lower()
                            if clean_tok and clean_tok not in self._tag_to_category_order:
                                self._tag_to_category_order[clean_tok] = order
                        self._tag_to_category_order[en.lower()] = order

        except Exception as e:
            print(f"[DBManager] Error loading database: {e}")

    def get_categories(self) -> List[Dict]:
        """Returns all categories sorted by category_order."""
        return self._categories_cache

    def get_tags_by_category(self, category_id: int) -> List[Dict]:
        """Returns all tags for a specific category ID."""
        return self._tags_by_category_cache.get(category_id, [])

    def search_tags(self, keyword: str) -> List[Dict]:
        """Searches tags by Japanese label, English prompt, or explanation Note."""
        kw = keyword.strip().lower()
        if not kw:
            return []

        kw_tokens = kw.replace(",", " ").split()
        results = []
        for cid, tag_list in self._tags_by_category_cache.items():
            for t in tag_list:
                ja = t.get("label_ja", "").lower()
                en = t.get("prompt_en", "").lower()
                note = str(t.get("note") or "").lower()
                # Match if all search query tokens appear in either ja, en, or note
                if all(tok in ja or tok in en or tok in note or 
                       tok.replace(" ", "") in ja.replace(" ", "") or 
                       tok.replace(" ", "") in en.replace(" ", "") or 
                       tok.replace(" ", "") in note.replace(" ", "") for tok in kw_tokens):
                    results.append(t)
        return results

    def get_tag_order(self, tag_en: str) -> int:
        """Returns the category order for an English tag (for prompt sorting)."""
        clean = tag_en.strip().lower()
        return self._tag_to_category_order.get(clean, 999)

    def translate_jp_to_en(self, jp_label: str) -> Optional[str]:
        return self._jp_to_en_map.get(jp_label.strip())

    def translate_en_to_jp(self, en_prompt: str) -> Optional[str]:
        return self._en_to_jp_map.get(en_prompt.strip().lower())

    def is_known_tag(self, text: str) -> bool:
        """Checks if the given English text matches any known tag in the database (case- and whitespace-insensitive)."""
        if not text:
            return False
        import re
        norm = re.sub(r"\s+", " ", text.strip().lower()).replace(", ", ",").replace(",", ", ")
        if norm in self._en_to_jp_map:
            return True
        # Compare without spaces/underscores
        raw_key = text.strip().lower().replace(" ", "").replace("_", "")
        for en_key in self._en_to_jp_map:
            if en_key.replace(" ", "").replace("_", "") == raw_key:
                return True
        return False

    def get_comma_tags(self) -> List[str]:
        """Returns all registered English tags that contain commas, sorted by length descending."""
        if not hasattr(self, "_comma_tags_cache") or not self._comma_tags_cache:
            self._comma_tags_cache = sorted(
                [en for en in self._en_to_jp_map.keys() if "," in en],
                key=len,
                reverse=True
            )
        return self._comma_tags_cache

    def get_sample_prompts(self) -> List[Dict[str, Any]]:
        """
        Retrieves sample prompts from SQLite 'sample_prompts' table (id, title, prompt, comment).
        If table does not exist or is empty, falls back to KENZEN_Sample_Prompts.json.
        """
        samples = []
        # 1. Try SQLite table
        if os.path.exists(self.db_path):
            try:
                with self.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sample_prompts';")
                    if cur.fetchone():
                        cur.execute("PRAGMA table_info(sample_prompts);")
                        cols = [c["name"] for c in cur.fetchall()]
                        has_comment = "comment" in cols
                        has_category = "category" in cols

                        col_query = ["id", "title", "prompt"]
                        if has_comment:
                            col_query.append("comment")
                        if has_category:
                            col_query.append("category")

                        cur.execute(f"SELECT {', '.join(col_query)} FROM sample_prompts ORDER BY id ASC;")
                        for row in cur.fetchall():
                            r_dict = dict(row)
                            if "comment" not in r_dict or r_dict["comment"] is None:
                                r_dict["comment"] = ""
                            if "category" not in r_dict or r_dict["category"] is None:
                                r_dict["category"] = "General"
                            samples.append(r_dict)
            except Exception as e:
                print(f"[DBManager] Note: Could not query sample_prompts table ({e}). Using JSON fallback.")

        if samples:
            return samples

        # 2. Fallback to KENZEN_Sample_Prompts.json
        import json
        from .path_utils import get_resource_path
        json_path = get_resource_path("KENZEN_Sample_Prompts.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8-sig") as f:
                    raw = json.load(f)
                    favs = raw.get("Favorites", [])
                    for idx, fv in enumerate(favs):
                        samples.append({
                            "id": fv.get("id", idx + 1),
                            "title": fv.get("description", f"Sample #{idx+1}"),
                            "prompt": fv.get("prompt", ""),
                            "comment": fv.get("comment", ""),
                            "category": "Sample"
                        })
            except Exception as e:
                print(f"[DBManager] Error reading sample prompts json: {e}")

        return samples
