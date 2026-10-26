Nepali OCR + Translate API

Quickstart:

1. Install system dependencies (Tesseract OCR and poppler for Windows).

2. Create a virtualenv and install Python deps:

```bash
python -m venv .venv
.venv\Scripts\activate
 pip install -r requirements.txt
```

3. Create a `.env` file from `.env.example` and set a real translation provider:

```bash
copy .env.example .env
```

Then update the values for your environment, for example:

```dotenv
LIBRETRANSLATE_URL=https://libretranslate.example.com/translate
OPENAI_API_KEY=your_openai_key_here
```

4. Run the app:

```bash
python main.py
```

Endpoints:
- `POST /extract` - upload `file` (pdf/docx/image). Form field `preeti` to convert Preeti.
- `POST /translate` - form `text` to translate.
- `POST /download` - form `original`, `translated`, `format` (`pdf` or `docx`).

Notes:
- The app loads environment variables from a local `.env` file automatically.
- Translation will only work when a real provider is configured. Public generic endpoints often rate-limit or block requests without an API key.
 
Windows prerequisites:

- Install Tesseract OCR (https://github.com/tesseract-ocr/tesseract). Add its `tesseract.exe` to your PATH or set `TESSERACT_CMD`.
- Install Poppler (for `pdf2image`) and add it to PATH, or set `POPPLER_PATH` in `.env`.
- For Nepali OCR, download `nep.traineddata` into a folder and set `TESSDATA_PREFIX` to that folder. For example: `C:\Users\ECS\tessdata`.

Translation providers:

- `LIBRETRANSLATE_URL`: use a self-hosted LibreTranslate instance or a licensed public endpoint.
- `OPENAI_API_KEY`: use an OpenAI-compatible API key for chat-completion translation.
- `GOOGLE_API_KEY`: optional Google Cloud Translation API key.
