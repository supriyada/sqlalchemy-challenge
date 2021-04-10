# sqlalchemy-challenge

## Overview:
climate of Honolulu, Hawaii is analysed.

## Pre-requisites:
>  The sqlite databse `hawaii.sqlite` with required tables: `measurement` and `station` <br>
>  `hawaii_measurement.csv` and `hawaii_stations.csv` <br>

## Steps followed: <br>
>   Used SQLAlchemy `create_engine` to connect to your sqlite database.<br> 
>   Use SQLAlchemy `automap_base()` to reflect your tables into classes and save a reference to those classes called `Station` and `Measurement`.<br>
>   Python is linked to the database by creating an SQLAlchemy session. <br><br>
>   The last 12 months of precipitation data is collected and plotted with Matplotlib.<br>
>   The station with highest number of observations is identified. It is `USC00519281` <br>
>   There are 9 stations in the dataset.<br>
>   The last 12 months of temperature observation data (TOBS) is retrieved and histogram is plotted. <br> <br>

### Climate app: <br>
>   Flask API is designed with the following routes:
> - `/`<br>
> - `/api/v1.0/precipitation` <br>
> - `/api/v1.0/stations` <br>
> - `/api/v1.0/tobs` <br>
> - `/api/v1.0/<start>` <br>
> - `/api/v1.0/<start>/<end>` <br>
>   `jsonify` is used to convert API data into a valid JSON response object. <br> <br>

### Temperature Analysis I
>   The average temperature in June & December at all stations across all available years in the dataset is calculated. <br>
>   The paired t-test is performed on the temperature values. <br> <br>

### Temperature Analysis II
>   The min, avg, and max temperatures for your trip using the matching dates from a previous year is calculated. <br>
>   Error bar is plotted. <br> <br>
>   
### Daily Rainfall Average
>   The rainfall per weather station is calculated. <br>
>   The min, avg, and max temperatures of daily normal is calculated. <br>
 
