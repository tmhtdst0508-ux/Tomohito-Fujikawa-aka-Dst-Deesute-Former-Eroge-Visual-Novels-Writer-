"""
IO / Settings Tab for KENZEN SeaArt Helper v5.0.0
Faithfully recreates VBA v4.2.0 Export (Backup) and Import (Restore) layout
with 7 items, Merge vs Overwrite modes, 50-item Favorites salvage, and clean About box.
"""

import os
import json
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QGroupBox, QMessageBox, QFileDialog, QRadioButton, QButtonGroup, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices
from ..core.config_manager import ConfigManager
from .style import COLOR_ACTION, COLOR_SUCCESS, COLOR_DANGER


class TabIO(QWidget):
    config_reloaded = Signal()
    config_reset_all_ui = Signal() # Issue 13

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # 1. Dual Columns: Export (Left) and Import (Right)
        h_main_io = QHBoxLayout()
        h_main_io.setSpacing(12)

        # --- LEFT: Export (Backup) ---
        grp_export = QGroupBox("Export (Backup)")
        exp_layout = QVBoxLayout(grp_export)
        exp_layout.setContentsMargins(10, 14, 10, 10)
        exp_layout.setSpacing(8)

        exp_grid = QGridLayout()
        exp_grid.setSpacing(8)

        self.exp_chk_pos_pre = QCheckBox("Positive Presets")
        self.exp_chk_pos_pre.setChecked(True)
        self.exp_chk_nega_stock = QCheckBox("Negative Stock")
        self.exp_chk_nega_stock.setChecked(True)

        self.exp_chk_nega_pre = QCheckBox("Negative Presets")
        self.exp_chk_nega_pre.setChecked(True)
        self.exp_chk_lora_base = QCheckBox("LoRA Base Data")
        self.exp_chk_lora_base.setChecked(True)

        self.exp_chk_lora_pre = QCheckBox("LoRA Presets")
        self.exp_chk_lora_pre.setChecked(True)
        self.exp_chk_fav = QCheckBox("Favorites")
        self.exp_chk_fav.setChecked(True)

        self.exp_chk_memo = QCheckBox("Mobile Memo")
        self.exp_chk_memo.setChecked(True)

        exp_grid.addWidget(self.exp_chk_pos_pre, 0, 0)
        exp_grid.addWidget(self.exp_chk_nega_stock, 0, 1)
        exp_grid.addWidget(self.exp_chk_nega_pre, 1, 0)
        exp_grid.addWidget(self.exp_chk_lora_base, 1, 1)
        exp_grid.addWidget(self.exp_chk_lora_pre, 2, 0)
        exp_grid.addWidget(self.exp_chk_fav, 2, 1)
        exp_grid.addWidget(self.exp_chk_memo, 3, 0)
        exp_layout.addLayout(exp_grid)

        exp_layout.addStretch()

        exp_btn_bar = QHBoxLayout()
        btn_exp_check_all = QPushButton("Check ALL")
        btn_exp_check_all.setProperty("btnType", "action")
        btn_exp_check_all.clicked.connect(self.on_export_check_all)

        btn_export = QPushButton("Export As JSON")
        btn_export.setProperty("btnType", "action")
        btn_export.setFixedHeight(36)
        btn_export.clicked.connect(self.on_export_config)

        exp_btn_bar.addWidget(btn_exp_check_all)
        exp_btn_bar.addWidget(btn_export)
        exp_layout.addLayout(exp_btn_bar)

        h_main_io.addWidget(grp_export, 1)

        # --- RIGHT: Import (Restore) ---
        grp_import = QGroupBox("Import (Restore)")
        imp_layout = QVBoxLayout(grp_import)
        imp_layout.setContentsMargins(10, 14, 10, 10)
        imp_layout.setSpacing(8)

        imp_grid = QGridLayout()
        imp_grid.setSpacing(8)

        self.imp_chk_pos_pre = QCheckBox("Positive Presets")
        self.imp_chk_pos_pre.setChecked(True)
        self.imp_chk_nega_stock = QCheckBox("Negative Stock")
        self.imp_chk_nega_stock.setChecked(True)

        self.imp_chk_nega_pre = QCheckBox("Negative Presets")
        self.imp_chk_nega_pre.setChecked(True)
        self.imp_chk_lora_base = QCheckBox("LoRA Base Data")
        self.imp_chk_lora_base.setChecked(True)

        self.imp_chk_lora_pre = QCheckBox("LoRA Presets")
        self.imp_chk_lora_pre.setChecked(True)
        self.imp_chk_fav = QCheckBox("Favorites")
        self.imp_chk_fav.setChecked(True)

        self.imp_chk_memo = QCheckBox("Mobile Memo")
        self.imp_chk_memo.setChecked(True)

        imp_grid.addWidget(self.imp_chk_pos_pre, 0, 0)
        imp_grid.addWidget(self.imp_chk_nega_stock, 0, 1)
        imp_grid.addWidget(self.imp_chk_nega_pre, 1, 0)
        imp_grid.addWidget(self.imp_chk_lora_base, 1, 1)
        imp_grid.addWidget(self.imp_chk_lora_pre, 2, 0)
        imp_grid.addWidget(self.imp_chk_fav, 2, 1)
        imp_grid.addWidget(self.imp_chk_memo, 3, 0)
        imp_layout.addLayout(imp_grid)

        # Import Mode Frame (Merge vs Overwrite)
        grp_mode = QGroupBox("Import Mode")
        mode_layout = QHBoxLayout(grp_mode)
        mode_layout.setContentsMargins(8, 6, 8, 6)

        self.rad_merge = QRadioButton("Add (Merge)")
        self.rad_merge.setChecked(True)
        self.rad_overwrite = QRadioButton("Overwrite (Replace)")

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.rad_merge)
        self.mode_group.addButton(self.rad_overwrite)

        mode_layout.addWidget(self.rad_merge)
        mode_layout.addWidget(self.rad_overwrite)
        imp_layout.addWidget(grp_mode)

        imp_layout.addStretch()

        imp_btn_bar = QHBoxLayout()
        btn_imp_check_all = QPushButton("Check ALL")
        btn_imp_check_all.setProperty("btnType", "action")
        btn_imp_check_all.clicked.connect(self.on_import_check_all)

        btn_import = QPushButton("Import From JSON")
        btn_import.setProperty("btnType", "success")
        btn_import.setFixedHeight(36)
        btn_import.clicked.connect(self.on_import_config)

        imp_btn_bar.addWidget(btn_imp_check_all)
        imp_btn_bar.addWidget(btn_import)
        imp_layout.addLayout(imp_btn_bar)

        h_main_io.addWidget(grp_import, 1)
        layout.addLayout(h_main_io, 1)

        # 2. Reset (NUKE) Button Bar
        reset_bar = QHBoxLayout()
        btn_nuke = QPushButton("⚠️ NUKE! (All Reset / 初期状態にリセット)")
        btn_nuke.setProperty("btnType", "danger")
        btn_nuke.setFixedHeight(34)
        btn_nuke.clicked.connect(self.on_reset_config)
        reset_bar.addWidget(btn_nuke)
        layout.addLayout(reset_bar)

        # 3. About Application
        info_box = QGroupBox("About Application")
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(12, 10, 12, 10)
        info_layout.setSpacing(4)

        lbl_app = QLabel("<b>KENZEN SeaArt Helper v5.1.1 (Python Edition)</b> — Stable Diffusion Prompt Engineering Assistant")
        lbl_app.setStyleSheet("color: #1E293B; font-size: 12px;")
        info_layout.addWidget(lbl_app)

        lbl_author = QLabel("• <b>Author:</b> Tomohito Fujikawa")
        lbl_author.setStyleSheet("color: #334155; font-size: 11px;")
        info_layout.addWidget(lbl_author)

        lbl_contact = QLabel('• <b>Contact:</b> <a href="https://dsblog.biz/" style="color: #2563EB;">https://dsblog.biz/</a>')
        lbl_contact.setOpenExternalLinks(True)
        lbl_contact.setStyleSheet("font-size: 11px;")
        info_layout.addWidget(lbl_contact)

        lbl_donate = QLabel('• <b>Donate:</b> <a href="https://paypal.me/dst0508" style="color: #059669; font-weight: bold;">https://paypal.me/dst0508</a>')
        lbl_donate.setOpenExternalLinks(True)
        lbl_donate.setStyleSheet("font-size: 11px;")
        info_layout.addWidget(lbl_donate)

        layout.addWidget(info_box)

    def on_export_check_all(self):
        all_checked = all([
            self.exp_chk_pos_pre.isChecked(), self.exp_chk_nega_stock.isChecked(),
            self.exp_chk_nega_pre.isChecked(), self.exp_chk_lora_base.isChecked(),
            self.exp_chk_lora_pre.isChecked(), self.exp_chk_fav.isChecked(),
            self.exp_chk_memo.isChecked()
        ])
        new_state = not all_checked
        self.exp_chk_pos_pre.setChecked(new_state)
        self.exp_chk_nega_stock.setChecked(new_state)
        self.exp_chk_nega_pre.setChecked(new_state)
        self.exp_chk_lora_base.setChecked(new_state)
        self.exp_chk_lora_pre.setChecked(new_state)
        self.exp_chk_fav.setChecked(new_state)
        self.exp_chk_memo.setChecked(new_state)

    def on_import_check_all(self):
        all_checked = all([
            self.imp_chk_pos_pre.isChecked(), self.imp_chk_nega_stock.isChecked(),
            self.imp_chk_nega_pre.isChecked(), self.imp_chk_lora_base.isChecked(),
            self.imp_chk_lora_pre.isChecked(), self.imp_chk_fav.isChecked(),
            self.imp_chk_memo.isChecked()
        ])
        new_state = not all_checked
        self.imp_chk_pos_pre.setChecked(new_state)
        self.imp_chk_nega_stock.setChecked(new_state)
        self.imp_chk_nega_pre.setChecked(new_state)
        self.imp_chk_lora_base.setChecked(new_state)
        self.imp_chk_lora_pre.setChecked(new_state)
        self.imp_chk_fav.setChecked(new_state)
        self.imp_chk_memo.setChecked(new_state)

    def on_export_config(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"KENZEN_Backup_{timestamp}.json"

        fname, _ = QFileDialog.getSaveFileName(
            self,
            "設定のエクスポート / Export Configuration",
            default_filename,
            "JSON Files (*.json)"
        )
        if not fname:
            return

        export_data = {}
        if self.exp_chk_fav.isChecked():
            export_data["Favorites"] = self.config.get_favorites()
        if self.exp_chk_lora_base.isChecked():
            export_data["LoRAData"] = self.config.get_lora_list()
        if self.exp_chk_lora_pre.isChecked():
            export_data["LoRAPresets"] = self.config.get_lora_presets()
        if self.exp_chk_pos_pre.isChecked():
            export_data["PositivePresets"] = self.config.get_positive_presets()
            export_data["PositiveStock"] = self.config.get_positive_stock()
        if self.exp_chk_nega_pre.isChecked():
            export_data["NegativePresets"] = self.config.get_negative_presets()
        if self.exp_chk_nega_stock.isChecked():
            export_data["NegativeStock"] = self.config.get_negative_stock()
        if self.exp_chk_memo.isChecked():
            export_data["MobileMemos"] = self.config.get_mobile_memos()

        try:
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(
                self,
                "完了 / Success",
                f"選択した設定をエクスポートしました！\nExported to:\n{fname}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

    def on_import_config(self):
        """Issue 4: Robust importing supporting all legacy/v5 structures without type errors."""
        fname, _ = QFileDialog.getOpenFileName(
            self,
            "設定ファイルのインポート / Import Configuration",
            "",
            "JSON Files (*.json)"
        )
        if not fname:
            return

        if self.config.is_master_config_file(fname):
            QMessageBox.critical(
                self,
                "インポートエラー / Import Error",
                "「KENZEN_Config.json」は現在使用中の母艦設定ファイルのため、インポートできません。\n\n"
                "エクスポートしたバックアップファイル（例: KENZEN_Backup_*.json）を選択してください。\n\n"
                "'KENZEN_Config.json' cannot be imported as it is the active master configuration."
            )
            return

        is_merge = self.rad_merge.isChecked()

        try:
            raw_imported = self.config.read_json_safely(fname)
            normalized = self.config.normalize_imported_data(raw_imported)

            salvaged_count = 0
            salvage_filename = ""
            import_summary = []

            # 1. Favorites
            if self.imp_chk_fav.isChecked() and "Favorites" in normalized:
                imported_favs = normalized["Favorites"]
                if is_merge:
                    curr_favs = self.config.get_favorites()
                    curr_prompts = {str(f.get("prompt", "")).strip() for f in curr_favs}
                    added_favs = 0
                    for f in imported_favs:
                        pr = str(f.get("prompt", "")).strip()
                        if pr and pr not in curr_prompts:
                            new_id = (max([int(item.get("id", 0)) for item in curr_favs]) + 1) if curr_favs else 1
                            curr_favs.append({"id": new_id, "prompt": pr, "description": str(f.get("description", ""))})
                            curr_prompts.add(pr)
                            added_favs += 1
                    target_favs = curr_favs
                    import_summary.append(f"• Favorites: {added_favs} 件 (Total: {len(target_favs)})")
                else:
                    target_favs = imported_favs
                    import_summary.append(f"• Favorites: {len(target_favs)} 件")

                if len(target_favs) > 50:
                    self.config.data["Favorites"] = target_favs[:50]
                    salvaged_favs = target_favs[50:]
                    salvaged_count = len(salvaged_favs)

                    # Issue 5: Naming rule KENZEN_Fav_Overflow_yymmdd_HHMMSS.json
                    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
                    base_dir = os.path.dirname(os.path.abspath(self.config.config_path))
                    salvage_filename = os.path.join(base_dir, f"KENZEN_Fav_Overflow_{timestamp}.json")
                    with open(salvage_filename, "w", encoding="utf-8") as sf:
                        json.dump({"Favorites": salvaged_favs}, sf, indent=2, ensure_ascii=False)
                else:
                    self.config.data["Favorites"] = target_favs

            # 2. LoRA Base Data
            if self.imp_chk_lora_base.isChecked() and "LoRAData" in normalized:
                if is_merge:
                    curr_loras = self.config.get_lora_list()
                    curr_aliases = {str(l.get("alias", "")) for l in curr_loras}
                    added_lora = 0
                    for lora in normalized["LoRAData"]:
                        if str(lora.get("alias", "")) not in curr_aliases:
                            curr_loras.append(lora)
                            curr_aliases.add(str(lora.get("alias", "")))
                            added_lora += 1
                    self.config.data["LoRAData"] = curr_loras
                    import_summary.append(f"• LoRA Base Data: {added_lora} 件 (Total: {len(curr_loras)})")
                else:
                    self.config.data["LoRAData"] = normalized["LoRAData"]
                    import_summary.append(f"• LoRA Base Data: {len(normalized['LoRAData'])} 件")

            # 3. LoRA Presets
            if self.imp_chk_lora_pre.isChecked() and "LoRAPresets" in normalized:
                if is_merge:
                    curr_presets = self.config.get_lora_presets()
                    curr_presets.update(normalized["LoRAPresets"])
                    self.config.data["LoRAPresets"] = curr_presets
                    import_summary.append(f"• LoRA Presets: {len(normalized['LoRAPresets'])} 件")
                else:
                    self.config.data["LoRAPresets"] = normalized["LoRAPresets"]
                    import_summary.append(f"• LoRA Presets: {len(normalized['LoRAPresets'])} 件")

            # 4. Positive Presets & Stock
            if self.imp_chk_pos_pre.isChecked():
                if "PositivePresets" in normalized:
                    if is_merge:
                        curr_pos = self.config.get_positive_presets()
                        curr_pos.update(normalized["PositivePresets"])
                        self.config.data["PositivePresets"] = curr_pos
                    else:
                        self.config.data["PositivePresets"] = normalized["PositivePresets"]
                    import_summary.append(f"• Positive Presets: {len(normalized.get('PositivePresets', {}))} 件")

                if "PositiveStock" in normalized:
                    if is_merge:
                        curr_stock = set(self.config.get_positive_stock())
                        curr_stock.update(normalized["PositiveStock"])
                        self.config.data["PositiveStock"] = list(curr_stock)
                    else:
                        self.config.data["PositiveStock"] = normalized["PositiveStock"]
                    import_summary.append(f"• Positive Stock: {len(normalized.get('PositiveStock', []))} 件")

            # 5. Negative Presets & Stock
            if self.imp_chk_nega_pre.isChecked() and "NegativePresets" in normalized:
                if is_merge:
                    curr_nega = self.config.get_negative_presets()
                    curr_nega.update(normalized["NegativePresets"])
                    self.config.data["NegativePresets"] = curr_nega
                else:
                    self.config.data["NegativePresets"] = normalized["NegativePresets"]
                import_summary.append(f"• Negative Presets: {len(normalized['NegativePresets'])} 件")

            if self.imp_chk_nega_stock.isChecked() and "NegativeStock" in normalized:
                if is_merge:
                    curr_n_stock = set(self.config.get_negative_stock())
                    curr_n_stock.update(normalized["NegativeStock"])
                    self.config.data["NegativeStock"] = list(curr_n_stock)
                else:
                    self.config.data["NegativeStock"] = normalized["NegativeStock"]
                import_summary.append(f"• Negative Stock: {len(normalized['NegativeStock'])} 件")

            # 6. Mobile Memos
            if self.imp_chk_memo.isChecked() and "MobileMemos" in normalized:
                if is_merge:
                    curr_memos = self.config.get_mobile_memos()
                    added_memos = 0
                    for m in normalized["MobileMemos"]:
                        if m not in curr_memos:
                            curr_memos.append(m)
                            added_memos += 1
                    self.config.data["MobileMemos"] = curr_memos
                    import_summary.append(f"• Mobile Memos: {added_memos} 件 (Total: {len(curr_memos)})")
                else:
                    self.config.data["MobileMemos"] = normalized["MobileMemos"]
                    import_summary.append(f"• Mobile Memos: {len(normalized['MobileMemos'])} 件")

            self.config._validate_and_repair()
            self.config.save()
            self.config_reloaded.emit()

            mode_text = "マージ追加 (Merge)" if is_merge else "上書き置換 (Overwrite)"
            msg = f"選択した項目を {mode_text} でインポートしました！\nConfiguration imported successfully!\n\n"
            if import_summary:
                msg += "[インポート結果 / Import Details]\n" + "\n".join(import_summary)
            
            if salvaged_count > 0:
                msg += (
                    f"\n\n⚠️ 【注意 / Notice】\nお気に入りの登録上限(50件)を超えた {salvaged_count} 件は、"
                    f"以下のサルベージファイルに退避保存しました：\n{salvage_filename}"
                )

            QMessageBox.information(self, "完了 / Success", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import: {e}")

    def on_reset_config(self):
        """Issue 13: NUKE resets config, purges registry API keys, and triggers all UI controls reset."""
        ans = QMessageBox.question(
            self,
            "⚠️ 初期化確認 / Confirm Reset",
            "すべての設定・プリセットを初期状態にリセットしますか？\n（保存されているAPIキー等のレジストリ情報も完全に消去されます）\n\nAre you sure you want to reset all settings to default?\n(Saved API keys in Windows Registry will also be deleted.)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            from ..core.config_manager import DEFAULT_CONFIG
            # 1. Delete Gemini API key from Windows Registry
            self.config.delete_gemini_api_key_registry()

            # 2. Reset config data
            self.config.data = json.loads(json.dumps(DEFAULT_CONFIG))
            self.config.save()
            self.config_reloaded.emit()
            self.config_reset_all_ui.emit()
            QMessageBox.information(
                self,
                "初期化完了 / Success",
                "設定および全タブの入力内容、APIキーのレジストリ情報を初期状態にリセットしました。\nSettings, UI fields, and registry API keys reset to factory default."
            )
