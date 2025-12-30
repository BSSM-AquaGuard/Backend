from fastapi import APIRouter, Request, HTTPException
import asyncio
from typing import List

from core.lora.protocol import DataPacket
from app.cache import packet_to_dict

router = APIRouter(prefix="/submodules", tags=["submodules"])


@router.get("/", summary="List cached latest values")
async def list_cached(request: Request):
    cache = request.app.state.cache
    items = cache.all()
    return [packet_to_dict(p) for p in items.values()]


@router.get("/{sub_id}", summary="Get latest value for a submodule by id")
async def get_latest(sub_id: int, request: Request):
    driver = request.app.state.lora_driver
    cache = request.app.state.cache

    loop = asyncio.get_event_loop()
    try:
        packet = await loop.run_in_executor(None, driver.receive)
    except Exception:
        packet = None

    if packet is not None:
        # update cache with received packet
        try:
            cache.set(packet.id, packet)
        except Exception:
            pass
        # if the packet matches requested id, return it
        if packet.id == sub_id:
            return packet_to_dict(packet)

    # fallback to cache
    cached = cache.get(sub_id)
    if cached is not None:
        return packet_to_dict(cached)

    raise HTTPException(status_code=404, detail="No data for requested submodule")
