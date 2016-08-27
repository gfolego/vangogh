#!/usr/bin/Rscript --vanilla

# tidy_dataset.R
# Copyright 2016
#   Guilherme Folego (gfolego@gmail.com)
#   Otavio Gomes (otaviolmiro@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



# This script makes an attempt to follow Google's R Style Guide
# For more information, please refer to
#   https://google-styleguide.googlecode.com/svn/trunk/Rguide.xml


# Required libraries
suppressPackageStartupMessages(library("argparse"))
suppressPackageStartupMessages(library("dplyr"))
suppressPackageStartupMessages(library("data.table"))


# Constants
defaultDensity <- 196.3
defaultRatio   <- 0.05


# Printf
printf <- function(...) invisible(cat(sprintf(...)))

# Parse command line arguments
ParseArgs <- function() {
    parser = ArgumentParser(description='Merge and clean CSV files')

    parser$add_argument('-o', '--output', type='character', nargs=1,
                        help='output csv file')
    parser$add_argument('-d', '--density', type='double', nargs=1,
                        default=defaultDensity,
                        help='minimum density value (in pixels per painted inch)')
    parser$add_argument('-r', '--ratio', type='double', nargs=1,
                        default=defaultRatio,
                        help='maximum density ratio value')
    parser$add_argument('files', type='character', nargs='+',
                        help='input csv files')
    parser$add_argument('-v', '--verbose', action='count', default=0,
                        help='verbosity level')


    args <- parser$parse_args()
    printf("Arguments:\n")
    print(args)

    # Check output
    out.dir <- args$output
    if (is.null(out.dir)) {
        stop(sprintf("error: argument -o/--output is required\n"),
             call. = FALSE)
    }  else if (file.access(dirname(out.dir), mode = 2) == -1) {
        stop(sprintf("Cannot create specified file ( %s )\n", out.dir),
             call. = FALSE)
    }

    # Check input
    CheckFile <- function(filename) {
        if (file.access(filename, mode = 4) == -1) {
            stop(sprintf("Cannot read specified file ( %s )\n", filename),
            call. = FALSE)
        }
    }
    lapply(args$files, CheckFile)

    # Check verbose
    if (is.null(args$verbose)) {
        args$verbose <- 0
    }
    if (args$verbose >= 3) {
        options("verbose" = TRUE, "datatable.verbose" = TRUE)
    }

    return (args)
}

# Read CSV file
ReadCSV <- function(filename) {
    printf("Reading file %s ...\n", filename)
    filename %>%
    read.csv(check.names = FALSE, as.is = TRUE, comment.char = "") %>%
    return
}

# Write CSV file
WriteCSV <- function(dataset, filename) {
    dataset[] <- lapply(dataset, as.character)
    write.csv(dataset, file = filename, eol = "\r\n", row.names = FALSE)
}

# Clean dataset
CleanDataset <- function(dataset) {

    # Key by PageID and remove duplicates
    dataset <- dataset %>% data.table %>% setkey("PageID") %>% unique

    # Remove entries with empty values
    dataset <- dataset[Artist != ""][PaintingID != ""][RealDimensions != ""]

    # Remove missing artists
    dataset <- filter(dataset, ! grepl("(unknown|anonym)", Artist, ignore.case = TRUE))

    # Remove missing dimensions
    dataset <- filter(dataset, ! grepl("(gallery|institution|notes|references)",
                               RealDimensions, ignore.case = TRUE)) %>% data.table
    dataset <- dataset[RealDimensions %like% "[0-9]"]

    # Remove some painting IDs
    dataset <- dataset[PaintingID %like% "[0-9]"]

    # Remove some artists
    dataset <- filter(dataset, ! grepl("^\\|", Artist)) %>% data.table

    # Parse RealDimensions
    dataset[, RealDimensions:=chartr("A-Z,", "a-z.", RealDimensions)]
    dataset <- dataset[RealDimensions %like% "(cm|mm|in)"]
    dataset[, RealDimensions := ParseRealDimensions(RealDimensions)]
    dataset <- dataset[RealDimensions %like% "^[0-9\\.]+\\|[0-9\\.]+\\|(cm|mm|in)$"]

    # Convert to inches
    dataset[, c("RealHeightInches", "RealWidthInches") :=
            ConvertDimensions(RealDimensions, PixelHeight, PixelWidth),
            by = 1:nrow(dataset)]
    dataset[, RealDimensions := NULL]

    # Calculate densities
    dataset[, "DensityHeight" := PixelHeight / RealHeightInches]
    dataset[, "DensityWidth"  := PixelWidth  / RealWidthInches]
    dataset[, "DensityRatio"  := abs(DensityHeight - DensityWidth) / pmin(DensityHeight, DensityWidth)]

    # Remove duplicated painting IDs by keeping the larger images
    dataset <- dataset %>%
        arrange(desc(PixelHeight), desc(PixelWidth)) %>%
        unique(by = "PaintingID") %>% data.table %>% setkey("PageID")

    return (dataset)
}

ParseRealDimensions <- function(rd) {
    rd <- gsub("(?: |-)1/2 ", ".5 ", rd)
    rd <- gsub("(?: |-)1/4 ", ".25 ", rd)
    rd <- gsub("(?: |-)3/4 ", ".75 ", rd)
    rd <- gsub("(?: |-)1/8 ", ".125 ", rd)
    rd <- gsub("(?: |-)3/8 ", ".375 ", rd)
    rd <- gsub("(?: |-)5/8 ", ".625 ", rd)
    rd <- gsub("(?: |-)7/8 ", ".875 ", rd)
    rd <- gsub("(?: |-)1/16 ", ".0625 ", rd)
    rd <- gsub("(?: |-)3/16 ", ".1875 ", rd)
    rd <- gsub("(?: |-)5/16 ", ".3125 ", rd)
    rd <- gsub("(?: |-)11/16 ", ".6875 ", rd)
    rd <- gsub("(?: |-)13/16 ", ".8125 ", rd)
    rd <- gsub("(?: |-)15/16 ", ".9375 ", rd)
    rd <- sub("\\(.*\\)$", "", rd)
    rd <- sub("^en\\|", "", rd)
    rd <- sub("^de\\|.*?je ", "", rd)
    rd <- sub("^\\*? ?[a-z]+: ?", "", rd)
    rd <- sub("^\\(?([0-9\\.]+).*?([0-9\\.]+)(?: | \\(w\\) )?([a-z]{2}).*$",
              "\\1|\\2|\\3", rd)
    rd <- sub("^.*?size ?\\|(?:units?=)? ?([a-z]{2})(?:ch)? ?\\|?(?:length=\\|)?(?:height=)? ?([0-9\\.]+) ?\\|(?:width=)? ?([0-9\\.]+).*$",
              "\\2|\\3|\\1", rd)
    rd <- sub("^.*?size ?\\|(?:units?=)? ?([a-z]{2})(?:ch)? ?\\|?(?:length=\\|)?(?:width=)? ?([0-9\\.]+) ?\\|(?:height=)? ?([0-9\\.]+).*$",
              "\\3|\\2|\\1", rd)
    rd <- sub("^w([0-9\\.]+) x h([0-9\\.]+).*?([a-z]{2})$",
              "\\2|\\1|\\3", rd)
    rd <- sub(".*?height.*?([0-9\\.]+).*?([a-z]{2})\\|([0-9\\.]+)$",
              "\\1|\\3|\\2", rd)
    return (rd)
}

ConvertDimensions <- function(dim, p.height, p.width) {

    # Extract data
    height  <- as.numeric(sub("^([0-9\\.]+)\\|([0-9\\.]+)\\|(cm|mm|in)$", "\\1", dim))
    width   <- as.numeric(sub("^([0-9\\.]+)\\|([0-9\\.]+)\\|(cm|mm|in)$", "\\2", dim))
    unit    <- sub("^([0-9\\.]+)\\|([0-9\\.]+)\\|(cm|mm|in)$", "\\3", dim)

    # Adjust accordingly
    ratio   <- switch(unit,
                      "in" = 1.00,
                      "cm" = 2.54,
                      "mm" = 25.4)

    height  <- height / ratio
    width   <- width  / ratio

    # Unfortunately, there are two standards (HxW, WxH)
    # This is a small hack to overcome the problem
    if (p.height > p.width) {
        h = max(height, width)
        w = min(height, width)
    } else {
        h = min(height, width)
        w = max(height, width)
    }

    # Return
    return (list(h, w))
}

# Filter by minimum density
FilterMinimumDensity <- function(dataset, density = defaultDensity) {
    dataset <- dataset[DensityHeight >= density][DensityWidth >= density]
    return (dataset)
}

# Filter by maximum density ratio
FilterMaximumRatio <- function(dataset, ratio = defaultRatio) {
    dataset <- dataset[DensityRatio <= ratio]
    return (dataset)
}


# Main
if (! interactive()) {

    # Parse arguments
    args <- ParseArgs()
    output <- args$output
    files <- args$files
    density <- args$density
    ratio <- args$ratio
    verbose <- args$verbose

    # Read all files and merge
    named.list <- lapply(files, ReadCSV)
    dataset <- rbindlist(named.list)
    rm("named.list")

    # Clean dataset
    dataset <- CleanDataset(dataset)

    # Filter density
    dataset <- FilterMinimumDensity(dataset, density)
    dataset <- FilterMaximumRatio(dataset, ratio)

    # Write output csv file
    WriteCSV(dataset, output)

    printf("\nDone!\n")
}

