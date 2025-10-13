import glob
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from scipy.spatial import cKDTree

from .timeseries import timeseries

class camxdata():
    def __init__(self, dir = None):
        if dir is None:
            raise TypeError("interactive file selector is not written yet")
        else:
            self.files=sorted(glob.glob(dir+"/*.nc"))
            self.dir=dir

        #initialize times, lat, lon, etc, and validate each file as it gets checked
        file_times = []
        file_starttime = []
        file_stoptime = []
        times = []
         
        for i, file in enumerate(self.files):
            ds = xr.open_dataset(file)
            if i == 0:
                self.latitude = ds.latitude
                self.longitude = ds.longitude
                self.topo = ds.topo
                self.z = ds.z
                self.LAY = len(ds['LAY'])
                self.ROW = len(ds['ROW'])
                self.COL = len(ds['COL'])
                self.variables = list(ds.data_vars)
                
            f_lat = ds.latitude
            f_lon = ds.longitude
            f_topo = ds.topo
            f_lay = len(ds['LAY'])

            if not self.latitude.equals(f_lat) or not self.longitude.equals(f_lon) or not self.topo.equals(f_topo) or f_lay != self.LAY:
                raise IOError(f".nc files in the file list are not congruent in space. error occured reading {file}")

            for v in list(ds.data_vars):
                if v not in self.variables:
                    raise ValueError(f"files in the file list have different variables. error occured reading {file}")

            YYYYjjj = ds['TFLAG'][:,0,0].values #Year/day-of-year format
            hhmmss = ds['TFLAG'][:,0,1].values
        
            # get starttimes for each point
            dt = [(datetime.strptime(str(a)+"+0000","%Y%j%z") + timedelta(hours=b/10000)) for a,b in zip(YYYYjjj,hhmmss)]
            file_times.append(np.array(dt))
            times.extend(dt)

            #get file start and stop to enable lookups later
            time_step_hr = ds.attrs['TSTEP']/10000
            file_starttime.append(dt[0])
            file_stoptime.append(dt[-1]+timedelta(hours=time_step_hr))
        
        #get time metadata set up
        self.file_times=np.array(file_times)
        self.file_starttime=np.array(file_starttime)
        self.file_stoptime=np.array(file_stoptime)
        self.file_ts = timeseries(self.file_starttime,np.arange(len(self.files)),stop_times=self.file_stoptime)
        self.time=np.array(times)
        self.stoptime = max(self.time)
        self.starttime = min(self.time)

        #build tree for nearest neighbors searching (2D)
        lat_flat = self.latitude.values.ravel()
        lon_flat = self.longitude.values.ravel()
        self.tree = cKDTree(np.column_stack([lat_flat, lon_flat]))


        

    def _get_time_file_index(self,dt_utc: "datetime"):
        """Take a datetime, return index of file and index of timestamp as a tuple"""
        ifile = self.file_ts.instantaneous_value(dt_utc)
        times = self.file_times[ifile]
        itime = np.searchsorted(times,dt_utc,side="right")-1
        return ifile,itime
    
    def _dt_to_utc(self,dt):
        if dt.tzinfo is None:
            raise ValueError("No timezone-naive timestamps!")
        return dt.astimezone(ZoneInfo("UTC"))
    
    def _get_row_col(self,lat,lon):
        _, idx = self.tree.query([lat, lon]) # use ckdtree
        row, col = np.unravel_index(idx, self.latitude.shape) # Map flat index back to 2D row/col
        return row, col
    
    def _get_layer(self,z_m_agl,lat,lon,time,AMSL=False):
        """
        This gets the layer index for a given altitude/lat/lon at a fixed point in time (since layer heights vary in time)
        """
        dt_utc = self._dt_to_utc(time)
        FILE, TSTEP=self._get_time_file_index(dt_utc)       
        ROW, COL = self._get_row_col(lat,lon)

        topo_z = self.topo[ROW][COL].values
        if AMSL:    #if input given relative to sea level, subtract off ground level to get AGL
            z_m_agl -= topo_z

        ds = xr.open_dataset(self.files[FILE])
        z_vals = ds.z.isel(TSTEP=TSTEP, ROW=ROW, COL=COL).values
        lay = np.abs(z_vals - z_m_agl).argmin()
        return lay
            
    def get(self, var, time=None, LAT=None, LON=None, z_m_agl = None):
        """
        infers what kind of dataset you're asking for based on the inputs you give
        ...probably going to be a shitshow for a while...
        """

        if var not in self.variables:
            raise ValueError(f"{var} not in variables of this camxdata instance")

        

        if time is None:
            time = self.time

        if LAT is not None and LON is not None: #we have defined space
            if len(LAT) > 1 and len(LAT) == len(LON):
                
                if isinstance(time,datetime):
                    raise ValueError('camxdata.get cant do this yet (LAT/LON arrays, single timestamp)')
                
                if len(time) > 1:   #Multiple times in multiple spaces
                    #return a timeseries object (usos.timeseries) with LAT/LON data encoded

                    print("Lydia's code goes here") 
                    print(f"DEBUG: len(time) = {len(time)}, len(LAT) = {len(LAT)}, len(LON) = {len(LON)}")

                    if not (len(time) == len(LAT) == len(LON)):
                        raise ValueError("For multiple points/times, time, LAT, and LON must all be the same length")

                    values = []
                    times_out = []
                    open_file = None
                    ds = None
                    n_total = 0
                    n_appended = 0

                    try:
                        for dt, lat_i, lon_i in zip(time, LAT, LON):
                            n_total += 1
                            dt_utc = self._dt_to_utc(dt)

                            # ALWAYS append something so outputs align 1:1 with inputs
                            if dt_utc < self.starttime or dt_utc > self.stoptime:
                                values.append(np.nan)
                                times_out.append(dt)
                                n_appended += 1
                                continue

                            ifile, TSTEP = self._get_time_file_index(dt_utc)
                            if ifile != open_file:
                                if ds is not None:
                                    ds.close()
                                ds = xr.open_dataset(self.files[ifile])
                                open_file = ifile

                            ROW, COL = self._get_row_col(lat_i, lon_i)
                            if z_m_agl is None:
                                LAY = 0
                            else:
                                # Reuse open ds and known TSTEP to avoid double-open
                                LAY = self._get_layer(z_m_agl, lat_i, lon_i, dt, ds=ds, TSTEP=TSTEP)

                            # Robust, name-based indexing (handles ROW/COL vs Y/X)
                            sel = {}
                            for name in ds[var].dims:
                                u = name.upper()
                                if u == 'TSTEP':
                                    sel[name] = TSTEP
                                elif u == 'LAY':
                                    sel[name] = LAY
                                elif u in ('ROW', 'Y'):
                                    sel[name] = ROW
                                elif u in ('COL', 'X'):
                                    sel[name] = COL

                            try:
                                v = ds[var].isel(**sel).values
                                try:
                                    v = float(v)
                                except Exception:
                                    arr = np.asarray(v)
                                    v = arr.item() if arr.size == 1 else np.nan
                            except Exception as e:
                                # If indexing fails for any reason, append NaN but keep alignment
                                # (and you can log the first few errors if needed)
                                v = np.nan

                            values.append(v)
                            times_out.append(dt)
                            n_appended += 1
                    finally:
                        if ds is not None:
                            ds.close()

                    print(f"[camxdata.get route] iterated={n_total} appended={n_appended}")
                    return timeseries(times_out, values)  # don't rely on .LAT/.LON on the timeseries
                                
            else: # single point in space

                ROW,COL = self._get_row_col(LAT,LON)

                if isinstance(time,datetime): #single point in space and time
                    
                    #get file, time
                    dt_utc = self._dt_to_utc(time)
                    FILE, TSTEP=self._get_time_file_index(dt_utc)
                    ds = xr.open_dataset(self.files[FILE])

                    # get layer
                    if z_m_agl is None:
                        LAY = 0 #default to surface layer
                    else:
                        LAY = self._get_layer(z_m_agl,LAT,LON,time)

                    #get value
                    val = ds[var][TSTEP][LAY][ROW][COL].values
                    ds.close()
                    return val
                
                elif len(time) > 1: #single point in space, multiple points in time
                    
                    # map out points in time to a list of files. then loop through files, grabbing all points from that file
                    # before closing
                    values = []
                    times = []
                    open_file = None
                    for dt in time:
                        dt_utc = self._dt_to_utc(dt)
                        
                        if dt_utc < self.starttime or dt_utc > self.stoptime:
                            continue
                    
                        ifile, TSTEP = self._get_time_file_index(dt_utc)
                        if ifile != open_file:
                            if open_file is not None:
                                ds.close()
                            ds = xr.open_dataset(self.files[ifile])
                            open_file = ifile

                        # get layer
                        if z_m_agl is None:
                            LAY = 0 #default to surface layer
                        else:
                            LAY = self._get_layer(z_m_agl,LAT,LON,time)   #RIGHT NOW THIS DOUBLE-OPENS THE DS. MODIFY TO ACCCEPT THE Z FIELD AS AN INPUT
                        
                        val = ds[var][TSTEP][LAY][ROW][COL].values
                        values.append(val)
                        times.append(dt)

                    return timeseries(times,values)
        raise ValueError("That's not a supported combination of inputs for camxdata.get()")

    def average_timeseries_surface(self, ts : timeseries):
        if ts.LAT is None or ts.LON is None:
            raise ValueError('ts passed to camxdata.average_timeseries_surface is missing LAT/LON data')

        valid_mask = np.isfinite(ts.LAT) & np.isfinite(ts.LON)
        valid_lat = ts.LAT[valid_mask]
        valid_lon = ts.LON[valid_mask]
        valid_data = ts.data[valid_mask] 

        # Query nearest grid point for each data point
        _, idx = self.tree.query(np.column_stack([valid_lat, valid_lon]))

        # Accumulate statistics
        bin_dict = {}

        for i, val in zip(idx, valid_data):
            if i not in bin_dict:
                bin_dict[i] = []
            bin_dict[i].append(val)


        stats_arrays = {key: np.full((self.ROW,self.COL), np.nan) for key in ['mean', 'median', 'std', 'min', 'max', 'N']}
        
        for i, values in bin_dict.items():
            y, x = np.unravel_index(i, (self.ROW,self.COL))
            arr = np.array(values)
            N = np.sum(~np.isnan(arr))
            if N>0:
                stats_arrays['mean'][y, x] = np.nanmean(arr)
                stats_arrays['median'][y, x] = np.nanmedian(arr)
                stats_arrays['std'][y, x] = np.nanstd(arr)
                stats_arrays['min'][y, x] = np.nanmin(arr)
                stats_arrays['max'][y, x] = np.nanmax(arr)
                stats_arrays['N'][y, x] = N

        # Create Dataset
        ds = xr.Dataset(
            {key: (("y", "x"), val) for key, val in stats_arrays.items()},
            coords={
                "latitude": (("y", "x"), self.latitude.data),
                "longitude": (("y", "x"), self.longitude.data)
            }
        )

        return ds
    

    def get_surface_field(self, var, time):
        dt_utc = self._dt_to_utc(time)
        FILE, TSTEP = self._get_time_file_index(dt_utc)
        LAY= 0
        ds = xr.open_dataset(self.files[FILE])
        field = ds[var][TSTEP][LAY]
        return field
