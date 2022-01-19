import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, render_template


MAX_DATE_STR = '2017-08-23'
SQLITE_FILE_URL = "sqlite:///Resources/hawaii.sqlite"

################################################
# Database Setup
#################################################
engine = create_engine(SQLITE_FILE_URL)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    max_date = dt.datetime.fromisoformat(MAX_DATE_STR).date()
    year_date_down = max_date - dt.timedelta(days=365)
    year_date_down
    
    # Query for the dates and precipitation values
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date <= MAX_DATE_STR).\
    filter(Measurement.date >= year_date_down).all()
    

    # Convert to list of dictionaries to jsonify
    prcp_data_list = []

    for date, prcp in prcp_data:
        new_prcp_dict = {}
        new_prcp_dict[date] = prcp
        prcp_data_list.append(new_prcp_dict)

    session.close()

    return jsonify(prcp_data_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    stations = {}

    # Query all stations
    results = session.query(Station.station, Station.name).all()
    for s,name in results:
        stations[s] = name

    session.close()
 
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the last date contained in the dataset and date from one year ago
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year_date = (dt.datetime.strptime(last_date[0],'%Y-%m-%d') \
                    - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query for the dates and temperature values
    results =   session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date >= last_year_date).\
                order_by(Measurement.date).all()

    # Convert to list of dictionaries to jsonify
    tobs_date_list = []

    for date, tobs in results:
        new_dict = {}
        new_dict[date] = tobs
        tobs_date_list.append(new_dict)

    session.close()

    return jsonify(tobs_date_list)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    return_list = []

    results =   session.query(  Measurement.date,\
                                func.min(Measurement.tobs), \
                                func.avg(Measurement.tobs), \
                                func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()

    for date, min, avg, max in results:
        new_dict = {}
        new_dict["Date"] = date
        new_dict["TMIN"] = min
        new_dict["TAVG"] = avg
        new_dict["TMAX"] = max
        return_list.append(new_dict)

    session.close()    

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    new_start = start.replace(" ", "")
    new_end = end.replace(" ", "")
    results = session.query(func.avg(Measurement.tobs),func.min(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    new_data = list(np.ravel(results))
    
    session.close()    

    return jsonify(new_data)

if __name__ == '__main__':
    app.run(debug=True)


