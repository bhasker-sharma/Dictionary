from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import pandas as pd
import os

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

OXFORD_API_ENDPOINT = 'https://od-api-sandbox.oxforddictionaries.com/api/v2/entries/en-gb/'
APP_ID = 'b0055a25'
APP_KEY = '01cb81621c34d84d37b3852da0be33d6'

CSV_FILE = 'words.csv'
if not os.path.isfile(CSV_FILE):
    df = pd.DataFrame(columns=['Sr.No', 'Word', 'Meaning'])
    df.to_csv(CSV_FILE, index=False)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, word: str = Form(...)):
    headers = {
        'app_id': APP_ID,
        'app_key': APP_KEY
    }
    response = requests.get(OXFORD_API_ENDPOINT + word.lower(), headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            meaning = data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['definitions'][0]
        except (KeyError, IndexError):
            return templates.TemplateResponse("index.html", {"request": request, "error": "Meaning not found."})

        # Read current CSV
        df = pd.read_csv(CSV_FILE)
        new_row = pd.Series([len(df) + 1, word, meaning], index=df.columns)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        return templates.TemplateResponse("index.html", {"request": request, "word": word, "meaning": meaning})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Word not found."})
