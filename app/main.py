from fastapi import FastAPI
from core.lora import LoraDriver, LoraPins
from core.lora.protocol import DataPacket

app = FastAPI()

pins = LoraPins(m0=17, m1=27, aux=22)
lora_driver = LoraDriver(port="/dev/ttyS0", baudrate=9600, pins=...)  # specify appropriate pins

@app.get("/")
async def read_root():
    packet = lora_driver.receive()
    return packet