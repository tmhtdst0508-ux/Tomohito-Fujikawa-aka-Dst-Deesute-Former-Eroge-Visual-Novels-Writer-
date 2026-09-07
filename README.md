[**(日本語は下にあります)**](#japanese)

> **[Notice]** Starting with **v5.0.0**, this tool is a standalone application—**Microsoft Excel is no longer required!**  
> However, it is exclusively built for Windows desktop environments.  
> Sorry, prompt mages on mobile devices, this "forbidden door" still requires a PC key to unlock its true power! 💻✨

> **[注意]** **v5.0.0** より、本ツールはスタンドアロン（単体起動）アプリへと進化しました。**Microsoft Excelは一切不要です！**  
> ただし、動作環境はWindowsデスクトップ（PC）専用となります。  
> モバイル術士の皆様には申し訳ありませんが、この「禁断の扉」を開くには、引き続き「PC環境」というキーをご用意ください。 💻✨

💬 *Want to share your thoughts on my philosophy? Let's discuss it in the [[Discussions thread]](https://github.com/tmhtdst0508-ux/KENZEN-SeaArt-Helper/discussions)!*  
💬 開発理念なんかを、[ディスカッションスレッド](https://github.com/tmhtdst0508-ux/KENZEN-SeaArt-Helper/discussions)に書いています。お手柔らかに！

---

# Welcome to the KENZEN SeaArt Helper! 🤝

Greetings to all fellow AI Mages in Japan and across the world who strive for "KENZEN" (Wholesome™/NSFW) art!

I am Tomohito Fujikawa (aka "D.S.T." or "Deeste"). I am a writer who has spent approximately 15 years on the front lines of over 60 PC eroge (Visual Novel) titles, weaving scenarios and situations. In my pursuit of the ultimate "KENZEN (NSFW)" AI illustrations, I hit a wall: *"I need a system to manage my deep-seated karma (fetishes) and complex prompts more intuitively and safely."*

That is exactly why I forged this tool for my comrades (read: you degenerates). **KENZEN SeaArt Helper** is the ultimate standalone cockpit for AI mages wielding SeaArt and Stable Diffusion.

**How to Download & Launch**
1. Download `KENZEN_SeaArt_Helper_v5.1.1.zip` from the GitHub Releases.
2. Extract the ZIP file to any local folder on your PC (e.g. `C:\Tools\KENZEN_SeaArt_Helper`). *(Notice: Do NOT run directly from Cloud sync folders like OneDrive or Dropbox!)*
3. Double-click `KENZEN_SeaArt_Helper.exe` to launch immediately. No installation or Excel setup required!

<a id="created-with-kenzen-seaart-helper"></a>
## 🔞 Created with KENZEN SeaArt Helper

Want to see what this tool can actually create?

The story-driven adult AI CG collections created using KENZEN SeaArt Helper.

* 80 carefully selected CGs
* A complete original story in 4 chapters
* Written by a former professional Japanese eroge scenario writer
* English edition available

* [***Melancholy & Bliss of a Futanari Office Lady***](https://dst-fujikawa.itch.io/melancholy-bliss-of-a-futanari-office-lady) (Free trial [**here**](https://dst-fujikawa.itch.io/melancholy-bliss-of-a-futanari-office-lady-free-trial))
* [***That Handsome Captain's Unexpected Secret***](https://dst-fujikawa.itch.io/that-handsome-captains-unexpected-secret) (Free trial [**here**](https://dst-fujikawa.itch.io/that-handsome-captains-unexpected-secret-trial-ver))
* [***Rebellion at Futanari Academy***](https://dst-fujikawa.itch.io/rebellion-at-futanari-academy) (Free Trial [**here**](https://dst-fujikawa.itch.io/rebellion-at-futanari-academy-trial-ver))
* [***Futanari Idol's Special Fan Service!***](https://dst-fujikawa.itch.io/futanari-idols-special-fan-service) (Free Trial [**here**](https://dst-fujikawa.itch.io/futanari-idols-special-fan-service-trialver))
* [***Futanari in the Mirror***](https://dst-fujikawa.itch.io/futanari-in-the-mirror) (Free Trial [**here**](https://dst-fujikawa.itch.io/futanari-in-the-mirror-trial-ver))
* [***In Brief: I Am Futanari, Yet I Adore Thee***](https://dst-fujikawa.itch.io/in-brief-i-am-futanari-yet-i-adore-thee) (Free Trial [**here**](https://dst-fujikawa.itch.io/in-brief-i-am-futanari-yet-i-adore-thee-trial-ver))

> **Adults only (18+).** The linked pages contain explicit fictional sexual content.

 - [What's New?](#whatsnew)

 - [1. Introduction & Setup](#en_1)

 - [2. Windows & Tab Controls](#en_2)

 - - [2-0. Tag Matrix Window (Tag & Sample Database)](#en_2-0)

 - - [2-1 "Cockpit" Tab](#en_2-1)

 - - [2-2. "Positive" Tab](#en_2-2)

 - -  [2-3. "Negative" Tab ](#en_2-3)

 - - [2-4. "LoRA" Tab)](#en_2-4)

 - - [2-5. "Favorite" Tab](#en_2-5)

 - - [2-6. "Gacha!" Tab ](#en_2-6)

 - - [2-7. "Mobile Memo" Tab](#en_2-7)

- - [2-8. "IO / Settings" Tab](#en_2-8)

 - [3. Mobile HTML & Bookmarklet](#en_3)

- [4. Disclaimer & Contact](#en_4)

 - [5. License](#en_5)

 - [6. Troubleshooting & FAQ](#en_6)

 ---
<a id = "whatsnew"></a>
## 🚀 Release v5.1.1: Precision & Default Presets Update! 🎯🔄✨

* 🔄 **Default Preset Auto-Deploy & "Call Default" Button / デフォルトプリセット自動展開 ＆ 復元ボタン:** Presets designated via "⭐ Set as Default" across Positive, Negative, and LoRA tabs now automatically deploy to active lists and previews upon application launch! A dedicated "🔄 Call Default" button has also been added to all three tabs to instantly restore or apply default presets on demand.
* 🛡️ **Comma-Containing Tag Wildcard Protection / カンマ付きタグのワイルドカード保護:** Fixed an issue where dynamic prompts formatting (`{}`) erroneously split single tags containing commas (such as `ass up, face down`) into pipe-separated fragments (`{ass up | face down}`). Single and multi-tag selections are now accurately preserved.
* 🎛️ **Weight Pulldown Checkbox Interlocking / 重み付けプルダウン連動修正:** Fixed an issue where the weight pulldown was accessible even when the "Weight:" checkbox was disabled. It is now strictly locked and grayed out until the checkbox is explicitly checked.
* 📋 **Favorites Instant Detail Preview / お気に入り選択時の即時反映:** Clicking, selecting, or navigating rows in the Favorites tab now immediately reflects the Description and Prompt in the detail panel without latency.
* ⚡ **Global Shortcuts & Focus Transition / ショートカット＆フォーカス自動遷移:** Full integration of `Ctrl+Shift+L` for instant LoRA insertion into Cockpit tail with automatic tab switching and editor focus, alongside `Ctrl+Shift+P` for positive tags.
---

# ■ KENZEN SeaArt Helper Manual (v5.1.1)

_Prefer offline reading? [Download the PDF Manual here!](docs/KENZEN_SeaArt_Helper_Manual_v5.1.1.pdf)_

**TL;DR:** This is a standalone desktop application specialized in building, weighting, and managing NSFW generation prompts for SeaArt & Stable Diffusion. Includes SQLite-backed 41-category matrix, LoRA managers, and AI Gacha alchemy powered by Google Gemini API.

---

<a id = "en_1"></a>
## 1. Introduction & Setup

* **Architecture:** Standalone Windows Application built with Python 3 & PySide6 (Qt).
* **Open Source & Transparency:** All source code is hosted openly on GitHub.
* **Safety First:**
  * **Local Execution Guard:** Strictly prevents running within cloud-synced folders (OneDrive, Dropbox, Google Drive) to prevent JSON/SQLite file locking issues.
  * **Single Instance Manager:** Prevents launching duplicate instances; trying to open a second instance automatically activates and brings the running window to front.

---
<a id ="en_2"></a>
## 2. Windows & Tab Controls

<a id = "en2-0"></a>
### 2-0. Tag Matrix Window (Tag & Sample Database)

![Tag_Matrix](images/Tag_matrix_20260823.jpg)


The Dictionary Matrix displays all 41 categories (0. Particles/Prepositions through 40. Censorship Fixes & Others) in an intuitive side-by-side layout:
* **Tag Matrix Tab:** Displays categories across scrollable columns with Japanese labels on the left and English prompt tags on the right. Clicking a tag immediately transfers it to the Cockpit!
* **Sample Prompts Tab:** A built-in repository of master-crafted prompt archetypes ready to load directly into the Cockpit.
* - **Two copy modes:** Left-clicking a tag copies it with a comma and a half-width space (, ), while right-clicking copies it with just a half-width space ( ) and sends it to Cockpit. For example, if you want to type “`sitting on chair`” left-click to copy “`sitting`,” right-click to copy “`on`” (without the comma), and then right-click again to copy “`chair`.”
* **Quick Search & Jump (A-Z Sorted & 3-Pulse Flash):** All tags within each category are strictly sorted alphabetically by English prompt (A–Z, case-insensitive). Searching via Enter or **Next ▶** immediately scrolls directly to the matched cell and highlights it with a vivid 3-pulse yellow flash (`#FEF08A` / `#F59E0B`), sequentially looping through subsequent matches. The Jump dropdown instantly navigates across all 41 categories (including Category 0. Particles/Prepositions).

---

<a id = "en_2-1"></a>
### 2-1. "Cockpit" Tab

![Cockpit_tab](images/Cockpit_tab_20260823.jpg)

The central command center for assembling, tweaking, and finalizing your generation prompts.

* **Top App Title & Matrix Launcher:** Displays tool status and a button to re-summon the Dictionary Matrix window at any time.
* **Main Prompt Editor :** Free-form editing canvas with real-time feedback and automatic comma formatting.
* **Weight Controls (0.5 – 1.5):** Select any text block and click **Apply Weight (tag:w)** to wrap it into `(tag:weight)`. Toggle **Enable Weight** for automatic single-tag weighting upon addition (weight pulldown is strictly locked until the checkbox is enabled).
* **Wrap Dynamic Prompts (`{A | B | C}`):** Instantly formats comma-separated tokens into Dynamic Prompts syntax `{optionA | optionB | optionC}` (or unwraps back), with robust preservation for single tags that inherently contain commas (such as `ass up, face down`).
* **Sort Prompts (41 Categories & Smart Hierarchy):** Re-organizes chaotic prompt strings strictly according to Base Positive rules, LoRA triggers, and the 41 database categories.
  * **Selection Range Sort:** When text is highlighted/selected in the editor, clicking **Sort Prompts** sorts **ONLY the selected text range** by database category order, replacing it in-place without altering surrounding prompts.
  * **Multi-BREAK & LoRA Trigger Relocation:** When sorting across entire prompts containing `BREAK` syntax, registered LoRA triggers (even if added after BREAK or separated without commas) are automatically extracted and relocated into the **1st block immediately following Base Positive quality tags** (Score 0.5), while `<lora:...>` blocks are neatly positioned at the prompt tail.
  * **Nested Bracket & Dynamic Prompts Protection:** Compound weighted groups like `(tag1, tag2:1.3)` and Dynamic Prompts `{optionA | optionB}` are preserved completely intact and evaluated by their internal tags for optimal category positioning.
* **Done! (Clean & Copy to Clipboard):** Scrubs duplicate commas/spaces, sanitizes the prompt, and copies it cleanly to the Windows clipboard.
* **Soft Clear vs Hard Clear:**
  * 🗑 **Clear (Yellow):** Clears the text editor while safely preserving Undo history.
  * 💣 **Delete All (Red):** Completely clears text and wipes all Undo history after confirmation.
* **Send to Favorites & Precise 1-Step Undo:** One-click dispatch of the active prompt to the Favorites tab. The **Undo** button provides precise, single-step rollback (up to 50 levels) to previous prompt states.

---

<a id = "en_2-2"></a>
### 2-2. "Positive" Tab

![Positive_tab](images/Positive_tab_20260907.jpg)

Manage and deploy your standard positive quality boosters.

* **Dual Listbox Layout:** Manage your library in the **Stock** listbox on the left, and curate active tags in the **Applied** listbox on the right.
* **Bulk Import:** Paste raw comma-separated prompt dumps to strip brackets, clean weights, and extract clean tokens into your stock.
* **Selection Preview & Reordering:** Live preview reflecting selected items in the Applied list, with dedicated Up/Down reordering controls.
* **Preset Management & Auto-Deploy with 🔄 Call Default:** Save named Positive presets and assign a startup **Default Preset** via **⭐ Set as Default** to automatically deploy them on application launch. Click **🔄 Call Default** at any time to instantly restore or apply your default preset. Selecting any preset from the dropdown automatically populates the Applied list, **selects all items immediately**, and outputs the full comma-separated prompt to the Preview Box for instant dispatch (`Ctrl+Shift+P`) without manual re-selection. Includes strict case-insensitive duplicate prevention when adding tags to stock.
* **🚀 Send Applied Tags to Cockpit Beginning (`Ctrl+Shift+P`):** Automatically injects the applied positive tags to the *very beginning* of the Cockpit prompt with strict duplicate detection.

---

<a id = "en_2-3"></a>
### 2-3. "Negative" Tab

![Negative_tab](images/Negative_tab_20260907.jpg)

Manage your essential negative blacklist prompts.

* **Dual Listbox (Stock & Applied) with Auto-Deploy & 🔄 Call Default:** Mirroring the Positive tab, curate active negative tags seamlessly. Designated default presets automatically deploy upon application launch, and can be restored at any time via **🔄 Call Default**. Selecting any Negative preset instantly populates the Applied list, selects all items, and generates the active preview for one-click clipboard copying. Duplicate stock tags are automatically skipped.
* **Negative Weighting (1.0 – 1.5):** Apply fine-tuned emphasis weights directly to negative tokens within the Preview box.
* **LoRA Negative Receiver:** Direct bridge receiving recommended negative tags dispatched from the LoRA tab.
* **Direct Clipboard Copy:** Copies sanitized negative tag chains straight to your clipboard.

---

<a id = "en_2-4"></a>
### 2-4. "LoRA" Tab (The LoRA Forge & Vault)

![LoRA_tab](images/LoRA_tab_20260907.jpg)

Complete visual architecture for LoRA integration and trigger word management.

* **Dual Pane Vault & Configuration:**
  * **Left:** Registered LoRA Library list with individual weight indicators and reordering controls.
  * **Right:** Dedicated configuration panel separating **System Name** (read-only from file) and **LoRA Alias** (custom nickname).
* **Automatic File Hash Extractor:** Browse any `.safetensors` file to automatically compute its short SHA-256 hash (10 characters) and auto-fill model names.
* **Trigger Selection & Individual Weighting (1.0 – 1.5):** Selectively toggle registered trigger keywords and apply custom weights upon wrapping.
* **Wrap with Name / Wrap with Hash:** Format triggers into `<lora:name:weight>` or `<lora:hash:weight>` tailored for SeaArt or SD WebUI in the dedicated preview.
* **LoRA Presets with ⭐ Set as Default & 🔄 Call Default:** Save favorite LoRA combinations as named presets. Use **⭐ Set as Default** to automatically load them into preview on startup, and click **🔄 Call Default** to restore anytime.
* **Preview Controls:**
  * **Remove LoRA:** Intelligently extracts and deletes a specific LoRA and its related triggers from the preview box without destroying other tags.
  * **Forget LoRA:** Completely clears all input fields, checkboxes, and preview for a fresh start.
* **Send LoRA Negative / Send to Fav / Send to Cockpit (Ctrl+Shift+L Shortcut):** Bridge tags seamlessly to Negative Preview, Favorites, or Cockpit with duplicate prevention. Pressing **Ctrl+Shift+L** from any tab instantly appends generated LoRA tags from the preview box to the end of Cockpit prompt (prompts a warning dialog if the preview box is empty). When sending to Cockpit, KENZEN intelligently inspects existing LoRA tags, skips duplicates, and seamlessly appends only newly added LoRA tags.

---

<a id = "en_2-5"></a>
### 2-5. "Favorites" Tab (The Fetish Vault)

![Favorites_tab](images/Favorites_tab_20260823.jpg)

Save, search, curate, and export your masterpiece prompts.

* **Master Table & Instant Real-Time Preview:** Displays saved entries with numbered index, Description, and Full Prompt. Real-time keyword search across titles and prompts. Selecting or navigating table rows immediately displays description and prompt details without delay.
* **Splitter Detail & Edit Pane with 🧹 Clear Input:** Live text fields for adjusting Descriptions and Prompts, with **Pull from Cockpit** integration. Features a dedicated **🧹 Clear Input** button to clear editing fields without affecting saved database records. Protected with a 50-entry cap and normalized duplicate prompt prevention.
* **Add, Update, Reorder & Undo:** Duplicate prevention on addition, single-row update, Up/Down reordering, and dedicated **Undo Fav** protection.
* **Mobile JSON Export:** Export favorites directly into mobile-ready JSON for on-the-go browsing.
* **50-Item Limit & Automatic Salvage:** If importing more than 50 favorites, excess items are automatically safeguarded into an overflow backup file (`KENZEN_Fav_Overflow_yymmdd_HHMMSS.json`).

---

<a id = "en_2-6"></a>
### 2-6. "Gacha!" Tab (AI Auto-Pilot Prompt Alchemy)

![Gacha_tab](images/Gacha_tab_20260823.jpg)

AI-powered brainstorming utilizing the Google Gemini API (`gemini-3.7-flash`).

* **API Key Setup & Auto-Save:** Securely enter your Gemini API key with masked input and show/hide toggles.
* **Surprise Me! (SFW / NSFW / Hardcore):** Inject randomized thematic database tags to inspire creative and unexpected scene generations.
* **Cooldown Guard (15s):** 15-second protective timer preventing API spamming and accidental quota consumption.
* **Daily Runs Tracker & Quota Configurator:** Tracks estimated daily free quota resets at Pacific Time (PT). **Double-click** the quota status label to customize the daily limit (e.g. for paid API tier users).

---

<a id = "en_2-7"></a>
### 2-7. "Mobile Memo" Tab

![MobileMemo_tab](images/MobileMemo_tab_20260823.jpg)

Synchronize ideas and notes captured via the Mobile HTML web app.

* **Categorized Badge Badges:** Memos automatically display typed badges: `[Memo]`, `[URL]`, or `[Hash]`.
* **Smart Double-Click Action:**
  * `[URL]`: Opens link immediately in your default web browser.
  * `[Hash]`: Copies the hash value straight to your clipboard.
  * `[Memo]`: Focuses the text editor for instant tweaking.
* **Mobile JSON Import & Master Config Sync:** Import mobile notes and commit them to master `KENZEN_Config.json` storage.

---

<a id = "en_2-8"></a>
### 2-8. "IO / Settings" Tab

![IO_tab](images/io_tab_20260823.jpg)

Complete backup, restore, and maintenance center.

* **7-Item Granular Export & Import:** Checkbox control over Positive Presets, Positive/Negative Stock, Negative Presets, LoRA Base Data, LoRA Presets, Favorites, and Mobile Memos.
* **Merge vs Overwrite Modes:** Choose whether to non-destructively merge imported JSON assets or cleanly overwrite existing settings.
* **⚠️ NUKE! (Factory Reset):** Complete reset restoring all configurations, presets, and UI fields back to factory defaults.

---

<a id = "en_3"></a>
## 3. Mobile HTML & Bookmarklet

![Mobile_html](images/mobile_20260823.jpg)

* **`KENZEN_Mobile.html`:** Located in the `KENZEN_Mobile` folder. Open on any mobile browser to view exported Favorites and capture on-the-go memos without requiring desktop hardware.
* **`KENZEN_GetURL_BM.txt` (Bookmarklet):** Mobile browser bookmarklet to extract and copy LoRA hashes directly while browsing SeaArt on your phone.

---

<a id = "en_4"></a>
## 4. Disclaimer & Contact

* **Generation Disclaimer:** Generation results are non-deterministic and depend entirely on your AI model and backend parameters. The author assumes no responsibility for outputs.
* **Tested Models:** [REED XXX illustrious SDXL V15.0](https://civitai.red/models/1717562/reedxxxillustrioussdxl) & SDXL / Illustrious models.
* **Author:** Tomohito Fujikawa (aka "D.S.T." / "Deeste" / Former Eroge Scenario Writer).
* **Blog & Contact:** [dsblog.biz](https://dsblog.biz/)
* **Donations:** [PayPal Donation](https://paypal.me/dst0508)
* **Creator Works:** Check out commercial story-driven AI CG collections on [itch.io](https://dst-fujikawa.itch.io).

<a id = "en_5"></a>
## 5. License

The source code is licensed under the MIT License.
The `tags.db` database is provided under a separate license and is not covered by the MIT License.
See [LICENSE-DATA.md](LICENSE-DATA.md) for details.

<a id = "en_6"></a>
## 6. Troubleshooting & FAQ

### Antivirus or Windows SmartScreen Warnings (False Positives)

When downloading or running this application, your security software (such as ESET, Avast, or Windows SmartScreen) may flag it as "Suspicious" or unrecognized.

**This is a false positive.**
Because this software is built and packaged using Python and PyInstaller without an expensive commercial code-signing certificate, certain heuristic scanners automatically flag newly released binaries as unfamiliar files.

* **Digital Signature:** All official binaries are digitally signed by the developer.
* **Integrity Verification:** Every release is scanned on VirusTotal, and official SHA-256 checksums are published. Please check the specific release notes on the [Releases Page](https://github.com/tmhtdst0508-ux/KENZEN-SeaArt-Helper/releases) to verify the scan results and file hashes before reporting an issue.
* **Workaround:** If the file is quarantined or blocked, you may safely add it to your antivirus exclusion list or select "More info" -> "Run anyway" in Windows SmartScreen.

---

<a id="japanese"></a>
# KENZEN SeaArt Helperへようこそ！🤝

**日本の、そして世界中の「KENZEN」なる同志たるAI術師の皆様、ようこそ！**

不二川巴人（ふじかわ ともひと。あるいは「でぇすて」）と申します。約15年間にわたり、60タイトル以上のPC美少女ゲームの最前線で、シナリオやシチュエーションを紡いできた物書きです。究極の「KENZEN（NSFW）」なAIイラストを追い求める中で、「己の深淵なる業（性癖）と複雑怪奇なプロンプトを、もっと直感的に、かつ安全に管理するシステムが必要だ」という壁にぶち当たりました。

だからこそ、同志たち（と書いて「お前等」と読む）のためにこのツールを錬成しました。**KENZEN SeaArt Helper**は、SeaArtとStable Diffusionを駆使するAI術師のための究極のスタンドアロン・コックピットです。

**ダウンロードと起動方法**
1. GitHubのReleasesページから `KENZEN_SeaArt_Helper_v5.1.1.zip` をダウンロードします。
2. PC上の任意のローカルフォルダ（例：`C:\Tools\KENZEN_SeaArt_Helper`）にZIPを解凍します。（※OneDriveやDropbox等のクラウド同期フォルダ直下には置かないでください）
3. フォルダ内の `KENZEN_SeaArt_Helper.exe` をダブルクリックするだけで即座に起動します。Excelのインストールやマクロの許可設定は一切不要です！

<a id="created-with-kenzen-jp"></a>
## 🔞 KENZEN SeaArt Helperによる制作例

「このツールで、実際にどんな作品が作れるのか？」

KENZEN SeaArt Helperを使用して制作した、物語連動型AI成人向けCG集を公開しています。

* 厳選CG80枚
* 全4章の完全書き下ろしストーリー
* 元商業エロゲーシナリオライターによる構成・執筆
* 英語版をitch.ioにて販売中

* [**「ふたなりOLの憂鬱と幸福」**](https://dst-fujikawa.itch.io/melancholy-bliss-of-a-futanari-office-lady) （無料体験版は[**こちら**](https://dst-fujikawa.itch.io/melancholy-bliss-of-a-futanari-office-lady-free-trial)）
* [**「男前なアイツの意外な秘密」**](https://dst-fujikawa.itch.io/that-handsome-captains-unexpected-secret) （無料体験版は[**こちら**](https://dst-fujikawa.itch.io/that-handsome-captains-unexpected-secret-trial-ver)）
* [**「私立ふたなり学園の下剋上」**](https://dst-fujikawa.itch.io/rebellion-at-futanari-academy) （無料体験版は[**こちら**](https://dst-fujikawa.itch.io/rebellion-at-futanari-academy-trial-ver)）
* [**「ふたなりアイドルのファンサービス！」**](https://dst-fujikawa.itch.io/futanari-idols-special-fan-service) （無料体験版は[**こちら**](https://dst-fujikawa.itch.io/futanari-idols-special-fan-service-trialver)）
* [**「鏡の中のふたなり」**](https://dst-fujikawa.itch.io/futanari-in-the-mirror) （無料体験版は[**こちら**](https://dst-fujikawa.itch.io/futanari-in-the-mirror-trial-ver)）
* [***「前略、ふたなりですが、お慕い申し上げております」***](https://dst-fujikawa.itch.io/in-brief-i-am-futanari-yet-i-adore-thee) (無料体験版は [**こちら**](https://dst-fujikawa.itch.io/in-brief-i-am-futanari-yet-i-adore-thee-trial-ver))

> **18歳未満閲覧禁止。** リンク先には、架空の成人キャラクターによる露骨な性的表現が含まれます。

---
- [更新履歴](#whatsnew_jp)

- [1. はじめに・システム仕様](#ja_1)

 - [2. ウィンドウおよび各タブの操作方法](#ja_2)

 - - [2-0. 辞書マトリクスウィンドウ（Tag & Sample Database）](#ja_2-0)

 - - [2-1 「Cockpit」タブ（プロンプト構築の司令塔）](#ja_2-1)

 - - [2-2. 「Positive」タブ（ポジティブプロンプト管理）](#ja_2-2)

 - -  [2-3. 「Negative」タブ（絶許ブラックリスト）](#ja_2-3)

 - - [2-4. 「LoRA」タブ（LoRAの鍛冶場＆金庫）](#ja_2-4)

 - - [2-5. 「Favorites」タブ（性癖の金庫室）](#ja_2-5)

 - - [2-6. 「Gacha!」タブ（AIお任せ・プロンプト錬成）](#ja_2-6)

 - - [2-7. 「Mobile Memo」タブ（モバイルメモ管理）](#ja_2-7)

- - [2-8.「IO / Settings」タブ（設定・バックアップ管理）](#ja_2-8)

 - [3. モバイル版HTML ＆ ブックマークレット](#ja_3)

- [4. 免責事項・連絡先](#ja_4)

 - [5. ライセンス](#ja_5)

 - [6. トラブルシューティング & FAQ](#ja_6)

<a id = "whatsnew_jp"></a>
## 🚀 【v5.1.1 リリース！】: プリセット自動展開＆高精度デバッグアップデート！🎯🔄✨

* 🔄 **デフォルトプリセットの自動展開＆「🔄 Call Default」ボタン新設:** Positive、Negative、LoRA の各タブにおいて、「⭐ Set as Default」で設定したプリセットがアプリ起動時に自動展開されるようになりました！さらに、いつでもワンクリックでデフォルト設定を復元・展開できる「🔄 Call Default」ボタンを全3タブに追加。LoRAタブにも「⭐ Set as Default」を新設しました。
* 🛡️ **カンマを含むタグのワイルドカード（`{}`）保護修正:** `ass up, face down` のように内部にカンマを含む単一タグを `{}` で括った際、カンマで機械的に分割されてパイプ `|`（`{ass up | face down}`）に化けてしまう不具合を解消。単一・複数選択時ともに正確に保護・展開されます。
* 🎛️ **Cockpit 重み付けプルダウンのチェックボックス連動修正:** 「Weight:」チェックボックスがオフの時でも重み付けプルダウンが操作できてしまっていた問題を修正し、チェック時のみ有効化（オフ時はグレーアウト）されるよう連動を徹底。
* 📋 **Favorites タブの選択時即時反映:** お気に入り一覧の行をクリック・選択・キー移動した際、詳細欄（説明・プロンプト）に即座に内容が反映されるよう操作感を大幅改善。
* ⚡ **ショートカットの利便性強化:** 全タブ共通で「`Ctrl+Shift+L`」を押すだけでLoRAプレビュー欄のタグをCockpit末尾へ即座に挿入し、Cockpitタブへの自動画面切り替え＆エディタへのフォーカス移動を完備。
---

# ■ KENZEN SeaArt Helper マニュアル（v5.1.1）

_オフラインマニュアルは [こちらからダウンロードして下さい。](docs/KENZEN_SeaArt_Helper_Manual_v5.1.1.pdf)_

**要約：SeaArt及びStable Diffusionでの、NSFW・高精度プロンプト構築と管理に特化したスタンドアロンデスクトップツールです。SQLiteによる41カテゴリの辞書マトリクス、LoRA鍛冶場、Google Gemini APIによるAIガチャ錬成を搭載しています。**

---

<a id = "ja_1"></a>
## 1. はじめに・システム仕様

* **動作環境:** Windows 10 / 11 (64bit)
* **開発言語・基盤:** Python 3 + PySide6 (Qt)
* **透明性の確保:** 全ソースコードをGitHubにて公開。バックドア等は一切含まれていません。
* **安全設計:**
  * **クラウド同期ガード:** OneDriveやDropbox等のクラウド同期ディレクトリ上での直接実行を防止し、ファイルのロック破損を防ぎます。
  * **多重起動防止機構:** 重複起動を防止し、既に起動中のウィンドウを自動で最前面にアクティブ化します。

---

<a id = "ja_2"></a>
## 2. ウィンドウおよび各タブの操作方法

<a id = "ja_2-0"></a>
### 2-0. 辞書マトリクスウィンドウ（Tag & Sample Database）

![Tag_Matrix](images/Tag_matrix_20260823.jpg)

41カテゴリ（0.接続助詞・前置詞 ～ 40.修正その他）の全タグを一覧できる専用ウィンドウです。
* **タグ辞書マトリクス:** カテゴリごとに左列（日本語ラベル）、右列（英語タグ）がセットで並びます。セルをクリックするだけで、即座にCockpitのプロンプト末尾へ転送されます。
* **2つのコピーモード:**タグを左クリックすると、「`, `」（カンマと半角スペース）で、右クリックすると、「` `」（半角スペースのみ）でコピーされ、Cockpitへ送られます。例えば、「`sitting on chair`」としたい場合、「`sitting`」で左クリックコピー、「`on`」で右クリックコピー（カンマなし）「`chair`」で再度右クリックコピーすればOKです。
* **サンプルプロンプト集:** 作者厳選のシチュエーション呪文を収録。ワンクリックでCockpitへ展開し、ベース呪文として活用できます。
* **クイック検索 & カテゴリジャンプ（A〜Zアルファベット順＆3回点滅ハイライト）:** 各カテゴリ内のタグは英語プロンプトのアルファベット順（A〜Z・大文字小文字不問）で整列しています。検索バーにキーワードを入力して Enter または「Next ▶」を押すと、該当セルへ即座にスクロールして鮮やかな黄色で3回点滅（Flash）し、連続押下で次候補へ順次巡回ジャンプします。カテゴリジャンプのコンボボックスからは「0. 接続助詞・前置詞」を含む全41カテゴリへ瞬時に移動・最上部復帰できます。

---

<a id = "ja_2-1"></a>
### 2-1. 「Cockpit」タブ（プロンプト構築の司令塔）

![Cockpit_tab](images/Cockpit_tab_20260823.jpg)

プロンプトの編集、重み付け、並び替え、クリップボード転送を行うメイン画面です。

* **辞書マトリクス表示ボタン:** 閉じてしまった辞書マトリクスウィンドウをいつでも再呼び出しできます。
* **メインプロンプトエディタ:** タグの追記、手動編集が自由に行えるテキストエリア。
* **重み付け機能 (0.5 ～ 1.5):** テキストを選択して **Apply Weight (tag:w)** を押すと `(tag:1.2)` の形式で重み付けされます。**Enable Weight** にチェックを入れておくと、マトリクスからタグを追加した際に自動で重み付けが適用されます（チェックボックスがオフの時はプルダウン操作が無効化されます）。
* **Dynamic Prompts Wrap (`{A | B | C}`):** カンマ区切りの複数タグを選択してボタンを押すと、ワイルドカード記法 `{tag1 | tag2 | tag3}` へ一括変換（または解除）します。`ass up, face down` などのカンマを含むタグも分割されず正確に保護されます。
* **Sort Prompts (41カテゴリ自動整列 ＆ スマート階層化):** 散らかったプロンプトを、ベースポジティブ、LoRAトリガー、および41カテゴリの並び順に沿って瞬時に整列・ソートします。
  * **選択範囲のみのソート（Selection Sort）:** エディタ内でテキストを選択（ドラッグ等）した状態でソートボタンを押すと、**選択された範囲のタグのみがカテゴリ順に整列** され、前後のプロンプトを崩さずにインプレース置換されます。
  * **BREAK構文時のLoRAトリガー自動再配置:** `BREAK` を含む複数ブロックのプロンプトにおいて、BREAK以降や末尾に追加されたLoRAトリガーワードを自動検知し、**第1ブロックの品質ポジティブタグ（`masterpiece`等）の直後（優先スコア 0.5 の位置）** へ自動移動させます。`<lora:...>` タグ本体はプロンプト最末尾へスマート配置されます。
  * **複合重み括弧・Dynamic Promptsの完全保護:** `(tag1, tag2:1.3)` などの複合重み括弧や `{A | B}` 構文を一切破壊せず、内包されたタグに基づき最適なカテゴリ順位へ整列します。
* **Done! (Clean & Copy to Clipboard):** 余分なカンマやスペースを自動クリーニングし、クリップボードにコピーします。
* **Clear と Delete All:**
  * 🗑 **Clear (履歴保持・黄色):** Undo（アンドゥ）履歴を残したままエディタをクリアします。
  * 💣 **Delete All (履歴ごと消去・赤色):** アンドゥ履歴を含め、完全に初期化します。
* **Send to Favorites / 精密1ステップUndo:** お気に入りタブへのワンクリック転送に対応。Undo（元に戻す）ボタンは1回のクリックで直前の入力状態へ「1ステップずつ正確に」戻る最大50段階の履歴管理を搭載しています。

---

<a id = "ja_2-2"></a>
### 2-2. 「Positive」タブ（ポジティブプロンプト管理）

![Positive_tab](images/Positive_tab_20260907.jpg)

AIの描写クオリティを底上げするポジティブタグの管理画面です。

* **手持ちストック ＆ 適用リストの2カラム構造:** 左側のストック一覧から、今回使いたいタグを選んで右側の適用リストへ転送します。
* **生プロンプト一括インポート (Bulk Import):** 既存のカンマ区切り呪文を貼り付けるだけで、記号や重みを自動除去して一括登録できます。
* **選択プレビュー & 順序入れ替え:** 適用リスト内で選択されたタグのみがプレビュー欄に表示され、▲/▼ボタンで出力順序を自在にソート可能。
* **プリセット保存・起動時自動展開 ＆ 🔄 Call Default:** よく使うポジティブタグの組み合わせを名前付きプリセットとして保存でき、「**⭐ Set as Default**」で次回起動時の標準プリセットに指定して自動展開可能。新設された「**🔄 Call Default**」ボタンで、いつでもワンクリックでデフォルト設定を展開・復元できます。プリセットを選択すると、適用リストへの展開と同時に **すべてのタグが自動的に全選択** され、下部のプレビュー欄にもプロンプトが即座に出力されます。マウスで再選択することなく、そのまま「`Ctrl+Shift+P`」でCockpit先頭へ送信できます（ストック追加時の重複防止ガード付き）。
* **🚀 Send Applied Tags to Cockpit Beginning (`Ctrl+Shift+P`):** 適用タグを、Cockpitプロンプトの**最先頭**へスマートに挿入します（重複検知ガード付き）。

---

<a id = "ja_2-3"></a>
### 2-3. 「Negative」タブ（絶許ブラックリスト）

![Negative_tab](images/Negative_tab_20260907.jpg)

破綻や不要な要素を排除するネガティブプロンプトの管理画面です。

* **手持ちストック ＆ 適用リスト（起動時自動展開 ＆ 🔄 Call Default）:** ポジティブタブと同様の2カラム構成で快適に管理。「**⭐ Set as Default**」で起動時の自動展開に対応し、新設された「**🔄 Call Default**」ボタンでいつでもデフォルト設定を即座に復元できます。ネガティブプリセットを選択すると、適用リストが自動で全選択されてプレビュー欄に即時反映され、ワンクリックでクリップボードへコピーできます。ストック追加時の重複登録も自動でスキップされます。
* **ネガティブ重み付け (1.0 ～ 1.5):** プレビュー欄内の特定タグを選択し、強調したい度合いに合わせて重み付けを適用。
* **LoRAネガティブ受信機能:** LoRAタブから転送された固有の推奨ネガティブタグを直接プレビュー欄に合流させます。
* **クリップボード直接コピー:** 適用ネガティブプロンプトを一発でクリップボードへコピー。

---

<a id = "ja_2-4"></a>
### 2-4. 「LoRA」タブ（LoRAの鍛冶場＆金庫）

![LoRA_tab](images/LoRA_tab_20260907.jpg)

LoRAタグ `<lora:name:strength>` とトリガーワードの組み合わせを完全掌握する専用タブです。

* **ライブラリ一覧 ＆ 詳細設定パネル:**
  * **左側:** 登録済みLoRA一覧（強度表示、▲/▼によるソート、削除）。
  * **右側:** ファイル名から取得された **System Name (編集不可)** と、自由に命名できる **LoRA Alias** を完全分離して管理。
* **短縮ハッシュ自動算出:** `.safetensors` ファイルを指定するだけで、Auto V2ハッシュとモデル名を自動抽出。
* **トリガーワード選択 ＆ 個別重み付け (1.0 ～ 1.5):** 登録されたトリガーワードから必要なものを選択し、指定の強度でラップ可能。
* **Wrap with Name / Wrap with Hash:** WebUI向けの名前ラップ、SeaArt向けのハッシュラップをワンクリックで切り替え。
* **LoRAプリセットの標準化（⭐ Set as Default ＆ 🔄 Call Default）:** 頻用するLoRAの組み合わせをプリセットとして保存可能。「**⭐ Set as Default**」で次回起動時にプレビュー欄へ自動展開でき、新設された「**🔄 Call Default**」ボタンでいつでも即座に復元できます。
* **プレビュー個別制御:**
  * **Remove LoRA:** プレビュー内に存在する特定のLoRAタグおよび関連トリガーのみをピンポイントで除外。
  * **Forget LoRA:** 入力欄やチェックボックス、プレビューを一括で初期化。
* **LoRAネガティブ転送 / Fav転送 / Cockpit転送（Ctrl+Shift+L ショートカット対応）:** 完成したLoRA群を各タブへ安全に受け渡し。全タブ共通で「`Ctrl+Shift+L`」を押すと、LoRAプレビュー欄のタグをCockpitの末尾へ即時挿入します（プレビュー欄が空の場合は注意ダイアログを表示）。Cockpit転送時は既存のLoRAタグを自動スキップし、新規追加されたLoRAタグのみをスマート差分転送（末尾マージ）します。

---

<a id = "ja_2-5"></a>
### 2-5. 「Favorites」タブ（性癖の金庫室）

![Favorites_tab](images/Favorites_tab_20260823.jpg)

完成した傑作プロンプトを整理・保存・活用するデータベースです。

* **一覧テーブル ＆ 選択時即時反映:** 番号、タイトル（Description）、プロンプトを一覧表示。検索窓からの瞬時絞り込みに加え、行をクリック・上下キー移動した際に即座に詳細欄へタイトルとプロンプトが反映されます。
* **詳細・編集スプリッター ＆ 🧹 Clear Input（入力消去）:** 選択したお気に入りのタイトルとプロンプトを下部エリアで直接微調整。**Pull from Cockpit** で現在のコックピット内容をワンタッチ取得。新設された「**🧹 Clear Input / 入力消去**」ボタンにより、保存済みレコードに影響を与えずに入力欄をワンクリックでクリアできます。最大50件の登録上限ガードおよび空白正規化による重複登録防止機能を完備。
* **新規登録・上書き更新・Undo Fav:** プロンプトの完全一致重複ガード、1行更新、誤操作を防ぐアンドゥ機能を完備。
* **モバイル用JSON出力:** お気に入りデータをスマホ版HTMLで扱えるJSON形式として書き出し。
* **50件上限オーバーフロー退避（サルベージ機能）:** お気に入りが50件の上限を超えてインポートされた場合、溢れたデータは自動的に `KENZEN_Fav_Overflow_yymmdd_HHMMSS.json` として退避保存されます。

---

<a id = "ja_2-6"></a>
### 2-6. 「Gacha!」タブ（AIお任せ・プロンプト錬成）

![Gacha_tab](images/Gacha_tab_20260823.jpg)

Google Gemini API（`gemini-3.7-flash`）によるAIプロンプト自動生成機能です。

* **APIキー設定 ＆ マスク表示:** APIキーを安全に保存・管理（表示/非表示トグル付き）。
* **Surprise Me! (SFW / NSFW / Hardcore):** データベースからランダムにインスピレーションタグを抽出し、AIに斬新なプロンプトを考案させます。
* **15秒クールダウンガード:** 連打によるAPI制限エラーと残弾浪費を防ぐ安全タイマー。
* **残弾カウンター ＆ 上限変更（ダブルクリック）:** 本日の残り生成枠を表示（PT時間0時リセット）。ステータス部分を**ダブルクリック**することで、API課金ユーザー向けに1日の上限回数を自由に変更可能です。

---

<a id = "ja_2-7"></a>
### 2-7. 「Mobile Memo」タブ（モバイルメモ管理）

![MobileMemo_tab](images/MobileMemo_tab_20260823.jpg)

外出先でスマホ版HTMLに書き留めたアイデアを母艦に取り込みます。

* **自動バッジ分類:** メモ内容に応じて `[Memo]`, `[URL]`, `[Hash]` のバッジを自動付与。
* **スマート・ダブルクリックアクション:**
  * `[URL]`: 既定のブラウザでWebページを即座に開きます。
  * `[Hash]`: ハッシュ値を直接クリップボードにコピーします。
  * `[Memo]`: 右側の編集エリアにフォーカスします。
* **モバイルJSON取込 ＆ 母艦Config同期:** モバイルから送られたメモを統合し、母艦の `KENZEN_Config.json` に永久保存。

---

<a id = "ja_2-8"></a>
### 2-8. 「IO / Settings」タブ（設定・バックアップ管理）

![IO_tab](images/io_tab_20260823.jpg)

全データの保全とメンテナンスを一括で行う管理センターです。

* **7項目の個別バックアップ & リストア:** Positive Presets / Negative Stock / Negative Presets / LoRA Base Data / LoRA Presets / Favorites / Mobile Memo をチェックボックスで個別指定可能。
* **マージ（追加）と上書きの選択:** 既存設定を活かしたまま追加合流させるか、完全に置き換えるかを選択可能。
* **⚠️ NUKE! (All Reset):** 全設定、プリセット、UIフィールドを完全初期化（工場出荷状態に戻す）。

---

<a id = "ja_3"></a>
## 3. モバイル版HTML ＆ ブックマークレット

![Mobile_html](images/mobile_20260823.jpg)

* **`KENZEN_Mobile.html`:** `KENZEN_Mobile` フォルダに同梱。スマホのブラウザで開くことで、外出先でもFavoritesの閲覧や新規メモの作成が可能です。
* **`KENZEN_GetURL_BM.txt` (ブックマークレット):** スマホでSeaArtのLoRAページを閲覧中に起動すると、そのLoRAのハッシュ値を瞬時に抽出・コピーできます。

---

<a id = "ja_4"></a>
## 4. 免責事項・連絡先

* **免責事項:** 生成結果はAIモデルおよび設定に依存します。本ツールの使用によるいかなる損害についても、作者は責任を負いかねます。
* **検証モデル:** [REED XXX illustrious SDXL V15.0](https://civitai.red/models/1717562/reedxxxillustrioussdxl) 
* **作者:** 不二川巴人（ふじかわ ともひと / 「でぇすて」あるいは「不二川“でぇすて”巴人」 / 元商業エロゲーシナリオライター）
* **連絡先・ブログ:** [dsblog.biz](https://dsblog.biz/)
* **開発支援（投げ銭）:** [PayPal Donation](https://paypal.me/dst0508)
* **商業制作例:** 本ツールを使用して制作した成人向けCG集を [itch.io](https://dst-fujikawa.itch.io) にて公開中。


<a id = "ja_5"></a>
## 5. ライセンス

KENZEN SeaArt Helper のソースコードには MIT License が適用されます。

ただし、`tags.db` およびその内容には MIT License は適用されません。
`tags.db` には別途独自ライセンスが適用されます。

詳細は [LICENSE-DATA.md](LICENSE-DATA.md) をご確認ください。

<a id = "ja_6"></a>
## 6. トラブルシューティング & FAQ

### セキュリティソフトや Windows SmartScreen による警告について（誤検知への対応）

本アプリのダウンロード時や起動時に、セキュリティソフト（ESET、Avastなど）や Windows SmartScreen から「疑わしいファイル」「認識されないアプリ」として警告が表示されたり、ファイルが隔離される場合があります。

**これらはすべて誤検知（False Positive）によるものです。**  
本ソフトウェアは Python (PyInstaller) を用いてビルド・パッケージングされており、高額な市販コードサイニング証明書を使用していないため、一部のセキュリティソフトの推測検知（ヒューリスティック機能）によって「未知の新規バイナリ」として機械的にフラグ付けされることがあります。

* **デジタル署名の付与:** 公式配布バイナリには、すべて開発者によるデジタル署名を適用しています。
* **安全性の検証:** 各バージョンは公開前に必ず VirusTotal にてスキャンを実施し、公式な SHA-256 チェックサムを公開しています。スキャン結果の詳細やハッシュ値については、各バージョンの [Releases ページ](https://github.com/tmhtdst0508-ux/KENZEN-SeaArt-Helper/releases) をご確認ください。
* **対処方法:** ファイルがブロックされたり隔離された場合は、セキュリティソフトの検出除外（ホワイトリスト）に登録するか、Windows SmartScreen の「詳細情報」をクリックして「実行」を選択してください。


**さあ、進化した独立コックピットで、良きKENZENなるAIライフを！😊**

![FLAG_COUNTER](https://s01.flagcounter.com/count2/rmpG/bg_FFFFFF/txt_000000/border_CCCCCC/columns_3/maxflags_12/viewers_0/labels_1/pageviews_1/flags_0/percent_0/)
