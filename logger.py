import requests, json
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import sqlite3

from config import *
from key import *

def getBODS(operators=['CBNL'], flag=''):
    url = 'https://data.bus-data.dft.gov.uk/api/v1/datafeed/?operatorRef='+','.join(operators)+flag+'&api_key='+BODSKEY
    # print(url)
    data = requests.get(url)
    root = ET.fromstring(data.text)
    vehicles = root.findall('.//{http://www.siri.org.uk/siri}VehicleActivity')
    buses = []
    for vehicleElem in vehicles:
        bus = {}
        elems = [
            ('RecordedAtTime', './/{http://www.siri.org.uk/siri}RecordedAtTime'),
            ('ItemIdentifier', './/{http://www.siri.org.uk/siri}ItemIdentifier'),
            ('ValidUntilTime', './/{http://www.siri.org.uk/siri}ValidUntilTime'),
            
            ('OperatorRef', './/{http://www.siri.org.uk/siri}OperatorRef'),
            ('LineRef', './/{http://www.siri.org.uk/siri}LineRef'),
            ('DirectionRef', './/{http://www.siri.org.uk/siri}DirectionRef'),
            ('JourneyDate', './/{http://www.siri.org.uk/siri}DataFrameRef'),
            ('JourneyCode', './/{http://www.siri.org.uk/siri}DatedVehicleJourneyRef'),
            ('PublishedLineName', './/{http://www.siri.org.uk/siri}PublishedLineName'),
            ('OperatorRef', './/{http://www.siri.org.uk/siri}OperatorRef'),

            ('OriginStopRef', './/{http://www.siri.org.uk/siri}OriginRef'),
            ('OriginStopName', './/{http://www.siri.org.uk/siri}OriginName'),
            ('DestinationStopRef', './/{http://www.siri.org.uk/siri}DestinationRef'),
            ('DestinationStopName', './/{http://www.siri.org.uk/siri}DestinationName'),
            ('DepartureTime', './/{http://www.siri.org.uk/siri}OriginAimedDepartureTime'),
            ('ArrivalTime', './/{http://www.siri.org.uk/siri}DestinationAimedArrivalTime'),

            ('Latitude', './/{http://www.siri.org.uk/siri}Latitude'),
            ('Longitude', './/{http://www.siri.org.uk/siri}Longitude'),
            ('Bearing', './/{http://www.siri.org.uk/siri}Bearing'),
            ('BlockRef', './/{http://www.siri.org.uk/siri}BlockRef'),
            ('VehicleRef', './/{http://www.siri.org.uk/siri}VehicleRef'),
            ('DriverRef', './/{http://www.siri.org.uk/siri}DriverRef'),

            ('TicketServiceCode', './/{http://www.siri.org.uk/siri}TicketMachineServiceCode'),
            ('TicketJourneyCode', './/{http://www.siri.org.uk/siri}JourneyCode'),
            ('VehicleUniqueId', './/{http://www.siri.org.uk/siri}VehicleUniqueId'),
        ]

        for key, elem in elems:
            try:
                value = vehicleElem.find(elem).text
                if key in ['RecordedAtTime', 'DepartureTime', 'ArrivalTime']:
                    if value is not None:
                        # Parse the timestamp, remove the timezone, and format it back as a string
                        timestamp = datetime.fromisoformat(value.split('+')[0])
                        bus[key] = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
                    else:
                        bus[key] = None
                else:
                    bus[key] = value
            except AttributeError:
                bus[key] = None

        # print(bus)
        
        # (bus['VehicleRef'], bus['PublishedLineName'], bus['Latitude'], bus['Longitude'], bus['Bearing'], bus['RecordedAtTime'], bus['DepartureTime'], 
        #  bus['JourneyCode'], bus['DestinationStopName'], bus['DirectionRef'], bus['LineRef'], bus['BlockRef'])
        buses.append(bus)
    return buses

def getCentrebus():
    url = 'https://portal.centrebus.info/v5/widget/api/buses?region=&showBusesNotInService=false'
    headers = {'referer': 'https://portal.centrebus.info/WidgetV5/BusTracker'}
    data = requests.get(url, headers=headers)
    txt = data.text
    busses = json.loads(data.text)
    return busses

    
if __name__ == '__main__':
    while True:
        try:
            buses = getBODS(OPERATORS)
            # buses.append(sample)
            if buses:
                # print('Tracking...')
                con = sqlite3.connect(LOG_PATH)
                cur = con.cursor()
                for bus in buses:
                    # print(bus)
                    result = cur.execute("SELECT vehicle FROM buslog WHERE operator=? AND vehicle=? AND updatedTime=?", (bus['OperatorRef'], bus['VehicleRef'], bus['RecordedAtTime'])).fetchone()
                    # print(result)
                    if not result: 
                        # cur.execute("INSERT INTO buslog (vehicle, route, latitude, longitude, bearing, updatedTime, departureTime, journeyCode, destination, direction, lineRef, blockRef) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        #             (bus['VehicleRef'], bus['PublishedLineName'], bus['Latitude'], bus['Longitude'], bus['Bearing'], bus['RecordedAtTime'], bus['DepartureTime'], bus['JourneyCode'], bus['DestinationStopName'], bus['DirectionRef'], bus['LineRef'], bus['BlockRef']))
                        cur.execute('''INSERT INTO buslog (vehicle, block, journeyDate, journeyCode, route, lineRef, direction, operator,\
                                                            latitude, longitude, bearing, updatedTime,\
                                                            departureTime, arrivalTime, departureStop, arrivalStop, origin, destination,\
                                                            ticketServiceCode, ticketJourneyCode, driver, vehicleID,\
                                                            bodsId, validUntil) VALUES (?,?,?,?,?,?,?,?, ?,?,?,?, ?,?,?,?,?,?, ?,?,?,?, ?,?)''',
                                    (bus['VehicleRef'], bus['BlockRef'], bus['JourneyDate'], bus['JourneyCode'], bus['PublishedLineName'], bus['LineRef'], bus['DirectionRef'], bus['OperatorRef'],
                                     bus['Latitude'], bus['Longitude'], bus['Bearing'], bus['RecordedAtTime'], 
                                     bus['DepartureTime'], bus['ArrivalTime'], bus['OriginStopRef'], bus['DestinationStopRef'], bus['OriginStopName'], bus['DestinationStopName'], 
                                     bus['TicketServiceCode'], bus['TicketJourneyCode'], bus['DriverRef'], bus['VehicleUniqueId'],
                                     bus['ItemIdentifier'], bus['ValidUntilTime']))
                        print(bus['VehicleRef'], bus['BlockRef'], bus['PublishedLineName'], bus['JourneyCode'])

                    else:
                        pass
                        # print('Ignoring', bus['VehicleRef'])
                con.commit()
                con.close()
        except requests.exceptions.RequestException as error:
            print('An error occured', error)
        # except Exception as error:
        #     print('An error occured', error)
        time.sleep(1)
        
