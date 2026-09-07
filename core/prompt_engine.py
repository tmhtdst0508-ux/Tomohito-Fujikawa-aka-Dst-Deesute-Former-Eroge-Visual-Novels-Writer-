"""
Prompt Engine for KENZEN SeaArt Helper v5.0.0
Handles prompt cleaning (standardizing comma spacing, clean BREAK lines),
category hierarchy sorting with Base Positive (score 0.0), LoRA triggers (score 0.5),
Dynamic Prompts wrapping ({A | B | C}), weight formatting, and undo history.
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Set, Tuple
from .db_manager import DBManager


# Standard Base Positive Quality Tags (Score 0.0)
BASE_POSITIVE_TAGS = {
    "masterpiece", "best quality", "amazing quality", "absurdres",
    "high quality", "ultra-detailed", "8k", "best_quality", "amazing_quality"
}


def sanitize_sd_prompt(raw_text: str) -> str:
    """
    Strictly sanitizes Stable Diffusion prompt text:
    1. Normalizes full-width alphanumeric and punctuation characters to standard ASCII.
    2. Completely removes dangerous / buggy characters:
       ?, !, @, /, \\, ", ', `, ^, ~, *, +, &, %, $, #, ;, control characters, zero-width chars.
    3. Preserves legitimate SD syntax:
       (), [], {}, <>, :, _, -, ,, ., |, \\n, spaces, and BREAK.
    4. Strips empty brackets: (), [], {}, <>, (:)
    5. Normalizes consecutive commas and whitespace.
    """
    if not raw_text:
        return ""

    text = str(raw_text)

    # 1. Normalize full-width characters (NFKC handles full-width A-Z, 0-9, etc.)
    text = unicodedata.normalize("NFKC", text)

    # 2. Specific punctuation normalization
    text = text.replace("\u3000", " ") # Full-width space
    text = text.replace("\uff0c", ",") # Full-width comma
    text = text.replace("，", ",")
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("［", "[").replace("］", "]")
    text = text.replace("｛", "{").replace("｝", "}")
    text = text.replace("＜", "<").replace("＞", ">")
    text = text.replace("：", ":")
    text = text.replace("｜", "|")
    text = text.replace("—", "-").replace("―", "-").replace("ー", "-")

    # 3. Strip invisible and control characters
    text = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # 4. Remove all dangerous / buggy characters (both half-width and remaining full-width)
    # Target: ?, !, @, /, \, ", ', `, ^, ~, *, +, &, %, $, #, ;, ￥
    dangerous_chars = r'[?!@/\\"\'`^~*+&%$#;￥？！＠／＼”’｀＾～＊＋＆％＄＃；]'
    text = re.sub(dangerous_chars, "", text)

    # 5. Clean up corrupted or empty brackets
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\[\s*\]", "", text)
    text = re.sub(r"\{\s*\}", "", text)
    text = re.sub(r"<\s*>", "", text)
    text = re.sub(r"\(\s*:\s*[0-9.]*\s*\)", "", text)

    # 6. Normalize commas and spaces per line
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        if not l:
            continue
        # Consecutive commas
        l = re.sub(r",[\s,]*", ", ", l)
        l = re.sub(r"\s+,\s*", ", ", l)
        l = re.sub(r"^\s*,\s*", "", l)
        l = re.sub(r"\s*,\s*$", "", l)
        l = re.sub(r"[ \t]+", " ", l).strip()
        if l:
            cleaned_lines.append(l)

    return "\n".join(cleaned_lines)


def sanitize_api_key(raw_key: str) -> str:
    """Strictly cleans Google Gemini API Key, stripping spaces, quotes, newlines, and illegal characters."""
    if not raw_key:
        return ""
    # Gemini API keys consist of letters, digits, underscores, and hyphens (AIzaSy...)
    cleaned = re.sub(r"[^A-Za-z0-9_\-]", "", str(raw_key).strip())
    return cleaned


# Particles, Prepositions, and Common Modifiers that should NOT override Noun Head categories in subphrase matching
PREP_WORDS = {
    "with", "and", "on", "over", "to", "behind", "only", "from",
    "inside", "in", "at", "by", "for", "of", "about", "into", "through",
    "above", "below", "between", "under", "not"
}

PREP_AND_MODIFIERS = {
    "with", "and", "on", "over", "to", "behind", "only", "from",
    "inside", "in", "at", "by", "for", "of", "about", "into", "through",
    "above", "below", "between", "under", "not",
    "japanese", "traditional", "modern", "vintage", "retro", "western", "eastern",
    "chinese", "korean", "asian", "american", "european",
    "wooden", "stone", "metal", "metallic", "leather", "plastic", "glass", "paper",
    "big", "small", "huge", "tiny", "large", "mini", "giant",
    "dark", "light", "bright", "dim", "neon", "glow", "glowing",
    "pink", "red", "blue", "green", "black", "white", "yellow", "purple", "orange", "brown", "gray", "grey"
}


def split_top_level_tags(text: str) -> List[str]:
    """
    Splits prompt text by commas at the top-level ONLY.
    Commas inside parentheses (), curly braces {}, brackets [], or angle brackets <>
    are preserved intact without splitting.
    """
    if not text:
        return []

    chunks = []
    current = []
    paren_depth = 0
    brace_depth = 0
    bracket_depth = 0
    angle_depth = 0

    for ch in text:
        if ch == '(':
            paren_depth += 1
            current.append(ch)
        elif ch == ')':
            paren_depth = max(0, paren_depth - 1)
            current.append(ch)
        elif ch == '{':
            brace_depth += 1
            current.append(ch)
        elif ch == '}':
            brace_depth = max(0, brace_depth - 1)
            current.append(ch)
        elif ch == '[':
            bracket_depth += 1
            current.append(ch)
        elif ch == ']':
            bracket_depth = max(0, bracket_depth - 1)
            current.append(ch)
        elif ch == '<':
            angle_depth += 1
            current.append(ch)
        elif ch == '>':
            angle_depth = max(0, angle_depth - 1)
            current.append(ch)
        elif ch == ',' and paren_depth == 0 and brace_depth == 0 and bracket_depth == 0 and angle_depth == 0:
            token = "".join(current).strip()
            if token:
                chunks.append(token)
            current = []
        else:
            current.append(ch)

    if current:
        token = "".join(current).strip()
        if token:
            chunks.append(token)

    return chunks


class PromptEngine:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.history_stack: List[str] = []
        self.max_history = 50

    def push_history(self, text: str):
        if not self.history_stack or self.history_stack[-1] != text:
            self.history_stack.append(text)
            if len(self.history_stack) > self.max_history:
                self.history_stack.pop(0)

    def undo(self) -> Optional[str]:
        """Pops and returns the previous prompt state (single-step undo)."""
        if self.history_stack:
            return self.history_stack.pop()
        return None

    def clear_history(self):
        """Clears undo history stack completely."""
        self.history_stack.clear()

    def clean_prompt(self, raw_text: str) -> str:
        """
        Standardizes separators and formats BREAK syntax cleanly without commas:
        masterpiece, 1girl
        BREAK
        dialogue
        Strictly sanitizes invalid/buggy characters (?, !, @, /, \\, quotes, etc.).
        """
        if not raw_text:
            return ""

        # Strictly sanitize all dangerous characters and normalize
        sanitized = sanitize_sd_prompt(raw_text)
        
        # Normalize BREAK: remove any surrounding commas and ensure it is on its own line
        text = re.sub(r"\s*,\s*\bBREAK\b", "\nBREAK", sanitized, flags=re.IGNORECASE)
        text = re.sub(r"\bBREAK\b\s*,\s*", "BREAK\n", text, flags=re.IGNORECASE)

        # Process each line
        lines = text.splitlines()
        cleaned_lines = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            if line_str.upper() == "BREAK":
                cleaned_lines.append("BREAK")
                continue

            # Replace multiple consecutive commas with a single comma
            line_str = re.sub(r",[\s,]*", ", ", line_str)
            # Remove space before commas
            line_str = re.sub(r"\s+,\s*", ", ", line_str)
            # Clean up leading/trailing commas and spaces
            line_str = re.sub(r"^\s*,\s*", "", line_str)
            line_str = re.sub(r"\s*,\s*$", "", line_str)
            line_str = re.sub(r"[ \t]+", " ", line_str).strip()

            if line_str:
                cleaned_lines.append(line_str)

        return "\n".join(cleaned_lines)

        return "\n".join(cleaned_lines)

    def append_tag(self, current_text: str, new_tag: str, is_comma: bool = True) -> str:
        """
        Appends tag with comma (Left-Click) or space (Right-Click).
        Special handling:
        - If new_tag is BREAK: placed on a new line without commas.
        - If current_text ends with BREAK: next tag starts on a new line without leading comma.
        - If new_tag starts with <lora:: append with space.
        """
        new_tag_clean = new_tag.strip()
        if not new_tag_clean:
            return current_text

        current = current_text.strip()
        if not current:
            if new_tag_clean.upper() == "BREAK":
                return "BREAK\n"
            return new_tag_clean

        # Adding BREAK
        if new_tag_clean.upper() == "BREAK":
            clean_curr = current.rstrip().rstrip(",")
            return f"{clean_curr}\nBREAK\n"

        # Previous line was BREAK
        if current.endswith("BREAK") or current.endswith("BREAK\n"):
            clean_curr = current.rstrip()
            return f"{clean_curr}\n{new_tag_clean}"

        # LoRA tag
        if new_tag_clean.startswith("<lora:"):
            return f"{current} {new_tag_clean}"

        if is_comma:
            return f"{current}, {new_tag_clean}"
        else:
            return f"{current} {new_tag_clean}"

    def format_weight(self, tag: str, weight: float) -> str:
        """Formats tag with weight, e.g. (tag:1.2). If weight==1.0, strips weight."""
        tag = tag.strip()
        # Strip existing outer weight brackets repeatedly
        while True:
            m = re.match(r"^\((.+?):[0-9.]+\)$", tag)
            if m:
                tag = m.group(1).strip()
            else:
                break
        
        if weight == 1.0 or not tag:
            return tag
        return f"({tag}:{weight:.1f})"

    def wrap_dynamic_prompts(self, selected_text: str) -> str:
        """
        Converts tags into '{A | B}', or unwraps back to comma-separated tags.
        Protects comma-containing tags (e.g. 'ass up, face down') from being mistakenly split into 'ass up | face down'.
        """
        text = selected_text.strip()
        if not text:
            return selected_text

        # 1. Unwrapping if already wrapped with { ... }
        if text.startswith("{") and text.endswith("}"):
            inner = text[1:-1].strip()
            if "|" in inner:
                parts = [p.strip() for p in inner.split("|") if p.strip()]
                return ", ".join(parts)
            else:
                return inner

        # 2. Check if selected text is a single known tag (with or without weight brackets)
        tag_core = text
        m_weight = re.match(r"^\((.+?):[0-9.]+\)$", tag_core)
        if m_weight:
            tag_core = m_weight.group(1).strip()

        if hasattr(self.db, "is_known_tag") and self.db.is_known_tag(tag_core):
            return "{" + text + "}"

        # 3. If text already contains '|', wrap choices as is
        if "|" in text:
            parts = [p.strip() for p in text.split("|") if p.strip()]
            return "{" + " | ".join(parts) + "}"

        # 4. Multi-tag separation with protection for comma-containing DB tags
        if "," in text:
            comma_tags = self.db.get_comma_tags() if hasattr(self.db, "get_comma_tags") else []
            sentinel = "___KENZEN_COMMA___"
            protected_text = text
            for ct in comma_tags:
                ct_pattern = re.escape(ct).replace(r"\,", r"\s*,\s*")
                def replace_comma(m):
                    return re.sub(r"\s*,\s*", sentinel, m.group(0))
                protected_text = re.sub(ct_pattern, replace_comma, protected_text, flags=re.IGNORECASE)

            raw_parts = [p.strip() for p in protected_text.split(",") if p.strip()]
            restored_parts = [p.replace(sentinel, ", ").strip() for p in raw_parts if p.strip()]

            if len(restored_parts) > 1:
                return "{" + " | ".join(restored_parts) + "}"
            elif len(restored_parts) == 1:
                return "{" + restored_parts[0] + "}"

        # 5. Default fallback: wrap single item
        return "{" + text + "}"

    def sort_prompt(self, prompt: str, registered_lora_triggers: Optional[Set[str]] = None) -> str:
        """
        Sorts tags strictly following the KENZEN hierarchy:
        - If 'BREAK' exists:
          1. Extracts any LoRA tags <lora:...> and registered LoRA trigger words from anywhere in the prompt (including after BREAK).
          2. Moves all LoRA triggers into the 1st block immediately after Base Positive quality tags (Score 0.5).
          3. Sorts the 1st block tags.
          4. Places <lora:...> tags at the very end of the prompt.
          5. Cleans and preserves subsequent BREAK segments.
        - If no 'BREAK': sorts the single block.
        """
        if not prompt.strip():
            return ""

        if registered_lora_triggers is None:
            registered_lora_triggers = set()
        else:
            registered_lora_triggers = {t.lower().strip() for t in registered_lora_triggers if t.strip()}

        # Check for BREAK syntax
        break_match = re.search(r"\bBREAK\b", prompt)
        if break_match:
            break_start = break_match.start()
            before_break = prompt[:break_start].rstrip().rstrip(",")
            after_break = prompt[break_start:] # Contains BREAK and following lines

            # 1. Extract all <lora:...> tags from after_break
            after_loras = re.findall(r"<lora:[^>]+>", after_break, re.IGNORECASE)
            after_no_lora = re.sub(r"<lora:[^>]+>", "", after_break, flags=re.IGNORECASE)

            # 2. Extract registered LoRA triggers from after_break
            pulled_triggers = []
            if registered_lora_triggers:
                after_lines = after_no_lora.splitlines()
                cleaned_after_lines = []
                for aline in after_lines:
                    if not aline.strip():
                        continue
                    if re.match(r"^\s*BREAK\s*$", aline, re.IGNORECASE):
                        cleaned_after_lines.append("BREAK")
                        continue

                    # Smart tag chunk extraction handles space-separated triggers like 'pink kimono sound effects'
                    chunks = self._extract_tag_chunks(aline, registered_lora_triggers)
                    kept_chunks = []
                    for c in chunks:
                        clean_c = c
                        m = re.match(r"^\((.+?):[0-9.]+\)$", clean_c)
                        if m:
                            clean_c = m.group(1).strip()
                        clean_c_lower = clean_c.lower()
                        clean_c_norm = clean_c_lower.replace("_", " ").replace("-", " ")

                        if clean_c_lower in registered_lora_triggers or clean_c_norm in registered_lora_triggers:
                            pulled_triggers.append(c) # Move this trigger to 1st block
                        else:
                            kept_chunks.append(c)

                    if kept_chunks:
                        cleaned_after_lines.append(", ".join(kept_chunks))
                
                after_cleaned_text = "\n".join(cleaned_after_lines)
            else:
                after_cleaned_text = after_no_lora

            # 3. Append pulled triggers to before_break
            if pulled_triggers:
                triggers_str = ", ".join(pulled_triggers)
                if before_break:
                    before_break = f"{before_break}, {triggers_str}"
                else:
                    before_break = triggers_str

            # 4. Sort 1st block (triggers will automatically receive score 0.5 right after quality tags)
            sorted_before = self._sort_single_block(before_break, registered_lora_triggers)

            # 5. Extract <lora:...> from sorted_before as well
            before_loras = re.findall(r"<lora:[^>]+>", sorted_before, re.IGNORECASE)
            sorted_before_no_lora = re.sub(r"<lora:[^>]+>", "", sorted_before, flags=re.IGNORECASE).strip()
            sorted_before_no_lora = re.sub(r",\s*$", "", sorted_before_no_lora).strip()

            all_loras = before_loras + after_loras
            # Unique LoRA tags preserving order
            seen_loras = set()
            unique_loras = []
            for l in all_loras:
                l_clean = l.strip()
                if l_clean and l_clean.lower() not in seen_loras:
                    seen_loras.add(l_clean.lower())
                    unique_loras.append(l_clean)

            # 6. Clean up after_break lines
            after_cleaned = self.clean_prompt(after_cleaned_text)

            # 7. Reconstruct final prompt
            parts = []
            if sorted_before_no_lora:
                parts.append(sorted_before_no_lora)
            if after_cleaned:
                parts.append(after_cleaned)

            combined_body = "\n".join(parts)

            # Append all <lora:...> tags at the very end with space
            if unique_loras:
                lora_tail = " ".join(unique_loras)
                if combined_body:
                    return f"{combined_body} {lora_tail}"
                else:
                    return lora_tail
            else:
                return combined_body

        return self._sort_single_block(prompt, registered_lora_triggers)

    def sort_prompt_segment(self, segment_text: str, registered_lora_triggers: Optional[Set[str]] = None) -> str:
        """Sorts a highlighted selection segment independently without altering surrounding prompt structure."""
        if not segment_text.strip():
            return segment_text
        if registered_lora_triggers is None:
            registered_lora_triggers = set()
        else:
            registered_lora_triggers = {t.lower().strip() for t in registered_lora_triggers if t.strip()}
        return self._sort_single_block(segment_text, registered_lora_triggers)

    def _sort_single_block(self, block_text: str, registered_lora_triggers: Set[str]) -> str:
        lines = block_text.splitlines()
        sorted_lines = []

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # 1. Extract <lora:...> blocks
            lora_blocks = re.findall(r"<lora:[^>]+>", line_str, re.IGNORECASE)
            text_part = re.sub(r"<lora:[^>]+>", "", line_str, flags=re.IGNORECASE).strip()

            # 2. Smart tag chunk extraction (splits adjacent un-commaed tags e.g. 'solo (sound effects:1.3) handfixer')
            raw_chunks = self._extract_tag_chunks(text_part, registered_lora_triggers)
            scored_items = []

            for idx, raw_chunk in enumerate(raw_chunks):
                clean_tag = raw_chunk
                m = re.match(r"^\((.+?):[0-9.]+\)$", clean_tag)
                if m:
                    clean_tag = m.group(1).strip()

                # Dynamic Prompts {A | B | C} support
                dp_best_order = None
                if clean_tag.startswith("{") and clean_tag.endswith("}"):
                    inner_dp = clean_tag[1:-1].strip()
                    dp_options = [p.strip() for p in re.split(r"[|,]", inner_dp) if p.strip()]
                    for opt in dp_options:
                        opt_clean = re.sub(r"^\((.+?):[0-9.]+\)$", r"\1", opt).strip()
                        opt_ord = self.db.get_tag_order(opt_clean)
                        if opt_ord >= 900:
                            sub_opt = self._match_subphrase_order(opt_clean)
                            if sub_opt is not None and sub_opt < 900:
                                opt_ord = sub_opt
                        if opt_ord < 900:
                            if dp_best_order is None or opt_ord < dp_best_order:
                                dp_best_order = opt_ord

                clean_lower = clean_tag.lower()
                clean_norm = clean_lower.replace("_", " ").replace("-", " ")

                # 2-1. Base Positive (Score 0.0)
                if clean_lower in BASE_POSITIVE_TAGS or clean_norm in BASE_POSITIVE_TAGS:
                    score = 0.0
                # 2-2. LoRA Trigger (Score 0.5)
                elif clean_lower in registered_lora_triggers or clean_norm in registered_lora_triggers:
                    score = 0.5
                elif clean_lower in PREP_WORDS or clean_norm in PREP_WORDS:
                    # Standalone particles/prepositions do not precede art style tags
                    score = 990.0
                elif dp_best_order is not None:
                    score = float(dp_best_order * 10 + 10)
                else:
                    order = self.db.get_tag_order(clean_tag)
                    if order < 900:
                        score = float(order * 10 + 10)
                    else:
                        sub_order = self._match_subphrase_order(clean_tag)
                        if sub_order is not None and sub_order < 900:
                            score = float(sub_order * 10 + 11.0)
                        elif order == 990:
                            score = 990.0
                        else:
                            score = 999.0

                scored_items.append((score, idx, raw_chunk))

            # 3. Stable sort by score, preserving original order on tie
            scored_items.sort(key=lambda x: (x[0], x[1]))

            # 4. Rebuild line
            sorted_tags = [item[2] for item in scored_items]
            res_line = ", ".join(sorted_tags)

            # Append LoRA blocks at the end with a single space
            if lora_blocks:
                lora_str = " ".join(lora_blocks)
                if res_line:
                    res_line = f"{res_line} {lora_str}"
                else:
                    res_line = lora_str

            sorted_lines.append(res_line)

        return "\n".join(sorted_lines)

    def _extract_tag_chunks(self, text_part: str, registered_lora_triggers: Set[str]) -> List[str]:
        """
        Extracts tag chunks from text_part.
        Preserves nested parentheses, brackets, and dynamic prompts intact while
        extracting space-separated standalone LoRA triggers.
        """
        if not text_part.strip():
            return []

        norm = text_part.strip()

        # Insert commas between adjacent parentheses: ') (' -> '), ('
        norm = re.sub(r"(\))\s*(\()", r"\1, \2", norm)
        # Insert commas between word and parenthesis: 'solo (' -> 'solo, ('
        norm = re.sub(r"([a-zA-Z0-9_-])\s*(\()", r"\1, \2", norm)
        # Insert commas between parenthesis and word: ')' 'word' -> '), word'
        norm = re.sub(r"(\))\s*([a-zA-Z0-9_-])", r"\1, \2", norm)

        # Check for registered LoRA triggers
        for trig in sorted(registered_lora_triggers, key=len, reverse=True):
            if not trig:
                continue
            # Match trigger as standalone word with space
            pattern = rf"(?<!,)\s+\b({re.escape(trig)})\b"
            norm = re.sub(pattern, r", \1", norm, flags=re.IGNORECASE)
            pattern2 = rf"\b({re.escape(trig)})\b\s+(?!,)"
            norm = re.sub(pattern2, r"\1, ", norm, flags=re.IGNORECASE)

        chunks = split_top_level_tags(norm)
        return chunks

    def _match_subphrase_order(self, text: str) -> Optional[int]:
        """
        Matches compound / multi-word tags against the database by finding the most specific subphrase.
        Prioritizes:
        1. Longest subphrase matches (e.g. 'living room' [2 words] > 'japanese' [1 word]).
        2. Rightmost matches for equal lengths (English Noun Head priority, e.g. 'japanese room' -> 'room').
        3. Excludes standalone particles, prepositions, and modifiers from dominating the head noun.
        """
        clean_text = text.replace(",", " ")
        tokens = clean_text.replace("_", " ").replace("-", " ").split()
        if len(tokens) <= 1:
            return None

        best_match = None # (length, end_index, order)

        for i in range(len(tokens)):
            for j in range(i + 1, min(len(tokens) + 1, i + 6)): # phrases up to 5 words
                sub = " ".join(tokens[i:j])
                sub_lower = sub.lower()
                
                # If standalone 1-word modifier/prep, ignore in primary pass
                if (j - i == 1) and (sub_lower in PREP_AND_MODIFIERS):
                    continue

                order = self.db.get_tag_order(sub)
                if order is not None and order < 900 and order > 0:
                    match_len = j - i
                    match_end = j
                    if best_match is None:
                        best_match = (match_len, match_end, order)
                    else:
                        curr_len, curr_end, curr_order = best_match
                        if match_len > curr_len:
                            best_match = (match_len, match_end, order)
                        elif match_len == curr_len and match_end >= curr_end:
                            best_match = (match_len, match_end, order)

        # Fallback: if no non-modifier matched, check any token
        if best_match is None:
            for i in range(len(tokens)):
                for j in range(i + 1, min(len(tokens) + 1, i + 6)):
                    sub = " ".join(tokens[i:j])
                    order = self.db.get_tag_order(sub)
                    if order is not None and order < 900 and order > 0:
                        return order
            return None

        return best_match[2]
