import json
import re
from collections import defaultdict


FIELDS = {"bus_id": int, "stop_id": int, "stop_name": str,
          "next_stop": int, "stop_type": str, "a_time": str}


def validate(records):
    errors = dict.fromkeys(FIELDS, 0)
    for stop in records:
        for field, expected in FIELDS.items():
            value = stop.get(field)
            valid = type(value) is expected
            if field in ("stop_name", "a_time"):
                valid = valid and bool(value)
            if field == "stop_type":
                valid = valid and len(value) <= 1
            if valid and field == "stop_name":
                valid = re.fullmatch(r"[A-Z][A-Za-z ]* (Road|Avenue|Boulevard|Street)", value) is not None
            if valid and field == "stop_type":
                valid = value in ("", "S", "O", "F")
            if valid and field == "a_time":
                valid = re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", value) is not None
            if not valid:
                errors[field] += 1
    return errors


def main():
    records = json.loads(input())
    errors = validate(records)
    route_times = defaultdict(list)
    for stop in records:
        route_times[stop["bus_id"]].append(stop)
    for stops in route_times.values():
        previous = None
        for stop in stops:
            value = stop["a_time"]
            if not isinstance(value, str) or re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", value) is None:
                continue
            if previous is not None and value <= previous:
                errors["a_time"] += 1
                break
            previous = value
    print(f"Type and field validation: {sum(errors.values())} errors")
    for field, count in errors.items():
        print(f"{field}: {count}")
    routes = defaultdict(list)
    for stop in records:
        routes[stop["bus_id"]].append(stop)
    print("\nLine names and number of stops:")
    for bus_id, stops in sorted(routes.items()):
        print(f"bus_id: {bus_id} stops: {len(stops)}")
    for bus_id, stops in sorted(routes.items()):
        if sum(stop["stop_type"] == "S" for stop in stops) != 1 or sum(stop["stop_type"] == "F" for stop in stops) != 1:
            print(f"There is no start or end stop for the line: {bus_id}")
            return
    starts = {stop["stop_name"] for stop in records if stop["stop_type"] == "S"}
    finishes = {stop["stop_name"] for stop in records if stop["stop_type"] == "F"}
    stop_routes = defaultdict(set)
    for stop in records:
        stop_routes[stop["stop_name"]].add(stop["bus_id"])
    transfers = {name for name, buses in stop_routes.items() if len(buses) > 1}
    print()
    for label, names in (("Start", starts), ("Transfer", transfers), ("Finish", finishes)):
        print(f"{label} stops: {len(names)} {sorted(names)}")
    on_demand = {stop["stop_name"] for stop in records if stop["stop_type"] == "O"}
    on_demand -= starts | finishes | transfers
    print(f"On demand stops: {len(on_demand)} {sorted(on_demand)}")


if __name__ == "__main__":
    main()
