![Lamudi Logo](lamudi_logo.png)

# Lamudi Scraper

Lamudi Scraper is a Python-based web scraping tool designed to extract property listings from Lamudi's website. It collects detailed information about properties, including location, price, amenities, and more.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Sample Output](#sample-output)

## Installation

To install the necessary dependencies, you can use the provided `requirements.txt` file. It is recommended to use a virtual environment.

1. Clone the repository:
    ```sh
    git clone https://github.com/njolnir/Lamudi-Scraper.git
    cd Lamudi-Scraper
    ```

2. Create a virtual environment (optional but recommended):
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

The scraper can be used to fetch CONDOMINIUM property listings from Lamudi's website. You can run the scraper using the following commands:

1. Update the `lamudi_scraper.py` file with the desired parameters or provide inputs directly when prompted.

2. Run the scraper:
    ```sh
    python lamudi_scraper.py
    ```

Example usage:
```sh
Please enter the province: cavite
Please enter the property type: condo
Please enter the number of properties to scrape: 10
```

## Sample Output

You can download the CSV file [here](https://github.com/njolnir/lamudiscraper/blob/main/data/scraped/full/cavite_condo.csv).

