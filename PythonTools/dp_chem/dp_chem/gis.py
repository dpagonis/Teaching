from pathlib import Path
import zipfile
import os
import geopandas as gpd
from shapely.geometry import Point
import cartopy.crs as ccrs
from pyproj import Transformer
import numpy as np
import pandas as pd

from .timeseries import timeseries

EA_CRS = "EPSG:6933"   # Cylindrical Equal‑Area (world)
WGS_CRS = "EPSG:4326"

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Base directory for gis data, relative to the script's location
BASE_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'GISData')

class gis:
    def __init__(self, shape_source, field_map=None, crs_fallback=WGS_CRS):
        """
        shape_source : str | Path
            Path to a .zip or a directory containing .shp/.dbf/.shx
        field_map : dict
            Friendly -> raw field names, e.g. {"pop": "POP10"}
        crs_fallback : str
            Use this if .prj is missing.
        """
        src = Path(os.path.join(BASE_DIR, shape_source))


        # 1. Unzip if needed
        if src.suffix == ".zip":
            out_dir = src.with_suffix("")
            if not out_dir.exists():
                zipfile.ZipFile(src).extractall(out_dir)
            src = out_dir

        # 2. Read shapefile
        gdf = gpd.read_file(src)
        if gdf.crs is None:
            gdf = gdf.set_crs(crs_fallback)
        self.original_crs = gdf.crs

        # 3. Field map
        self.field = field_map or {}
        self.field['area']='area_km2'

        # 4. Pre‑project and spatial index
        self.gdf = gdf.to_crs(EA_CRS)
        self.gdf["area_km2"] = self.gdf.geometry.area / 1e6
        self.sidx = self.gdf.sindex

    # --------------------------------------------------

    def _poly_at(self, lat, lon):
        """Return the equal‑area GeoSeries row containing the point or None."""
        pt = Point(lon, lat)                          # EPSG:4326 order = (x,y) = (lon,lat)
        pt = gpd.GeoSeries([pt], crs=WGS_CRS).to_crs(EA_CRS).iloc[0]

        hits = self.sidx.query(pt, predicate="intersects")
        return None if hits.size == 0 else self.gdf.iloc[hits[0]]

    # --------------------------------------------------

    @property
    def gdf_wgs(self):
        return self.gdf.to_crs(WGS_CRS)

    # --------------------------------------------------

    def query(self, lat, lon, *params):
        """
        lat, lon : float  (degrees, WGS‑84)
        params   : one or more attribute names *or* 'area'
        Returns a scalar (one param) or dict (many).
        """
        poly = self._poly_at(lat, lon)
        if poly is None:
            return None

        if not params:
            raise ValueError("Please request at least one parameter")

        out = {}
        for p in params:
            if p == "area":
                out[p] = poly["area_km2"]
            else:
                raw = self.field.get(p, p)            # translate friendly -> raw
                out[p] = poly[raw]

        return out if len(params) > 1 else out[params[0]]
    
    # --------------------------------------------------
    
    def query_many(self, lat_arr, lon_arr, *params):
        if len(lat_arr) != len(lon_arr):
            raise ValueError("lat and lon must be equal‑length")

        # ---- build point GeoDataFrame -----------------------------------
        pts = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(lon_arr, lat_arr, crs=WGS_CRS)
        ).to_crs(self.gdf.crs)

        raw_cols =[self.field.get(p, p) for p in params]      # map if present, else literal
        raw_cols.append("geometry")
        right_df = self.gdf[raw_cols]

        # ---- spatial join ----------------------------------------------
        right_df = self.gdf[raw_cols]
        joined = gpd.sjoin(pts, right_df, how="left", predicate="within").reset_index(drop=True)

        # ---- post‑processing -------------------------------------------
        
        for p in params:
            
            raw = self.field.get(p, p)
            joined[p] = joined[raw]


        return joined if len(params) > 1 else joined[params[0]]
    
    # --------------------------------------------------

    def _add_summary_columns(self, summary_df, basename):
        """
        Adds derived summary columns to self.gdf using a given base name.

        Parameters:
        summary_df (pd.DataFrame): DataFrame with summary stats, same index as self.gdf.
        base (str): Base string for new column names (e.g., 'pop_density').
        """
        for col in summary_df.columns:
            new_col = f"{basename}_{col}"
            self.gdf[new_col] = summary_df[col]

    # --------------------------------------------------

    def _stats_grouped_data(self, grouped_data):
        """
        Summarizes grouped data for each geometry row in self.gdf.

        Parameters
        ----------
        grouped_data : np.ndarray of np.ndarray
            Output from group_data_by_geometry.
        mode : str
            Type of summary. Currently supports:
                - 'stats': count, mean, median, std, min, max

        Returns
        -------
        pd.DataFrame
            Summary statistics or other metrics, indexed to match self.gdf.
        """
        results = []

        for values in grouped_data:
            if len(values) > 0 and sum(np.isfinite(values)) > 0:
                summary = {
                    "N": len(values),
                    "mean": np.nanmean(values),
                    "median": np.nanmedian(values),
                    "std": np.nanstd(values),
                    "min": np.nanmin(values),
                    "max": np.nanmax(values)
                }
            else:
                summary = {
                    "N": 0,
                    "mean": np.nan,
                    "median": np.nan,
                    "std": np.nan,
                    "min": np.nan,
                    "max": np.nan
                }

            results.append(summary)

        return pd.DataFrame(results, index=self.gdf.index)

    # --------------------------------------------------
    
    def join(self,data, calcname = 'calc'):
        """
        Generalized join function using type-based dispatching.

        Parameters
        ----------
        data : object
            Input data object. Supported types:
                - timeseries
                - xarray.DataArray

        Returns
        -------
        pd.DataFrame
            Summary result based on spatial grouping.
        """
        import xarray as xr

        if isinstance(data, timeseries):  # Replace with your actual class
            grouped_data = self.group_data_by_geometry(data.LAT, data.LON, data.data)
            calcname = data.name
            
        elif isinstance(data, xr.DataArray):
            # Try common names for latitude and longitude
            lat_names = ['lat', 'latitude', 'y']
            lon_names = ['lon', 'longitude', 'x']
            name_names = ['long_name', 'name', 'standard_name', 'variable_name']

            lat = lon = None
            for name in lat_names:
                if name in data.coords:
                    lat = data[name].values
                    break
            for name in lon_names:
                if name in data.coords:
                    lon = data[name].values
                    break
            for name in name_names:
                if name in data.attrs:
                    calcname = data.attrs[name]
                    break

            if lat is None or lon is None:
                raise TypeError("xarray.DataArray in gis.join() didn't find recognizable lat/lon coordinates")

            grouped_data = self.group_data_by_geometry(lat, lon, data.data)
        else:
            raise TypeError(f"Unsupported input type for join(): {type(data)}")
        
        stats_df = self._stats_grouped_data(grouped_data)
        self._add_summary_columns(stats_df, calcname)
        return stats_df

    # --------------------------------------------------

    def plot(self, ax=None, column = None, **kwargs):
        """
        Transforms gdf to WGS crs and plots it.

        Parameters:
        ax (matplotlib.axes.Axes, optional): Axis with Cartopy support.
        column: column to use for color plotting
        **kwargs: Passed through to GeoDataFrame.plot.

        Returns:
        matplotlib.axes.Axes: The axis with the plot.
        """

        gdf_wgs = self.gdf_wgs

        if column is None:
            kwargs.setdefault("facecolor", "none")
        else:
            kwargs.setdefault('legend',True)
        kwargs.setdefault("edgecolor", "black")
        kwargs.setdefault("linewidth", 1)
        kwargs.setdefault("cmap", "plasma")

        return gdf_wgs.plot(ax=ax, transform=ccrs.PlateCarree(), column=column, **kwargs)

    # --------------------------------------------------

    def find_row(self,column,value):
        #returns index of the row in the gdf where a column has a specified value

        matches = self.gdf[self.gdf[column] == value]

        if len(matches) == 0:
            raise ValueError(f"No match found for {value} in column '{column}'")
        if len(matches) > 1:
            raise ValueError(f"Multiple matches found for {value} in column '{column}'")

        return matches.index[0]

    # --------------------------------------------------

    def extract_data_in_shape(self, lat_array, lon_array, data_array, row_index, gdf_geom_col='geometry'):
        grouped_data = self.group_data_by_geometry(self, lat_array, lon_array, data_array, gdf_geom_col=gdf_geom_col)
        return grouped_data[row_index]
    
    # --------------------------------------------------

    def group_data_by_geometry(self, lat_array, lon_array, data_array, gdf_geom_col='geometry'):
        """
        Groups data values by the containing geometry in self.gdf_eq using spatial joins.

        Parameters:
            lat_array, lon_array, data_array (np.ndarray): N-Dimensional arrays of lat, lon, and data.
            gdf_geom_col (str): Name of the geometry column in self.gdf_eq.

        Returns:
            np.ndarray: Object array where each element is an np.ndarray of data values within the corresponding geometry.
                indices match self.gdf
        """
        if lat_array.shape != lon_array.shape or lat_array.shape != data_array.shape:
            raise ValueError("lat_array, lon_array, and data_array must have the same shape")

        # Flatten arrays
        lat_flat = lat_array.ravel()
        lon_flat = lon_array.ravel()
        data_flat = data_array.ravel()

        # Project to gdf CRS
        transformer = Transformer.from_crs(WGS_CRS, self.gdf.crs, always_xy=True)
        x_proj, y_proj = transformer.transform(lon_flat, lat_flat)
        points = [Point(x, y) for x, y in zip(x_proj, y_proj)]

        # Spatial join to find containing geometry for each point
        point_gdf = gpd.GeoDataFrame({'data': data_flat}, geometry=points, crs=self.gdf.crs)
        joined = gpd.sjoin(point_gdf, self.gdf[[gdf_geom_col]], how='left', predicate='within')
        joined = joined.dropna(subset=['index_right'])
        joined['index_right'] = joined['index_right'].astype(int)
        
        # Initialize empty object array with one slot per geometry row
        result = np.empty(len(self.gdf), dtype=object)
        for i in range(len(result)):
            result[i] = np.array([])

        # Fill each geometry bin with its corresponding data values
        for idx, group in joined.groupby('index_right'):
            if idx is not np.nan:
                result[idx] = group['data'].values

        return result