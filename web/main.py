from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json, os

app = FastAPI()

app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

DATA_FILE = "data/drops.json"


def load_drops():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_drops(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.get("/admin")
def admin_panel(request: Request):
    drops = load_drops()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "drops": drops}
    )


@app.post("/update")
def update_drop(
    key: str = Form(...),
    title: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
):
    drops = load_drops()

    drops[key]["title"] = title
    drops[key]["price"] = price
    drops[key]["description"] = description

    save_drops(drops)
    return RedirectResponse("/admin", status_code=303)
