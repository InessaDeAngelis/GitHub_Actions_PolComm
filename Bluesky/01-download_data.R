#### Preamble ####
# Purpose: Download posts tagged with #CdnPoli from Bluesky
# Author: Inessa De Angelis
# Date: 17 June 2025
# Contact: inessa.deangelis@mail.utoronto.ca 
# License: MIT
# Pre-requisites: None

#### Workspace setup ####
## Packages ##
library(tidyverse)
library(atrrr)
library(dotenv)

## Authenticate ##
bluesky_username <- Sys.getenv("BLUESKY_USERNAME")
bluesky_password <- Sys.getenv("BLUESKY_AUTH")

# Check if credentials are available #
if (is.null(bluesky_username) || is.null(bluesky_password) || bluesky_username == "" || bluesky_password == "") {
  stop("Bluesky credentials not found in GitHub secrets!")
}

auth(bluesky_username, password = bluesky_password)

#### Download data ####
## Function for last run time file ##
update_last_run_time <- function(file_path) {
  current_time <- Sys.time()  # Get current date and time
  formatted_time <- format(current_time, "%Y-%m-%d %H:%M:%S")  
  write(formatted_time, file = file_path)
}

get_last_run_time <- function(file_path) {
  if (file.exists(file_path)) {
    last_run_time <- readLines(file_path)
    return(as.POSIXct(last_run_time, format = "%Y-%m-%d %H:%M:%S"))
  } else {
    return(NA) 
  }
}

## Get the last run time ##
last_run_time <- get_last_run_time("Bluesky/last_run_time.txt")

## Search from #cdnpoli posts ##
posts <- search_post("#cdnpoli", limit = Inf)

## Filter posts based off date in last run time file ##
if (!is.na(last_run_time)) {
  posts <- posts |>
    filter(as.POSIXct(indexed_at, format = "%Y-%m-%d %H:%M:%S") > last_run_time)
}

## Get current date to use in the file name ##
current_date <- format(Sys.Date(), "%Y-%m-%d")

## Save posts ##
csv_filename <- paste0("Bluesky/cdnpoli_posts_", current_date, ".csv")
write_csv(posts, csv_filename)

## Update the last run time file ##
update_last_run_time("Bluesky/last_run_time.txt")