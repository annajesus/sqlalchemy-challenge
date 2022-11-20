import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import timedelta
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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


#################################################
# Flask Routes
#################################################

"""List all the available routes."""
@app.route("/")
def home():
    return ("Surfs Up Weather API!<br><br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


"""Convert the query results from your precipitation analysis (i.e. retrieve only the
    last 12 months of data) to a dictionary using date as the key and prcp as the value."""
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query all measurement info
    results = session.query(Measurement).all()

    session.close()

    # Create a dictionary from the row data and append to a list of yr_prcp_results
    yr_prcp_results = []
    for result in results:
        yr_prcp_dict = {}
        yr_prcp_dict["date"] = result.date
        yr_prcp_dict["prcp"] = result.prcp
        yr_prcp_results.append(yr_prcp_dict)

    return jsonify(yr_prcp_results)


"""Return a JSON list of stations from the dataset."""
@app.route("/api/v1.0/stations")
def stations():
    # Query all station 
    station_results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(station_results))

    return jsonify(stations = stations) 


"""Query the dates and temperature observations of the most-active station for the previous year of data."""
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in data set.
    past_date_one_yr = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation observations
    prcp_scores_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > past_date_one_yr).all()

    session.close()
    
    # Convert list of tuples into normal list
    temperature_list = list(np.ravel(prcp_scores_query))

	# Jsonify summary
    return jsonify(temperature_list)


"""Return a JSON list of the minimum temperature, the average temperature, and the
    maximum temperature for a specified start or start-end range."""
@app.route("/api/v1.0/<start>")
def start_date(start):
    # create search for user input
    search_date = dt.datetime.strptime(start, "%Y-%m-%d")
    last_year = dt.timedelta(days=365)
    
    start = search_date - last_year
    end = dt.date(2017, 8, 23)

    # For a specified start date, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Convert list of tuples into normal list
    json_start_query = list(np.ravel(start_query))

    return jsonify(json_start_query)



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # create search for user input
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    last_year = dt.timedelta(days=365)

    start = start_date - last_year
    end = end_date - last_year

    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    start_end_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Convert list of tuples into normal list
    json_start_end_query = list(np.ravel(start_end_query))

    return jsonify(json_start_end_query)

if __name__ == '__main__':
    app.run(debug=True)

