library(dplyr)
library(readr)
library(stringr)

# Set the base path and reports path
# Example:
# BASE_PATH <- file.path("C:", "Users", "Aaron", "Desktop", "Bioinformatics-Project-EPA-s-Air-Quality-System-Effect-on-Health")
#
# alternatively, you can use also set the set the current working directory to the desired path at the same time
# BASE_PATH <- setwd("/Users/Aaron/Desktop/Bioinformatics-Project-EPA-s-Air-Quality-System-Effect-on-Health")

BASE_PATH <- file.path("")

REPORTS_PATH <- file.path(BASE_PATH, "Lead")
years <- c()

# Recursively find all CSV files in subdirectories
csv_files <- list.files(REPORTS_PATH, pattern = "\\.csv$", recursive = TRUE, full.names = TRUE)
cat("Found CSV files:\n")

# Function to extract year from filename like 'Lead2019output.csv'
extract_year_from_filename <- function(filename) {
  m <- str_match(basename(filename), "Lead(\\d{4})output\\.csv")
  if (!is.na(m[1,2])) return(m[1,2]) else return(NA)
}

# Read and combine all CSVs, adding a Year column
all_dataframes <- lapply(csv_files, function(f) {
  df <- read_csv(f, show_col_types = FALSE)
  year <- extract_year_from_filename(f)
  df$Year <- year
  years <<- c(years, year)
  return(df)
})

combined_df <- bind_rows(all_dataframes)
cat("Combined dataframe dimensions (rows, columns): ", paste(dim(combined_df), collapse=", "), "\n")

# Save the combined dataframe
years_clean <- sort(na.omit(unique(years)))
if (length(years) > 0) {
  out_file <- file.path(BASE_PATH, sprintf("Lead%s-%soutput.csv", years_clean[1], years_clean[length(years)]))
} else {
  out_file <- file.path(BASE_PATH, "Lead_combined_output.csv")
}
write_csv(combined_df, out_file)