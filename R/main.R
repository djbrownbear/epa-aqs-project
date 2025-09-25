# Load required libraries
library(httr)
library(jsonlite)
library(readr)
library(dplyr)
library(lubridate)

# Define pollutants
pollutants <- list(
  "Carbon Monoxide" = 42101,
  "Lead PM10" = 81102,
  "PM2.5" = 88101,
  "Ozone" = 44201,
  "Nitrogen Dioxide" = 42602,
  "Sulfur Dioxide" = 42401,
  "PM10" = 81101
)

# REMINDER FOR FIRST TIME USE!
# You need to edit the .Renvrion file and add the relevant information
API_EMAIL = Sys.getenv("API_EMAIL")
API_KEY = Sys.getenv("API_KEY")

print(API_EMAIL)
print(API_KEY)

# Function to format date to YYYYMMDD
format_date_to_yyyymmdd <- function(date_str) {
  date_str <- gsub("/|\\\\", "-", date_str)
  tryCatch({
    date_obj <- ymd(date_str)
    if (is.na(date_obj)) date_obj <- mdy(date_str)
    if (is.na(date_obj)) stop("Invalid date format.")
    format(date_obj, "%Y%m%d")
  }, error = function(e) {
    stop("Date format must be 'YYYY-MM-DD', 'MM-DD-YYYY', 'YYYY/MM/DD', or 'MM/DD/YYYY'.")
  })
}

# Function to mask API key and email in data
mask_api_key_and_email <- function(data) {
  if (!is.null(data$key)) data$key <- "***MASKED***"
  if (!is.null(data$email)) data$email <- "***MASKED***"
  return(data)
}

# Function to save JSON to file
save_json_to_file <- function(data, filename) {
  write_json(data, filename, pretty = TRUE, auto_unbox = TRUE)
}

# Function to load JSON to dataframe
load_json_to_dataframe <- function(filename, record_path = "Data") {
  data <- fromJSON(filename)
  if (!is.null(data[[record_path]])) {
    df <- as.data.frame(data[[record_path]])
    return(df)
  } else {
    stop("Record path not found in JSON.")
  }
}

# Function to get air quality data
get_air_quality_data <- function(pollutant, start_date, end_date, base_url = "https://aqs.epa.gov/data/api/annualData/byCounty", state = "06", county = "001", email = API_EMAIL , key = API_KEY) {
  if (key == "") stop("API_KEY is not set in the environment variables.")
  params <- list(
    email = email,
    key = key,
    param = pollutant,
    state = state,
    county = county,
    bdate = format_date_to_yyyymmdd(start_date),
    edate = format_date_to_yyyymmdd(end_date)
  )
  res <- GET(base_url, query = params)
  if (status_code(res) != 200) {
    stop(paste("HTTP error:", status_code(res)))
  }
  data <- content(res, as = "parsed", type = "application/json")
  return(data)
}

# Main script
cat("Available pollutants:\n")
for (name in names(pollutants)) {
  cat(paste(name, ":", pollutants[[name]], "\n"))
}
selected_name <- readline(prompt = "Enter pollutant name from the list above: ")
pollutant <- pollutants[[selected_name]]
if (is.null(pollutant)) {
  stop("Invalid pollutant name. Please choose from the list.")
}
start_date <- readline(prompt = "Enter start date (YYYY-MM-DD or MM-DD-YYYY): ")
end_date <- readline(prompt = "Enter end date (YYYY-MM-DD or MM-DD-YYYY): ")
data <- get_air_quality_data(pollutant, start_date, end_date)
filename <- paste0("air_quality_data_", pollutant, ".json")
data <- mask_api_key_and_email(data)
save_json_to_file(data, filename)
df <- load_json_to_dataframe(filename, record_path = "Data")
cat("DataFrame head:\n")
print(head(df))
