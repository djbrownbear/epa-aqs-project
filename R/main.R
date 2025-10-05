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

aggregation_list <- list(
"by site" = "by_site",
"by county" = "by_county",
"by state" = "by_state",
"by box" = "by_box",
"by monitoring agency" = "by_MA",
"by quality assurance organization" = "by_pqao",
"by core statistical area" = "by_cbsa"
)

services_list <- list(
  "Monitors" = "monitors",
  "Sample Data" = "sampledata",
  "Daily Summary Data" = "dailysummary",
  "Annual Summary Data" = "annualsummary",
  "Quarterly Summary Data" = "quarterlysummary",
  "Quality Assurance - Blanks Data" = "qa_blanks",
  "Quality Assurance - Collocated Assessments" = "qa_collocated_assessments",
  "Quality Assurance - Flow Rate Verifications" = "qa_flowrateverification",
  "Quality Assurance - Flow Rate Audits" = "qa_flowrateaudit",
  "Quality Assurance - One Point Quality Control Raw Data" = "qa_one_point_qc",
  "Quality Assurance - PEP Audits" = "qa_pep_audit",
  "Transaction Sample - AQS Submission data in transaction Format (RD)" = "transactionsample",
  "Quality Assurance - Annual Performance Evaluations" = "qa_annualperformanceeval",
  "Quality Assurance - Annual Performance Evaluations in the AQS Submission transaction format (RD)" = "qa_annualperformanceevaltransaction"
)

# REMINDER FOR FIRST TIME USE!
# You need to edit the .Renvrion file and add the relevant information
API_EMAIL = Sys.getenv("API_EMAIL")
API_KEY = Sys.getenv("API_KEY")

# Check to prevent API calls if user credentials are not found
if (nchar(API_EMAIL) == 0 || nchar(API_KEY) == 0) {
  stop("Credentials not found - please check your .Renviron file")
}

# Function to save JSON to file
save_json_to_file <- function(data, filename) {
  write_json(data, filename, pretty = TRUE, auto_unbox = TRUE)
}

# Main script
cat("EPA AQS Data Download\n")

use_user_settings <- readline(prompt = "Use the existing user settings? (y or n)")

# Set credentials for RAQSAPI
aqs_credentials(username = Sys.getenv("API_EMAIL"), key = Sys.getenv("API_KEY"))

if (use_user_settings == "y"){
  if (!exists("user_settings")) user_settings <- readRDS("user_settings.rds")
  # Prompt for new dates
  new_bdate <- as.Date(format_date_to_yyyymmdd(readline("Enter new begin date (YYYYMMDD): ")), "%Y%m%d")
  new_edate <- as.Date(format_date_to_yyyymmdd(readline("Enter new end date (YYYYMMDD): ")), "%Y%m%d")

  args <- build_args_from_settings(user_settings, bdate = new_bdate, edate = new_edate)
  # Use args for filename construction
  param_safe <- gsub(",", "_", args$parameter)
  bdate_str <- format(args$bdate, "%Y%m%d")
  edate_str <- format(args$edate, "%Y%m%d")
  filename <- paste0(args$service, "_", args$aggregation, "_", param_safe, "_", bdate_str, "_", edate_str, ".json")
} else {
  service <- select_one_option(services_list, "Select a service:")
  aggregation <- select_one_option(aggregation_list, "Select aggregation type: ")

  state <- readline(prompt = "Enter state FIPS code (2 digits, e.g., 06): ")
  state <- sprintf("%02s", state)

  county <- NULL

  if (aggregation %in% c("by_county", "by_site")) {
    county <- readline(prompt = "Enter county FIPS code (3 digits, e.g., 001): ")
    county <- sprintf("%03s", county)
  }

  # Pollutant selection
  # TODO - fix to allow multiple parameters
  param <- select_multiple_options(pollutants, "Select pollutant(s) by number:")

  bdate <- readline(prompt = "Enter begin date (YYYYMMDD): ")
  edate <- readline(prompt = "Enter end date (YYYYMMDD): ")
  bdate <- as.Date(format_date_to_yyyymmdd(bdate), format = "%Y%m%d")
  edate <- as.Date(format_date_to_yyyymmdd(edate), format = "%Y%m%d")

  args <- build_aqs_args(
    service,
    aggregation,
    param,
    bdate,
    edate,
    state,
    county
  )
  param_safe <- gsub(",", "_", param)
  bdate_str <- format(bdate, "%Y%m%d")
  edate_str <- format(edate, "%Y%m%d")
  filename <- paste0(service, "_", aggregation, "_", param_safe, "_", bdate_str, "_", edate_str, ".json")
}
result <- do.call(call_aqs_service, args)
cat("Retrieving data...")

for (i in 1:length(result)){
  # Dynamically handle saving based on presence of Header and Data
  if (!is.null(result[[i]]$Header) && !is.null(result[[i]]$Data)) {
    # return_header = TRUE: save both header and data
    res <- result[[i]]
    res$Header$url <- mask_query_params(res$Header$url, c("email", "key"))
    # When multiple results are returned (e.g., one per year), update the filename to indicate the specific year being saved
    query_params <- get_query_params(res$Header$url, c("bdate", "edate"))
    bdate <- query_params$bdate
    edate <- query_params$edate
    filename <- paste0(service, "_", aggregation, "_", param_safe, "_", bdate, "_", edate, ".json")
    save_json_to_file(list(Header = res$Header, Data = res$Data), filename)
  } else if (!is.null(result$Data)) {
    # return_header = FALSE: save just data
    save_json_to_file(result$Data, filename)
  } else {
    # fallback: try to save the result as-is
    save_json_to_file(result, filename)
  }
}

cat("DataFrame head:\n")
print(head(result))

user_settings <- list(
  service = service,
  aggregation = aggregation,
  stateFIPS = state,
  parameter = param
)

if (use_user_settings=="y"){
  user_settings$bdate <- new_bdate
  user_settings$edate <- new_edate
} else {
  user_settings$bdate <- bdate
  user_settings$edate <- edate
}

saveRDS(user_settings, "user_settings.rds")

cat("Script completed\n")
