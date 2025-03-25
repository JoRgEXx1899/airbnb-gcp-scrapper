import requests  # Lib for make requests to web pages
from urllib.parse import urlparse, parse_qs, urlunparse
import json

from bs4 import BeautifulSoup  # Interpreter of response
import pandas as pd

from grid import grid

def scrap_airbnb_call(origin_url: str):
    global countExploreSplitStaysListingItem
    countExploreSplitStaysListingItem = 0
    # Parsing the URL
    parsed_url = urlparse(origin_url)
    # Extract URL parameters
    query_params = parse_qs(parsed_url.query)
    # get the coords parameters
    ne_lat = query_params.get('ne_lat', [None])[0]
    ne_lng = query_params.get('ne_lng', [None])[0]
    sw_lat = query_params.get('sw_lat', [None])[0]
    sw_lng = query_params.get('sw_lng', [None])[0]
    data_columns = ["latitude", "longitude", "avgRatingLocalized", "airbnb_id",
                    "name", "roomTypeCategory", "pdpUrlType", "title", "adults",
                    "checkin", "checkout", "children", "infants", "pets",
                    "originalPrice", "discountedPrice", "qualifier",
                    "shortQualifier"]
    global data_df
    data_df = pd.DataFrame(columns=data_columns)
    del data_columns
    # CALLS the grid and iterates through the grid building the url
    grid_points = grid(float(ne_lat), float(ne_lng),
                       float(sw_lat), float(sw_lng))
    base_url = origin_url
    print("ne_lat: ", ne_lat, "ne_lng: ", ne_lng,
          "sw_lat: ", sw_lat, "sw_lng: ", sw_lng)
    for point in grid_points:
        p1 = point["right_up"]
        p2 = point["left_down"]
        # print(p1.lat, p1.lon, p2.lat, p2.lon)
        base_url = base_url.replace(ne_lat, str(p1.lat)).replace(ne_lng, str(p1.lon)).replace(
            sw_lat, str(p2.lat)).replace(sw_lng, str(p2.lon))
        # print(base_url)
        airbnb_data_scrapper(base_url)
        base_url = origin_url
    print(data_df)
    print("Items de tipo split:", countExploreSplitStaysListingItem)


def airbnb_data_scrapper(url: str):
    # Get a request from the website and stores it in variable 'response'
    response = requests.get(url)
    # Get the text of the response
    content = response.text
    # Instantiates a BeautifulSoup with content and parser as args
    soup = BeautifulSoup(content, "lxml")
    # Search for the id "data-injector-instances" which contains the script label with json data
    container = soup.find(id="data-injector-instances")
    # Get json data from the container by text stripping
    json_data = json.loads(container.text.strip())
    # Search "mapSearchResults" in JSON content using the recoursive function find_key
    map_search_results = find_key(json_data, 'mapSearchResults')
    # If found "mapSearchResults" then extract data from the result
    if map_search_results:
        # Makes json from results[0][0]
        k = 0
        for item in map_search_results[0]:
            json_items_data = json.loads(json.dumps(item))
            # with open('item.json', 'w') as archivo:
            #    json.dump(json_items_data, archivo)
            # Extracting data items in json data
            
            if (json_items_data["__typename"] == "StaySearchResult"):
                # Listing section
                coordinate = json_items_data["listing"]["coordinate"]
                avgRatingLocalized = json_items_data["listing"]["avgRatingLocalized"]
                airbnb_id = json_items_data["listing"]["id"]
                airbnb_name = json_items_data["listing"]["name"]
                airbnb_roomTypeCategory = json_items_data["listing"]["roomTypeCategory"]
                airbnb_pdpUrlType = json_items_data["listing"]["pdpUrlType"]
                airbnb_title = json_items_data["listing"]["title"]
                # listingParamOverrides section
                airbnb_adults = json_items_data["listingParamOverrides"]["adults"]
                airbnb_checkin = json_items_data["listingParamOverrides"]["checkin"]
                airbnb_checkout = json_items_data["listingParamOverrides"]["checkout"]
                airbnb_children = json_items_data["listingParamOverrides"]["children"]
                airbnb_infants = json_items_data["listingParamOverrides"]["infants"]
                airbnb_pets = json_items_data["listingParamOverrides"]["pets"]
                # pricingQuote/structuredStayDisplayPrice/primaryLine section

                try:
                    airbnb_originalPrice = json_items_data["pricingQuote"][
                        "structuredStayDisplayPrice"]["primaryLine"]["originalPrice"]
                except:
                    airbnb_originalPrice = json_items_data["pricingQuote"][
                        "structuredStayDisplayPrice"]["primaryLine"]["price"]
                try:
                    airbnb_discountedPrice = json_items_data["pricingQuote"][
                        "structuredStayDisplayPrice"]["primaryLine"]["discountedPrice"]
                except:
                    airbnb_discountedPrice = json_items_data["pricingQuote"][
                        "structuredStayDisplayPrice"]["primaryLine"]["price"]
                airbnb_qualifier = json_items_data["pricingQuote"][
                    "structuredStayDisplayPrice"]["primaryLine"]["qualifier"]
                airbnb_shortQualifier = json_items_data["pricingQuote"][
                    "structuredStayDisplayPrice"]["primaryLine"]["shortQualifier"]

                # Build data-row according with data structure defined
                data_row = {"latitude": coordinate["latitude"],
                            "longitude": coordinate["longitude"],
                            "avgRatingLocalized": avgRatingLocalized,
                            "airbnb_id": airbnb_id,
                            "name": airbnb_name,
                            "roomTypeCategory": airbnb_roomTypeCategory,
                            "pdpUrlType": airbnb_pdpUrlType,
                            "title": airbnb_title,
                            "adults": airbnb_adults,
                            "checkin": airbnb_checkin,
                            "checkout": airbnb_checkout,
                            "children": airbnb_children,
                            "infants": airbnb_infants,
                            "pets": airbnb_pets,
                            "originalPrice": airbnb_originalPrice,
                            "discountedPrice": airbnb_discountedPrice,
                            "qualifier": airbnb_qualifier,
                            "shortQualifier": airbnb_shortQualifier
                            }
                # Insert the data_row into data_df pandas dataframe
                data_df.loc[len(data_df)] = data_row
            else:
                if (json_items_data["__typename"] == "ExploreSplitStaysListingItem"):
                    global countExploreSplitStaysListingItem
                    countExploreSplitStaysListingItem +=1
    else:
        print("No se encontró 'mapSearchResults' en el JSON")


# Define the URL of the website to scrap
website = f"""https://www.airbnb.com.co/s//homes?tab_id=home_tab&
refinement_paths%5B%5D=%2Fhomes&
flexible_trip_lengths%5B%5D=one_week&
monthly_start_date=2024-06-01&
monthly_length=3&
monthly_end_date=2024-09-01&
price_filter_input_type=0&
channel=EXPLORE&
query=&
place_id=ChIJKcumLf2bP44RFDmjIFVjnSM&
date_picker_type=calendar&
source=structured_search_input_header&search_type=user_map_move&
price_filter_num_nights=5&
ne_lat=4.8182340428972985&
ne_lng=-73.96681769000264&
sw_lat=4.475083707098524&
sw_lng=-74.26571085143124&
zoom=11.507946901397487&
zoom_level=11.507946901397487&
search_by_map=true&
federated_search_session_id=90291fe8-ec87-434e-bd1f-5ec83f4d9a16&
pagination_search=true&
cursor=eyJzZWN0aW9uX29mZnNldCI6MCwiaXRlbXNfb2Zmc2V0IjoxOCwidmVyc2lvbiI6MX0%3D
"""
website = "https://www.airbnb.com.co/s/Bogot%C3%A1--Bogot%C3%A1--D.C.--Colombia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-08-01&monthly_length=3&monthly_end_date=2024-11-01&price_filter_input_type=0&channel=EXPLORE&query=Bogot%C3%A1%2C%20Bogot%C3%A1%2C%20D.C.&place_id=ChIJKcumLf2bP44RFDmjIFVjnSM&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=5&ne_lat=4.606690414707041&ne_lng=-74.06431787502396&sw_lat=4.597383926177129&sw_lng=-74.0724235536706&zoom=16.71250000000001&zoom_level=16.71250000000001&search_by_map=true"


def find_key(data, key_to_find):
    """Busca recursivamente todas las ocurrencias de una clave en un diccionario o lista."""
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == key_to_find:
                results.append(value)
            elif isinstance(value, (dict, list)):
                results.extend(find_key(value, key_to_find))

    elif isinstance(data, list):
        for item in data:
            results.extend(find_key(item, key_to_find))

    return results


if __name__ == "__main__":
    url = "https://www.airbnb.com.co/s/Bogot%C3%A1--Bogot%C3%A1--D.C.--Colombia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-08-01&monthly_length=3&monthly_end_date=2024-11-01&price_filter_input_type=0&channel=EXPLORE&query=Bogot%C3%A1%2C%20Bogot%C3%A1%2C%20D.C.&place_id=ChIJKcumLf2bP44RFDmjIFVjnSM&date_picker_type=calendar&source=structured_search_input_header&search_type=user_map_move&search_mode=regular_search&price_filter_num_nights=5&ne_lat=4.609507976708671&ne_lng=-74.0676079667669&sw_lat=4.592563549694838&sw_lng=-74.08236604516912&zoom=15.847999999967364&zoom_level=15.847999999967364&search_by_map=true"
    scrap_airbnb_call(url)
