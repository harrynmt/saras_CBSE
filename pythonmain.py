import requests
from bs4 import BeautifulSoup
import json
import ast
import csv
import os
import glob
import re
import pandas as pd

# Read the HTML file
with open('data.html', 'r') as file:
    html_code = file.read()

# Parse the HTML code using BeautifulSoup
soup = BeautifulSoup(html_code, 'html.parser')

# Find all tables in the HTML
tables = soup.find_all('table')
table = tables[0]
# Dictionary to store table data
# table_data = {}
newHeaders = []
# Loop through each table
for idx, table in enumerate(tables):
    # table_name = f'Table_{idx + 1}'
    # table_data[table_name] = []

    # Find all rows in the table
    rows = table.find_all('tr')
    fullData = []
    # Loop through each row
    # for row in rows:
    for num, row in enumerate(rows):
        row_data = []
        cells = row.find_all(['td', 'th'])

        # Loop through each cell in the row
        for cell in cells:
            cell_data = cell.get_text(strip=True)
            if cell.find('a'):
                cell_data += f" ({cell.find('a')['href']})"  # Include link if <a> tag is present
                numbers = re.findall(r'\d+', cell_data)

                # Get the last number (assuming there is at least one number in the string)
                affNo = numbers[-1] if numbers else None
                 
                url = f'https://saras.cbse.gov.in/SARAS/AffiliatedList/AfflicationDetails/{affNo}'
                print(f"Scraping {url}...")
                response = requests.get(url)
                html_content = response.text
                # Parse the HTML code using BeautifulSoup
                soup1 = BeautifulSoup(html_content, 'html.parser')

                # Find all tables in the HTML
                view_table = soup1.find_all('table')
                myTable = view_table[0]
                for myTableRowNum, myTableRow in enumerate(myTable.find_all('tr')):
                    itemSubTable = [myTablecell.get_text(strip=True) for myTablecell in myTableRow.find_all(['td', 'th'])]
                    if itemSubTable[0] != 'Details Of The School Filled up AFFILIATION/OASIS' :
                        if itemSubTable[1] == '':
                            row_data.append('None')
                        else :
                            row_data.append(itemSubTable[1])
                        if num == 1:
                             newHeaders.append(itemSubTable[0])

            else : row_data.append(cell_data)
        fullData.append(row_data)

    fullData[0].pop()
    fullData[0] = fullData[0] + newHeaders
    # print(fullData[0])

with open('full_table_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for data in fullData:
        writer.writerow(data)

csv_file = 'full_table_data.csv'
df = pd.read_csv(csv_file)

def split_data_and_save(csv_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Define a function to extract Address, Phone, and Email from the 'Address,Phone & Email' column
    def extract_info(row):
        address = row.split('Address :')[1].split('Phone No :')[0].strip()
        phone = row.split('Phone No :')[1].split('Email :')[0].strip().replace(',',' ').replace('-', ' ')
        email = row.split('Email :')[1].split('Website')[0].strip().replace('[at]', '@').replace('[dot]', '.')

        return pd.Series([address, phone, email])

    # Apply the function to create new columns
    df[['Address', 'Phone', 'Email']] = df['Address,Phone & Email'].apply(extract_info)

    # Convert the column to string and remove leading whitespaces
    df['Phone'] = df['Phone'].astype(str).str.lstrip()

    # Drop the 'Address,Phone & Email' column
    df.drop(columns=['Address,Phone & Email'], inplace=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file, index=False)

# Call the function with the path to your CSV file
split_data_and_save('full_table_data.csv')

# Print a message indicating the CSV file was cleaned
print(f'CSV file {csv_file} cleaned.')




