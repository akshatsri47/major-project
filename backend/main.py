import argparse
import json
import logging
import uuid
import os

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

logger = logging.getLogger("pc")

ROOT = os.path.dirname(__file__)

# rooms = { room_id: { "pc": RTCPeerConnection, "audio": MediaStreamTrack } }
rooms = {}


# ------------------------
# Static files
# ------------------------

async def index(request):
    return web.FileResponse(os.path.join(ROOT, "index.html"))


async def javascript(request):
    return web.FileResponse(os.path.join(ROOT, "client.js"))


async def call_page(request):
    return web.FileResponse(os.path.join(ROOT, "index.html"))


# ------------------------
# WebRTC signaling
# ------------------------

async def offer(request):
    params = await request.json()
    room_id = params.get("room")

    if not room_id:
        return web.json_response({"error": "Missing room ID"}, status=400)

    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = f"PeerConnection({uuid.uuid4()})"

    logger.info("%s Created for room %s", pc_id, room_id)

    if room_id not in rooms:
        rooms[room_id] = {"pc": None, "audio": None}

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("%s State: %s", pc_id, pc.connectionState)

        if pc.connectionState in ("failed", "closed", "disconnected"):
            room = rooms.get(room_id)
            if room and room["pc"] == pc:
                rooms[room_id] = {"pc": None, "audio": None}
            await pc.close()

    @pc.on("track")
    def on_track(track):
        logger.info("%s Track received: %s", pc_id, track.kind)

        if track.kind != "audio":
            return

        room = rooms[room_id]

        # If someone is already waiting in this room
        if room["pc"] and room["audio"]:
            logger.info("🔗 Connecting callers in room %s", room_id)

            # Send each other's audio
            pc.addTrack(room["audio"])
            room["pc"].addTrack(track)

            # Clear room lobby
            rooms[room_id] = {"pc": None, "audio": None}
        else:
            logger.info("⏳ Caller waiting in room %s", room_id)
            rooms[room_id] = {"pc": pc, "audio": track}

    # SDP handshake
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response(
        {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
    )


# ------------------------
# Main
# ------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Room-based 1-to-1 WebRTC audio relay")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app = web.Application()

    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_get("/call/{room}", call_page)
    app.router.add_post("/offer", offer)

    web.run_app(app, host=args.host, port=args.port)
