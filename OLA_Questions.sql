CREATE  Database Ola;
Use Ola;

# Q1. Retrieve all successful bookings:

Create VIEW Successful_Bookings AS
SELECT * FROM bookings 
WHERE Booking_Status = 'Success';

# Retrieving data from View:
SELECT * FROM Successful_Bookings;

# Q2. Find the average ride distance for each vehicle type:

CREATE VIEW ride_distance_for_each_vehicle AS
SELECT Vehicle_Type, AVG(Ride_Distance)
AS avg_distance FROM bookings
GROUP BY Vehicle_Type;

# Retrieving data from View:
SELECT * FROM ride_distance_for_each_vehicle;

# Q3. Get the total number of cancelled rides by customers:

CREATE VIEW canceled_rides_by_customers AS
SELECT COUNT(*) FROM bookings
WHERE Booking_Status = 'Canceled by Customer';

# Retrieving data from View:
SELECT * FROM canceled_rides_by_customers;

# Q4. List the top 5 customers who booked the highest number of rides:

CREATE VIEW Top_5_Customers AS
SELECT Customer_ID, COUNT(Booking_ID) AS total_rides
FROM bookings
GROUP BY Customer_ID
ORDER BY total_rides DESC LIMIT 5;

# Retrieving data from View:
SELECT * FROM Top_5_Customers;

# Q5. Get the number of rides cancelled by drivers due to personal and car-related issues:

CREATE VIEW Rides_Canceled_by_Drivers_P_C_Issues AS
SELECT COUNT(*) FROM bookings
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

# Retrieving data from View:
SELECT * FROM Rides_Canceled_by_Drivers_P_C_Issues;

# Q6. Find the maximum and minimum driver ratings for Prime Sedan bookings:

CREATE VIEW maximum_and_minimum_driver_ratings_for_Prime_Sedan AS
SELECT MAX(Driver_Ratings) AS max_rating,
MIN(Driver_Ratings) as min_rating
FROM bookings WHERE Vehicle_Type = 'Prime Sedan';

# Retrieving data from View:
SELECT * FROM maximum_and_minimum_driver_ratings_for_Prime_Sedan;

# Q7. Retrieve all rides where payment was made using UPI:

CREATE VIEW UPI_Payment AS
SELECT * FROM bookings
WHERE Payment_Method = 'UPI';

# Retrieving data from View:
SELECT * FROM UPI_Payment;

# Q8. Find the average customer rating per vehicle type:

CREATE VIEW AVG_Customer_Rating AS
SELECT Vehicle_Type, AVG(Customer_Rating) AS avg_customer_rating
FROM bookings
GROUP BY Vehicle_Type;

# Retrieving data from View:
SELECT * FROM AVG_Customer_Rating;

# Q9. Calculate the total booking value of rides completed successfully:

CREATE VIEW total_successful_ride_value AS
SELECT SUM(Booking_Value) AS total_successful_ride_value
FROM bookings
WHERE Booking_Status = 'Success';

# Retrieving data from View:
SELECT * FROM total_successful_ride_value;

# Q10. List all incomplete rides along with the reason

CREATE VIEW Incomplete_Rides_Reason AS
SELECT Booking_ID, Incomplete_Rides_Reason
FROM bookings
WHERE Incomplete_Rides = 'Yes';

# Retrieving data from View:
SELECT * FROM Incomplete_Rides_Reason;

