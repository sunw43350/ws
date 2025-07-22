import datetime

def prune_old_data(symbol_exchange_data, retention_minutes):
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=retention_minutes)
    for symbol, exchanges in symbol_exchange_data.items():
        for exchange, data in exchanges.items():
            times = data['times']
            idx = next((i for i, t in enumerate(times) if t >= cutoff), len(times))
            data['times'] = times[idx:]
            data['bid'] = data['bid'][idx:]
            data['ask'] = data['ask'][idx:]
