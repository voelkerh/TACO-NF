#import "@preview/graceful-genetics:0.2.0" as graceful-genetics
#import "@preview/physica:0.9.3"

#show: graceful-genetics.template.with(
  title: [Interactive comparison of taxonomic classification tools for WGS-data],
  authors: (
    (
      name: "Johanna Swift",
      department: "Primary Logistics Department",
      institution: "Delivery Institute",
      city: "Berlin",
      country: "Germany",
      mail: "swift@delivery.de",
    ),
  ),
  date: (
    year: 2025,
    month: "January",
    day: 31,
  ),
  keywords: (
    "Taxonomy",
    "Whole Genome Sequencing",
    "Classfication tools",
  ),
  abstract: [
    Some abstract text.
  ],
)

# Introduction
Introduction text

# Materials and methods

## Implementation and reproducability

## Data and ground truth generation

# Results

## Structure of the pipeline
- Add a figure here

## Description of pipeline steps

## Exemplary output

# Discussion

# Data availability
- Where is the pipeline hosted
- Which license

# Supplementary data

# Acknowledgements
- Students from earlier semesters

# References

#figure(
  image("a-mail.png"),
  caption: [
    Visualization of the FTL Earth-to-Mars communication capabilities enabled by A-Mail.
  ],
)