#!/usr/bin/env python3
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

SOURCE_URL = "https://geminisport.ua/price/drop-ru.xml"
OUTPUT = Path("gemini-sport-ru.xml")
ALLOWED_VENDORS = {"gemini", "gemini sport"}

request = urllib.request.Request(
    SOURCE_URL,
    headers={"User-Agent": "Mozilla/5.0 (compatible; GeminiSportFeedFilter/1.0)"}
)
with urllib.request.urlopen(request, timeout=180) as response:
    source_data = response.read()

# Parse the complete supplier feed. Abort on invalid XML rather than publish a broken feed.
parser = ET.XMLParser()
root = ET.fromstring(source_data, parser=parser)

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
    if vendor in ALLOWED_VENDORS:
        selected.append(offer)

if not selected:
    raise RuntimeError("No Gemini / Gemini Sport offers found; refusing to overwrite the published feed.")

# Keep the original shop metadata, categories, and the matching offers.
for offer in list(offers):
    offers.remove(offer)
for offer in selected:
    offers.append(offer)

# Preserve the supplier's YML doctype used by the source feed.
xml_body = ET.tostring(root, encoding="utf-8")
content = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<!DOCTYPE yml_catalog SYSTEM "shops.dtd">\n'
    + xml_body
)
OUTPUT.write_bytes(content)

print(
    f"Updated {OUTPUT}: {len(selected)} offers selected from {len(all_offers)} "
    f"at {datetime.now(timezone.utc).isoformat()}"
)
