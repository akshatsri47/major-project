import argparse
import asyncio
import logging
import uuid

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

logger = logging.getLogger("pc")

# rooms = { room_id: { "pc1": RTCPeerConnection, "pc2": RTCPeerConnection, "track1": MediaStreamTrack, "track2": MediaStreamTrack } }
rooms = {}


# ------------------------
# CORS middleware
# ------------------------

@web.middleware
async def cors_middleware(request, handler):
    # Preflight support
    if request.method == "OPTIONS":
        return web.Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# ------------------------
# WebRTC signaling API
# ------------------------

async def offer(request):
    try:
        params = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    room_id = params.get("room")
    sdp = params.get("sdp")
    sdp_type = params.get("type")

    if not room_id or not sdp or not sdp_type:
        return web.json_response(
            {"error": "Missing required fields: room, sdp, type"}, status=400
        )

    offer = RTCSessionDescription(sdp=sdp, type=sdp_type)

    pc = RTCPeerConnection()
    pc_id = f"PeerConnection({uuid.uuid4()})"

    logger.info("%s Created for room %s", pc_id, room_id)

    if room_id not in rooms:
        rooms[room_id] = {"pc1": None, "pc2": None, "track1": None, "track2": None}

    room = rooms[room_id]

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        logger.info("%s State: %s", pc_id, pc.connectionState)

        if pc.connectionState in ("failed", "closed", "disconnected"):
            if room.get("pc1") == pc:
                room["pc1"] = None
                room["track1"] = None
            elif room.get("pc2") == pc:
                room["pc2"] = None
                room["track2"] = None
            await pc.close()

    # Determine if this is the first or second peer in the room
    is_first_peer = room["pc1"] is None
    
    if is_first_peer:
        logger.info("⏳ First caller connecting to room %s", room_id)
        room["pc1"] = pc
    else:
        logger.info("🔗 Second caller connecting to room %s", room_id)
        room["pc2"] = pc


    @pc.on("track")
    def on_track(track):
        logger.info("%s Track received: %s", pc_id, track.kind)

        if track.kind != "audio":
            return

        # Store the track for this peer
        if is_first_peer:
            room["track1"] = track
            logger.info("✅ Received track from first peer in room %s", room_id)
            
            # Forward track1 to peer 2 if peer 2 exists
            if room["pc2"]:
                try:
                    logger.info("🔄 Adding track1 to peer 2")
                    room["pc2"].addTrack(track)
                    logger.info("✅ Successfully added track1 to peer 2")
                except Exception as e:
                    logger.warning("Could not add track1 to peer 2 (may need renegotiation): %s", e)
        else:
            room["track2"] = track
            logger.info("✅ Received track from second peer in room %s", room_id)
            
            # Forward track2 to peer 1 if peer 1 exists
            if room["pc1"]:
                try:
                    logger.info("🔄 Adding track2 to peer 1")
                    room["pc1"].addTrack(track)
                    logger.info("✅ Successfully added track2 to peer 1")
                except Exception as e:
                    logger.warning("Could not add track2 to peer 1 (may need renegotiation): %s", e)

    # SDP handshake - set remote description first
    await pc.setRemoteDescription(offer)
    
    # If this is the second peer and we already have track1, add it BEFORE creating answer
    # This is critical - tracks must be added before setLocalDescription
    if not is_first_peer and room["track1"]:
        try:
            logger.info("🔄 Adding existing track1 to peer 2 BEFORE creating answer")
            pc.addTrack(room["track1"])
        except Exception as e:
            logger.error("Error adding track1 to peer 2: %s", e)
    
    # Create and set local description (answer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.json_response(
        {
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type,
        }
    )


# ------------------------
# Main
# ------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebRTC Signaling API (Room-based 1-to-1)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    app = web.Application(middlewares=[cors_middleware])
    app.router.add_post("/offer", offer)

    web.run_app(app, host=args.host, port=args.port)
