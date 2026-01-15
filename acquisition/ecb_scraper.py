import csv
import asyncio
import aiohttp

base_currency = "EUR"
target_currency = "CAD"

async def get_ecb_data():
    url = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata&startPeriod=2025-12-01"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.text()
                lines = data.splitlines()
                for line in lines[1:]:
                    fields = line.split(',')
                    print(fields[6] + ' - ' + fields[7])



asyncio.run(get_ecb_data())