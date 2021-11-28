"""A module with helper functions to process data."""

import os
from datetime import datetime

from shapely.geometry import LineString, Point
import pandas as pd
import geopandas as gpd


def swap(x):
    coords = list(x.coords)
    # Swap each coordinate using list comprehension and create Points
    coords = [Point(t[1], t[0]) for t in coords]
    return LineString(coords)


def clean_df(df):
    """Add date time index and year column for summary data

    Parameters
    ----------
    df : Pandas DataFrame

    """

    df["date"] = pd.to_datetime(df.start_date_local)

    df.set_index("date", inplace=True)
    df["year"] = df.index.year

    return df


def _calculate_elapsed(act_object):
    """Helper function that makes sure elapsed time includes both days and seconds.
    By default returns time in hours.

    """
    days = act_object.days * 24
    hours = act_object.seconds / 60 / 60
    return days + hours


def get_activities(client):
    """Grab all activities and turn into df
    TODO: add a limit or date span to this as an input

    NOTE: I am adding a helper to fix elapsed time

    Parameters
    ----------
    client : stravalib Client object
        This object stores your token and has numerous methods available to grab
        data from the Strava api.
    """

    activities = client.get_activities()

    # Generate a dataframe of all activities
    cols = [
        "name",
        "average_speed",
        "distance",
        "total_elevation_gain",
        "start_date_local",
        "type",
    ]
    data = []
    for activity in activities:
        my_dict = activity.to_dict()

        data.append(
            [activity.id]
            + [_calculate_elapsed(activity.elapsed_time)]
            + [my_dict.get(x) for x in cols]
        )

    # Add activity id and elapsed time cols name
    cols[0:0] = "activity_id", "elapsed_hours"

    all_data_df = pd.DataFrame(data, columns=cols)

    # Note - we will want to parse out runs  & hikes vs other types?
    print(
        "Looks like you've been a busy bee. "
        "I've found {} activities.".format(len(all_data_df))
    )

    csv_path = "all_activities.csv"
    print(
        "Great! I have everything I need - I'm saving your data to a "
        "file called {}.".format(csv_path)
    )
    all_data_df.to_csv(csv_path)

    return clean_df(all_data_df)


def convert_units_df(df):
    """Convert dataframe units to ft and miles

    Parameters
    -----------
    df : pandas dataframe
        DataFrame containing Strava data for every activity.

    """
    df["elevation_gain_ft"] = df["total_elevation_gain"] * 3.28084
    df["miles"] = df.distance * 0.000621371
    df["miles_per_hour"] = df["average_speed"] * 2.23694
    df["pace_min_miles"] = 60 / df["miles_per_hour"]
    return df


def summarize_daily_data(df):
    """Create summary df with daily data totals.

    Parameters
    ----------
    df : Pandas dataframe
        DataFrame containing strava activities and a date index.

    Returns
    -------
    df : Pandas DataFrame
        DF containing daily summarized data and a doy and year column

    Also saves an daily_sum_all_activities to the data/ directory.

    """
    # Summarize totals by day
    df = df.resample("D").sum()
    # Add year and doy
    df["doy"] = df.index.dayofyear
    # Calculate this again because otherwise the years are added if there are multiple activities
    df["year"] = df.index.year

    # daily_data_df["day"] = daily_data_df.index.day
    # Optional export as csv
    df.to_csv(os.path.join("data", "daily_sum_all_activities.csv"))
    return df


def get_stream_data(client, theyear, df, types):
    """Downloads data from strava for a specific year.
    Assumes authentication is already in place

    Parameters
    ----------
    client : stravalib client object
    theyear : int
        the year that you wish to grab data for
    df : pandas dataframe
        a dataframe containing the activity idea in an "activity_id" column
        for every activity that you wish to get
    types : list
        the types of objects you wish to return from the stream (gps, etc)

    """

    # Subset to the year of interest
    subset = df[df.index.year == theyear]
    # Loop through each activity and get the latlon data
    # this is a big request that will hit rate limits if provided with too many activities at once
    gdf_list = []
    for i, act in enumerate(subset["activity_id"].values):
        act_data = client.get_activity_streams(act, types=types)
        # print(act)
        # Some activities have no information associated with them
        if act_data:
            try:
                gdf_list.append(
                    [act, LineString(act_data["latlng"].data), act_data["latlng"].data]
                )
            except KeyError:
                # some activities have no gps data like swimming and short activities
                print(
                    "LatLon is missing from activity {}. Moving to next activity".format(
                        act
                    )
                )

    print(
        "You have made {} requests. Strava limits requests to 600 every 15 mins".format(
            i
        )
    )
    print(datetime.now())
    df = pd.DataFrame(gdf_list, columns=["activity_id", "geometry", "xy"])

    gdf = gpd.GeoDataFrame(df, geometry=df.geometry, crs="EPSG:4326")
    # Swap xy - using swap function below
    # gdf["geometry"] = gdf.geometry.map(
    # lambda polygon: shapely.ops.transform(lambda x, y: (y, x), polygon))

    gdf.geometry = gdf.geometry.map(swap)
    # Export to shapefile
    file_name = os.path.join("data", "strava_data_" + str(theyear) + ".shp")
    gdf[["activity_id", "geometry"]].to_file(file_name)

    return gdf
