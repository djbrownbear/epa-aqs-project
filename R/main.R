source("helper_functions.r")

# Load required libraries
library(RAQSAPI)
library(lubridate)
library(jsonlite)

# Pollutant options (single source of truth)
pollutants <- list(
  "Lead (TSP) LC" = 14129,
  "Carbon monoxide" = 42101,
  "Sulfur dioxide" = 42401,
  "Nitrogen dioxide (NO2)" = 42602,
  "Ozone" = 44201,
  "PM10 Total 0-10um STP" = 81102,
  "Lead PM10 LC FRM/FEM" = 85129,
  "PM2.5 - Local Conditions" = 88101
)

# REMINDER FOR FIRST TIME USE!
# You need to edit the .Renvrion file and add the relevant information
API_EMAIL = Sys.getenv("API_EMAIL")
API_KEY = Sys.getenv("API_KEY")

# Function to format date to YYYYMMDD
format_date_to_yyyymmdd <- function(date_str) {
  # Accepts YYYYMMDD, YYYY-MM-DD, MM-DD-YYYY, YYYY/MM/DD, MM/DD/YYYY
  date_str <- gsub("/|\\\\", "-", date_str)
  # If already 8 digits, assume it's YYYYMMDD
  if (grepl("^\\d{8}$", date_str)) {
    return(date_str)
  }
  # Try parsing as YYYY-MM-DD or MM-DD-YYYY
  date_obj <- suppressWarnings(ymd(date_str))
  if (is.na(date_obj)) date_obj <- suppressWarnings(mdy(date_str))
  if (is.na(date_obj)) stop("Date format must be 'YYYYMMDD', 'YYYY-MM-DD', 'MM-DD-YYYY', 'YYYY/MM/DD', or 'MM/DD/YYYY'.")
  format(date_obj, "%Y%m%d")
}

# Function to mask API key and email in data
# NOT necessary if return_header = FALSE
mask_api_key_and_email <- function(data) {
  if (!is.null(data$Header$url$key)) data$Header$url$key <- "***MASKED***"
  if (!is.null(data$Header$url$email)) data$Header$url$email <- "***MASKED***"
  return(data)
}

# Function to save JSON to file
save_json_to_file <- function(data, filename) {
  write_json(data, filename, pretty = TRUE, auto_unbox = TRUE)
}

# Main script
cat("EPA AQS Data Download\n")

# Set credentials for RAQSAPI
aqs_credentials(username = Sys.getenv("API_EMAIL"), key = Sys.getenv("API_KEY"))

service <- readline(prompt = "Enter service (e.g., annualsummary, dailysummary, sampledata, etc.): ")
aggregation <- readline(prompt = "Enter 'by' (e.g., by_county, by_state, by_site, etc.): ")

state <- readline(prompt = "Enter state FIPS code (2 digits, e.g., 06): ")
state <- sprintf("%02s", state)

# Pollutant selection
cat("Select pollutant(s) by number (comma-separated for multiple):\n")
pollutant_names <- names(pollutants)
for (i in seq_along(pollutant_names)) {
  cat(sprintf("  %d. %s (%d)\n", i, pollutant_names[i], pollutants[[i]]))
}
selected <- readline(prompt = "Enter your choice(s): ")
selected_idxs <- as.integer(unlist(strsplit(selected, ",")))
selected_idxs <- selected_idxs[!is.na(selected_idxs) & selected_idxs >= 1 & selected_idxs <= length(pollutants)]
if (length(selected_idxs) == 0) {
  stop("Invalid selection. Exiting.")
}
param <- as.character(unname(unlist(pollutants[selected_idxs])))

bdate <- readline(prompt = "Enter begin date (YYYYMMDD): ")
edate <- readline(prompt = "Enter end date (YYYYMMDD): ")
bdate <- as.Date(format_date_to_yyyymmdd(bdate),format='%Y%m%d')
edate <- as.Date(format_date_to_yyyymmdd(edate),format='%Y%m%d')

result <- call_aqs_service(
  service = service,
  aggregation = aggregation,
  parameter = param,
  bdate = bdate,
  edate = edate,
  stateFIPS = state,
  return_header = FALSE
)

param_safe <- gsub(",", "_", param)
filename <- paste0(service,"_", aggregation, "_", param_safe,"_", bdate,"_", edate,".json")

# Dynamically handle saving based on presence of Header and Data
if (!is.null(result$Header) && !is.null(result$Data)) {
  # return_header = TRUE: save both header and data
  result$Header$url <- mask_api_key_and_email(result$Header$url)
  save_json_to_file(list(Header = result$Header, Data = result$Data), filename)
} else if (!is.null(result$Data)) {
  # return_header = FALSE: save just data
  save_json_to_file(result$Data, filename)
} else {
  # fallback: try to save the result as-is
  save_json_to_file(result, filename)
}

cat("DataFrame head:\n")
print(head(result))
cat("Script completed\n")