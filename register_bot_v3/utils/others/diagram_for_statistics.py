import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from io import BytesIO



def sort_by_day(sql_response):
    result_dict = {}
    for item in sql_response:

        day = item["day"]
        if day not in result_dict:
            result_dict[day] = {"lump_sum": 0, "by_month": 0}
        value = item["price"] if "price" in item.keys() else 1
        if item["client_id"] is None:
            result_dict[day]["lump_sum"] += value
        else:
            result_dict[day]["by_month"] += value
    return result_dict


def create_chart(data, year, month, payments=False):
    labels = []
    lump_sum = []
    by_month = []

    for key, value in data.items():
        labels.append(str(key))
        lump_sum.append(value.get("lump_sum", 0))
        by_month.append(value.get("by_month", 0))

    labels.append("Jami")
    lump_sum.append(sum(lump_sum))
    by_month.append(sum(by_month))

    fig, ax = plt.subplots(figsize=(10, 5))

    bars1 = ax.bar(labels, lump_sum, label="Kunlik")
    bars2 = ax.bar(labels, by_month, bottom=lump_sum, label="Oylik")

    max_value = max([l + b for l, b in zip(lump_sum, by_month)])
    ax.set_ylim(0, max_value * 1.2)
    ax.grid(axis="y", linestyle="-", linewidth=0.8, alpha=0.8)
    # Sonlarni yozish
    for i, bar in enumerate(bars1):
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h / 2,
                str(lump_sum[i]),
                ha="center",
                va="center",
                fontsize=18,
            )

    for i, bar in enumerate(bars2):
        h = bar.get_height()
        if h > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                lump_sum[i] + h / 2,
                str(by_month[i]),
                ha="center",
                va="center",
                fontsize=18,
            )

    ax.set_title(
        f"{year}-yil {month} oyi pul tushumlari"
        if payments
        else f"{year}-yil {month} oyi mijozlar oqimi"
    )
    ax.set_xlabel("Oy kunlari")
    ax.set_ylabel("Pul miqdori" if payments else "Soni")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)

    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight", pad_inches=0.5)
    plt.close(fig)
    buffer.seek(0)
    buffer.name = "pay.png" if payments else "reg.png"

    return buffer
