import pandas as pd 

@pd.api.extensions.register_dataframe_accessor("strava")
class StravaClean:
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        # verify there is an activity id column
        if "activity_id" not in obj.columns:
            raise AttributeError("Must have activity id.")
            
    def add_elapsed_time(self):
        self._obj.elapsed_time=pd.to_timedelta(self._obj.elapsed_time)
        # Convert to hours and consider activities that are >24 hours
        self._obj["elapsed_hours"] = ((self._obj.elapsed_time.dt.seconds/60)/60)+(self._obj.elapsed_time.dt.days*24)
        
    def convert_units_df(self):
        """Convert dataframe units to ft and miles

        Parameters
        -----------
        df : pandas dataframe
            DataFrame containing Strava data for every activity.

        """
        self._obj["elevation_gain_ft"] = self._obj["total_elevation_gain"]*3.28084
        self._obj["miles"] = self._obj.distance * 0.000621371
        self._obj["miles_per_hour"] = self._obj["average_speed"]*2.23694
        self._obj["pace_min_miles"] = 60/self._obj["miles_per_hour"]
        
    def summarize_daily_data(self):
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
        # Is this bad practice?
        new_df = self._obj.copy()
        # Summarize totals by day
        new_df = new_df.resample("D").sum()
        # Add year and doy
        new_df["doy"] = new_df.index.dayofyear
        # Calculate this again because otherwise the years are added if there are multiple activities
        new_df["year"] = new_df.index.year

        return new_df
    
    def summarize_monthly(self, date=None):
        """Create summary df with monthly totals.

        Parameters
        ----------
        df : Pandas dataframe
            DataFrame containing daily summarized strava activities and a date index.
        date : string
            Starting date to clip data 

        Returns
        -------
        df : Pandas DataFrame
            DF containing daily summarized data and a doy and year column

        Also saves an daily_sum_all_activities to the data/ directory.

        """   
        
        new_df = self._obj.copy()
        monthly_df = new_df.resample('M').sum()
        # Double check as i may not need these columns
        monthly_df['month'] = monthly_df.index.month
        monthly_df['year'] = monthly_df.index.year
        monthly_df['doy'] = monthly_df.index.dayofyear
        if date is not None:
            monthly_df = monthly_df[date:]
            
        return monthly_df
    
    
    def calc_month_sum_by_year(self, col_name):
        """Create summary df with monthly totals.

        Parameters
        ----------
        df : Pandas dataframe
            DataFrame containing monthly summarized strava activities and a date index.
        col_name : string
            Column to summarize 

        Returns
        -------
        df : Pandas DataFrame
            DF containing daily summarized data and a doy and year column

        Also saves an daily_sum_all_activities to the data/ directory.

        """      
    

        df = self._obj.copy()
        df = df[[col_name]]

        df["year"] = df.index.year
        df["month"] = df.index.month
        # Set index
        df.set_index('month','year', inplace=True)
        df.set_index('year', append=True, inplace=True)
        df = df.unstack()
        df.columns = df.columns.droplevel(0)

        # Revese column order when returned
        return df.iloc[:, ::-1]    
      
