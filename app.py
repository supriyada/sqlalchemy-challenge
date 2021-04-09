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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
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
    # Query all passengers
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
    return (f"The lowest temperature recorded: {mi_temp}</br>"
            f"The highest temperature recorded: {ma_temp}</br>"
            f"The average temperature recorded: {avg_temp}</br>")

def to_date(date_string): 
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError('{} is not valid date in the format YYYY-MM-DD'.format(date_string))


if __name__ == '__main__':
    app.run(debug=True)