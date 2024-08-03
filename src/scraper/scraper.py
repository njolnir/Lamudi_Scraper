import pandas as pd
import numpy as np
import re
import requests
from bs4 import BeautifulSoup as bs
import time
from tqdm import tqdm

from src.utils.last_word import get_word_after_last_comma

def scraper(province, property_type, num):
    """
    Scrapes Lamudi website for properties.

    Args:
        province (str): Province to search for properties.
        property_type (str): Type of property to search for.
        num (int): Number of properties to scrape.

    Returns:
        pd.DataFrame: DataFrame containing scraped properties.
    """
    data = []
    listing = []
    links = []
    skus = set()  # Use a set to keep track of unique SKUs
    count = 0  # Initialize a counter
    print('SCRAPING. . .')

    # Get the maximum page number
    URL = f'https://www.lamudi.com.ph/buy/{province}/{property_type}/'
    page = requests.get(URL)
    soup = bs(page.content, 'html.parser')
    div = soup.find('div', class_='BaseSection Pagination')
    max_page_num = int(div.get('data-pagination-end'))

    for page_num in range(1, max_page_num + 1):
        try:
            if page_num == 1:
                URL = f'https://www.lamudi.com.ph/buy/{province}/{property_type}/'
            else:
                URL = f'https://www.lamudi.com.ph/buy/{province}/{property_type}/?page={page_num}'
            print(f"Scraping page {page_num}...")
            page = requests.get(URL)
            soup = bs(page.content, 'html.parser')
            results_link = soup.find_all("div", attrs={"class": "row ListingCell-row ListingCell-agent-redesign"})
            results_sku = soup.find_all("div", attrs={"class": "ListingCell-MainImage"})
            print(f"Found {len(results_sku)} results on page {page_num}...")
        except Exception as e:
            print(f"Error on page {page_num}: {e}")
            continue  # Continue to the next page instead of breaking

        for sku_tag, link_tag in zip(results_sku, results_link):
            sku = sku_tag.find('div')["data-sku"]
            if sku in skus:  # If SKU is already in the set, skip it
                continue
            skus.add(sku)  # Add SKU to the set
            link = link_tag.find('a')['href']
            listing.append([sku, link])
            count += 1
            if count >= num:
                break

        if count >= num:
            break

    # Convert the listing list to a DataFrame
    listing_df = pd.DataFrame(listing, columns=['SKU', 'link'])
    links = listing_df['link']

    for index, each in tqdm(enumerate(links), total=len(links), desc="Processing details"):
        prop_details = {}
        amenities = []
        temp = []
        features = {}
        URL = each
        page = requests.get(URL)
        soup = bs(page.content, 'html.parser')

        all_sku = soup.find("div", attrs={"class": "Banner-Images"})
        all_amenities = soup.find_all("span", attrs={"class": "material-icons material-icons-outlined"})
        all_loc = soup.find_all("h3", attrs={"class": "Title-pdp-address"})
        all_price = soup.find_all("div", attrs={"class": "Title-pdp-price"})
        all_features = soup.find_all("div", attrs={"class": "columns medium-6 small-6 striped"})
        all_lat_long = soup.find_all("div", attrs={"class": "LandmarksPDP-Wrapper"})

        try:
            all_agent_name = soup.find("div", attrs={"class": "AgentInfoV2-agent-name"}).get_text().strip()
            all_agent_agency = soup.find("div", attrs={"class": "AgentInfoV2-agent-agency"}).get_text().strip()
            all_overview = soup.find("div", attrs={"class": "ViewMore-text-description"}).get_text().strip().replace(
                '\n', '').replace('\xa0', '')
        except:
            all_agent_name = ''
            all_agent_agency = ''
            all_overview = ''

        for each in all_amenities:
            amenities.append(each.get_text().strip())

        loc_final = ''
        for each in all_loc:
            loc_text = each.get_text().strip().replace('\n', '')
            loc_final = re.sub(' +', ' ', loc_text)

        price = 0
        for each in all_price:
            try:
                price = each.get_text().replace('₱', '').replace(',', '').strip()
                price = int(price)
            except:
                price = each.get_text().replace('₱', '').replace(',', '').strip().split('\n')
                price = price[0].strip()
                try:
                    price = int(price)
                except:
                    price = 0

        temp = []
        for each in all_features:
            details = each.get_text().strip().split('\n')
            for detail in details:
                detail = detail.strip()
                if detail != '':
                    temp.append(detail)

        features = {}
        for i in range(len(temp)):
            if i % 2 == 0:
                try:
                    features[temp[i]] = temp[i + 1]
                except:
                    pass

        latitude = ''
        longitude = ''
        for each in all_lat_long:
            longitude = each.get('data-lon', '')
            latitude = each.get('data-lat', '')

        try:
            prop_details["SKU"] = all_sku["data-sku"] if all_sku else ''
            prop_details['text_location'] = loc_final
            prop_details['price'] = price
            prop_details['amenities'] = amenities
            prop_details['features'] = features
            prop_details['latitude'] = latitude
            prop_details['longitude'] = longitude
            prop_details['agent_name'] = all_agent_name
            prop_details['agency_name'] = all_agent_agency
            prop_details['overview'] = all_overview

        except:
            pass

        data.append(prop_details)
        time.sleep(0.5)

    listing_details_df = pd.DataFrame(data)

    # Exploding Amenities
    amenities = pd.get_dummies(listing_details_df['amenities'].explode())
    amenities_res = amenities.groupby(amenities.index).sum()
    raw_df = pd.concat([listing_details_df, amenities_res], axis=1, ignore_index=False)
    raw_df = raw_df.join(pd.DataFrame.from_records(raw_df['features'].mask(raw_df.features.isna(), {}).tolist())).fillna(0)
    raw_df.drop(columns=['features', 'amenities'], inplace=True)
    raw_df.drop_duplicates(keep='first', inplace=True)

    # Feature Selection
    staging_df = raw_df.merge(listing_df[['SKU', 'link']], on='SKU', how='left')
    staging_df = staging_df[['SKU', 'Condominium Name', 'text_location', 'price', 'Floor area (m²)', 'Bedrooms', 'Baths', 'gite', 'fitness_center', 'pool', 'security', 'camera_indoor', 'room_service', 'local_parking', 'link']]

    column_name_mapping = {
        'Condominium Name': 'Name',
        'text_location': 'Location',
        'price': 'TCP',
        'Floor area (m²)': 'Floor_Area',
        'gite': 'Club House',
        'fitness_center': 'Gym',
        'pool': 'Swimming Pool',
        'security': 'Security',
        'camera_indoor': 'CCTV',
        'room_service': 'Reception Area',
        'local_parking': 'Parking Area',
        'link': 'Source'
    }

    staging_df.rename(columns=column_name_mapping, inplace=True)
    staging_df['Location'] = staging_df['Location'].astype(str)
    staging_df['City/Town'] = staging_df['Location'].apply(get_word_after_last_comma)
    staging_df['Province'] = province.upper()
    staging_df['Name'] = staging_df['Name'].astype(str)
    staging_df['Name'] = staging_df['Name'].str.upper()

    info_df = staging_df[['SKU', 'Name', 'Location', 'City/Town', 'TCP', 'Floor_Area']]
    amenities_df = staging_df[['SKU', 'Name', 'Bedrooms', 'Baths',
        'Club House', 'Gym', 'Swimming Pool', 'Security', 'CCTV',
        'Reception Area', 'Parking Area', 'Source']]

    # Define File name
    file_name = f"{province}_{property_type}.csv"
    file_name_info = f"{province}_{property_type}_info.csv"
    file_name_amenities = f"{province}_{property_type}_amenities.csv"

    # Define File path
    path = f"data/scraped/full/{file_name}"
    path_info = f"data/scraped/info/{file_name_info}"
    path_amenities = f"data/scraped/amenities/{file_name_amenities}"

    # Save as csv
    staging_df.to_csv(path, index=False)
    info_df.to_csv(path_info, index=False)
    amenities_df.to_csv(path_amenities, index=False)

    return staging_df


# Example usage, which will only run if the script is executed directly
if __name__ == "__main__":
    province = input("Please enter the province: ")
    property_type = input("Please enter the property type: ")
    num = int(input("Please enter the number of properties to scrape: "))