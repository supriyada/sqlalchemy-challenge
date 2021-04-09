import numpy as np

from sqlalchemy import *
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
import pandas as pd
import datetime

from flask import Flask, jsonify

global most_recent_date_f
global start_date_f

# Database Setup
#----------------
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
#------------
app = Flask(__name__)

# Flask Routes
#-------------

@app.route("/")
def welcome():
    
    global most_recent_date_f
    global start_date_f
    session = Session(engine)

    recent_date_f = session.query(Measurement).order_by(Measurement.date.desc()).first()
    most_recent_date_f = parse(recent_date_f.date)
    start_date_f = most_recent_date_f  + relativedelta(months=-12) - timedelta(days=1)

    session.close()

    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"The precipitation data for the last year: /api/v1.0/precipitation<br/>"
        f"The list of stations from dataset: /api/v1.0/stations<br/>"
        f"The temperature observations of the most active station: /api/v1.0/tobs<br/>"
        f"To find temperature statistics from a given start date [YYYY-MM-DD]: /api/v1.0/<start><br/>"
        f"To find temperature statistics from a given date range [YYYY-MM-DD]: /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_result_f = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date.between(start_date_f,most_recent_date_f)).all()

    session.close()

    prcp_dict = [r._asdict() for r in query_result_f]

    return jsonify(prcp_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    active_station_f = session.query(Measurement.station, func.count().label("measurement_count"))\
                                                        .group_by(Measurement.station)\
                                                        .order_by(desc(func.count())).first()

    most_active_station_f = active_station_f.station
        
    active_station_tob_f = session.query(Measurement.date,Measurement.tobs).\
                filter(Measurement.date.between(start_date_f, most_recent_date_f)).\
                filter(Measurement.station == most_active_station_f).all()

    session.close()

    tobs_dict = [t._asdict() for t in active_station_tob_f]
    
    return jsonify(tobs_dict)


@app.route("/api/v1.0/stations")
def station_names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/<start>")
def temp_start_date(start):
    range_start_date = to_date(start)
    session = Session(engine)

    only_start_date_result = session.query(Measurement, \
                               func.min(Measurement.tobs).label("mini_temp"),\
                                func.max(Measurement.tobs).label("max_temp"),\
                                func.avg(Measurement.tobs).label("average_temp")).\
                                filter(Measurement.date >= range_start_date).all()
    
    session.close()

    for result in only_start_date_result:
        mi_temp = result.mini_temp
        ma_temp = result.max_temp
        avg_temp = result.average_temp

    st_date_dict = [{"Minimum temperature": mi_temp,\
                    "Maximum temperature" : ma_temp,\
                    "Average temperature" : avg_temp}]

    return jsonify(st_date_dict)


@app.route("/api/v1.0/<start>/<end>")
def temp_start_end_date(start,end):
    range_st_date = to_date(start)
    range_end_date = to_date(end)

    if  range_st_date > range_end_date:
        return f"You have entered date range [Start date:{range_st_date},End date: {range_end_date}].</br>\
        Please enter the start date less than the end date!!!"

    else:
        session = Session(engine)

        start_end_date_result = session.query(Measurement, \
                                func.min(Measurement.tobs).label("mini_temp1"),\
                                    func.max(Measurement.tobs).label("max_temp1"),\
                                    func.avg(Measurement.tobs).label("average_temp1")).\
                                    filter(Measurement.date >= range_st_date).\
                                    filter(Measurement.date <= range_end_date).all()
        
        session.close()

        for results in start_end_date_result:
            mi_temp1 = results.mini_temp1
            ma_temp1 = results.max_temp1
            avg_temp1 = results.average_temp1

        st_end_date_dict = [{"Minimum temperature": mi_temp1,\
                    "Maximum temperature" : ma_temp1,\
                    "Average temperature" : avg_temp1}]

        return jsonify(st_end_date_dict)

def to_date(date_string): 
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError('{} is not valid date. Please enter in the format YYYY-MM-DD'.format(date_string))


if __name__ == '__main__':
    app.run(debug=True)