import asyncio
import websockets
import json
from aiortc import RTCPeerConnection, RTCSessionDescription , RTCIceCandidate
import cv2
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("webrtc_receiver")

async def handle_webrtc_connection(websocket):
    pc = RTCPeerConnection()

    @pc.on("track")
    async def on_track(track):
        logger.info(f"Receiving track: {track.kind}")
        if track.kind == "video":
            while True:
                try:
                    frame = await track.recv()
                    if frame is not None:
                        logger.debug("Received a video frame")

                        # Convert WebRTC frame to a NumPy array for OpenCV
                        frame_np = frame.to_ndarray(format="bgr24")
                        if frame_np is not None:
                            cv2.imshow("Screen Sharing", frame_np)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                logger.info("Exiting video display loop")
                                break
                except Exception as e:
                    logger.error(f"Error processing video frame: {e}")
                    break

    try:
        async for message in websocket:
            data = json.loads(message)
            logger.info(f"Received message: {data}")

            if "offer" in data:
                logger.info("Received SDP offer")
                offer = RTCSessionDescription(sdp=data["offer"]["sdp"], type=data["offer"]["type"])
                await pc.setRemoteDescription(offer)
                logger.info("Set remote description")

                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                logger.info("Created and set local SDP answer")

                await websocket.send(json.dumps({
                    "answer": {
                        "sdp": pc.localDescription.sdp,
                        "type": pc.localDescription.type
                    }
                }))
                logger.info("Sent SDP answer")

            if "iceCandidate" in data:
                candidate_data = data["iceCandidate"]
                logger.info(f"Received ICE candidate: {candidate_data}")

                try:
                    # Parse the ICE candidate string
                    candidate_parts = candidate_data["candidate"].split()
                    if len(candidate_parts) >= 8:
                        foundation = candidate_parts[0]
                        component = int(candidate_parts[1])
                        protocol = candidate_parts[2].lower()
                        priority = int(candidate_parts[3])
                        ip = candidate_parts[4]
                        port = int(candidate_parts[5])
                        type = candidate_parts[7]
                        # Construct an RTCIceCandidate object
                        candidate = RTCIceCandidate(
                            foundation=foundation,
                            component=component,
                            protocol=protocol,
                            priority=priority,
                            ip=ip,
                            port=port,
                            type=type,
                            sdpMid=candidate_data.get("sdpMid", "0"),  # Default to "0" if missing
                            sdpMLineIndex=candidate_data.get("sdpMLineIndex", 0)  # Default to 0 if missing
                        )
                        #  pass candidate data  constructing RTCIceCandidate
                        await pc.addIceCandidate(candidate)
                        logger.info("Added ICE candidate successfully")
                    else : 
                        logger.error("Invalid ICE candidate format")

                except Exception as e:
                    logger.error(f"Failed to add ICE candidate: {e}")

    except Exception as e:
        logger.error(f"Error in WebRTC connection handler: {e}")
    finally:
        logger.info("Closing WebRTC peer connection")
        await pc.close()
        cv2.destroyAllWindows()

async def start_webrtc_receiver():
    while True:
        try:
            #note that this ip address is the laptop ip address
            async with websockets.connect("ws://192.168.254.18:8766") as websocket:
                logger.info("Connected to WebSocket server")
                await handle_webrtc_connection(websocket)
        except ConnectionRefusedError:
            logger.error("Unable to connect to the WebSocket server. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    logger.info("Starting WebRTC receiver...")
    asyncio.run(start_webrtc_receiver())
