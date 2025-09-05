
# Getting Started

See the Sign Up section to register an email address for API access.

## Sign Up

This service creates an account or resets a password. Requires validation of registered email address. Email will be sent to the registered address from <aqsdatamart@epa.gov>.

| Service | Filter | Endpoint   | Required Variables | Optional Variables |
|---------|--------|------------|--------------------|--------------------|
| Sign up |        | `signup`   | [`email`](mailto:) |                    |

**Examples:**

Use this service to register as a user. A verification email will be sent to the email account specified. To register using the email address "<myemail@example.com>" create and request this link (**Replace `"myemail@example.com"` in the example with your email address.**):

[https://aqs.epa.gov/data/api/signup?email=myemail@example.com](https://aqs.epa.gov/data/api/signup?email=myemail@example.com)

To reset a key: If the request is made with an email that is already registered, a new key will be issued for that account and emailed to the listed address. Usage is the same as above.

## Set up Environment Variables

Update the **.env.template** file with the details generated from registering for API access, `API_KEY` & `API_EMAIL`. Save the updated file as .env (remove the .template).

## Install Dependencies 
**NOTE: Virtual Environment recommended!**

In the desired environment, run `pip install -r requirements.txt` to install the required dependencies.

## Start the Dash/Plotly App
`python run app.py`

or 

`python3 run app.py`

Now, in the browser you can view the Dash application.

By default, the app will run locally at <http://127.0.0.1:8050/>

NOTE: The sample data, `air_quality_data.json`, is pulled from the following date range 2020-01-02 to 2020-06-30 with California and Alameda County as the respective State and County filters.

## API Examples

Visit https://aqs.epa.gov/aqsweb/documents/data_api.html for more details.

### Sample List of States

```
{
  "Header": [
    {
      "status": "Success",
      "request_time": "2025-08-30T03:44:49-04:00",
      "url": "https://aqs.epa.gov/data/api/list/states?email=test@aqs.api&key=test",
      "rows": 56
    }
  ],
  "Data": [
    {
      "code": "01",
      "value_represented": "Alabama"
    },
    {
      "code": "02",
      "value_represented": "Alaska"
    },
    {
      "code": "04",
      "value_represented": "Arizona"
    },
    {
      "code": "05",
      "value_represented": "Arkansas"
    },
    {
      "code": "06",
      "value_represented": "California"
    },
    {
      "code": "08",
      "value_represented": "Colorado"
    },
    {
      "code": "09",
      "value_represented": "Connecticut"
    },
    {
      "code": "10",
      "value_represented": "Delaware"
    },
    {
      "code": "11",
      "value_represented": "District Of Columbia"
    },
    {
      "code": "12",
      "value_represented": "Florida"
    },
    {
      "code": "13",
      "value_represented": "Georgia"
    },
    {
      "code": "15",
      "value_represented": "Hawaii"
    },
    {
      "code": "16",
      "value_represented": "Idaho"
    },
    {
      "code": "17",
      "value_represented": "Illinois"
    },
    {
      "code": "18",
      "value_represented": "Indiana"
    },
    {
      "code": "19",
      "value_represented": "Iowa"
    },
    {
      "code": "20",
      "value_represented": "Kansas"
    },
    {
      "code": "21",
      "value_represented": "Kentucky"
    },
    {
      "code": "22",
      "value_represented": "Louisiana"
    },
    {
      "code": "23",
      "value_represented": "Maine"
    },
    {
      "code": "24",
      "value_represented": "Maryland"
    },
    {
      "code": "25",
      "value_represented": "Massachusetts"
    },
    {
      "code": "26",
      "value_represented": "Michigan"
    },
    {
      "code": "27",
      "value_represented": "Minnesota"
    },
    {
      "code": "28",
      "value_represented": "Mississippi"
    },
    {
      "code": "29",
      "value_represented": "Missouri"
    },
    {
      "code": "30",
      "value_represented": "Montana"
    },
    {
      "code": "31",
      "value_represented": "Nebraska"
    },
    {
      "code": "32",
      "value_represented": "Nevada"
    },
    {
      "code": "33",
      "value_represented": "New Hampshire"
    },
    {
      "code": "34",
      "value_represented": "New Jersey"
    },
    {
      "code": "35",
      "value_represented": "New Mexico"
    },
    {
      "code": "36",
      "value_represented": "New York"
    },
    {
      "code": "37",
      "value_represented": "North Carolina"
    },
    {
      "code": "38",
      "value_represented": "North Dakota"
    },
    {
      "code": "39",
      "value_represented": "Ohio"
    },
    {
      "code": "40",
      "value_represented": "Oklahoma"
    },
    {
      "code": "41",
      "value_represented": "Oregon"
    },
    {
      "code": "42",
      "value_represented": "Pennsylvania"
    },
    {
      "code": "44",
      "value_represented": "Rhode Island"
    },
    {
      "code": "45",
      "value_represented": "South Carolina"
    },
    {
      "code": "46",
      "value_represented": "South Dakota"
    },
    {
      "code": "47",
      "value_represented": "Tennessee"
    },
    {
      "code": "48",
      "value_represented": "Texas"
    },
    {
      "code": "49",
      "value_represented": "Utah"
    },
    {
      "code": "50",
      "value_represented": "Vermont"
    },
    {
      "code": "51",
      "value_represented": "Virginia"
    },
    {
      "code": "53",
      "value_represented": "Washington"
    },
    {
      "code": "54",
      "value_represented": "West Virginia"
    },
    {
      "code": "55",
      "value_represented": "Wisconsin"
    },
    {
      "code": "56",
      "value_represented": "Wyoming"
    },
    {
      "code": "66",
      "value_represented": "Guam"
    },
    {
      "code": "72",
      "value_represented": "Puerto Rico"
    },
    {
      "code": "78",
      "value_represented": "Virgin Islands"
    },
    {
      "code": "80",
      "value_represented": "Country Of Mexico"
    },
    {
      "code": "CC",
      "value_represented": "Canada"
    }
  ]
}
```

### Sample List of Counties by State (for California)

```
{
  "Header": [
    {
      "status": "Success",
      "request_time": "2025-08-30T02:54:44-04:00",
      "url": "https://aqs.epa.gov/data/api/list/countiesByState?email=test@aqs.api&key=test&state=06",
      "rows": 58
    }
  ],
  "Data": [
    {
      "code": "001",
      "value_represented": "Alameda"
    },
    {
      "code": "003",
      "value_represented": "Alpine"
    },
    {
      "code": "005",
      "value_represented": "Amador"
    },
    {
      "code": "007",
      "value_represented": "Butte"
    },
    {
      "code": "009",
      "value_represented": "Calaveras"
    },
    {
      "code": "011",
      "value_represented": "Colusa"
    },
    {
      "code": "013",
      "value_represented": "Contra Costa"
    },
    {
      "code": "015",
      "value_represented": "Del Norte"
    },
    {
      "code": "017",
      "value_represented": "El Dorado"
    },
    {
      "code": "019",
      "value_represented": "Fresno"
    },
    {
      "code": "021",
      "value_represented": "Glenn"
    },
    {
      "code": "023",
      "value_represented": "Humboldt"
    },
    {
      "code": "025",
      "value_represented": "Imperial"
    },
    {
      "code": "027",
      "value_represented": "Inyo"
    },
    {
      "code": "029",
      "value_represented": "Kern"
    },
    {
      "code": "031",
      "value_represented": "Kings"
    },
    {
      "code": "033",
      "value_represented": "Lake"
    },
    {
      "code": "035",
      "value_represented": "Lassen"
    },
    {
      "code": "037",
      "value_represented": "Los Angeles"
    },
    {
      "code": "039",
      "value_represented": "Madera"
    },
    {
      "code": "041",
      "value_represented": "Marin"
    },
    {
      "code": "043",
      "value_represented": "Mariposa"
    },
    {
      "code": "045",
      "value_represented": "Mendocino"
    },
    {
      "code": "047",
      "value_represented": "Merced"
    },
    {
      "code": "049",
      "value_represented": "Modoc"
    },
    {
      "code": "051",
      "value_represented": "Mono"
    },
    {
      "code": "053",
      "value_represented": "Monterey"
    },
    {
      "code": "055",
      "value_represented": "Napa"
    },
    {
      "code": "057",
      "value_represented": "Nevada"
    },
    {
      "code": "059",
      "value_represented": "Orange"
    },
    {
      "code": "061",
      "value_represented": "Placer"
    },
    {
      "code": "063",
      "value_represented": "Plumas"
    },
    {
      "code": "065",
      "value_represented": "Riverside"
    },
    {
      "code": "067",
      "value_represented": "Sacramento"
    },
    {
      "code": "069",
      "value_represented": "San Benito"
    },
    {
      "code": "071",
      "value_represented": "San Bernardino"
    },
    {
      "code": "073",
      "value_represented": "San Diego"
    },
    {
      "code": "075",
      "value_represented": "San Francisco"
    },
    {
      "code": "077",
      "value_represented": "San Joaquin"
    },
    {
      "code": "079",
      "value_represented": "San Luis Obispo"
    },
    {
      "code": "081",
      "value_represented": "San Mateo"
    },
    {
      "code": "083",
      "value_represented": "Santa Barbara"
    },
    {
      "code": "085",
      "value_represented": "Santa Clara"
    },
    {
      "code": "087",
      "value_represented": "Santa Cruz"
    },
    {
      "code": "089",
      "value_represented": "Shasta"
    },
    {
      "code": "091",
      "value_represented": "Sierra"
    },
    {
      "code": "093",
      "value_represented": "Siskiyou"
    },
    {
      "code": "095",
      "value_represented": "Solano"
    },
    {
      "code": "097",
      "value_represented": "Sonoma"
    },
    {
      "code": "099",
      "value_represented": "Stanislaus"
    },
    {
      "code": "101",
      "value_represented": "Sutter"
    },
    {
      "code": "103",
      "value_represented": "Tehama"
    },
    {
      "code": "105",
      "value_represented": "Trinity"
    },
    {
      "code": "107",
      "value_represented": "Tulare"
    },
    {
      "code": "109",
      "value_represented": "Tuolumne"
    },
    {
      "code": "111",
      "value_represented": "Ventura"
    },
    {
      "code": "113",
      "value_represented": "Yolo"
    },
    {
      "code": "115",
      "value_represented": "Yuba"
    }
  ]
}
```

### Sample List of Pollutant Parameters
```
{
  "Header": [
    {
      "status": "Success",
      "request_time": "2025-08-30T03:40:30-04:00",
      "url": "https://aqs.epa.gov/data/api/list/parametersByClass?email=test@aqs.api&key=test&pc=CRITERIA",
      "rows": 8
    }
  ],
  "Data": [
    {
      "code": "14129",
      "value_represented": "Lead (TSP) LC"
    },
    {
      "code": "42101",
      "value_represented": "Carbon monoxide"
    },
    {
      "code": "42401",
      "value_represented": "Sulfur dioxide"
    },
    {
      "code": "42602",
      "value_represented": "Nitrogen dioxide (NO2)"
    },
    {
      "code": "44201",
      "value_represented": "Ozone"
    },
    {
      "code": "81102",
      "value_represented": "PM10 Total 0-10um STP"
    },
    {
      "code": "85129",
      "value_represented": "Lead PM10 LC FRM/FEM"
    },
    {
      "code": "88101",
      "value_represented": "PM2.5 - Local Conditions"
    }
  ]
}
```