import pandas as pd
import requests
from io import StringIO
import re

def ActinicFlux(latitude, longitude, date, timeStamp, kmAltitude, ozone = 300, groundLevel_km = 0, albedo = 0.1):
    """
    Fetches UV radiation data from the NCAR TUV calculator and returns it as a DataFrame.
    
    Parameters:
    -----------
    latitude : float
        Latitude for the calculation. Should be a float between -90 and 90. North is positive.
        
    longitude : float
        Longitude for the calculation. Should be a float between -180 and 180. East is positive.
        
    date : str
        Date for the calculation in 'YYYYMMDD' format.
        
    timeStamp : str
        Time for the calculation in 'HH:MM:SS' format.
        timeStamp must be UTC
        
    kmAltitude : float
        Altitude in kilometers for the measurement point. Should be a non-negative float.

    ozone (optional): float
        thickness of the ozone layer in Dobson units
        
    groundLevel_km (optional): float
        height of ground level above seal level, kilometers.

    albedo (optional): float
        reflectivity of surface. white = 1, black = 0

        
    Returns:
    --------
    pd.DataFrame or None
        A DataFrame containing the UV radiation data if the API call is successful.
        Returns None if the API call fails.
        
    Example:
    --------
    >>> df = DP_TUV_ActinicFlux(latitude=0, longitude=0, date='20150630', timeStamp='12:00:00', kmAltitude=0)
    >>> print(df)
    
    Notes:
    ------
    - The function assumes that certain other parameters (e.g., 'wStart', 'ozone', etc.) are set to default values.
    - Ensure that you have access to the internet and that the NCAR TUV calculator is online and operational.
    """
    
    base_url = "https://www.acom.ucar.edu/cgi-bin/acom/TUV/V5.3/tuv"
    
    def get_time_decimal(sTime):
      try:
          hours, minutes, seconds = map(int, sTime.split(":"))
          decimal_time = hours + minutes / 60 + seconds / 3600
          return decimal_time
      except ValueError:
          print("Invalid time format. Please use HH:MM:SS")
          return None

    params = {
        'wStart': 280,
        'wStop': 900,
        'wIntervals': 620,
        'inputMode': 0,
        'latitude': latitude,
        'longitude': longitude,
        'date': date,
        'timeStamp': timeStamp,
        'ozone': ozone,
        'zenith':0,
        'albedo': albedo,
        'gAltitude': groundLevel_km,
        'mAltitude': kmAltitude,
        'taucld': 0.00,
        'zbase': 4.0,
        'ztop': 5.0,
        'tauaer': 0.0,
        'ssaaer': 0.990,
        'alpha': 1,
        'outputMode': 4,
        'nStreams': -2,
        'time':get_time_decimal(timeStamp),
        'dirsun': 1.0,
        'difdn': 1.0,
        'difup': 1.0
    }

    # Construct the full URL for debugging
    #full_url = requests.Request('GET', base_url, params=params).prepare().url
    #print(f"Full URL: {full_url}")
    
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        content = response.text
        #print(content)  # Add this line for debugging
        data_str = content.split("\n")[23:]  # Skip first 23 lines
        data_str = "\n".join(data_str)
        
        column_names = ["LOWER WVL", "UPPER WVL", "DIRECT", "DIFFUSE DOWN", "DIFFUSE UP", "TOTAL"]
        
        df = pd.read_csv(StringIO(data_str), header=None, sep='\s+', names=column_names)
        
        return df
    else:
        print(f"Failed to get data: {response.status_code}")
        return None
    
def jValues(latitude, longitude, date, timeStamp, kmAltitude, ozone = 300, groundLevel_km = 0, albedo = 0.1):

    base_url = "https://www.acom.ucar.edu/cgi-bin/acom/TUV/V5.3/tuv"
    
    def get_time_decimal(sTime):
      try:
          hours, minutes, seconds = map(int, sTime.split(":"))
          decimal_time = hours + minutes / 60 + seconds / 3600
          return decimal_time
      except ValueError:
          print("Invalid time format. Please use HH:MM:SS")
          return None

    params = {
        'wStart': 280,
        'wStop': 900,
        'wIntervals': 620,
        'inputMode': 0,
        'latitude': latitude,
        'longitude': longitude,
        'date': date,
        'timeStamp': timeStamp,
        'ozone': ozone,
        'zenith':0,
        'albedo': albedo,
        'gAltitude': groundLevel_km,
        'mAltitude': kmAltitude,
        'taucld': 0.00,
        'zbase': 4.0,
        'ztop': 5.0,
        'tauaer': 0.0,
        'ssaaer': 0.990,
        'alpha': 1,
        'outputMode': 2,
        'nStreams': -2,
        'time':get_time_decimal(timeStamp),
        'dirsun': 1.0,
        'difdn': 1.0,
        'difup': 1.0
    }

    # Construct the full URL for debugging
    #full_url = requests.Request('GET', base_url, params=params).prepare().url
    #print(f"Full URL: {full_url}")
    
    response = requests.get(base_url, params=params)


    if response.status_code == 200:
        content = response.text
        lines = content.splitlines()
        # locate the start of the photolysis-rate table
        start_idx = None
        for i, line in enumerate(lines):
            #print(line)
            if "PHOTOLYSIS RATES" in line.upper():
                start_idx = i + 1  # data starts after this line
                break

        if start_idx is not None:
            # parse lines until blank line or non-matching format
            data = []
            float_re = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
            pat = re.compile(rf"^\s*(\d+)\s+(.*?)\s+({float_re})\s*$")

            for line in lines[start_idx:]:
                if not line.strip():
                    break
                m = pat.match(line)
                if not m:
                    # stop if we’ve reached another section
                    # (or continue to skip stray lines—choose your preference)
                    break
                idx, reaction, rate = m.groups()
                data.append({"index": int(idx), "reaction": reaction.strip(), "rate_s^-1": float(rate)})

            df = pd.DataFrame(data).set_index('index')
        
            return df
    else:
        print(f"Failed to get data: {response.status_code}")
        return None
    
def jNO2(latitude, longitude, date, timeStamp, kmAltitude, ozone = 300, groundLevel_km = 0, albedo = 0.1):
    df = jValues(latitude, longitude, date, timeStamp, kmAltitude, ozone, groundLevel_km, albedo)
    if df is not None:
        try:
            if 6 in df.index:
                pos = df.index.get_loc(6)
                jno2 = df.iloc[pos]['rate_s^-1']
            else:
                print("NO2 photolysis rate not found in the data.")
                return None
            return jno2
        except IndexError:
            print("NO2 photolysis rate not found in the data.")
            return None
    else:
        return None


if __name__ == '__main__':
    j = jNO2(latitude=0, longitude=0, date='20150630', timeStamp='12:00:00', kmAltitude=0)
    print(j)