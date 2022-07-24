#!/usr/bin/env python3
"""
Update the database with the latest fuel prices
"""
import re
import time

from sqlalchemy import insert, update

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
        # For some reason there are duplicate stations with slightly different coordinates in the rss feed
        if station_info["trading-name"] in names:
            continue
        names.append(station_info["trading-name"])

        latitude = float(station_info["latitude"])
        longitude = float(station_info["longitude"])
        info_args = {
            "name": station_info["trading-name"],
            "description": re.sub(cleanup_description, "", station_info["description"]),
            "brand": station_info["brand"],
            "suburb": station_info["location"],
            "address": station_info["address"],
            "last_update": last_update,
            # Not every station will have every fuel type, so we use `.get` to avoid KeyError
            "unleaded_91": station_info.get("unleaded_91"),
            "unleaded_95": station_info.get("unleaded_95"),
            "unleaded_98": station_info.get("unleaded_98"),
            "diesel": station_info.get("diesel"),
            "premium_diesel": station_info.get("premium_diesel"),
            "lpg": station_info.get("lpg"),
            "e85": station_info.get("e85"),
        }

        with Session() as session:
            station_exists = (
                session.query(Station.name)
                .filter_by(latitude=latitude, longitude=longitude)
                .first()
                is not None
            )

            if not station_exists:
                info_args.update({"latitude": latitude, "longitude": longitude})
                insert_stmt = insert(Station).values(
                    info_args,
                )
                session.execute(insert_stmt)
                session.commit()
                continue

            update_stmt = (
                update(Station)
                .where(Station.latitude == latitude, Station.longitude == longitude)
                .values(info_args)
            )
            session.execute(update_stmt)
            session.commit()


if __name__ == "__main__":
    update_db()
