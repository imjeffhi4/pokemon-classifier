from transformers import ViTForImageClassification, ViTFeatureExtractor
from fastapi import FastAPI, Request
import json
from PIL import Image
import re
from pydantic import BaseModel
import torch
import requests
import logging
from fastapi.middleware.cors import CORSMiddleware
import base64
from io import BytesIO
from starlette.responses import FileResponse 
from fastapi.staticfiles import StaticFiles
logging.getLogger('transformers').setLevel(logging.CRITICAL)

app = FastAPI()
app.mount("/public", StaticFiles(directory="public"), name="public")
origins = [
    "http://localhost:8000",
    "http://127.0.0.1::8000",
    "https://main-pokemon-classifier-imjeffhi4.endpoint.ainize.ai"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = ViTForImageClassification.from_pretrained( "./PokemonModel").to(device)
feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224') # resizes and normalizes 

with open('pokemon_data.json', 'r', encoding='utf-8') as r:
    pokedex = json.load(r)

class ImageInput(BaseModel):
    img_url: str

@app.get("/")
async def read_index():
    """Returns Built Svelte file"""
    return FileResponse('public/index.html')  # change to this

def get_pillow_image(data):
    """Takes either img url or base64 string and converts to PIL format"""
    if re.search('^http', data):
        img = Image.open(requests.get(data, stream=True).raw).convert("RGB")
    else:
        image_data = re.sub('^data:image/.+;base64,', '', data)
        img = Image.open(BytesIO(base64.b64decode(image_data))).convert("RGB")
    return img

@app.post('/classify/')
async def get_pokemon_image(x: Request):
    """Calls VIT model and returns Name, SVG, and default img_url"""
    user_input = await x.json()
    data = user_input['poke_image']
    img = get_pillow_image(data)
    extracted = feature_extractor(images=img, return_tensors='pt').to(device)
    predicted_id = model(**extracted).logits.argmax(-1).item()
    predicted_pokemon = model.config.id2label[predicted_id]
    predicted_id = predicted_id + 1
    if predicted_id<=649:
        with open(f"./images/{predicted_id}_0.png", 'rb') as r:
            output_string = "data:image/png;base64,".encode() + base64.b64encode(r.read())
    else:
        output_string = None
    default_url = pokedex[str(predicted_id)]['Image URL']
    return {"Name": predicted_pokemon, "Display": output_string, "Default": default_url}

