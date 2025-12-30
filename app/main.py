from fastapi import FastAPI
from core.lora.driver import LoraDriver
from core.lora.pins import LoRaPins
from app.cache import SimpleCache

from app.routes.submodule import router as submodule_router

app = FastAPI()

# configure pins and driver (adjust pins/port as needed)
pins = LoRaPins(m0=17, m1=27, aux=22)
lora_driver = LoraDriver(port="/dev/ttyS0", baudrate=9600, pins=pins)

# attach shared objects to app state
app.state.lora_driver = lora_driver
app.state.cache = SimpleCache(ttl=300)

app.include_router(submodule_router)

@app.get("/healthz")
async def health():
    return {"status": "ok"}