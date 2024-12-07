CREATE TABLE buslog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle VARCHAR(255),
    block VARCHAR(255),
    journeyDate DATE,
    journeyCode VARCHAR(10),
    route VARCHAR(255),
    lineRef VARCHAR(255),
    direction VARCHAR(255),
    operator VARCHAR(255),

    latitude DECIMAL(8,6),
    longitude DECIMAL(9,6),
    bearing INTEGER,
    updatedTime DATETIME,

    departureTime DATETIME,
    arrivalTime DATETIME,
    departureStop VARCHAR(255),
    arrivalStop VARCHAR(255),
    origin VARCHAR(255),
    destination VARCHAR(255),

    ticketServiceCode VARCHAR(255),
    ticketJourneyCode VARCHAR(255),
    driver VARCHAR(255),
    vehicleID VARCHAR(255),

    bodsId VARCHAR(255),
    validUntil DATETIME
);

CREATE INDEX idx_operator_vehicle_updatedTime ON buslog (operator, vehicle, updatedTime);