# EldhoAi

**EldhoAi** is a Windows desktop AI assistant by **REAL_ELDHO**. It combines hosted AI chat with web search, image and document understanding, speech input, and local text-to-speech.

> **Project license:** EldhoAi is not open-source software. The repository is public for viewing, but use and redistribution rights are limited by [`LICENSE`](LICENSE). Do not copy, modify, repackage, or redistribute EldhoAi without the copyright holder's written permission.

## Features

- Streaming AI chat using NVIDIA's OpenAI-compatible API.
- Tavily web search with links to sources.
- Image understanding for PNG, JPG, and JPEG attachments.
- Text and code attachments, PDF text extraction, and Microsoft Word (`.docx`) extraction.
- Voice input using NVIDIA Riva speech recognition and local text-to-speech through `pyttsx3`.
- Persistent chat history, chat rename/delete, edit and regenerate, stop generation, and export to TXT/Markdown.
- Dark/light/system appearance and adjustable AI settings.

## Download and install on Windows

1. Open this repository on GitHub and select **Releases**.
2. Download the official installer asset named `EldhoAi_Setup_1.0.0.exe` from the release. If no release is published yet, the installer is not available for download yet.
3. Run the installer and finish setup. You can create a desktop shortcut if offered.
4. Before launching EldhoAi for the first time, configure your API keys as described in [Configure your API keys](#configure-your-api-keys).
5. Launch EldhoAi from the Start Menu or desktop shortcut.

The installer does **not** include the maintainer's API keys. Each user must configure their own keys and comply with the service providers' terms, limits, and any applicable charges.

## Configure your API keys

EldhoAi uses external services. Internet access is required for AI chat, web search, image analysis, and voice transcription.

### 1. Get an NVIDIA API key

1. Open the [NVIDIA GLM-5.3 Flash model page](https://build.nvidia.com/z-ai/glm-5-3-flash).
2. Sign in or create an NVIDIA account.
3. Follow NVIDIA's **Get API Key** flow and create a key that has access to the models/endpoints you plan to use.
4. Store the key privately. Do not post it in an issue, screenshot, chat, or public repository.

The same `NVIDIA_API_KEY` setting is used for AI chat and NVIDIA-hosted vision/speech calls. Endpoint access may depend on NVIDIA's current catalog, account, and service terms.

### 2. Get a Tavily API key

1. Open [Tavily](https://tavily.com/) and create an account.
2. Find your API key in the Tavily dashboard.
3. Keep it private. The key is only needed for EldhoAi's web-search feature.

### 3. Create the `.env` configuration file

**For the installed Windows app:**

1. Press `Win + R`.
2. Enter `%LOCALAPPDATA%\EldhoAi` and press Enter. If Windows says the folder does not exist yet, create a folder named `EldhoAi` inside `%LOCALAPPDATA%`.
3. Create a new text file in that folder named exactly `.env` (not `.env.txt`). If using Notepad, choose **Save as type: All files** when saving it.
4. Put the following lines into the file and replace the placeholders with your own keys:

   ```env
   NVIDIA_API_KEY=paste_your_own_nvidia_key_here
   TAVILY_API_KEY=paste_your_own_tavily_key_here
   NVIDIA_ASR_FUNCTION_ID=d3fe9151-442b-4204-a70d-5fcc597fd610
   ```

5. Save the file, then launch EldhoAi.

`NVIDIA_ASR_FUNCTION_ID` is optional: the application has a default function ID, and the value above shows that default. If NVIDIA changes the service or the function is unavailable for your account, consult the current voice-transcription instructions before changing it.

**For an authorized source-code run:** copy `.env.example` to `.env` in the repository root, then fill in your own key values. In PowerShell, you can run:

```powershell
Copy-Item .env.example .env
notepad .env
```

Do not share the real `.env` file or commit it to Git. The included `.gitignore` excludes it; `.env.example` is a template containing no API secrets.

## Which AI model should I choose?

Choose the chat model inside **EldhoAi → Settings → AI Model**. The current app offers these options:

| Model in Settings | Best starting point | Why choose it? |
|---|---|---|
| **GLM-5.3 Flash (Recommended)** — `z-ai/glm-5.3-flash` | Most users; everyday questions, writing, explanations, and coding | This is EldhoAi's default. NVIDIA describes the model as an efficiency-focused multimodal model for assistant and agent workloads. Start here for a balanced everyday experience. [Official model card](https://build.nvidia.com/z-ai/glm-5-3-flash/modelcard). |
| **GLM-5.3** — `z-ai/glm-5.3` | Try it for complex coding, multi-step reasoning, and long tasks | NVIDIA describes it for complex coding and long-horizon agentic work. It may respond differently or take longer depending on the prompt and current service load. [Official model card](https://build.nvidia.com/z-ai/glm-5-3/modelcard). |

**Recommendation:** leave **GLM-5.3 Flash (Recommended)** selected unless you have a task that benefits from trying GLM-5.3. Compare both on your own prompts. Availability, latency, rate limits, and any usage charges can change, so check the provider's current model page and terms.

Image attachments currently route through a separate vision model configured by the application (`meta/llama-3.2-11b-vision-instruct`), rather than the text-model selection above. Vision access is also subject to the NVIDIA endpoint's current availability.

**The model is selected in the app's Settings, not in `.env`.** Do not add a `MODEL_NAME` or `ELDHOAI_MODEL` line to `.env` expecting it to change the current selector; the app does not currently read those variables.

## Privacy and local data

- The API keys in your `.env` file are local configuration and must not be included in a public release.
- Conversations, settings, and saved image attachments are stored locally by the application.
- Messages and selected file/image contents are sent to the relevant hosted AI/search services when you use those features.
- When you activate voice input, recorded audio is sent to NVIDIA's hosted speech-recognition service for transcription. Text-to-speech uses a local Windows speech engine.
- Do not attach confidential material unless you are comfortable sending it to the relevant service.
- Back up your conversation data before reinstalling, moving, or uninstalling the app.

## Source setup (maintainer / authorized contributors)

The public repository does not by itself grant permission to modify or redistribute the software. See [`LICENSE`](LICENSE). These steps are for the copyright holder and anyone who has received permission to work on the source.

1. Install 64-bit Python. EldhoAi was packaged with Python 3.14 on Windows; compatibility of other Python versions depends on the installed dependencies.
2. Open a terminal in the project root and create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Create and edit `.env` using the steps above.
4. Run the desktop application:

   ```powershell
   python main.py
   ```

## Build the Windows app (maintainer / authorized contributors)

1. Activate the project's virtual environment.
2. Install build dependencies:

   ```powershell
   pip install -r requirements-build.txt
   ```

3. Keep `main.py`, all Python modules, `EldhoAi.ico`, `rthook_eldhoai.py`, `prepare_portable_data.py`, and `build_eldhoai.bat` together in the project root.
4. Run:

   ```powershell
   .\build_eldhoai.bat
   ```

5. After a successful portable build, open `EldhoAi_Installer.iss` in Inno Setup Compiler and compile it to create the Setup executable. See [`BUILD_WINDOWS.md`](BUILD_WINDOWS.md).

The build output is created under `dist/`; it is intentionally excluded from the Git repository. Publish the compiled installer as a GitHub Release asset, after checking that it contains no personal data or secrets.

## Troubleshooting

- **NVIDIA key error:** check that `.env` is spelled correctly, is saved in the expected location, and contains your own `NVIDIA_API_KEY`.
- **Web search fails:** check `TAVILY_API_KEY` and Tavily's current quota/account status.
- **Vision fails:** verify the NVIDIA key has access to the vision endpoint used by the application.
- **Voice transcription fails:** check Windows microphone privacy permissions, microphone selection, internet access, and access to the configured NVIDIA Riva function.
- **PDF has no extracted text:** scanned PDFs containing only page images may need OCR; OCR is not included.
- **Packaged app fails to start:** inspect `%LOCALAPPDATA%\EldhoAi\logs\startup_error.log` if the diagnostic log exists.
- **Service/model not available:** provider model IDs, access rules, rate limits, and terms can change. Check the linked official model page and retry later if appropriate.

## License and third-party services

See [`LICENSE`](LICENSE). EldhoAi is not published under an OSI-approved open-source license. The included custom license grants only the limited rights stated in the file. Third-party packages and online services remain subject to their own licenses and terms.
