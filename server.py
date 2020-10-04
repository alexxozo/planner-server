from flask import Flask, render_template, request
import sys, datetime, copy

app = Flask(__name__)

default_input_data = [
    "USM,HKT,2017-02-11T06:25:00,2017-02-11T07:25:00,PV404,24,1,9",
    "USM,HKT,2017-02-12T12:15:00,2017-02-12T13:15:00,PV755,23,2,9",
    "USM,HKT,2017-02-12T21:15:00,2017-02-12T22:15:00,PV729,25,1,14",
    "USM,HKT,2017-02-11T14:50:00,2017-02-11T15:50:00,PV966,21,1,17",
    "USM,HKT,2017-02-12T00:35:00,2017-02-12T01:35:00,PV398,24,1,14",
    "USM,HKT,2017-02-12T05:15:00,2017-02-12T06:15:00,PV870,19,1,13",
    "USM,HKT,2017-02-12T10:00:00,2017-02-12T11:00:00,PV320,22,1,18",
    "USM,HKT,2017-02-12T13:40:00,2017-02-12T14:40:00,PV540,26,2,13",
    "USM,HKT,2017-02-12T09:30:00,2017-02-12T10:30:00,PV290,19,2,8",
    "USM,HKT,2017-02-11T02:40:00,2017-02-11T03:40:00,PV876,25,2,16",
    "USM,HKT,2017-02-12T09:35:00,2017-02-12T10:35:00,PV275,24,2,17",
    "HKT,USM,2017-02-12T10:35:00,2017-02-12T11:30:00,PV996,23,1,15",
    "HKT,USM,2017-02-11T15:45:00,2017-02-11T16:40:00,PV243,22,1,6",
    "HKT,USM,2017-02-11T19:05:00,2017-02-11T20:00:00,PV146,21,2,5",
    "HKT,USM,2017-02-12T16:00:00,2017-02-12T16:55:00,PV634,21,1,12",
    "HKT,DPS,2017-02-12T00:00:00,2017-02-12T03:40:00,PV961,70,1,39",
    "HKT,USM,2017-02-12T00:20:00,2017-02-12T01:15:00,PV101,18,2,7",
    "HKT,DPS,2017-02-11T12:00:00,2017-02-11T15:40:00,PV100,96,1,40",
    "HKT,USM,2017-02-12T22:05:00,2017-02-12T23:00:00,PV672,24,2,5",
    "HKT,USM,2017-02-11T06:30:00,2017-02-11T07:25:00,PV442,17,1,11",
    "HKT,USM,2017-02-12T07:15:00,2017-02-12T08:10:00,PV837,18,1,12",
    "BWN,DPS,2017-02-11T06:10:00,2017-02-11T08:30:00,PV953,48,1,25",
    "BWN,DPS,2017-02-12T14:35:00,2017-02-12T16:55:00,PV388,49,1,30",
    "BWN,DPS,2017-02-11T05:35:00,2017-02-11T07:55:00,PV378,59,1,29",
    "BWN,DPS,2017-02-12T10:35:00,2017-02-12T12:55:00,PV046,50,1,25",
    "BWN,DPS,2017-02-11T13:40:00,2017-02-11T16:00:00,PV883,51,1,26",
    "BWN,DPS,2017-02-12T19:10:00,2017-02-12T21:30:00,PV999,54,2,23",
    "BWN,DPS,2017-02-11T16:15:00,2017-02-11T18:35:00,PV213,55,2,22",
    "BWN,DPS,2017-02-11T02:35:00,2017-02-11T04:55:00,PV873,46,1,34",
    "BWN,DPS,2017-02-11T01:15:00,2017-02-11T03:35:00,PV452,57,1,33",
    "BWN,DPS,2017-02-12T08:45:00,2017-02-12T11:05:00,PV278,41,2,22",
    "BWN,DPS,2017-02-12T22:50:00,2017-02-13T01:10:00,PV042,56,2,31",
    "DPS,HKT,2017-02-12T08:25:00,2017-02-12T12:05:00,PV207,83,1,38",
    "DPS,BWN,2017-02-12T17:15:00,2017-02-12T19:40:00,PV620,43,2,25",
    "DPS,BWN,2017-02-11T13:15:00,2017-02-11T15:40:00,PV478,47,1,23",
    "DPS,HKT,2017-02-11T09:15:00,2017-02-11T12:55:00,PV414,67,1,49",
    "DPS,HKT,2017-02-12T08:25:00,2017-02-12T12:05:00,PV699,78,2,41",
    "DPS,HKT,2017-02-12T15:20:00,2017-02-12T19:00:00,PV974,85,1,38",
    "DPS,HKT,2017-02-11T00:20:00,2017-02-11T04:00:00,PV519,79,2,44",
    "DPS,HKT,2017-02-11T08:50:00,2017-02-11T12:30:00,PV260,89,1,43",
    "DPS,BWN,2017-02-12T16:45:00,2017-02-12T19:10:00,PV451,57,1,24",
    "DPS,BWN,2017-02-11T22:10:00,2017-02-12T00:35:00,PV197,50,1,30"
]

class Flight:
    def __init__(self, source, destination, departure, arrival, flight_number, price, bags_allowed, bag_price):
        self.source = source
        self.destination = destination
        self.departure = datetime.datetime.strptime(departure, '%Y-%m-%dT%H:%M:%S')
        self.arrival = datetime.datetime.strptime(arrival, '%Y-%m-%dT%H:%M:%S')
        self.flight_number = flight_number
        self.price = float(price)
        self.bags_allowed = int(bags_allowed)
        self.bag_price = float(bag_price)

class Trip:
    def __init__(self, flights, number_of_bags, bag_price, price):
        self.flights = flights
        self.number_of_bags = int(number_of_bags)
        self.bag_price = float(bag_price)
        self.price = float(price)

def matching(first_flight, second_flight, needed_bags):
    difference = second_flight.departure - first_flight.arrival
    hours = abs(difference.total_seconds()) / 3600
    if first_flight.destination == second_flight.source and second_flight.bags_allowed >= needed_bags and hours >= 1 and hours <= 4:
        return True
    else:
        return False

def findTrip(last_index, flights, trip, result, visited, needed_bags):
    last_flight = flights[last_index]
    trip.flights.append(last_flight)

    trip.price = trip.price + last_flight.price
    trip.bag_price = trip.bag_price + needed_bags * last_flight.bag_price
    result.append(copy.deepcopy(trip))
    visited[last_flight.destination] = True

    for index in range(last_index + 1, len(flights)):
        current_flight = flights[index]
        if matching(last_flight, current_flight, needed_bags) and not visited[current_flight.destination]:
            findTrip(index, flights, trip, result, visited, needed_bags)
            visited[current_flight.destination] = False
            trip.price = trip.price - current_flight.price
            del trip.flights[-1]
    return result

def compute_flights_for(number_of_bags, input_array=None):
    flights = []
    visited = {}

    # DEBUGGING INPUT
    if input_array == None:
        input_array = default_input_data

    for line in input_array:
        line = line.split(',')
        flights.append(Flight(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7]))
        visited[line[0]] = False
        visited[line[1]] = False

    flights.sort(key=lambda f : f.arrival)


    visited = {key: False for key, value in visited.items()}
    itineraries = []
    for index in range(len(flights)):
        if number_of_bags <= flights[index].bags_allowed:
            result = findTrip(index, flights, Trip([], number_of_bags, 0, 0), [], visited, number_of_bags)
            for t in result:
                itineraries.append(t)
    return itineraries


@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        input_array = []
        for line in request.form['input_data'].splitlines()[1:]:
            input_array.append(line)
        return render_template("index.html", zero_itineraries=compute_flights_for(0, input_array), one_itineraries=compute_flights_for(1, input_array), two_itineraries=compute_flights_for(2, input_array))
    else:
        return render_template("index.html", zero_itineraries=compute_flights_for(0), one_itineraries=compute_flights_for(1), two_itineraries=compute_flights_for(2))

if __name__ == "__main__":
    app.run(debug=True)