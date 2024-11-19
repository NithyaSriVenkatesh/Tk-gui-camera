import asyncio
import websockets

connected = set()

async def server(websocket, path):
    connected.add(websocket)
    print(f"Received connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            for conn in connected:
                if conn != websocket:
                    await conn.send(message)
    finally:
        connected.remove(websocket)

start_server = websockets.serve(server, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

