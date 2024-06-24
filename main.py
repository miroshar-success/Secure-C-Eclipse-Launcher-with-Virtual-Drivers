import asyncio
import websockets
import os
import subprocess
import time
import logging
import shutil
import win32gui
import ctypes
import ctypes.wintypes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SERVER_URL = "ws://localhost:8765"

VK_C = 0x43
VK_CONTROL = 0x11
VK_SNAPSHOT = 0x2C

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleCtrlHandler(None, True)

def find_eclipse():
    eclipse_path = shutil.which("eclipse")
    if eclipse_path:
        logger.info(f"Eclipse found in: {eclipse_path}")
    else:
        logger.error("Eclipse not found in system PATH.")
    return eclipse_path

async def download_project():
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            await websocket.send("REQUEST_PROJECT")
            project_code = await websocket.recv()
            logger.info("Project code downloaded successfully.")
            return project_code
    except Exception as e:
        logger.error(f"Error downloading project: {e}")
        raise

def create_virtual_drive():
    try:
        subprocess.run(["imdisk", "-a", "-s", "64M", "-m", "Q:"])
        logger.info("Virtual drive created in Q:\\")
        return "Q:\\"
    except Exception as e:
        logger.error(f"Error creating virtual drive: {e}")
        raise

def save_project_to_drive(project_code, drive_path):
    try:
        project_dir = os.path.join(drive_path, "project")
        os.makedirs(project_dir, exist_ok=True)
        with open(os.path.join(project_dir, "project_code.zip"), "wb") as file:
            file.write(project_code)
        logger.info(f"Project code saved in {project_dir}")
    except Exception as e:
        logger.error(f"Error saving project to virtual drive: {e}")
        raise

def launch_eclipse(eclipse_path, project_path):
    try:
        process = subprocess.Popen([eclipse_path, "-data", project_path])
        logger.info("Eclipse launched successfully.")
        return process
    except Exception as e:
        logger.error(f"Error launching Eclipse: {e}")
        raise

def is_eclipse_foreground():
    foreground_window = win32gui.GetForegroundWindow()
    window_text = win32gui.GetWindowText(foreground_window)
    return 'Eclipse' in window_text

def block_copy_and_screenshot():
    while True:
        if is_eclipse_foreground():
            # Bloquear copia
            if user32.GetAsyncKeyState(VK_CONTROL) & 0x8000 and user32.GetAsyncKeyState(VK_C) & 0x8000:
                logger.info("Blocked copy attempt in Eclipse.")
                user32.BlockInput(True)
                time.sleep(0.1)
                user32.BlockInput(False)
            # Bloquear capturas de pantalla
            if user32.GetAsyncKeyState(VK_SNAPSHOT) & 0x8000:
                logger.info("Blocked screenshot attempt in Eclipse.")
                clear_clipboard()
        time.sleep(0.1)

def clear_clipboard():
    user32.OpenClipboard(0)
    user32.EmptyClipboard()
    user32.CloseClipboard()

def monitor_eclipse(process, drive_path):
    try:
        while True:
            if process.poll() is not None:
                logger.info("Eclipse has closed.")
                break
            time.sleep(5)
    except Exception as e:
        logger.error(f"Error when monitoring Eclipse: {e}")
    finally:
        remove_virtual_drive(drive_path)

def remove_virtual_drive(drive_path):
    try:
        subprocess.run(["imdisk", "-d", "-m", drive_path])
        logger.info(f"Virtual drive in {drive_path} unmounted.")
    except Exception as e:
        logger.error(f"Error unmounting virtual drive: {e}")

async def main():
    try:
        eclipse_path = find_eclipse()
        if not eclipse_path:
            raise RuntimeError("Eclipse is not available. Make sure Eclipse is installed and in the system PATH.")
        
        project_code = await download_project()
        drive_path = create_virtual_drive()
        save_project_to_drive(project_code, drive_path)
        eclipse_process = launch_eclipse(eclipse_path, drive_path)
        copy_blocker = asyncio.create_task(asyncio.to_thread(block_copy_and_screenshot))
        monitor_eclipse(eclipse_process, drive_path)
        copy_blocker.cancel()
    except Exception as e:
        logger.critical(f"Critical error in main flow: {e}")

if __name__ == "__main__":
    asyncio.run(main())