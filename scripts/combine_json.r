library(jsonlite)
library(dplyr)
library(zoo)

# Read and flatten a single JSON file
read_flatten_json <- function(filepath, flatten_header = TRUE) {
  j <- fromJSON(filepath)
  header <- if (is.list(j$Header) && length(j$Header) == 1) j$Header[[1]] else j$Header
  data <- as.data.frame(j$Data)
  if (flatten_header && !is.null(header)) {
    for (name in names(header)) {
      data[[name]] <- header[[name]]
    }
  }
  data
}

# Combine all matching JSON files in a directory
combine_json_files <- function(data_dir, pattern = "^*\\.json$", flatten_header = TRUE) {
  files <- list.files(data_dir, pattern = pattern, full.names = TRUE)
  if (length(files) == 0) stop("No matching files found.")
  all_data <- lapply(files, read_flatten_json, flatten_header = flatten_header)
  bind_rows(all_data)
}

# Add end-of-quarter date column
add_quarter_end_date <- function(df, year_col = "year", quarter_col = "quarter", date_col = "date") {
  df[[year_col]] <- as.integer(df[[year_col]])
  df[[quarter_col]] <- as.integer(df[[quarter_col]])
  df$yearqtr <- paste(df[[year_col]], "Q", df[[quarter_col]], sep = "")
  df[[date_col]] <- as.Date(as.yearqtr(df$yearqtr, format = "%Y Q%q"), frac = 1)
  df$yearqtr <- NULL
  df
}

# Main function
main <- function(data_dir = NULL, pattern = NULL, output_file = NULL) {
  if (is.null(data_dir)) data_dir <- readline("Enter the directory containing JSON files: ")
  if (is.null(pattern)) pattern <- {
    cat("Enter pattern to match start of filename\n i.e. quarterlysummary or press Enter to leave blank\n")
    readline("Input: ")
    }
  if (pattern == "") {
    pattern <- "*\\.json$"
  }
  if (is.null(output_file)) output_file <- paste0("combined_data_", format(Sys.Date(), "%Y%m%d"), ".csv")
  combined_df <- combine_json_files(data_dir, pattern)
  combined_df <- add_quarter_end_date(combined_df)
  write.csv(combined_df, output_file, row.names = FALSE)
  cat("Combined data saved to", normalizePath(output_file), "\n")
}

# Run main if script is executed directly
main()