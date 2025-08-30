# Project Prompt

Working sample of the prompt to generate the first API call

I am accessing the [EPA AQS API](https://aqs.epa.gov/data/api/) to get air quality data. Using Python and the requests library:

- Write a script that retrieves data from the API and processes it.
- I would like to get data for a specific pollutant (e.g., PM2.5) for a given date range and location (e.g., a specific city or state).
  - List of States are provided at: https://aqs.epa.gov/data/api/list/states?email=test@aqs.api&key=test.
  - List of Counties by State are provided by calling: https://aqs.epa.gov/data/api/list/countiesByState?email=test@aqs.api&key=test&state=06
  - List of available Pollutant parameters are available at: https://aqs.epa.gov/data/api/list/parametersByClass?email=test@aqs.api&key=test&pc=CRITERIA
- Handle any potential errors that may arise during the API request.
- Here is an example of a test api call to retrieve annualData: "https://aqs.epa.gov/data/api/annualData/byCounty?email=test@aqs.api&key=test&param=88101,88502&bdate=20160101&edate=20160229&state=37&county=183"
- Use an .env file to load the following environmental variables API_KEY and API_EMAIL. Note: this is used for best security practices.
- Allow users to input a start date (bdate) and end date (edate) with the request. The format of dates must be YYYYMMDD. Create a helper function to convert the provided dates to the required format and handle cases where dates are separated by characters "-", "/", and "\".