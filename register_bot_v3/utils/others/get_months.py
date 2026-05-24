from datetime import date


def get_12_months():
    today = date.today()
    year, month = today.year, today.month

    last_12_months = []
    for _ in range(12):
        last_12_months.append(f"{year}-{month:02d}")
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return last_12_months
