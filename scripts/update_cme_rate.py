import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.request import Request, urlopen

URL = 'https://www.cme.sr/Home/GetTodaysExchangeRates/?BusinessDate=2016-07-25'

def build_rate(rows, now):
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError('Unexpected CME response')
    row = rows[0]
    rate = Decimal(str(row['SaleUsdExchangeRate']))
    date = datetime.strptime(row['BusinessDate'], '%d-%b-%Y').date()
    age = (now.date() - date).days
    if not rate.is_finite() or not 1 <= rate <= 1000 or not 0 <= age <= 3:
        raise ValueError('Invalid or outdated CME selling rate')
    return {
        'source': 'https://www.cme.sr/',
        'rate_type': 'USD cash selling rate',
        'base_rate': float(rate),
        'markup_srd_per_usd': 1.25,
        'shop_rate': float(rate + Decimal('1.25')),
        'source_date': date.isoformat(),
        'fetched_at': now.isoformat(),
    }

def main():
    req = Request(URL, data=b'', headers={'Content-Type': 'application/json', 'User-Agent': 'BitwiseMSP-rate-updater/1.0'})
    with urlopen(req, timeout=30) as response:
        rows = json.load(response)
    result = build_rate(rows, datetime.now(timezone.utc))
    path = Path('data/cme-rate.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('CME selling rate:', result['base_rate'], 'Shop rate:', result['shop_rate'])

if __name__ == '__main__':
    main()
