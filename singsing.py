import aiohttp
import asyncio
import json
import sys
from colorama import init, Fore, Style
import os

# Initialize colorama
init(autoreset=True)

# Define colors for printing
red = Fore.LIGHTRED_EX
blue = Fore.LIGHTBLUE_EX
green = Fore.LIGHTGREEN_EX
yellow = Fore.LIGHTYELLOW_EX
black = Fore.LIGHTBLACK_EX
white = Fore.LIGHTWHITE_EX
reset = Style.RESET_ALL
magenta = Fore.LIGHTMAGENTA_EX

async def auth(session, account):
    url = "https://miniapp-api.singsing.net/v2/auth"
    payload = json.dumps({})
    headers = {
        'x-tg-data': f'{account}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0'
    }

    async with session.post(url, headers=headers, data=payload) as response:
        response_data = await response.json()
        access_token = response_data.get("data", {}).get("access_token")
        username = response_data.get("data", {}).get("user", {}).get("first_name")
        return access_token, username

async def daily_login(session, access_token):
    url = "https://miniapp-api.singsing.net/mission/achievement?"
    headers = {
        'authorization': f'Bearer {access_token}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    }
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def claim_offline_profit(session, access_token):
    url = "https://miniapp-api.singsing.net/game/user/claim-offline-profit"
    payload = json.dumps({"boost": False})
    headers = {
        'authorization': f'Bearer {access_token}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    }

    async with session.post(url, headers=headers, data=payload) as response:
        response_data = await response.json()
        profit = response_data.get("data", {}).get("profit")
        money = response_data.get("data", {}).get("user", {}).get("money")
        token = response_data.get("data", {}).get("user", {}).get("token")
        return profit, money, token

async def get_task(session, access_token):
    url = "https://miniapp-api.singsing.net/mission?group=main"
    headers = {
        'authorization': f'Bearer {access_token}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    }
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def solved_task(session, access_token, key):
    url = "https://miniapp-api.singsing.net/mission/check"
    payload = json.dumps({"mission_key": key})
    headers = {
        'authorization': f'Bearer {access_token}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    }

    async with session.post(url, headers=headers, data=payload) as response:
        return await response.json()

async def claim_daily(session, access_token, log_id):
    url = "https://miniapp-api.singsing.net/mission/achievement/claim"
    payload = json.dumps({"log_id": log_id})
    headers = {
        'authorization': f'Bearer {access_token}',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    }
    async with session.post(url, headers=headers, data=payload) as response:
        return await response.json()

def load_accounts(file_path):
    """Load the list of accounts from a file and return it as a list."""
    try:
        with open(file_path, 'r') as f:
            query = [line.strip() for line in f if line.strip()]
        return query , len(query)
    except FileNotFoundError:
        print(f"{red}Error: File '{file_path}' not found.{reset}")
        sys.exit(1)

async def main():
    init(autoreset=True)
    width = 45
    file_path = 'query.txt'
    accounts,total_accounts = load_accounts(file_path)

    if not accounts:
        print(f"{red}No accounts found in the file.{reset}")
        sys.exit(1)
    os.system('cls' if os.name == 'nt' else 'clear')

    ascii_art_lines = [
    "┏┓┳┳┓┏┓┏┓┳┳┓┏┓",
    "┗┓┃┃┃┃┓┗┓┃┃┃┃┓",
    "┗┛┻┛┗┗┛┗┛┻┛┗┗┛"
    ]

    banner = f"""
    {magenta}┏┓┳┳┓┏┓┏┓┳┳┓┏┓  {white}SingSing Auto Claim
    {magenta}┗┓┃┃┃┃┓┗┓┃┃┃┃┓  {green}Author : {white}MortyID
    {magenta}┗┛┻┛┗┗┛┗┛┻┛┗┗┛  {white}Github : {green}https://github.com/MortyID
    """
    print(banner)
    async with aiohttp.ClientSession() as session:
        for index, account in enumerate(accounts):
            access_token, username = await auth(session, account)
            print(f"=============== {green}{index + 1}/{total_accounts} | {username}{reset} ===============")
            
            profit, money, token = await claim_offline_profit(session, access_token)
            print(f"{green}Successfully claimed offline profit: {profit}{reset} 💸")
            await asyncio.sleep(1)
            print(f"{green}Total money accounts: {money} 💸{reset}")
            await asyncio.sleep(1)
            print(f"{green}Total token earned: {token} 🎤{reset}")
            await asyncio.sleep(1)

            response_data = await get_task(session, access_token)
            daily = await daily_login(session, access_token)

            for item in daily['data']['check_in']['data']:
                signin = item.get('state')
                if signin == "claimed":
                    log_id = item.get('log_id')
                    claimdaily = await claim_daily(session, access_token, log_id)
                    if claimdaily.get('success') is False:
                        message = claimdaily['error']['message']
                        print(f"{red}Status: {message} {reset}")
                        await asyncio.sleep(1)
                    else:
                        message = claimdaily['message']
                        print(f"{green}Status: {message} {reset}")
                        await asyncio.sleep(1)

            for item in response_data['data']:
                key = item.get('key')
                completed = item.get('completed')
                description = item.get('description')
                if not completed:
                    solvedtask = await solved_task(session, access_token, key)
                    result = solvedtask['data'].get('completed')
                    if result:
                        print(f"{green}Successfully solved task: {description}{reset}")
                        await asyncio.sleep(1)
                    else:
                        print(f"{red}Failed to solve task: {description}{reset}")
                        await asyncio.sleep(1)

if __name__ == "__main__":
    while True:
        asyncio.run(main())
