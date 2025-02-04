import asyncio
import subprocess

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from common.environ import Environ

router = APIRouter()

async def stream_pm2_logs(websocket: WebSocket):
    """Asynchronously stream PM2 logs to WebSocket clients."""

    process = await asyncio.create_subprocess_exec(
        "pm2", "logs", f"{Environ.NEURON_TYPE}_server_{Environ.WALLET_HOTKEY}", "--raw",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        while True:
            log_line = await process.stdout.readline()  # Non-blocking read
            if not log_line:
                await asyncio.sleep(0.1)  # Prevent busy waiting
                continue

            await websocket.send_text(log_line.decode().strip())  # Send log line
    except WebSocketDisconnect:
        print("🚪 WebSocket disconnected")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        print("🛑 Stopping PM2 log process")
        process.terminate()  # Ensure subprocess is terminated
        await process.wait()  # Wait for cleanup


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for streaming PM2 logs."""
    await websocket.accept()
    await stream_pm2_logs(websocket)
