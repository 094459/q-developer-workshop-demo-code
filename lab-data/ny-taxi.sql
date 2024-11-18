CREATE TABLE zones (
    zone_id INT AUTO_INCREMENT PRIMARY KEY,
    borough VARCHAR(50) NOT NULL,
    zone VARCHAR(100) NOT NULL,
    service_zone VARCHAR(50) NOT NULL
);

CREATE TABLE rate_codes (
    rate_code_id SMALLINT AUTO_INCREMENT PRIMARY KEY,
    rate_code_description VARCHAR(100) NOT NULL
);

CREATE TABLE payment_types (
    payment_type_id TINYINT AUTO_INCREMENT PRIMARY KEY,
    payment_type_description VARCHAR(50) NOT NULL
);

CREATE TABLE drivers (
    driver_id INT AUTO_INCREMENT PRIMARY KEY,
    driver_name VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100),
    address TEXT,
    joined_date DATE
);

CREATE TABLE vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_make VARCHAR(50),
    vehicle_model VARCHAR(50),
    license_plate VARCHAR(20) NOT NULL,
    registration_state VARCHAR(2),
    vehicle_year YEAR
);

CREATE TABLE trips (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    pickup_datetime DATETIME NOT NULL,
    dropoff_datetime DATETIME NOT NULL,
    passenger_count SMALLINT,
    trip_distance FLOAT,
    pickup_location_id INT NOT NULL,
    dropoff_location_id INT NOT NULL,
    rate_code_id SMALLINT,
    store_and_fwd_flag CHAR(1),
    driver_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    FOREIGN KEY (pickup_location_id) REFERENCES zones(zone_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES zones(zone_id),
    FOREIGN KEY (rate_code_id) REFERENCES rate_codes(rate_code_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);

CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    payment_type TINYINT NOT NULL,
    fare_amount FLOAT NOT NULL,
    extra FLOAT,
    mta_tax FLOAT,
    tip_amount FLOAT,
    tolls_amount FLOAT,
    total_amount FLOAT NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
    FOREIGN KEY (payment_type) REFERENCES payment_types(payment_type_id)
);
