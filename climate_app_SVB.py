import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
# DB setup
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect DB into new model
Base = automap_base()
# reflect tables
Base.prepare(engine, reflect=True)
# save references
Measurement = Base.classes.measurement
Station = Base.classes.station
# create session (Python-to-DB)
session = Session(engine)
# Flask setup
app = Flask(__name__)
# Flask routes
@app.route("/")
def welcome():
    return (
        f"Aloha API: Hawaiian Climate Analysis<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON precipitation data for previous year"""
    # 1 year ago from last date in DB
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for date & precipitation for previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    # Dict w/ date as key & prcp as value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
@app.route("/api/v1.0/stations")
def stations():
    """Return JSON list of stations"""
    results = session.query(Station.station).all()
    # Convert results into 1D array & convert to list
    stations = list(np.ravel(results))
    return jsonify(stations)
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (TOBS) for previous year"""
    # 1 year ago from last date in DB
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the primary station for all TOBS for previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # Convert results into 1D array & convert to list
    temps = list(np.ravel(results))
    # Results
    return jsonify(temps)
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # select
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        # Calculate TMIN, TAVG, TMAX for all dates >= start date
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into 1D array & convert to list
        temps = list(np.ravel(results))
        return jsonify(temps)
    # Calculate TMIN, TAVG, TMAX for dates btwn start >= X <= end dates inclusive
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # Convert results into 1D array & convert to list
    temps = list(np.ravel(results))
    return jsonify(temps)
if __name__ == '__main__':
    app.run()