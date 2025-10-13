import requests
import inspect
import os
import json
import pandas as pd

from .timeseries import timeseries

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'EPAData')

STATES = {
    "Utah" : 49
}

UTAH_COUNTIES = {
    "Beaver": "001",
    "Box Elder": "003",
    "Cache": "005",
    "Carbon": "007",
    "Daggett": "009",
    "Davis": "011",
    "Duchesne": "013",
    "Emery": "015",
    "Garfield": "017",
    "Grand": "019",
    "Iron": "021",
    "Juab": "023",
    "Kane": "025",
    "Millard": "027",
    "Morgan": "029",
    "Piute": "031",
    "Rich": "033",
    "Salt Lake": "035",
    "San Juan": "037",
    "Sanpete": "039",
    "Sevier": "041",
    "Summit": "043",
    "Tooele": "045",
    "Uintah": "047",
    "Utah": "049",
    "Wasatch": "051",
    "Washington": "053",
    "Wayne": "055",
    "Weber": "057"
}

UTAH_SITES = {
    "Hawthorne":"3006",
    "Harrisville":"1003",
}

PARAMETERS = {
    "Mixing Height": "61301",
    "Wind Speed - Scalar":"61101",
    "Wind Direction - Scalar":"61102",
    "Outdoor Temperature":"62101",
    "Relative Humidity":"62201",
    "Average Ambient Temperature":"68105",
    "Average Ambient Pressure":"68108",
    "Nitric oxide (NO)":"42601",
    "Total NMOC":"43102",
    "Solar radiation":"63301",
    "Lead (TSP) LC": "14129",
    "Carbon monoxide": "42101",
    "Sulfur dioxide": "42401",
    "Nitrogen dioxide (NO2)": "42602",
    "Ozone": "44201",
    "PM10 Total 0-10um STP": "81102",
    "Lead PM10 LC FRM-FEM": "85129",
    "PM25 - Local Conditions": "88101",
    "Carbon disulfide": "42153",
    "Sum of PAMS target compounds": "43000",
    "Total NMOC (non-methane organic compound)": "43102",
    "Ethane": "43202",
    "Ethylene": "43203",
    "Propane": "43204",
    "Propylene": "43205",
    "Acetylene": "43206",
    "Freon 113": "43207",
    "Freon 114": "43208",
    "Ethyl acetate": "43209",
    "n-Butane": "43212",
    "Isobutane": "43214",
    "trans-2-Butene": "43216",
    "cis-2-Butene": "43217",
    "1,3-Butadiene": "43218",
    "n-Pentane": "43220",
    "Isopentane": "43221",
    "1-Pentene": "43224",
    "trans-2-Pentene": "43226",
    "cis-2-Pentene": "43227",
    "3-Methylpentane": "43230",
    "n-Hexane": "43231",
    "n-Heptane": "43232",
    "n-Octane": "43233",
    "n-Nonane": "43235",
    "n-Decane": "43238",
    "Cyclopentane": "43242",
    "Isoprene": "43243",
    "2,2-Dimethylbutane": "43244",
    "2,4-Dimethylpentane": "43247",
    "Cyclohexane": "43248",
    "3-Methylhexane": "43249",
    "2,2,4-Trimethylpentane": "43250",
    "2,3,4-Trimethylpentane": "43252",
    "3-Methylheptane": "43253",
    "alpha-Pinene": "43256",
    "beta-Pinene": "43257",
    "Methylcyclohexane": "43261",
    "Methylcyclopentane": "43262",
    "2-Methylhexane": "43263",
    "1-Butene": "43280",
    "2,3-Dimethylbutane": "43284",
    "2-Methylpentane": "43285",
    "2,3-Dimethylpentane": "43291",
    "ISO-BUTYL ALCOHOL": "43306",
    "tert-butyl alcohol": "43309",
    "3-Chloropropene": "43335",
    "Methyl tert-butyl ether": "43372",
    "Tert-amyl methyl ether": "43373",
    "tert-Butyl ethyl ether": "43396",
    "Ethyl acrylate": "43438",
    "Methyl methacrylate": "43441",
    "Vinyl acetate": "43447",
    "Formaldehyde": "43502",
    "Acetaldehyde": "43503",
    "Acrolein - Unverified": "43505",
    "Acrolein - Verified": "43509",
    "Acetone": "43551",
    "Methyl ethyl ketone": "43552",
    "Methyl isobutyl ketone": "43560",
    "Acetonitrile": "43702",
    "Acrylonitrile": "43704",
    "Chloromethane": "43801",
    "Dichloromethane": "43802",
    "Chloroform": "43803",
    "Carbon tetrachloride": "43804",
    "Bromoform": "43806",
    "Trichlorofluoromethane": "43811",
    "Chloroethane": "43812",
    "1,1-Dichloroethane": "43813",
    "Methyl chloroform": "43814",
    "Ethylene dichloride": "43815",
    "Tetrachloroethylene": "43817",
    "1,1,2,2-Tetrachloroethane": "43818",
    "Bromomethane": "43819",
    "1,1,2-Trichloroethane": "43820",
    "1,1,2-Trichloro-1,2,2-trifluoroethane": "43821",
    "Dichlorodifluoromethane": "43823",
    "Trichloroethylene": "43824",
    "1,1-Dichloroethylene": "43826",
    "Bromodichloromethane": "43828",
    "1,2-Dichloropropane": "43829",
    "trans-1,3-Dichloropropene": "43830",
    "cis-1,3-Dichloropropene": "43831",
    "Dibromochloromethane": "43832",
    "Chloroprene": "43835",
    "Bromochloromethane": "43836",
    "trans-1,2-Dichloroethylene": "43838",
    "cis-1,2-Dichloroethene": "43839",
    "Ethylene dibromide": "43843",
    "Hexachlorobutadiene": "43844",
    "Dichlorotetrafluoroethane": "43852",
    "Vinyl chloride": "43860",
    "Vinyl bromide": "43861",
    "n-Undecane": "43954",
    "2-Methylheptane": "43960",
    "mp Xylene": "45109",
    "Benzene": "45201",
    "Toluene": "45202",
    "Ethylbenzene": "45203",
    "o-Xylene": "45204",
    "1,3,5-Trimethylbenzene": "45207",
    "1,2,4-Trimethylbenzene": "45208",
    "n-Propylbenzene": "45209",
    "Isopropylbenzene": "45210",
    "o-Ethyltoluene": "45211",
    "m-Ethyltoluene": "45212",
    "p-Ethyltoluene": "45213",
    "m-Diethylbenzene": "45218",
    "p-Diethylbenzene": "45219",
    "Styrene": "45220",
    "1,2,3-Trimethylbenzene": "45225",
    "Chlorobenzene": "45801",
    "1,2-Dichlorobenzene": "45805",
    "1,3-Dichlorobenzene": "45806",
    "1,4-Dichlorobenzene": "45807",
    "Benzyl chloride": "45809",
    "1,2,4-Trichlorobenzene": "45810",
    "2-chlorotoluene": "45811",
    "1,4-Dioxane": "46201",
}




class epa():
    def __init__(self, **kwargs):
        self.credentials = self._get_credentials()
        
        # Define defaults
        defaults = {
            "state": STATES['Utah'],
            "county": UTAH_COUNTIES['Salt Lake'],
            "site": UTAH_SITES["Hawthorne"],
            "bdate" : "20240701",
            "edate" : "20240831",
            "param" : PARAMETERS["Ozone"]
        }

        # initialize class with any provided kwargs
        defaults.update(kwargs)
        for key, value in defaults.items():
            setattr(self, key, value)

    def list_parameter_classes(self):
        endpoint = "list/classes"
        url = f'https://aqs.epa.gov/data/api/{endpoint}?email={self.credentials["email"]}&key={self.credentials["key"]}'
        resp_data = self._call_api(url)
        for l in resp_data:
            print(f"{l['code']}: {l['value_represented']}")

        return resp_data

    def list_parameters(self,param_class="ALL"):
        endpoint = "list/parametersByClass"
        url = f'https://aqs.epa.gov/data/api/{endpoint}?email={self.credentials["email"]}&key={self.credentials["key"]}'
        
        url += f'&pc={param_class}'

        resp_data = self._call_api(url)
        for l in resp_data:
            print(f"{l['code']}: {l['value_represented']}")

        return resp_data

    def monitors_by_state(self,show=False):
        endpoint = "monitors/byState"
        url = f'https://aqs.epa.gov/data/api/{endpoint}?email={self.credentials["email"]}&key={self.credentials["key"]}'
        
        url += f'&param={self.param}'
        url += f'&bdate={self.bdate}'
        url += f'&edate={self.edate}'
        url += f'&state={self.state}'
        resp_data = self._call_api(url)

        if show:
            print(json.dumps(resp_data,indent=4))

        return resp_data
    
    def monitors_by_county(self,show=False):
        endpoint = "monitors/byCounty"
        url = f'https://aqs.epa.gov/data/api/{endpoint}?email={self.credentials["email"]}&key={self.credentials["key"]}'
        
        url += f'&param={self.param}'
        url += f'&bdate={self.bdate}'
        url += f'&edate={self.edate}'
        url += f'&state={self.state}'
        url += f'&county={self.county}'
        resp_data = self._call_api(url)

        if show:
            print(json.dumps(resp_data,indent=4))

        return resp_data

    def sampledata_df(self, show=False):
        endpoint = "sampleData/bySite"
        url = f'https://aqs.epa.gov/data/api/{endpoint}?email={self.credentials["email"]}&key={self.credentials["key"]}'
        
        url += f'&param={self.param}'
        url += f'&bdate={self.bdate}'
        url += f'&edate={self.edate}'
        url += f'&state={self.state}'
        url += f'&county={self.county}'
        url += f'&site={self.site}'

        if show:
            print("Calling ",url)

        resp_data = self._call_api(url, show=False)
        
        try:
            if resp_data:
                df = pd.json_normalize(resp_data)
                return df
            else:
                raise ValueError("No response data returned from _call_api.")
        except Exception as e:
            print(f"Failed to process API response: {e}")
            return pd.DataFrame()  # Return an empty DataFrame in case of failure

    
    
    def _call_api(self,url,show=False):
        if show: print(f"calling {url}")
        
        try:
            response = requests.get(url)

            # Raise an exception for non-2xx status codes
            response.raise_for_status()

            # Parse the JSON response
            response_json = response.json()

            # Check if 'data' is in the response
            if 'Data' in response_json:
                # Pretty-print the 'data' portion
                if show:
                    print("Data Portion of the JSON Response:")
                    print(json.dumps(response_json['Data'], indent=4))
                return response_json['Data']
            else:
                print("No 'data' key found in the response.")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def _get_credentials(self):
        # Find the outermost script (__main__)
        for frame in inspect.stack():
            module = inspect.getmodule(frame.frame)
            if module and module.__name__ == "__main__":
                parent_script = module.__file__
                break
        else:
            raise RuntimeError("Could not determine the outermost script (__main__).")
        
        parent_dir = os.path.dirname(os.path.abspath(parent_script))
        credential_path = os.path.join(parent_dir,"EPA_login.txt")

        if not os.path.exists(credential_path):
            raise FileNotFoundError(f"Credential file '{credential_path}' not found. Register your email with the EPA and create the credential file. First line: email, second line: key")
        
        try:
            with open(credential_path, 'r') as file:
                lines = file.readlines()
                if len(lines) < 2:
                    raise ValueError("Credential file must contain at least two lines: email and key.")

                email = lines[0].strip()
                key = lines[1].strip()
                # Validate the email format (basic validation)
                if "@" not in email or "." not in email.split("@")[-1]:
                    raise ValueError(f"Invalid email format in the credential file: {email}")
        except Exception as e:
            raise RuntimeError(f"Error reading credentials: {e}")
        return {'email':email,'key':key}

