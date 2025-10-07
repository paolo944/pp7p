import json
import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pp7_api import sse_clients, dispatcher
from contextlib import asynccontextmanager
import uvicorn
import socket

with open("info.json", "r") as config_file:
    config = json.load(config_file)
    host = config["host"]
    port = int(config["port"])

def get_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

queues = asyncio.Queue()

def make_stream():
    async def event_stream():
        try:
            while True:
                data = await queues.get()
                yield f"data: {json.dumps(data)}\n\n"
        except asyncio.CancelledError:
            print("Stream fermé")

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting...")

    loop = asyncio.get_running_loop()
    sse_clients.start_api_stream(host, port)
    dispatcher.start_dispatcher(queues, loop)

    yield
    print("App shutting down")

app = FastAPI(lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=500)

@app.get("/api/sub")
async def sub_stream():
    return make_stream()

PUBLIC_DIR = os.path.join(os.getcwd(), "public")
app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="public")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"), headers={"Cache-Control": "public, max-age=604800"})

@app.get("/{path:path}")
async def serve_static(path: str):
    return FileResponse(os.path.join(PUBLIC_DIR, path), headers={"Cache-Control": "public, max-age=604800"})

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):
    return {"message": "Bad request"}

if __name__ == "__main__":
    ip = get_ip_local()
    print(f"IP locale: {ip}")
    uvicorn.run("main:app", port=60000, workers=1)
