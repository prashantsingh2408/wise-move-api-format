# Wise Move APIs

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