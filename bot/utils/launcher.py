import os
import glob
import argparse
import sys

import requests

from pyrogram import Client
from better_proxy import Proxy

from bot.config import settings
from bot.utils import logger
from bot.core.tapper import run_tapper_no_thread
from bot.core.query import run_tapper_no_thread_query
from bot.core.registrator import register_sessions

import importlib.util

curr_version = "3.0.5"

version = requests.get("https://raw.githubusercontent.com/vanhbakaa/moonbix-bot/refs/heads/main/version")
version_ = version.text.strip()
if curr_version == version_:
    logger.info("<cyan>Your version is up to date!</cyan>")
else:
    logger.warning(f"<yellow>New version detected {version_} please update the bot!</yellow>")
    sys.exit()
start_text = f"""

Version: {curr_version} 


Select an action:
 __ __  ___  ___  _ _  ___  _ __  _  MONBIX AUTO TASK AND PLAY GAME BOT
|  \  \| . || . || \ || . >| |\ \/   Author : D4rkCipherX
|     || | || | ||   || . \| | \ \   YouTube :https://youtube.com/@d4rkcipherx
|_|_|_|`___'`___'|_\_||___/|_|_/\_\  Note : MUST SUBSCRIBE MY YOUTUBE CHANNEL

    1. Run clicker (session)
    2. Create session
    3. Run clicker (Query)
"""

global tg_clients

def get_session_names() -> list[str]:
    session_names = sorted(glob.glob("sessions/*.session"))
    session_names = [
        os.path.splitext(os.path.basename(file))[0] for file in session_names
    ]

    return session_names


def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open(file="bot/config/proxies.txt", encoding="utf-8-sig") as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def get_tg_clients() -> list[Client]:
    global tg_clients

    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [
        Client(
            name=session_name,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir="sessions/",
            plugins=dict(root="bot/plugins"),
        )
        for session_name in session_names
    ]

    return tg_clients


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")

    action = parser.parse_args().action

    if not action:

        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ["1", "2", "3"]:
                logger.warning("Action must be 1, 2, 3 or 4")
            else:
                action = int(action)
                break

    if action == 2:
        await register_sessions()
    elif action == 1:
        tg_clients = await get_tg_clients()
        proxies = get_proxies()
        await run_tapper_no_thread(tg_clients=tg_clients, proxies=proxies)

    elif action == 3:
        with open("data.txt", "r") as f:
            query_ids = [line.strip() for line in f.readlines()]
        proxies = get_proxies()
        await run_tapper_no_thread_query(query_ids, proxies)


