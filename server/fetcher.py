import platform
from datetime import timedelta, date
import aiohttp
import asyncio
import sys
from concurrent.futures import ProcessPoolExecutor


async def fetch_rates(curr_date):
    """Fetching rates for a specific date"""
    async with aiohttp.ClientSession() as session:
        print(f'fetching rates for day {curr_date} started ...')
        url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={curr_date}'

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    rate_text = await resp.text()
                    print(f'fetching rates for day {curr_date} finished ...')
                    return rate_text
        except (aiohttp.ClientConnectionError, aiohttp.InvalidURL) as err:
            print(f'Connection error: {url}', str(err))

    return None


def run_fetch_rates(curr_date):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(fetch_rates(curr_date))


async def fetch_in_processes(amount_of_days):
    dates = []

    if amount_of_days > 0:
        for day in range(amount_of_days):
            curr_date = (date.today() - timedelta(days=day)
                         ).strftime("%d.%m.%Y")
            dates.append(curr_date)
    else:
        dates.append(
            (date.today() - timedelta(days=amount_of_days)).strftime("%d.%m.%Y"))

    rates = []
    with ProcessPoolExecutor(10) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(
            executor, run_fetch_rates, curr_date) for curr_date in dates]

        for task in asyncio.as_completed(tasks):
            result = await task
            if result:
                rates.append(result)

    return rates

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    amount_of_days = 0 if len(sys.argv) != 2 else int(sys.argv[1])

    print(asyncio.run(fetch_in_processes(amount_of_days)))
