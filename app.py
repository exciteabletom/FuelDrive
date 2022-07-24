from flask import Flask, render_template, request

from map import shortest_path, get_cheapest_stations_on_route

app = Flask(__name__)


@app.context_processor
def template_vars():
    return {
        "app_name": "FuelDrive",
    }


@app.route("/")
def main_page():
    return render_template("main.html")


@app.route("/find_stations/")
def find_stations():
    start = request.args.get("startCoords")
    end = request.args.get("endCoords")
    startAddress = request.args.get("startAddress")
    endAddress = request.args.get("endAddress")
    fuel_type = request.args.get("fueltype")
    distance = int(request.args.get("distance"))
    route_distance, path = shortest_path(start, end)
    close_stations = get_cheapest_stations_on_route(path, distance, fuel_type)

    return render_template(
        "find_stations.html",
        close_stations=close_stations,
        start=startAddress,
        end=endAddress,
    )


if __name__ == "__main__":
    app.run()
