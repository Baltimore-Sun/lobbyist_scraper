# import libraries. Requests helps us grab the webpage we want. BeutifulSoup helps us parse the webpages HTML. csv helps us output the data. Pandas helps us output the data in a nice-ish way. 
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# Step 1: Collect the links
# Because the website we're scraping is paginated, I had to look for a pattern in the URLs on each page. Each URL is the same, except for the end, where the URL says 'page=[insert pagination number]'. So here, I'm giving the repeatbale URL value and then describing how many pages I want this code to loop through

base_url = 'https://lobby-ethics.maryland.gov/public_access?filters%5Bar_date_end%5D=&filters%5Bar_date_start%5D=&filters%5Bar_lobbying_year%5D=2022&filters%5Bc_date_end%5D=&filters%5Bc_date_start%5D=&filters%5Bc_lobbying_year%5D=&filters%5Bdate_selection%5D=Lobbying+Year&filters%5Bemployer_name%5D=&filters%5Blar_date_end%5D=&filters%5Blar_date_start%5D=&filters%5Blar_lobbying_year%5D=&filters%5Blobbying_year%5D=2022&filters%5Breport_type%5D=Activity+Reports&filters%5Breports_containing%5D=&filters%5Bsearch_query%5D=&page='
pages = 394  # Define the number of pages you want to scrape

links = []

for page in range(1, pages + 1):
    url = base_url + str(page)

# Step 2: Grab the HTML attributes that you want to pull from the webpage. In this case, I'm looping through every link on the page first. This way, I won;t soend hours running the code just to have one of the links not work. 

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = response.content

    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')

    for table in tables:
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                for link in cell.find_all('a'):
                    links.append("https://lobby-ethics.maryland.gov/" + link['href'])

# step 3: write out the links we scraped to a csv

with open('./links.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Link'])
    writer.writerows([[link] for link in links])

# step 4: Now I'm asking the code to loop through every link I've grabbed and, once again, grab information in the specific HTML attributes. 
data2 = []

for link in links:
    response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    html = response.content

# here I want everything in the tbody div

    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('tbody')

# here, I want information in the col-md-12 class, but that class appears many times in the HTML code. To help with that, I'm asking it to always grab the 18th occurance of this class. 

    div_index = 18 
    specific_divs = soup.find_all('div', class_='col-md-12')

# And here I'm telling the code that if the 18th occurance of this class doesn't occur, to basically not freak out about it and that it's okay

    if div_index < len(specific_divs):
        specific_div = specific_divs[div_index]
        specific_text = specific_div.get_text(strip=True)
    else:
        specific_text = "Not Found" 

    # Here I'm asking the code to pull text from lists in the HTML

    ul_elements = soup.find_all('ul', class_='horizontal')
    ul_texts = [ul.get_text(strip=True) for ul in ul_elements]

# and here I'm appending some of the text I've pulld together

    combined_data = [specific_text] + ul_texts
    for table in tables:
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                combined_data.append(cell.text.strip())

    # Append the combined_data list to the data list
    data2.append(combined_data)

# Step 5: Here's where pandas comes in. I want to determine the number of columns based on the maximum number of elements in the data
num_columns = max(len(row) for row in data2)

# Step 6: Ensure all rows have the same number of elements as the number of columns
for i, row in enumerate(data2):
    if len(row) < num_columns:
        # If the row has fewer elements, pad it with None to match the number of columns
        data2[i] = row + [None] * (num_columns - len(row))
    elif len(row) > num_columns:
        # If the row has more elements, truncate it to match the number of columns
        data2[i] = row[:num_columns]

# Step 7: Print data2 to check for consistency
print(data2)

# Step 8: Convert the data to a DataFrame
df = pd.DataFrame(data2, columns=[f"Column {i + 1}" for i in range(num_columns)])

# Step 9: Convert 'data2' to a DataFrame with appropriate column names
num_columns = max(len(row) for row in data2)
column_names = [f"Column {i + 1}" for i in range(num_columns)]
df = pd.DataFrame(data2, columns=column_names)

#Step 10: output the data to a csv
output_file = './lobbyist_data.csv'
df.to_csv(output_file, index=False, encoding='utf-8', escapechar='\\')
