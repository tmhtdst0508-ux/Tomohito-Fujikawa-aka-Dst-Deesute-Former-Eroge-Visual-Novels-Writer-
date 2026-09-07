"""
Config Manager for KENZEN SeaArt Helper v5.1.1
Handles loading, saving, and updating JSON configuration with v4.2.0 exact default data,
BOM handling, selective export/import with Merge/Overwrite modes, and mobile memo parsing.
"""

import os
import sys
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple, Set


DEFAULT_CONFIG: Dict[str, Any] = {
    "Settings": {
        "AppName": "KENZEN SeaArt Helper v5.1.1",
        "GachaCount": 0,
        "MaxGachaQuota": 15,
        "LastPTDate": "",
        "SurpriseMe": False,
        "SurpriseLevel": "SFW", # SFW, NSFW, Hardcore
        "AutoSortOnDone": False,
        "AutoWrapBracket": False,
        "DefaultWeight": "1.1",
        "DefaultPositivePreset": "",
        "DefaultNegativePreset": "",
        "DefaultLoRAPreset": "",
    },
    "PositivePresets": {
        "REED_XXX_illustrious_SDXL": [
            "masterpiece",
            "best quality",
            "amazing quality",
            "absurdres"
        ]
    },
    "NegativePresets": {
        "REED_XXX_illustrious_SDXL": [
            "lowres", "bad anatomy", "bad hands", "text", "error", "missing fingers",
            "extra digit", "fewer digits", "cropped", "worst quality", "low quality",
            "normal quality", "jpeg artifacts", "signature", "watermark", "username", "blurry"
        ]
    },
    "PositiveStock": [
        "masterpiece",
        "best quality",
        "amazing quality",
        "absurdres"
    ],
    "NegativeStock": [
        "lowres", "bad anatomy", "bad hands", "text", "error", "missing fingers",
        "extra digit", "fewer digits", "cropped", "worst quality", "low quality",
        "normal quality", "jpeg artifacts", "signature", "watermark", "username",
        "blurry", "censor", "ugly", "deformed"
    ],
    "LoRAData": [],
    "LoRAPresets": {},
    "Favorites": [],
    "MobileMemos": []
}


import re

def parse_mobile_memo_item(item: Any) -> Tuple[str, str]:
    """
    Parses mobile memo item into (type, content) tuple.
    Intelligently classifies raw text:
    1. Explicit prefix: [Memo], [URL], [Hash]
    2. URL: starts with http:// or https://
    3. Hash: 8 to 64 hexadecimal characters (e.g. 10-char short hash 'df9cc99fac' or SHA256)
    4. Memo: all other text (descriptions, prompts, notes)
    """
    if isinstance(item, dict):
        m_type = str(item.get("Type") or item.get("type") or "").strip()
        m_content = str(item.get("Content") or item.get("content") or "").strip()
        if not m_type:
            # Auto detect if type is missing in dict
            if m_content.startswith("http://") or m_content.startswith("https://"):
                m_type = "URL"
            elif re.fullmatch(r"^[0-9a-fA-F]{8,64}$", m_content):
                m_type = "Hash"
            else:
                m_type = "Memo"
        return m_type, m_content
    elif item is not None:
        text = str(item).strip()
        m = re.match(r"^\[(Memo|URL|Hash)\]\s*(.*)$", text, re.IGNORECASE)
        if m:
            matched_type = m.group(1).upper()
            std_type = "URL" if matched_type == "URL" else ("Hash" if matched_type == "HASH" else "Memo")
            return std_type, m.group(2).strip()
        if text.startswith("http://") or text.startswith("https://"):
            return "URL", text
        if re.fullmatch(r"^[0-9a-fA-F]{8,64}$", text):
            return "Hash", text
        return "Memo", text
    return "Memo", ""


import ast

def format_lora_preset_preview(val: Any) -> str:
    """
    Parses LoRA preset value (which may be a list of dicts, a Python repr string,
    or a generated tag string) and formats it into standardized LoRA tags:
    <lora:ModelName:Strength> Trigger
    Unifying identifiers to System ModelName if available.
    """
    if not val:
        return ""

    items = None
    if isinstance(val, list):
        items = val
    elif isinstance(val, str):
        val_str = val.strip()
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                items = json.loads(val_str)
            except Exception:
                try:
                    items = ast.literal_eval(val_str)
                except Exception:
                    items = None
        else:
            return val_str

    if not items or not isinstance(items, list):
        return str(val)

    lora_tags = []
    for item in items:
        if not isinstance(item, dict):
            continue
        
        alias = str(item.get("Alias") or item.get("alias") or "").strip()
        model_name = str(item.get("ModelName") or item.get("model_name") or "").strip()
        hash_val = str(item.get("Hash") or item.get("hash") or "").strip()
        target_name = str(item.get("TargetName") or item.get("target_name") or "").strip()
        
        # Priority: System ModelName > TargetName > Hash > Alias
        identifier = model_name or target_name or hash_val or alias
        if not identifier:
            continue

        raw_strength = item.get("Strength") if item.get("Strength") is not None else item.get("weight")
        try:
            strength = float(raw_strength)
        except (ValueError, TypeError):
            strength = 1.0

        lora_tag = f"<lora:{identifier}:{strength:.2f}>"
        
        # Trigger
        trig = str(item.get("Trigger") if item.get("Trigger") is not None else item.get("triggers") or "").strip()
        
        if trig:
            lora_entry = f"{lora_tag} {trig}"
        else:
            lora_entry = lora_tag
        
        lora_tags.append(lora_entry)

    return " ".join(lora_tags)


def format_mobile_memo_item(item: Any) -> str:
    """Formats memo item into string e.g. [Memo] Text, [URL] Link, [Hash] Hash."""
    m_type, m_content = parse_mobile_memo_item(item)
    return f"[{m_type}] {m_content}" if m_content else ""


from .path_utils import get_resource_path


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            self.config_path = get_resource_path("KENZEN_Config.json")
        else:
            self.config_path = config_path
        self.data: Dict[str, Any] = {}
        self.recovery_notice: Optional[Dict[str, str]] = None
        self.load()

    @staticmethod
    def read_json_safely(file_path: str) -> Dict[str, Any]:
        """Reads JSON safely supporting UTF-8 with BOM, standard UTF-8, CP932, Shift_JIS."""
        encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
        last_err = None

        with open(file_path, "rb") as f:
            raw_bytes = f.read()

        for enc in encodings:
            try:
                text = raw_bytes.decode(enc)
                return json.loads(text)
            except Exception as e:
                last_err = e
                continue

        try:
            text = raw_bytes.decode("utf-8-sig", errors="replace")
            return json.loads(text)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON file {file_path}: {last_err or e}")

    def load(self):
        """
        Loads configuration from JSON file.
        If corruption/syntax error is detected:
        1. Rescues the corrupted file to a timestamped backup (_corrupted_YYYYMMDD_HHMMSS.json)
        2. Automatically recovers configuration from .bak backup
        3. Records recovery notice for bilingual user notification dialog.
        """
        bak_path = self.config_path + ".bak"
        corrupted_path = None

        if os.path.exists(self.config_path):
            try:
                # Check 0-byte or corrupted file
                if os.path.getsize(self.config_path) > 0:
                    raw_data = self.read_json_safely(self.config_path)
                    had_legacy_api_key = isinstance(raw_data, dict) and "GeminiAPIKey" in raw_data.get("Settings", {})
                    self.data = self.normalize_imported_data(raw_data)
                    self._validate_and_repair()
                    if had_legacy_api_key:
                        self.save()
                    return
                else:
                    print(f"[ConfigManager] Warning: {self.config_path} is 0 bytes (corrupted).")
            except Exception as e:
                print(f"[ConfigManager] Error reading config file: {e}.")

            # If we reach here, primary config file exists but is corrupted
            import re
            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(self.config_path)
            corrupted_path = f"{base}_corrupted_{now_str}{ext}"
            try:
                with open(self.config_path, "r", encoding="utf-8", errors="replace") as f_src:
                    corrupted_text = f_src.read()
                # Security Masking: Strip out any Gemini API key pattern from rescued corrupted file
                masked_text = re.sub(r'AIza[0-9A-Za-z-_]{35}', 'AIza_MASKED_FOR_SECURITY', corrupted_text)
                with open(corrupted_path, "w", encoding="utf-8") as f_dst:
                    f_dst.write(masked_text)
                print(f"[ConfigManager] Rescued and sanitized corrupted config to: {corrupted_path}")
            except Exception as e:
                print(f"[ConfigManager] Failed to rescue corrupted config: {e}")

        # Try recovery from .bak if primary file failed
        if os.path.exists(bak_path) and os.path.getsize(bak_path) > 0:
            try:
                raw_data = self.read_json_safely(bak_path)
                self.data = self.normalize_imported_data(raw_data)
                self._validate_and_repair()
                print(f"[ConfigManager] Successfully restored configuration from backup {bak_path}")
                self.recovery_notice = {
                    "status": "restored_from_backup",
                    "corrupted_path": corrupted_path or self.config_path,
                    "backup_path": bak_path
                }
                self.save()
                return
            except Exception as e:
                print(f"[ConfigManager] Error reading backup file: {e}.")

        # Fallback to pristine default config
        self.data = json.loads(json.dumps(DEFAULT_CONFIG))
        if corrupted_path:
            self.recovery_notice = {
                "status": "reset_to_default",
                "corrupted_path": corrupted_path
            }
        self.save()

    def normalize_imported_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes both v4 format and v5 format into unified v5 config structure (Issue 4 Safe)."""
        normalized = json.loads(json.dumps(DEFAULT_CONFIG))

        # 1. Settings
        if "Settings" in raw_data and isinstance(raw_data["Settings"], dict):
            for k, v in raw_data["Settings"].items():
                if k == "GeminiAPIKey":
                    if v and str(v).strip():
                        self.set_gemini_api_key(str(v).strip())
                    continue
                normalized["Settings"][str(k)] = v

        # 2. Favorites (v5 'Favorites' or v4 'Fav_List')
        fav_source = raw_data.get("Favorites") or raw_data.get("Fav_List") or []
        if isinstance(fav_source, list):
            fav_list = []
            for idx, item in enumerate(fav_source):
                if isinstance(item, dict):
                    prompt = str(item.get("prompt") if item.get("prompt") is not None else item.get("Prompt") or "")
                    desc = str(item.get("description") if item.get("description") is not None else item.get("Description") or "")
                    fav_list.append({
                        "id": idx + 1,
                        "prompt": prompt.strip(),
                        "description": desc.strip()
                    })
            if fav_list:
                normalized["Favorites"] = fav_list

        # 3. LoRA (v5 'LoRAData' or v4 'LoRA_List')
        lora_source = raw_data.get("LoRAData") or raw_data.get("LoRA_List") or []
        if isinstance(lora_source, list):
            lora_list = []
            for item in lora_source:
                if isinstance(item, dict):
                    alias = str(item.get("alias") if item.get("alias") is not None else item.get("Alias") or "Unknown").strip()
                    model_name = str(item.get("model_name") if item.get("model_name") is not None else item.get("ModelName") or alias).strip()
                    hash_val = str(item.get("hash") if item.get("hash") is not None else item.get("Hash") or "").strip()
                    trigger = str(item.get("triggers") if item.get("triggers") is not None else item.get("Trigger") or "").strip()
                    nega = str(item.get("negative") if item.get("negative") is not None else item.get("Negative") or "").strip()
                    raw_w = item.get("weight") if item.get("weight") is not None else item.get("Strength")
                    try:
                        weight = float(raw_w)
                    except (ValueError, TypeError):
                        weight = 1.0

                    lora_list.append({
                        "alias": alias,
                        "model_name": model_name,
                        "hash": hash_val,
                        "weight": weight,
                        "triggers": trigger,
                        "negative": nega
                    })
            if lora_list:
                normalized["LoRAData"] = lora_list

        # LoRA Presets
        lora_presets = raw_data.get("LoRAPresets") or raw_data.get("LoRA_Presets") or {}
        if isinstance(lora_presets, dict):
            normalized["LoRAPresets"] = {str(k): str(v) for k, v in lora_presets.items()}

        # 4. Positive Presets
        pos_pre_source = raw_data.get("PositivePresets") or raw_data.get("Positive_Presets") or {}
        if isinstance(pos_pre_source, dict):
            pos_presets = {}
            for name, val in pos_pre_source.items():
                if isinstance(val, list):
                    pos_presets[str(name)] = [str(t).strip() for t in val if str(t).strip()]
                elif isinstance(val, str):
                    pos_presets[str(name)] = [t.strip() for t in val.split(",") if t.strip()]
            if pos_presets:
                normalized["PositivePresets"] = pos_presets

        # 5. Negative Presets
        nega_pre_source = raw_data.get("NegativePresets") or raw_data.get("Negative_Presets") or {}
        if isinstance(nega_pre_source, dict):
            nega_presets = {}
            for name, val in nega_pre_source.items():
                if isinstance(val, list):
                    nega_presets[str(name)] = [str(t).strip() for t in val if str(t).strip()]
                elif isinstance(val, str):
                    nega_presets[str(name)] = [t.strip() for t in val.split(",") if t.strip()]
            if nega_presets:
                normalized["NegativePresets"] = nega_presets

        # 6. Positive Stock
        pos_stock_source = raw_data.get("PositiveStock") or raw_data.get("Positive_Default")
        if isinstance(pos_stock_source, list):
            normalized["PositiveStock"] = [str(t).strip() for t in pos_stock_source if str(t).strip()]
        elif isinstance(pos_stock_source, str) and pos_stock_source.strip():
            normalized["PositiveStock"] = [t.strip() for t in pos_stock_source.split(",") if t.strip()]

        # 7. Negative Stock
        nega_stock_source = raw_data.get("NegativeStock") or raw_data.get("Negative_Default")
        if isinstance(nega_stock_source, list):
            normalized["NegativeStock"] = [str(t).strip() for t in nega_stock_source if str(t).strip()]
        elif isinstance(nega_stock_source, str) and nega_stock_source.strip():
            normalized["NegativeStock"] = [t.strip() for t in nega_stock_source.split(",") if t.strip()]

        # 8. Mobile Memos (Issue 11: Format dictionary or string items properly)
        memo_source = raw_data.get("MobileMemos") or raw_data.get("Mobile_Memos") or raw_data.get("Mobile_Memo_Stock") or []
        if isinstance(memo_source, list):
            m_list = []
            for item in memo_source:
                formatted = format_mobile_memo_item(item)
                if formatted:
                    m_list.append(formatted)
            normalized["MobileMemos"] = m_list
        elif isinstance(memo_source, str) and memo_source.strip():
            normalized["MobileMemos"] = [m.strip() for m in memo_source.split("\n\n") if m.strip()]

        return normalized

    def _validate_and_repair(self):
        """Ensures all required top-level keys exist."""
        modified = False
        if "Settings" in self.data and "GeminiAPIKey" in self.data["Settings"]:
            val = str(self.data["Settings"].pop("GeminiAPIKey", "")).strip()
            if val:
                self.set_gemini_api_key(val)
            modified = True

        for key, val in DEFAULT_CONFIG.items():
            if key not in self.data:
                self.data[key] = json.loads(json.dumps(val))
                modified = True
            elif isinstance(val, dict):
                for subkey, subval in val.items():
                    if subkey not in self.data[key]:
                        self.data[key][subkey] = json.loads(json.dumps(subval))
                        modified = True

        if modified:
            self.save()

    def save(self):
        """Saves current configuration to JSON file atomically using a temporary file and keeps a .bak copy."""
        try:
            # 0. Security Guard: Ensure GeminiAPIKey is strictly stored in Windows Registry and completely purged from JSON
            if "Settings" in self.data and "GeminiAPIKey" in self.data["Settings"]:
                api_val = str(self.data["Settings"].pop("GeminiAPIKey", "")).strip()
                if api_val:
                    self.set_gemini_api_key(api_val)

            # 1. Edge-case Guard 2: Make backup of existing valid file before overwrite (must be > 10 bytes)
            if os.path.exists(self.config_path) and os.path.getsize(self.config_path) > 10:
                import shutil
                try:
                    shutil.copy2(self.config_path, self.config_path + ".bak")
                except Exception:
                    pass

            # 2. Atomic write to temporary file first, then replace
            tmp_path = self.config_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            os.replace(tmp_path, self.config_path)
        except Exception as e:
            print(f"[ConfigManager] Error saving config file: {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    # --- Setting Helpers ---
    def get_setting(self, key: str, default: Any = None) -> Any:
        if key == "GeminiAPIKey":
            return self.get_gemini_api_key(default or "")
        return self.data.get("Settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any):
        if key == "GeminiAPIKey":
            self.set_gemini_api_key(str(value))
            return

        if "Settings" not in self.data:
            self.data["Settings"] = {}
        self.data["Settings"][key] = value
        self.save()

    def get_gemini_api_key(self, default: str = "") -> str:
        """
        Retrieves Gemini API Key securely from Windows Registry (QSettings / winreg).
        Never leaves the raw API key inside KENZEN_Config.json file.
        """
        # 1. Try QSettings (HKCU\Software\KENZEN_SeaArt_Helper\Settings)
        try:
            from PySide6.QtCore import QSettings
            settings = QSettings("KENZEN_SeaArt_Helper", "Settings")
            key = settings.value("GeminiAPIKey", "")
            if key and str(key).strip():
                return str(key).strip()
        except Exception:
            pass

        # 2. Try VBA Legacy Registry (HKCU\Software\VB and VBA Program Settings\KENZEN_SeaArt_Helper\Settings\GeminiAPIKey)
        if sys.platform == "win32":
            try:
                import winreg
                reg_path = r"Software\VB and VBA Program Settings\KENZEN_SeaArt_Helper\Settings"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as k:
                    val, _ = winreg.QueryValueEx(k, "GeminiAPIKey")
                    if val and str(val).strip():
                        # Migrate to new registry
                        self.set_gemini_api_key(str(val).strip())
                        return str(val).strip()
            except Exception:
                pass

        # 3. Check JSON if previously saved there, then migrate to registry and purge from JSON
        json_key = self.data.get("Settings", {}).get("GeminiAPIKey", "")
        if json_key and str(json_key).strip():
            migrated_key = str(json_key).strip()
            self.set_gemini_api_key(migrated_key)
            return migrated_key

        return default

    def set_gemini_api_key(self, api_key: str):
        """Saves Gemini API Key strictly to Windows Registry (purging it from JSON file)."""
        clean_key = api_key.strip()
        try:
            from PySide6.QtCore import QSettings
            settings = QSettings("KENZEN_SeaArt_Helper", "Settings")
            settings.setValue("GeminiAPIKey", clean_key)
        except Exception as e:
            print(f"[ConfigManager] Error saving API key to registry: {e}")

        # Ensure JSON never stores raw API key or placeholder
        if "Settings" in self.data and "GeminiAPIKey" in self.data["Settings"]:
            self.data["Settings"].pop("GeminiAPIKey", None)
            self.save()

    def delete_gemini_api_key_registry(self):
        """
        Deletes Gemini API Key completely from Windows Registry (both QSettings and legacy VBA registry),
        and purges it from memory and settings payload.
        """
        # 1. QSettings removal (HKCU\Software\KENZEN_SeaArt_Helper\Settings\GeminiAPIKey)
        try:
            from PySide6.QtCore import QSettings
            settings = QSettings("KENZEN_SeaArt_Helper", "Settings")
            settings.remove("GeminiAPIKey")
            settings.sync()
        except Exception as e:
            print(f"[ConfigManager] Error removing API key from QSettings: {e}")

        # 2. Legacy VBA registry removal (HKCU\Software\VB and VBA Program Settings\KENZEN_SeaArt_Helper\Settings)
        if sys.platform == "win32":
            try:
                import winreg
                reg_path = r"Software\VB and VBA Program Settings\KENZEN_SeaArt_Helper\Settings"
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as k:
                        winreg.DeleteValue(k, "GeminiAPIKey")
                except FileNotFoundError:
                    pass
            except Exception as e:
                print(f"[ConfigManager] Error removing legacy API key from winreg: {e}")

        # 3. Purge from in-memory config payload
        if "Settings" in self.data and "GeminiAPIKey" in self.data["Settings"]:
            self.data["Settings"].pop("GeminiAPIKey", None)
            self.save()

    def get_gacha_quota(self) -> int:
        try:
            return int(self.get_setting("MaxGachaQuota", 15))
        except (ValueError, TypeError):
            return 15

    def set_gacha_quota(self, quota: int):
        self.set_setting("MaxGachaQuota", max(1, quota))

    def get_gacha_status_counts(self) -> Tuple[str, int, int]:
        """
        Returns (pt_date_str, remaining_runs, max_quota).
        Automatically resets used count if PT date changed.
        """
        import datetime
        utc_now = datetime.timezone.utc
        pt_now = datetime.datetime.now(utc_now) - datetime.timedelta(hours=8)
        pt_date = pt_now.strftime("%Y-%m-%d")

        last_date = self.get_setting("LastPTDate", "")
        used_count = self.get_setting("GachaCount", 0)

        if pt_date != last_date:
            used_count = 0
            self.set_setting("LastPTDate", pt_date)
            self.set_setting("GachaCount", 0)

        max_quota = self.get_gacha_quota()
        remaining = max(0, max_quota - used_count)
        return pt_date, remaining, max_quota

    # --- Favorites ---
    def get_favorites(self) -> List[Dict[str, Any]]:
        return self.data.get("Favorites", [])

    def set_favorites(self, favs: List[Dict[str, Any]]):
        self.data["Favorites"] = favs
        self.save()

    def add_favorite(self, prompt: str, description: str = "") -> Tuple[bool, int]:
        """
        Adds favorite with duplicate detection.
        Returns (success: bool, id_or_existing_id: int).
        """
        favs = self.get_favorites()
        p_clean = prompt.strip()
        
        # Check duplicate
        for idx, f in enumerate(favs):
            if f.get("prompt", "").strip() == p_clean:
                return False, f.get("id", idx + 1)

        new_id = (max([f.get("id", 0) for f in favs]) + 1) if favs else 1
        favs.append({"id": new_id, "prompt": p_clean, "description": description.strip()})
        self.set_favorites(favs)
        return True, new_id

    def is_master_config_file(self, file_path: str) -> bool:
        """Checks if the given file path is the active master config file or backup."""
        if not file_path:
            return False
        fname_lower = os.path.basename(file_path).lower()
        if fname_lower in ["kenzen_config.json", "kenzen_config.json.bak"]:
            return True
        try:
            abs_path = os.path.abspath(file_path).lower()
            if abs_path == os.path.abspath(self.config_path).lower():
                return True
            if abs_path == os.path.abspath(self.config_path + ".bak").lower():
                return True
        except Exception:
            pass
        return False

    # --- Mobile Memo Import (Issue 7-1 & 11) ---
    def import_mobile_memos_only(self, file_path: str) -> int:
        """
        Imports only Mobile_Memos from KENZEN_Mobile_Fav.json or KENZEN_Mobile.json.
        Correctly formats [Memo], [URL], [Hash] (Issue 11).
        Rejects importing active master config file (KENZEN_Config.json).
        """
        if self.is_master_config_file(file_path):
            raise ValueError("「KENZEN_Config.json」は母艦設定ファイルのため、インポート対象外です。")

        raw = self.read_json_safely(file_path)
        memos = raw.get("Mobile_Memos", []) or raw.get("MobileMemos", []) or raw.get("Mobile_Memo_Stock", [])

        current_memos = self.get_mobile_memos()
        added_count = 0
        for m in memos:
            formatted = format_mobile_memo_item(m)
            if formatted and formatted not in current_memos:
                current_memos.append(formatted)
                added_count += 1

        self.set_mobile_memos(current_memos)
        return added_count

    def export_mobile_fav_json(self, file_path: str):
        favs = self.get_favorites()
        memos = self.get_mobile_memos()
        mobile_data = {
            "Fav_List": [{"Prompt": f.get("prompt", ""), "Description": f.get("description", "")} for f in favs],
            "Mobile_Memos": memos
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(mobile_data, f, indent=2, ensure_ascii=False)

    # --- LoRA & LoRA Presets ---
    def get_lora_list(self) -> List[Dict[str, Any]]:
        return self.data.get("LoRAData", [])

    def save_lora_list(self, loras: List[Dict[str, Any]]):
        self.data["LoRAData"] = loras
        self.save()

    def get_lora_presets(self) -> Dict[str, Any]:
        return self.data.get("LoRAPresets", {})

    def save_lora_presets(self, presets: Dict[str, Any]):
        self.data["LoRAPresets"] = presets
        self.save()

    def get_all_lora_triggers(self) -> Set[str]:
        """Returns normalized set of all registered LoRA trigger words for PromptSort."""
        triggers = set()
        for lora in self.get_lora_list():
            trig_str = lora.get("triggers", "")
            if trig_str:
                for t in trig_str.split(","):
                    t_clean = t.strip().lower()
                    if t_clean:
                        triggers.add(t_clean)
        return triggers

    # --- Presets & Stock ---
    def get_positive_presets(self) -> Dict[str, List[str]]:
        return self.data.get("PositivePresets", {})

    def get_negative_presets(self) -> Dict[str, List[str]]:
        return self.data.get("NegativePresets", {})

    def get_positive_stock(self) -> List[str]:
        return self.data.get("PositiveStock", [])

    def set_positive_stock(self, stock: List[str]):
        self.data["PositiveStock"] = stock
        self.save()

    def get_negative_stock(self) -> List[str]:
        return self.data.get("NegativeStock", [])

    def set_negative_stock(self, stock: List[str]):
        self.data["NegativeStock"] = stock
        self.save()

    # --- Mobile Memos ---
    def get_mobile_memos(self) -> List[str]:
        return self.data.get("MobileMemos", [])

    def set_mobile_memos(self, memos: List[str]):
        self.data["MobileMemos"] = memos
        self.save()
