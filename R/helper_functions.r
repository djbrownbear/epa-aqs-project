call_aqs_service <- function(service, aggregation, ..., return_header = TRUE) {
  # service: e.g. "annualsummary", "dailysummary", "sampledata", etc.
  # aggregation: e.g. "by_county", "by_state", "by_site", etc.
  # ...: named arguments for the API call (parameter, bdate, edate, stateFIPS, etc.)
  # return_header: whether to return the header (default TRUE)

  # Build the function name
  fn_name <- paste0("aqs_", service, "_", aggregation)

  # Check if the function exists
  if (!exists(fn_name, mode = "function")) {
    stop(paste("Function", fn_name, "does not exist in RAQSAPI."))
  }

  # Build argument list
  args <- list(...)

  if (grepl("by_county", aggregation)) {
    county <- readline(prompt = "Enter county FIPS code (3 digits, e.g., 001): ")
    county <- sprintf("%03s", county)
    args$countycode <- county
  }
  args$return_header <- return_header

  # Call the function dynamically
  result <- do.call(fn_name, args)
  return(result)
}

# Example usage:
# result <- call_aqs_service(
#   service = "sampledata",
#   aggregation = "by_state",
#   parameter = "14129",
#   bdate = "20190101",
#   edate = "20191231",
#   stateFIPS = "06",
# )

select_one_option <- function(options, prompt_text = "Select one option by number:") {
  cat(prompt_text, "\n")
  options_names <- names(options)
  for (i in seq_along(options)) {
    cat(sprintf("  %d. %s\n", i, options_names[i]))
  }
  selected <- readline(prompt = "Enter your choice: ")
  selected_idx <- as.integer(selected)
  if (is.na(selected_idx) || selected_idx < 1 || selected_idx > length(options)) {
    stop("Invalid selection. Exiting.")
  }
  return(options[[selected_idx]])
}

select_multiple_options <- function(options, prompt_text) {
  cat(prompt_text, "\n")
  option_names <- names(options)
  for (i in seq_along(option_names)) {
    cat(sprintf("  %d. %s (%s)\n", i, option_names[i], options[[i]]))
  }
  selected <- readline("Enter your choice(s) (comma-separated): ")
  selected_idxs <- as.integer(unlist(strsplit(selected, ",")))
  selected_idxs <- selected_idxs[!is.na(selected_idxs) & selected_idxs >= 1 & selected_idxs <= length(options)]
  if (length(selected_idxs) == 0) stop("Invalid selection. Exiting.")
  as.character(unname(unlist(options[selected_idxs])))
}

build_aqs_args <- function(service, aggregation, param, bdate, edate, state, county = NULL) {
  args <- list(
    service = service,
    aggregation = aggregation,
    parameter = param,
    bdate = bdate,
    edate = edate,
    stateFIPS = state
  )
  if (aggregation %in% c("by_county", "by_site") && !is.null(county)) {
    args$countycode <- county
  }
  args
}

build_args_from_settings <- function(user_settings, bdate = NULL, edate = NULL) {
  args <- list(
    service = user_settings$service,
    aggregation = user_settings$aggregation,
    parameter = user_settings$parameter,
    bdate = if (!is.null(bdate)) bdate else user_settings$bdate,
    edate = if (!is.null(edate)) edate else user_settings$edate,
    stateFIPS = user_settings$stateFIPS
  )
  if (!is.null(user_settings$county) && user_settings$aggregation %in% c("by_county", "by_site")) {
    args$countycode <- user_settings$county
  }
  args
}

mask_query_params <- function(url, params, mask = "**MASKED**") {
    for (param in params) {
      # Regex: lookbehind for "param=" then replace until next "&" or end
      pattern <- paste0("(?<=", param, "=)[^&]+")
      url <- gsub(pattern, mask, url, perl = TRUE)
    }
    return(url)
}

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