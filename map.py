import requests
from sqlalchemy import select, column
from geopy import distance

from sql import Session, Station, fuel_types

with open("TOMTOM_KEY", "r") as f:
    api_key = f.readline().strip()


def shortest_path(start, dest, station=None):
    if not station:
        res = requests.get(
            f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{dest}/json?key={api_key}"
        )
    else:
        res = requests.get(
            f"https://api.tomtom.com/routing/1/calculateRoute/{start}:{station}:{dest}/json?key={api_key}"
        )
    res.raise_for_status()
    data = res.json()
    points = []
    for point in data["routes"][0]["legs"][0]["points"]:
        points.append((point["latitude"], point["longitude"]))

    return data["routes"][0]["summary"]["lengthInMeters"], points


def get_cheapest_stations_on_route(path, distance_km, fuel_type):
    l = len(path)
    # If path is too long grab ~100 points from the start, middle, and end to reduce size to ~300
    if l > 300:
        path = path[:100] + path[round(l / 2 - 50) : round(l / 2 + 50)] + path[-100:]

    start = path[0]
    end = path[-1]

    offset = 0.01
    if start[0] > end[0]:
        lat_cond = (start[0] + offset, end[0] - offset)
    else:
        lat_cond = (end[0] + offset, start[0] - offset)

    if start[1] > end[1]:
        long_cond = (start[1] + offset, end[1] - offset)
    else:
        long_cond = (end[1] + offset, start[1] - offset)

    with Session() as session:
        select_coords = select(
            Station.latitude,
            Station.longitude,
            Station.name,
            Station.address,
            Station.suburb,
            Station.description,
            fuel_types[fuel_type],
        ).where(
            lat_cond[0] > Station.latitude,
            Station.latitude > lat_cond[1],
            long_cond[0] > Station.longitude,
            Station.longitude > long_cond[1],
            fuel_types[fuel_type] != None,
        )

        stations = session.execute(select_coords).fetchall()

    close_stations = []
    for path_node in path:
        for station in stations:
            station = dict(station)
            if station in close_stations:
                continue
            if (
                distance.distance(
                    path_node, (station["latitude"], station["longitude"])
                ).km
                <= distance_km / 1.5  # divide to account for somewhat round trips
            ):
                close_stations.append(station)

    # Sort by best price
    close_stations.sort(key=lambda x: x[fuel_type])
    # Truncate stations and convert from Row to dict
    close_stations = [
        dict(i) for i in close_stations[: min((len(close_stations) - 1, 8))]
    ]

    for station in close_stations:
        price = station.pop(fuel_type)
        station["price"] = price

    return close_stations
