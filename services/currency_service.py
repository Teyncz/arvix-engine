from database.crud import get_last_entry_by_code


def convert_currency(base_currency: str, target_currency: str, amount: float) -> dict:

    data = {
        "base_currency": base_currency,
        "target_currency": target_currency,
        "input_amount": amount,
        "converted_amount": 0.0,
        "exchange_rate": 0.0,
        "last_update": None
    }

    if base_currency == "EUR":
        last_base_entry = get_last_entry_by_code(f"EUR{target_currency}")

        exchange_rate = float(last_base_entry['price_close']) if isinstance(last_base_entry, dict) and 'price_close' in last_base_entry else float(last_base_entry)
        last_update = last_base_entry['datetime'] if isinstance(last_base_entry, dict) and 'datetime' in last_base_entry else None

        data ["converted_amount"] = round(exchange_rate * amount, 2)
        data ["exchange_rate"] = exchange_rate
        data ["last_update"] = last_update

        return data

    elif target_currency == "EUR":
        last_target_entry = get_last_entry_by_code(f"EUR{base_currency}")

        exchange_rate = 1 / float(last_target_entry['price_close']) if isinstance(last_target_entry, dict) and 'price_close' in last_target_entry else float(last_target_entry)
        last_update = last_target_entry['datetime'] if isinstance(last_target_entry,dict) and 'datetime' in last_target_entry else None

        data ["converted_amount"] = round(exchange_rate * amount, 2)
        data ["exchange_rate"] = exchange_rate
        data ["last_update"] = last_update

        return data

    else:
        last_base_entry = get_last_entry_by_code(f"EUR{base_currency}")
        last_target_entry = get_last_entry_by_code(f"EUR{target_currency}")

        target_exchange_rate = float(last_target_entry['price_close']) if isinstance(last_target_entry, dict) and 'price_close' in last_target_entry else float(last_target_entry)
        base_exchange_rate = float(last_base_entry['price_close']) if isinstance(last_base_entry, dict) and 'price_close' in last_base_entry else float(last_base_entry)
        exchange_rate = target_exchange_rate / base_exchange_rate

        target_last_update = last_target_entry['datetime'] if isinstance(last_target_entry,dict) and 'datetime' in last_target_entry else None
        base_last_update = last_base_entry['datetime'] if isinstance(last_base_entry,dict) and 'datetime' in last_base_entry else None

        oldest_update = min(target_last_update, base_last_update)

        data ["converted_amount"] = round(exchange_rate * amount, 2)
        data ["exchange_rate"] = round(exchange_rate, 5)
        data ["last_update"] = oldest_update

        return data

