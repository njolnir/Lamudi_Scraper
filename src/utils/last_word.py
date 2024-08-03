import pandas
import numpy
import re


def get_word_after_last_comma(address):
    """
    Extracts the word or phrase that comes after the last comma in a given address string.

    Parameters:
    address (str): The address string to search within.

    Returns:
    str: The word or phrase following the last comma. If no comma is found, returns an empty string.
    """
    match = re.search(r',\s*([^,]+)\s*$', address)
    return match.group(1).strip() if match else ''

# Example usage, which will only run if the script is executed directly
if __name__ == "__main__":
    address = input("Please enter an address: ")
    result = get_word_after_last_comma(address)
    print(f"The word after the last comma is: '{result}'")