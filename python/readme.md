
# Getting Started - Python

## Set up Environment Variables

> [!IMPORTANT]
> Update the **.env.template** file with the details generated from registering for API access, `API_KEY` & `API_EMAIL`. Save the updated file as .env (remove the .template).

## Install Dependencies

> [!NOTE]
> Using a virtual environment is recommended!

In the desired environment, run `pip install -r requirements.txt` to install the required dependencies.

## Start the Dash/Plotly App

`python app.py`

or

`python3 app.py`

Now, in the browser you can view the Dash application.

By default, the app will run locally at <http://127.0.0.1:8050/>

NOTE: The sample data, `air_quality_data.json`, is pulled from the following date range 2019-01-01 to 2019-12-31 with California and Alameda County as the respective State and County filters.

## Troubleshooting

### Check if API is Available

| Service | Filter | Endpoint   | Required Variables | Optional Variables |
|---------|--------|------------|--------------------|--------------------|
|  | Is the API available for use? | metaData/isAvailable |  | email, key |

**Example:** To check if the API is up and running: <https://aqs.epa.gov/data/api/metaData/isAvailable>

### Request Limits and Terms of Service

> [!IMPORTANT]
> The API has the following limits imposed on request size:
>
> - **Length of time**. All services (except Monitor) must have the end date (edate field) be  in the same year as the begin date (bdate field).
> - **Number of parameters**. Most services allow for the selection of multiple parameter codes (param field). A maximum of 5 parameter codes may be listed in a single request.
>
> Please adhere to the following when using the API.
>
> - **Limit the size of queries**. Our database contains billions of values and you may request more than you intend. If you are unsure of the amount of data, start small and work your way up. We request that you limit queries to 1,000,000 rows of data each. You can use the "observation count" field on the annualData service to determine how much data exists for a time-parameter-geography combination. If you have any questions or need advice, please contact us.
> - **Limit the frequency of queries**. Our system can process a limited load. If scripting requests, please wait for one request to complete before submitting another and do not make more than 10 requests per minute. Also, we request a pause of 5 seconds between requests and adjust accordingly for response time and size.
>
> If you violate these terms, we may disable your account without notice (but we will be in contact via the email address provided).

## Exploratory Data Analysis (EDA)

A Juypter Notebook is available to explore within the `assets` directory.

### Columns Available Within the Sample Dataset

![alt text](assets/images/eda_columns_info.png)

### Heatmap of Correlation Between Variables Within the Sample Dataset

![alt text](assets/images/eda_example.png)
