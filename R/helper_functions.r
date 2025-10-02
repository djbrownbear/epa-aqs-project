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