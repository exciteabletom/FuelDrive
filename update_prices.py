#!/usr/bin/env python3
"""
Update the database with the latest fuel prices
"""
import re
import time

from sql import Station, Session
import requests
import feedparser

rss_url = "https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS"

REGION_CODES = range(1, 62)
FUEL_TYPES = {
    "unleaded_91": 1,
    "unleaded_95": 2,
    "diesel": 4,
    "lpg": 5,
    "unleaded_98": 6,
    "e85": 10,
    "premium_diesel": 11,
}

cleanup_description = re.compile("(^.*?),(.*?), ")


def get_stations():
    """
    Scrapes the FuelWatch RSS feed for information about WA petrol stations.

    :return: A list of petrol stations represented by dicts
    """
    stations = {}
    for region in REGION_CODES:
        for fuel_type in FUEL_TYPES:
            params = {
                "Product": FUEL_TYPES[fuel_type],
                "Region": region,
            }
            result = requests.get(
                rss_url, params, headers={"User-Agent": "FuelDrive/1.0"}
            )
            result.raise_for_status()  # Ensure that result was successful
            result.encoding = "UTF-8"

            entries = feedparser.parse(result.text).entries
            for station in entries:
                loc_id = f"{station.latitude} {station.longitude}"
                if stations.get(loc_id):
                    stations[loc_id][fuel_type] = station.price
                else:
                    price = station.pop("price")
                    station[fuel_type] = price
                    stations.update({loc_id: station})

    return list(stations.values())


def update_db():
    """
    Updates the database with the latest petrol station information
    """
    stations = get_stations()
    last_update = int(time.time())  # Unix epoch

    # list of station names already inserted into db
    names = []
    for station_info in stations:
        latitude = station_info["latitude"]
        longitude = station_info["longitude"]
        name = station_info["trading-name"]
        # For some reason there are duplicate stations with slightly different coordinates in the rss feed
        if name in names:
            continue
        names.append(name)
        description = re.sub(cleanup_description, "", station_info["description"])
        brand = station_info["brand"]
        suburb = station_info["location"]
        address = station_info["address"]

        # Not every station will have every fuel type, so we use `.get` to avoid KeyError
        unleaded_91 = station_info.get("unleaded_91")
        unleaded_95 = station_info.get("unleaded_95")
        unleaded_98 = station_info.get("unleaded_98")
        diesel = station_info.get("diesel")
        premium_diesel = station_info.get("premium_diesel")
        lpg = station_info.get("lpg")
        e85 = station_info.get("e85")

        with Session.begin() as session:
            station = (
                session.query(Station)
                .filter_by(latitude=latitude, longitude=longitude)
                .first()
            )

            if not station:
                station = Station(
                    latitude=latitude,
                    longitude=longitude,
                    name=name,
                    brand=brand,
                    description=description,
                    suburb=suburb,
                    address=address,
                    last_update=last_update,
                )

            session.add(station)
            station.last_update = last_update
            station.unleaded_91 = unleaded_91
            station.unleaded_95 = unleaded_95
            station.unleaded_98 = unleaded_98
            station.diesel = diesel
            station.premium_diesel = premium_diesel
            station.lpg = lpg
            station.e85 = e85

            # Update these just in case the petrol station changed ownership or opening hours
            station.name = name
            station.brand = brand
            station.description = description


if __name__ == "__main__":
    update_db()
