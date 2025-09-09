import json
import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pp7_api import stage, timer, sse_clients, dispatcher

# Charger config
with open('info.json', 'r') as config_file:
    config = json.load(config_file)
    host = config["host"]
    port = int(config["port"])

# Init objets
stage = stage.Stage(host, port)
timer = timer.Timer(host, port)

clients = []

def make_stream(filtre_type: str):
    async def event_stream():
        client = {"filtre": filtre_type}
        clients.append(client)
        last_timer = 0
        try:
            while True:
                data = dispatcher.ready_data.get(filtre_type)
                if data:
                    current_timer = data.get("timer/system_time")
                    if current_timer == last_timer:
                        # heartbeat pour garder la connexion ouverte
                        yield ": ping\n\n"
                    else:
                        yield f"data: {json.dumps(data)}\n\n"
                        last_timer = current_timer
                await asyncio.sleep(0.01)
        except GeneratorExit:
            if client in clients:
                clients.remove(client)
        except Exception as e:
            print("Erreur dans event_stream:", e)
            if client in clients:
                clients.remove(client)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=500)

@app.put("/api/stage/msg")
async def stage_send_msg(request: Request):
    data = await request.json()
    msg = data.get("user_input")
    print(msg)
    result = stage.send_msg(msg)
    return {"result": result}

@app.delete("/api/stage/msg")
async def stage_delete_msg():
    result = stage.delete_msg()
    return {"result": result}

@app.get("/api/timer/play/{uuid}")
async def play_timer(uuid: str):
    result = timer.play(uuid)
    return {"result": result}

@app.get("/api/timer/pause/{uuid}")
async def pause_timer(uuid: str):
    result = timer.pause(uuid)
    return {"result": result}

@app.get("/api/timer/reset/{uuid}")
async def reset_timer(uuid: str):
    result = timer.reset(uuid)
    return {"result": result}

@app.delete("/api/timer/{uuid}")
async def delete_timer(uuid: str):
    result = timer.delete(uuid)
    return {"result": result}

@app.put("/api/timer/{uuid}")
async def modify_timer(uuid: str):
    result = timer.modify(uuid)
    return {"result": result}

@app.post("/api/timer")
async def post_timer(request: Request):
    data = await request.json()
    result = timer.post(data)
    return {"result": result}

@app.get("/api/prompt")
async def prompt_stream():
    return make_stream("prompt")

@app.get("/api/sub")
async def sub_stream():
    return make_stream("sub")

@app.get("/api/status")
async def status_stream():
    return make_stream("status")

# --- Static files / pages ---

PUBLIC_DIR = os.path.join(os.getcwd(), "public")
app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="public")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(PUBLIC_DIR, "index.html"), headers={"Cache-Control": "public, max-age=604800"})

@app.get("/subtitles")
async def serve_sub():
    print("là ?")
    return FileResponse(os.path.join(PUBLIC_DIR, "subtitles.html"), headers={"Cache-Control": "public, max-age=604800"})

@app.get("/prompt")
async def serve_prompt():
    return FileResponse(os.path.join(PUBLIC_DIR, "prompteur.html"), headers={"Cache-Control": "public, max-age=604800"})

@app.get("/{path:path}")
async def serve_static(path: str):
    return FileResponse(os.path.join(PUBLIC_DIR, path), headers={"Cache-Control": "public, max-age=604800"})

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc):
    return {"message": "Bad request"}

@app.on_event("startup")
async def startup_event():
    print("startup lancé")
    sse_clients.start_api_stream(host, port)
    dispatcher.start_dispatcher()
