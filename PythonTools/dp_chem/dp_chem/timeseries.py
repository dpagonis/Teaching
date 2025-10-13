from datetime import datetime, timedelta
from dateutil import parser
import numpy as np
import pandas as pd
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings


class timeseries():
    _counter = 0

    def __init__(self, time, data, name=None, startstop=True, stop_times=None, LAT=None, LON=None, ALT=None):
        """
        time: list-like object of times
        data: numeric data, same length as time
        name: name of dataset to use in plots, etc
        startstop: set to False if data is instantaneous (no stop_times)
        stop_times: provide stop_times if data is startstop, but not continuous (e.g. there are delays between stop times and start times). for continuous data leave as None
        """

        self.data=np.array(data)
        self.t, self.tzinfo = self._parse_t_input(time) # returns a np array full of datetime.datetime objects, and the tzinfo string

        if len(self.t) == 0:
            return

        if not np.all(np.diff(self.t) > timedelta(0)):
            raise ValueError("Timestamps in `t` must be monotonically increasing.")

        if len(self.t) != len(self.data):
            raise ValueError("Incompatible time and data lengths")
        
        if name is None:
            self.name = f"ts{timeseries._counter}"
            timeseries._counter += 1  # Increment the shared counter
        else:
            self.name = name

        self.start = self.t[0]
        
        self.startstop = startstop      
        
        if self.startstop:
            if stop_times is None:
                self.t_stop = np.empty(len(self.t), dtype=object)
                self.t_stop[:-1] = self.t[1:]  # Set all but the last "stop" time to the next time point
                self.t_stop[-1] = self.t[-1] + np.diff(self.t)[-1]  #assume last two points have same dt
                self.continuous = True
            else:
                self.t_stop, _ = self._parse_t_input(stop_times) if stop_times is not None else None
                self.continuous = self._check_continuity(self.t,self.t_stop)
            self.stop = self.t_stop[-1]
        else:
            self.stop = self.t[-1]
            self.t_stop = None
            self.continuous = False

        self.dt = self._calculate_dt()

        if LAT is not None and LON is not None:
            if isinstance(LAT,(int, float)):
                self.LAT = np.full_like(self.t,LAT)
            else:
                try:
                    self.LAT=np.array(LAT)
                except (ValueError, TypeError):
                    raise TypeError("LAT/LON inputs must be number-like or array-like")
            if isinstance(LON,(int, float)):
                self.LON = np.full_like(self.t,LON)
            else:
                try:
                    self.LON=np.array(LON)
                except (ValueError, TypeError):
                    raise TypeError("LAT/LON inputs must be number-like or array-like") 
        else:
            self.LAT = None
            self.LON = None

        if ALT is not None:
            if isinstance(ALT,(int, float)):
                self.ALT = np.full_like(self.t,ALT)
            else:
                try:
                    self.ALT=np.array(ALT)
                except (ValueError, TypeError):
                    raise TypeError("altitude input must be number-like or array-like")
        else:
            self.ALT = None

        if self.ALT is not None and self.LAT is not None and self.LON is not None:
            self.spatial = True
        else:
            self.spatial = False

    def _parse_t_input(self,t):
        #figure out what kind of time data we've been given. turn it in to a nparray of datetime.datetimes and also capture time zone info (if any)
        
        t_out = None
        tz = None

        if len(t) == 0:
            return np.array([]), tz

        if isinstance(t,list):
            if isinstance(t[0],datetime):
                if t[0].tzinfo is not None:
                    tz = t[0].tzinfo
                    t_out = [dt.astimezone(tz) for dt in t]
                else:
                    t_out = t # keep it time-zone naive :(

            elif isinstance(t[0], str):
                # Parse each string to a datetime, detecting timezone if present
                parsed_times = [parser.parse(time_str) for time_str in t]
                
                # Check if there was timezone info
                if parsed_times[0].tzinfo is not None:
                    tz = parsed_times[0].tzinfo
                    t_out = [dt.astimezone(tz) for dt in parsed_times]
                else:
                    t_out = parsed_times # tz naive

        if isinstance(t, (pd.Series, pd.DatetimeIndex)):
            # Convert to datetime if not already in datetime64 dtype
            if not pd.api.types.is_datetime64_any_dtype(t):
                t = pd.to_datetime(t)

            # Now that `t` is datetime, handle timezone-aware data
            if isinstance(t, pd.Series):
                tz = t.dt.tz  # Capture timezone from the Series
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", FutureWarning)
                    t_out = np.array(t.dt.to_pydatetime())
                
            elif isinstance(t, pd.DatetimeIndex):
                tz = t.tz  # Capture timezone from the DatetimeIndex
                t_out = t.to_pydatetime()  # Convert to array of datetime.datetime


        elif isinstance(t, np.ndarray):
            if np.issubdtype(t.dtype, np.datetime64): # array of np.datetime64 objects
                t_out = pd.to_datetime(t).to_pydatetime()
            elif np.issubdtype(t.dtype, np.str_): #array of strings (unlikely)
                parsed_times = pd.to_datetime(t)
                if parsed_times.dt.tz is not None:
                    tz = parsed_times.dt.tz
                    t_out = parsed_times.dt.tz_convert(tz).to_pydatetime()
                else:
                    t_out = parsed_times.to_pydatetime()
            elif np.issubdtype(t.dtype, np.object_) and len(t) > 0:  # Ensure array is not empty
                first_element = t[0]  # Extract first element safely
                
                if isinstance(first_element, datetime):  # Array contains datetime.datetime objects
                    if first_element.tzinfo is not None:
                        tz = first_element.tzinfo
                    t_out = [dt.astimezone(tz) if tz else dt for dt in t]

                elif isinstance(first_element, datetime.date):  # Array contains datetime.date objects
                    t_out = np.array([datetime.combine(dt, datetime.min.time()) for dt in t])
        
        if t_out is None:
            raise TypeError("Unsupported type for 't' passed to timeseries")
        
        t_out_nparray = np.array(t_out) 
        
        return t_out_nparray, tz
    
    def _calculate_dt(self):
        """Calculate the time interval `dt` if the series is continuously spaced.

        Returns:
            timedelta: The interval `dt` between consecutive time points if consistent.
            None: If the time intervals are not consistent.
        """
        # Calculate the time differences between consecutive points
        if self.startstop:
            time_deltas = self.t_stop-self.t
        else:
            time_deltas = np.diff(self.t)
        
        deviation = np.abs(time_deltas-time_deltas.mean())

        if np.all(deviation < 0.05 * time_deltas.mean()):
            return time_deltas.mean()  
        else:
            return None  # The intervals are not consistent
        
    def _check_continuity(self,start_times,stop_times):
        # Check if every stop_time[i] matches start_time[i + 1] for i in range(n-1)
        for i in range(len(start_times) - 1):
            if stop_times[i] != start_times[i + 1]:
                return False
        return True

    def crop(self,t1: datetime=None, t2: datetime = None):
        """
        Crop a timeseries to the range [t1,t2]
        """
        if t1.tzinfo is None and self.tzinfo is not None:
            t1 = t1.replace(tzinfo=self.tzinfo)
        if t2.tzinfo is None and self.tzinfo is not None:
            t2 = t2.replace(tzinfo=self.tzinfo)

        if t1 < self.start or t1 is None:
            t1 = self.start
        if t2 > self.stop or t2 is None:
            t2 = self.stop

        if self.startstop:
            indexes_to_keep = np.where((self.t >= t1) & (self.t_stop <= t2))
            return timeseries(self.t[indexes_to_keep], self.data[indexes_to_keep],stop_times=self.t_stop[indexes_to_keep],name=self.name)

        else:
            indexes_to_keep = np.where((self.t >= t1) & (self.t <= t2))
            return timeseries(self.t[indexes_to_keep], self.data[indexes_to_keep], startstop = False, name=self.name)

    def filter(self, bool_array):
        """
        Filter the timeseries based on a boolean array.

        Parameters:
            bool_array (array-like): A boolean array with the same length as the timeseries.

        Returns:
            timeseries: A new timeseries object with data nan'ed out according to the boolean array.

        Raises:
            ValueError: If the boolean array length does not match the timeseries data length.
        """
        if len(bool_array) != len(self.data):
            raise ValueError("The boolean array must have the same length as the timeseries data.")

        filtered_data = np.where(bool_array, self.data, np.nan)
        return timeseries(self.t,filtered_data,name=self.name,startstop=self.startstop,stop_times=self.t_stop)

    def set_tz(self,time_zone):
        """
        Set the time zone of the timeseries directly. Use pytz codes
        "America/Denver" for MT; "MST"; "UTC"; etc
        """

        if len(self.t)==0:
            return #nothing to modify

        if self.tzinfo is None: #for naive timeseries, force tzinfo without any conversion
            self.tzinfo = pytz.timezone(time_zone)
            self.t = np.array([dt.replace(tzinfo=self.tzinfo) for dt in self.t])
            if self.t_stop is not None:
                self.t_stop = np.array([dt.astimezone(self.tzinfo) for dt in self.t_stop])
            self.start = self.start.replace(tzinfo=self.tzinfo)
            self.stop = self.stop.replace(tzinfo=self.tzinfo)
        else: #for aware timeseries, do the conversion
            self.tzinfo = pytz.timezone(time_zone)
            self.t = np.array([dt.astimezone(self.tzinfo) for dt in self.t])
            if self.t_stop is not None:
                self.t_stop = np.array([dt.astimezone(self.tzinfo) for dt in self.t_stop])
            self.start = self.start.astimezone(self.tzinfo)
            self.stop = self.stop.astimezone(self.tzinfo)
        

    def plot(self,t1: datetime=None, t2: datetime = None, ylabel=None, formatter="%b %d %H:%M", ts2=None):
        """
        Date components:
        - %Y : Full year, e.g., 2023
        - %y : Last two digits of the year, e.g., 23
        - %m : Month as zero-padded decimal, e.g., 07 for July
        - %B : Full month name, e.g., July
        - %b : Abbreviated month name, e.g., Jul
        - %d : Day of the month as zero-padded decimal, e.g., 01
        - %a : Abbreviated weekday name, e.g., Mon
        - %A : Full weekday name, e.g., Monday

        Time components:
        - %H : Hour (24-hour clock) as zero-padded decimal, e.g., 14
        - %I : Hour (12-hour clock) as zero-padded decimal, e.g., 02
        - %p : AM or PM
        - %M : Minute as zero-padded decimal, e.g., 05
        - %S : Second as zero-padded decimal, e.g., 09
        """

        if t1 is None:
            t1 = self.start
        if t2 is None:
            t2 = self.stop

        if t1.tzinfo is None and self.tzinfo is not None:
            t1 = t1.replace(tzinfo=self.tzinfo)
        if t2.tzinfo is None and self.tzinfo is not None:
            t2 = t2.replace(tzinfo=self.tzinfo)

        plt.plot(self.t[(self.t>=t1) & (self.t<=t2)], self.data[(self.t>=t1) & (self.t<=t2)], label=self.name)
        if isinstance(ts2,timeseries):
            plt.plot(ts2.t[(ts2.t>=t1) & (ts2.t<=t2)],ts2.data[(ts2.t>=t1) & (ts2.t<=t2)], label=ts2.name)
            plt.legend()
        if ylabel is not None:
            plt.ylabel(ylabel)
        if self.tzinfo:
            xlabel = self.tzinfo if self.tzinfo else "Time"
            plt.xlabel(xlabel)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(formatter, tz=self.tzinfo))
        plt.gcf().autofmt_xdate()

        plt.tight_layout()
        plt.show()
        plt.close()

    def mean(self, t1: datetime = None, t2: datetime = None) -> float:
        """
        calculate mean of data value over time interval [t1,t2]
        accounts for potentially variable timedeltas between points, nans, gaps, discontinuous data
        weights for interval length, incomplete overlap with an interval
        notice that this will inherently strip any spatial information from the timeseries, as it only operates on data

        returns nan if self does not have valid data in that time range
        """
        if t2<t1: raise ValueError('timeseries.mean was passed an invalid time range (t2 < t1)')

        # establish tz compatibility
        if t1.tzinfo is None and self.tzinfo is not None:
            t1 = t1.replace(tzinfo=self.tzinfo)
        if t2.tzinfo is None and self.tzinfo is not None:
            t2 = t2.replace(tzinfo=self.tzinfo)

        # skip it all if we're looking at a window outside of self
        if t1 > self.stop:
            return np.nan
        if t2 < self.start:
            return np.nan

        if t1 is None or t1 < self.start:
            t1 = self.start
        if t2 is None or t2 > self.stop:
            t2 = self.stop

        if self.startstop:
            
            # do searches for bounds — faster than np.where approach
            i1 = np.searchsorted(self.t,t1,side="right")-1
            i2 = np.searchsorted(self.t,t2,side="left")
            
            if i1 == i2:
                if i1 >= len(self.data):
                    return np.nan
                return self.data[i1]
            
            elif i1<i2:
                # interval spans multiple segments - extract them and average, accounting for variable time width
                data_segment = self.data[i1:i2 + 1]
                t_start_segment = self.t[i1:i2 + 1]
                t_stop_segment = self.t_stop[i1:i2 + 1]
                
                # Calculate duration of each segment (assuming datetime objects)
                durations = np.array([(stop - start).total_seconds() for start, stop in zip(t_start_segment, t_stop_segment)])
                durations[0] = (t_stop_segment[0]-t1).total_seconds() if (t_stop_segment[0]-t1).total_seconds() > 0 else 0
                durations[-1] = (t2-t_start_segment[-1]).total_seconds() if (t2-t_start_segment[-1]).total_seconds() > 0 else 0
                
                # Calculate weighted average, weighted by duration, skipping nans
                valid_data = data_segment[~np.isnan(data_segment)]
                valid_durations = durations[~np.isnan(data_segment)]
                if np.isnan(np.sum(valid_durations)):
                    return np.nan
                return np.sum(valid_data*valid_durations)/np.sum(valid_durations)
        else:
            #not startstop, just average any points inside the range
            index_list = np.where((self.t < t2) & (self.t >= t1))[0]
            
            if len(index_list) == 0:
                return np.nan   #nan out if there is no data in the interval

            data_segment = self.data[index_list]
            valid_data = data_segment[~np.isnan(data_segment)]
            return valid_data.mean() if len(valid_data) > 0 else np.nan
        
    def mean_spatial(self, t1: datetime = None, t2: datetime = None):
        """
        calculate mean of data and spatial info value over time interval [t1,t2]
        accounts for potentially variable timedeltas between points, nans, gaps, discontinuous data
        weights for interval length, incomplete overlap with an interval

        returns a tuple of d, lat, lon, alt over the specified time range
        output is all nans if self does not have valid data in that time range
        """

        if not self.spatial: raise TypeError('mean_spatial was called on a timeseries with no spatial data')

        if t2<t1: raise ValueError('timeseries.mean_spatial was passed an invalid time range (t2 < t1)')

        # establish tz compatibility
        if t1.tzinfo is None and self.tzinfo is not None:
            t1 = t1.replace(tzinfo=self.tzinfo)
        if t2.tzinfo is None and self.tzinfo is not None:
            t2 = t2.replace(tzinfo=self.tzinfo)

        # skip it all if we're looking at a window outside of self
        if t1 > self.stop:
            return np.nan, np.nan, np.nan, np.nan
        if t2 < self.start:
            return np.nan, np.nan, np.nan, np.nan

        if t1 is None or t1 < self.start:
            t1 = self.start
        if t2 is None or t2 > self.stop:
            t2 = self.stop

        if self.startstop:
            
            # do searches for bounds — faster than np.where approach
            i1 = np.searchsorted(self.t,t1,side="left")
            i2 = np.searchsorted(self.t,t2,side="right")
            
            if i1 == i2:
                if i1 >= len(self.data):
                    return np.nan, np.nan, np.nan, np.nan
                return self.data[i1], self.LAT[i1], self.LON[i1], self.ALT[i1]
            
            elif i1<i2:
                # interval spans multiple segments - extract them and average, accounting for variable time width
                data_segment = self.data[i1:i2 + 1]
                t_start_segment = self.t[i1:i2 + 1]
                t_stop_segment = self.t_stop[i1:i2 + 1]
                LAT_segment = self.LAT[i1:i2 + 1]
                LON_segment = self.LON[i1:i2 + 1]
                ALT_segment = self.ALT[i1:i2 + 1]
                
                # Calculate duration of each segment (assuming datetime objects)
                durations = np.array([(stop - start).total_seconds() for start, stop in zip(t_start_segment, t_stop_segment)])
                durations[0] = (t_stop_segment[0]-t1).total_seconds() if (t_stop_segment[0]-t1).total_seconds() > 0 else 0
                durations[-1] = (t2-t_start_segment[-1]).total_seconds() if (t2-t_start_segment[-1]).total_seconds() > 0 else 0
                
                # Calculate weighted average, weighted by duration, skipping nans
                valid_data = data_segment[~np.isnan(data_segment)]
                valid_durations = durations[~np.isnan(data_segment)]
                valid_LAT = LAT_segment[~np.isnan(data_segment)]
                valid_LON = LON_segment[~np.isnan(data_segment)]
                valid_ALT = ALT_segment[~np.isnan(data_segment)]
                if np.isnan(np.sum(valid_durations)):
                    return np.nan, np.nan, np.nan, np.nan
                
                d = np.sum(valid_data*valid_durations)/np.sum(valid_durations)
                lat = np.sum(valid_LAT*valid_durations)/np.sum(valid_durations)
                lon = np.sum(valid_LON*valid_durations)/np.sum(valid_durations)
                alt = np.sum(valid_ALT*valid_durations)/np.sum(valid_durations)
                
                return d, lat, lon, alt
        else:
            #not startstop, just average any points inside the range
            index_list = np.where((self.t < t2) & (self.t >= t1))[0]
            
            if len(index_list) == 0:
                return np.nan, np.nan, np.nan, np.nan   #nan out if there is no data in the interval

            data_segment = self.data[index_list]
            LAT_segment = self.LAT[index_list]
            LON_segment = self.LON[index_list]
            ALT_segment = self.ALT[index_list]
            valid_data = data_segment[~np.isnan(data_segment)]
            valid_LAT = LAT_segment[~np.isnan(data_segment)]
            valid_LON = LON_segment[~np.isnan(data_segment)]
            valid_ALT = ALT_segment[~np.isnan(data_segment)]
            
            if len(valid_data) == 0:
                return np.nan, np.nan, np.nan, np.nan   #nan out if there is no data in the interval
            
            d = np.mean(valid_data)
            lat = np.mean(valid_LAT)
            lon = np.mean(valid_LON)
            alt = np.mean(valid_ALT)
            return d, lat, lon, alt
            
    
    def instantaneous_value(self,t: datetime) -> float:
        """
        Retreive the instantaneous value of the timeseries at datetime t
        works on both instantaneous and startstop timeseries
        """

        if t.tzinfo is None and self.tzinfo is not None:
            t = t.replace(tzinfo=self.tzinfo)

        if self.startstop:
            index_list_1 = np.where(self.t <= t)[0]
            index_list_2 = np.where(self.t_stop > t)[0]
            if len(index_list_1) == 0 or len(index_list_2) == 0:
                return np.nan   #nan out if the instant is outside the time series
            i1 = index_list_1[-1]
            i2 = index_list_2[0]
            if i1 == i2:
                return self.data[i1]
            else:
                return np.nan # instant is in a discontinuity
        else:
            matching_indices = np.where(self.t == t)[0]
            if len(matching_indices) > 0:
                return self.data[matching_indices[0]]
            else:
                return np.nan

    def instantaneous_value_spatial(self,t: datetime):
        """
        Retreive the instantaneous data value and spatial information of the timeseries at datetime t
        works on both instantaneous and startstop timeseries

        returns a tuple of d, lat, lon, alt over the specified time range
        output is all nans if self does not have valid data in that time range
        """

        if t.tzinfo is None and self.tzinfo is not None:
            t = t.replace(tzinfo=self.tzinfo)

        if self.startstop:
            index_list_1 = np.where(self.t <= t)[0]
            index_list_2 = np.where(self.t_stop > t)[0]
            if len(index_list_1) == 0 or len(index_list_2) == 0:
                return np.nan, np.nan, np.nan, np.nan   #nan out if the instant is outside the time series
            i1 = index_list_1[-1]
            i2 = index_list_2[0]
            if i1 == i2:
                return self.data[i1], self.LAT[i1], self.LON[i1], self.ALT[i1]
            else:
                return np.nan, np.nan, np.nan, np.nan # instant is in a discontinuity
        else:
            matching_indices = np.where(self.t == t)[0]
            if len(matching_indices) > 0:
                return self.data[matching_indices[0]], self.LAT[matching_indices[0]], self.LON[matching_indices[0]], self.ALT[matching_indices[0]]
            else:
                return np.nan, np.nan, np.nan, np.nan

    def is_merged(self, other: "timeseries"):
        """True if the times series have identical time dimensions"""
        if np.array_equal(self.t, other.t):
            if self.startstop == other.startstop:
                if self.continuous == other.continuous:
                    return True
        return False

    def merge(self, other: "timeseries"):
        """
        merge two time series onto a common base
        - if both are continuous and both have constant spacing: rebase onto slower dataset
        - otherwise, reaverage other onto self
        """

        if self.spatial or other.spatial:
            warnings.warn(
                "Support for merge() on spatial time series is not fully supported. "
                "Please use merge_to_self for a time-based merge and let the developer know you need this.",
                UserWarning
            )
        
        second_start = max(self.start, other.start)
        first_stop = min(self.stop, other.stop)
        if second_start > first_stop:
            raise ValueError("Time series passed to merge do not overlap")
        
        overlap_timedelta = first_stop-second_start
        
        if self.startstop:
            overlap_mask = np.where((self.t >= second_start) & (self.t_stop <= first_stop))
        else:
            overlap_mask = np.where((self.t >= second_start) & (self.t <= first_stop))

        if self.startstop and other.startstop:
            
            if (self.dt is not None) and (other.dt is not None): #both datasets are regularly spaced
                
                if self.dt>other.dt:
                    slowts = self
                    fastts = other
                    selfisfast = False
                else:
                    slowts = other
                    fastts = self
                    selfisfast = True

                dt = slowts.dt

                if self.continuous and other.continuous:
                    overlap_start_pt = np.where(slowts.t >= second_start)[0][0]
                    overlap_stop_pt = np.where(slowts.t <= first_stop)[0][-1]
                    if overlap_stop_pt-overlap_start_pt < 1:
                        raise ValueError("Time series passed to merge do not overlap")
                    start_times = [t for t in slowts.t[overlap_start_pt:overlap_stop_pt+1]]
                    stop_times = [t+dt for t in start_times]

                    if selfisfast:
                        rebased_self = timeseries(start_times, [fastts.mean(t1,t2) for t1,t2 in zip(start_times,stop_times)],name=self.name)
                        rebased_other = timeseries(start_times,slowts.data[overlap_start_pt:overlap_stop_pt+1],name=other.name)
                    else:
                        rebased_self = timeseries(start_times,slowts.data[overlap_start_pt:overlap_stop_pt+1],name=self.name) 
                        rebased_other = timeseries(start_times, [fastts.mean(t1,t2) for t1,t2 in zip(start_times,stop_times)],name=other.name)
                    return rebased_self, rebased_other
            
            #if you hit this next line, one of your startstop time series is irregular in some way (discontinuous, variable dt)
            #so to keep things simple, we resample other onto self's time series
            
            self_segment_data =  self.data[overlap_mask]
            self_segment_t = self.t[overlap_mask]
            self_segment_t_stop = self.t_stop[overlap_mask]

            other_segment_data = [other.mean(t1,t2) for t1, t2 in zip(self_segment_t,self_segment_t_stop)]
            return timeseries(self_segment_t,self_segment_data,stop_times=self_segment_t_stop,name=self.name),timeseries(self_segment_t,other_segment_data,stop_times=self_segment_t_stop,name=other.name) 
                
            
        elif self.startstop and not other.startstop: #other is instantaneous, average other onto self's startstop windows
            self_segment_data =  self.data[overlap_mask]
            self_segment_t = self.t[overlap_mask]
            self_segment_t_stop = self.t_stop[overlap_mask]
            other_segment_data = [other.mean(t1,t2) for t1, t2 in zip(self_segment_t,self_segment_t_stop)]
            return timeseries(self_segment_t,self_segment_data,stop_times=self_segment_t_stop,name=self.name),timeseries(self_segment_t,other_segment_data,stop_times=self_segment_t_stop,name=other.name)
        
        elif not self.startstop and other.startstop: #other is startstop while we are instantaneous, snap other onto self
            self_segment_data =  self.data[overlap_mask]
            self_segment_t = self.t[overlap_mask]
            other_segment_data = [other.instantaneous_value(t) for t in self_segment_t]
            return timeseries(self_segment_t,self_segment_data, startstop=False, name=self.name),timeseries(self_segment_t,other_segment_data, startstop=False, name=other.name)

        elif not self.startstop and not other.startstop: #both instantaneous, grab shared time points then bail
            times = []
            self_segment_data=[]
            other_segment_data=[]
            for t in self.t:
                if t in other.t:
                    times.append(t)
                    self_segment_data.append(self.data[self.t == t][0])
                    other_segment_data.append(other.data[other.t == t][0])
                
            return timeseries(times,self_segment_data, startstop = False, name=self.name),timeseries(times, other_segment_data, startstop=False, name=other.name)

        else:
            raise TypeError("Time series for merging had a combination of continuity and start/stop properties that are not supported. Time to nag the developer!")

    def merge_to_self(self, other: "timeseries"):
        """
        merge a timeseries onto this object's time base
        returns  (copy of self, merged ts)
        """

        if other.spatial:
            return self._spatial_merge_to_self(other)
        
        if self.startstop and other.startstop:
            other_data = [other.mean(t1,t2) for t1, t2 in zip(self.t,self.t_stop)]
            return self,timeseries(self.t,other_data,stop_times=self.t_stop,name=other.name) 
                
        elif self.startstop and not other.startstop: #other is instantaneous, average other onto self's startstop windows
            other_segment_data = [other.mean(t1,t2) for t1, t2 in zip(self.t,self.t_stop)]
            return self,timeseries(self.t,other_segment_data,stop_times=self.t_stop,name=other.name)
        
        elif not self.startstop and other.startstop: #other is startstop while we are instantaneous, snap other onto self
            other_segment_data = [other.instantaneous_value(t) for t in self.t]
            return self, timeseries(self.t,other_segment_data, startstop=False, name=other.name)

        elif not self.startstop and not other.startstop: #both instantaneous, grab shared time points then bail
            times = []
            self_segment_data=[]
            other_segment_data=[]
            for t in self.t:
                if t in other.t:
                    times.append(t)
                    self_segment_data.append(self.data[self.t == t][0])
                    other_segment_data.append(other.data[other.t == t][0])
                
            return timeseries(times,self_segment_data, startstop = False, name=self.name),timeseries(times, other_segment_data, startstop=False, name=other.name)

        else:
            raise TypeError("Time series for merging had a combination of continuity and start/stop properties that are not supported. Time to nag the developer!")

    def _spatial_merge_to_self(self, other: "timeseries"):
        """
        do a merge, preseving all spatial information that is in other
        """

        D=[]
        LAT=[]
        LON=[]
        ALT=[]


        if self.startstop and other.startstop:
            for t1,t2 in zip(self.t,self.t_stop):
                d,lat,lon,alt = other.mean_spatial(t1,t2)
                D.append(d)
                LAT.append(lat)
                LON.append(lon)
                ALT.append(alt)
            return self,timeseries(self.t,D,LAT=LAT,LON=LON,ALT=ALT,stop_times=self.t_stop,name=other.name) 
                
        elif self.startstop and not other.startstop: #other is instantaneous, average other onto self's startstop windows
            for t1,t2 in zip(self.t,self.t_stop):
                d,lat,lon,alt = other.mean_spatial(t1,t2)
                D.append(d)
                LAT.append(lat)
                LON.append(lon)
                ALT.append(alt)
            return self,timeseries(self.t,D,stop_times=self.t_stop,LAT=LAT,LON=LON,ALT=ALT,name=other.name)
        
        elif not self.startstop and other.startstop: #other is startstop while we are instantaneous, snap other onto self
            for t in self.t:
                d,lat,lon,alt = other.instantaneous_value_spatial(t)
                D.append(d)
                LAT.append(lat)
                LON.append(lon)
                ALT.append(alt)            
            return self, timeseries(self.t,D,LAT=LAT,LON=LON,ALT=ALT, startstop=False, name=other.name)

        elif not self.startstop and not other.startstop: #both instantaneous, grab shared time points and go
            times = []
            other_segment_data=[]
            for t in self.t:
                if t in other.t:
                    d,lat,lon,alt = other.instantaneous_value_spatial(t)
                else:
                    d,lat,lon,alt = np.nan, np.nan, np.nan, np.nan
                D.append(d)
                LAT.append(lat)
                LON.append(lon)
                ALT.append(alt)   
            return self, timeseries(times, other_segment_data, startstop=False, name=other.name)

        else:
            raise TypeError("Time series for merging had a combination of continuity and start/stop properties that are not supported. Time to nag the developer!")


    def __len__(self):
        return len(self.t)
    
    def __add__(self, other):
        if isinstance(other, timeseries):
            if self.is_merged(other):
                new_data = [a + b for a, b in zip(self.data, other.data)]
                new_name = f"({self.name}+{other.name})" if self.name and other.name else None
            else:
                raise ValueError("attempted to add time series that were not merged")
        else:
            try:
                scalar = float(other)  # Coerce to float
                new_data = [a + scalar for a in self.data]
                new_name = self.name
            except (ValueError, TypeError):
                raise TypeError("Addition is only supported with a Timeseries, int, or float.")
        
        return timeseries(self.t,new_data,name=new_name)
    
    def __radd__(self,other):
        return self.__add__(other)  # Reuse the logic in __add__
    
    def __sub__(self, other):
        if isinstance(other, timeseries):
            if self.is_merged(other):
                new_data = [a - b for a, b in zip(self.data, other.data)]
                new_name = f"({self.name}-{other.name})" if self.name and other.name else None
            else:
                raise ValueError("attempted to subtract time series that were not merged")
        else:
            try:
                scalar = float(other)  # Coerce to float
                new_data = [a - scalar for a in self.data]
                new_name = self.name
            except (ValueError, TypeError):
                raise TypeError("Subtraction is only supported with a Timeseries, int, or float.")
        
        return timeseries(self.t, new_data, name=new_name)

    def __rsub__(self, other):
        try:
            scalar = float(other)  # Coerce to float
            new_data = [scalar - a for a in self.data]  # Reverse subtraction
            new_name = self.name
        except (ValueError, TypeError):
            raise TypeError("Subtraction is only supported with a Timeseries, int, or float.")
        
        return timeseries(self.t, new_data, name=new_name)

    def __mul__(self,other):
        if isinstance(other, timeseries):
            if self.is_merged(other):
                new_data = [a * b for a, b in zip(self.data, other.data)]
                new_name = f"({self.name}×{other.name})" if self.name and other.name else None
            else:
                raise ValueError("attempted to multiply time series that were not merged")
        else:
            # Attempt to multiply a numeric value with all elements
            try:
                scalar = float(other)  # Coerce to float
                new_data = [a * scalar for a in self.data]
                new_name = self.name
            except (ValueError, TypeError):
                raise TypeError("Multiplication is only supported with a Timeseries, int, or float.")

        return timeseries(self.t, new_data, name=new_name)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __truediv__(self,other):
        if isinstance(other, timeseries):
            if self.is_merged(other):
                new_data = [a / b if b != 0 else float('inf') for a, b in zip(self.data, other.data)]
                new_name = f"({self.name}/{other.name})" if self.name and other.name else None
            else:
                raise ValueError("attempted to divide time series that were not merged")
        else:
            # Attempt to multiply a numeric value with all elements
            try:
                scalar = float(other)  # Coerce to float
                if scalar == 0:
                    raise ZeroDivisionError("Division by zero is not allowed.")
                new_data = [a / scalar for a in self.data]
                new_name = self.name
            except (ValueError, TypeError):
                raise TypeError("Division is only supported with a Timeseries, int, or float.")

        return timeseries(self.t, new_data, name=new_name)

if __name__ == '__main__':


    # ts_null = timeseries([],[])

    tz = pytz.timezone('MST')
    now=datetime.now()
    t1 = [now.astimezone(tz) + timedelta(minutes=i*17) for i in range(240) ]
    data1 = [t.minute**0.5 for t in t1]
    # t2 = [now.astimezone(tz) + timedelta(minutes=20*i+20) for i in range(12) ]
    # data2 = [t.minute**0.5 + 5 for t in t2]
    ts = timeseries(t1,data1, startstop=False)
    # ts2 = timeseries(t2,data2,startstop=False)
    # ts3, ts4 = ts.merge(ts2)

    # plt.plot(ts.t,ts.data,'o-', label="ts1")
    # plt.plot(ts2.t,ts2.data,'o-', label="ts2",)
    # plt.scatter(ts3.t,ts3.data,color='red',label="ts1 resample",s=100)
    # plt.scatter(ts4.t,ts4.data,color='black',label="ts2 resample",s=100)
    # plt.legend()
    # plt.show()
    # plt.close()

    t1 = datetime(2024,11,13,9)
    t2 = t1+timedelta(hours=1)

    ts_c = ts.crop(t1,t2)
    
    print(len(ts_c.t))