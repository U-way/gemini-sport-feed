#!/usr/bin/env python3
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, ROUND_CEILING
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

SOURCE_URL = "https://geminisport.ua/price/drop-ru.xml"
OUTPUT = Path("gemini-sport-ru.xml")
ALLOWED_VENDORS = {"gemini", "gemini sport"}
TARGET_MARGIN = Decimal("0.40")

request = urllib.request.Request(
    SOURCE_URL,
    headers={"User-Agent": "Mozilla/5.0 (compatible; GeminiSportFeedFilter/1.0)"}
)
with urllib.request.urlopen(request, timeout=180) as response:
    source_data = response.read()

root = ET.fromstring(source_data)
shop = root.find("shop")
if shop is None:
    raise RuntimeError("The XML has no <shop> element.")
offers = shop.find("offers")
if offers is None:
    raise RuntimeError("The XML has no <offers> element.")

all_offers = offers.findall("offer")
selected = []
for offer in all_offers:
    vendor = (offer.findtext("vendor") or "").strip().casefold()
    if vendor not in ALLOWED_VENDORS:
        continue

    raw_wholesale = (offer.findtext("pricedrop") or "").strip().replace(",", ".")
    try:
        wholesale = Decimal(raw_wholesale)
    except InvalidOperation:
        raise RuntimeError(
            f"Offer {offer.get('id', '(no id)')} has missing/invalid <pricedrop>: {raw_wholesale!r}"
        )
    if wholesale <= 0:
        raise RuntimeError(
            f"Offer {offer.get('id', '(no id)')} has non-positive <pricedrop>: {raw_wholesale!r}"
        )

    # 40% gross margin of retail price means retail = wholesale / 0.60.
    calculated = wholesale / (Decimal("1") - TARGET_MARGIN)
    # Round UP to the next whole price ending in 9 (e.g. 408.33 -> 409; 450 -> 459).
    tens = (calculated / Decimal("10")).to_integral_value(rounding=ROUND_FLOOR)
    retail = tens * Decimal("10") + Decimal("9")
    if retail < calculated:
        retail += Decimal("10")

    price_element = offer.find("price")
    if price_element is None:
        price_element = ET.SubElement(offer, "price")
    price_element.text = str(int(retail))
    selected.append(offer)

if not selected:
    raise RuntimeError("No Gemini / Gemini Sport offers found; refusing to overwrite the published feed.")

for offer in list(offers):
    offers.remove(offer)
for offer in selected:
    offers.append(offer)

xml_body = ET.tostring(root, encoding="utf-8")
content = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<!DOCTYPE yml_catalog SYSTEM "shops.dtd">\n'
    + xml_body
)
OUTPUT.write_bytes(content)

print(
    f"Updated {OUTPUT}: {len(selected)} offers selected from {len(all_offers)}; "
    f"pricedrop converted to retail with 40% margin and upward rounding to ...9; "
    f"{datetime.now(timezone.utc).isoformat()}"
)
