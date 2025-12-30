from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from core.lora.driver import LoraDriver
from core.lora.pins import LoRaPins
from core.lora.exceptions import AuxTimeoutError
from core.lora.protocol import DataPacket

lora_driver: LoraDriver | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global lora_driver
    try:
        pins = LoRaPins(m0=17, m1=27, aux=22)
        lora_driver = LoraDriver(
            port="/dev/ttyS0",
            baudrate=9600,
            pins=pins
        )
        print("✅ LoRa initialized")
        yield
    except AuxTimeoutError as e:
        print(f"⚠️ LoRa init failed: {e}")
        lora_driver = None
        yield
    finally:
        if lora_driver:
            lora_driver.shutdown()
        print("🛑 LoRa shutdown")


app = FastAPI(lifespan=lifespan)


def get_latest_packet() -> DataPacket:
    if lora_driver is None:
        raise HTTPException(status_code=503, detail="LoRa not ready")

    packet = lora_driver.latest()
    if packet is None:
        raise HTTPException(status_code=404, detail="No LoRa data")

    return packet


# ----------------------
# API Endpoints
# ----------------------

@app.get("/")
async def read_all():
    """
    최신 LoRa 패킷 전체 반환
    """
    packet = get_latest_packet()
    return {
        "ph": packet.ph,
        "temperature": packet.temperature,
        "turbidity": packet.turbidity,
        "timestamp": packet.timestamp
    }


@app.get("/api/temperature")
async def get_temperature():
    packet = get_latest_packet()
    return {"temperature": packet.temperature}


@app.get("/api/ph")
async def get_ph():
    packet = get_latest_packet()
    return {"ph": packet.ph}


@app.get("/api/turbidity")
async def get_turbidity():
    packet = get_latest_packet()
    return {"turbidity": packet.turbidity}
