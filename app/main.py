from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from app.model_utils import run_prediction
from app.data_store import shared_state
from app.dash_layout import create_dash_app
from threading import Thread
from fastapi.staticfiles import StaticFiles
import uvicorn
import socket
import json

app = FastAPI()

# Allow cross-origin
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return HTMLResponse("<h3>✅ FastAPI backend is running.</h3>")

@app.get("/run-forecast")
def run_forecast(date: str = Query(...)):
    # You can simulate starting a TCP listener OR just confirm start
    return JSONResponse(content={"status": "success", "date": date})

# Launch Dash on background thread
Thread(target=lambda: create_dash_app(shared_state), daemon=True).start()

# Socket server that continuously receives and predicts
def socket_listener():
    HOST, PORT = '0.0.0.0', 65432
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()

    try:
        while True:
            data = conn.recv(8192)
            if not data:
                break
            message = json.loads(data.decode())
            run_prediction(message['features'], message['actual'], message['selected_date'], shared_state)
    finally:
        conn.close()
        s.close()

Thread(target=socket_listener, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
