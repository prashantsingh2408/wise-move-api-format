# Wise Move APIs

## Other repos
- [wise-move-landing-page](https://github.com/prashantsingh2408/wise-move-landing-page)
- [chat-app-ui](https://github.com/prashantsingh2408/chat-app-ui)
- [chat-app-wise-move-api](https://github.com/prashantsingh2408/chat-app-wise-move-api)

[prompt](PROMPT.md)

# Setup
## Create a virtual environment
    python -m venv venv
## Activate the virtual environment
## Windows
    venv\Scripts\activate
## macOS/Linux
    source venv/bin/activate

## Install required packages
    pip install -r requirements.txt

## Install Chromium and ChromeDriver (for Ubuntu)
    sudo apt-get install    chromium-browser chromium-chromedriver

## Run the FastAPI application
    uvicorn main:app --reload
    OR
    python -m uvicorn main:app --reload
