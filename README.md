# Python scraper for Maryland lobbying disclosure activity reports

This is a Python web scraper that pulls information from the 2022-23 lobbying registration session from the [Maryland Lobbying Registrations website](https://lobby-ethics.maryland.gov/public_access?filters%5Bar_date_end%5D=&filters%5Bar_date_start%5D=&filters%5Bar_lobbying_year%5D=2022&filters%5Bc_date_end%5D=&filters%5Bc_date_start%5D=&filters%5Bc_lobbying_year%5D=&filters%5Bdate_selection%5D=Lobbying+Year&filters%5Bemployer_name%5D=&filters%5Blar_date_end%5D=&filters%5Blar_date_start%5D=&filters%5Blar_lobbying_year%5D=&filters%5Blobbying_year%5D=2022&filters%5Breport_type%5D=Activity+Reports&filters%5Breports_containing%5D=&filters%5Bsearch_query%5D=&page=1) as of July 25, 2023.

This scraper was built as a part of two stories by Baltimore Sun politics reporter Sam Janesch. 

[Who paid lobbyists a total of $48.8 million to influence Maryland lawmaking, and what did they get?]([https://lobby-ethics.maryland.gov/public_access?filters%5Bar_date_end%5D=&filters%5Bar_date_start%5D=&filters%5Bar_lobbying_year%5D=2022&filters%5Bc_date_end%5D=&filters%5Bc_date_start%5D=&filters%5Bc_lobbying_year%5D=&filters%5Bdate_selection%5D=Lobbying+Year&filters%5Bemployer_name%5D=&filters%5Blar_date_end%5D=&filters%5Blar_date_start%5D=&filters%5Blar_lobbying_year%5D=&filters%5Blobbying_year%5D=2022&filters%5Breport_type%5D=Activity+Reports&filters%5Breports_containing%5D=&filters%5Bsearch_query%5D=&page=1](https://www.baltimoresun.com/politics/bs-md-pol-lobbying-2023-20230727-ivzyyt2p6rbylebn2wtmrleole-story.html))
[Here’s where lobbyists tried to influence some of Maryland’s biggest policy changes in 2023](https://www.baltimoresun.com/politics/bs-md-pol-lobbying-2023-sidebar-20230727-pm2gc7kb75dgrfqpbklj5pw5ae-story.html)

The scraper was built to collect information about topics and bills when the details of an activity report are expanded under sections A3, A7 and A8. The primary goal was to see who was paying lobbyists, the specific bills mentioned and the topics and descriptions used in these registrations. 

The data pulled using this scraper ultimately allowed The Sun to visualize which bills came up most frequently in activity reports as seen in the article about where lobbyists tried to influence some of Maryland’s biggest policy changes in 2023.

# How the scraper works:
The first step is to tell the scraper to grab the links off every page of activity reports from the November 2022 - October 2023 lobbying year. We’ll then save all the links as a csv. At the time of this scraping, there were 394 pages and 3933 activity reports. 

To do this, first identify the base URL you want to scrape. In this case, that’s the URL when we go to Maryland Lobbying Registrations and select the ‘Nov 2022 - Oct 2023’ lobbying year from the drop down menu. 

Because the data on this website is paginated, we have to tell the scraper how many pages we want to scrape through. Luckily, the base URL for each page is the same except for the last digit, which identifies which page we’re on. This means we just have to tell the scraper the number of pages to loop through and to keep looping once it reaches the end of a page.

	base_url = 'https://lobby-ethics.maryland.gov/public_access?filters%5Bar_date_end%5D=&filters%5Bar_date_start%5D=&filters%5Bar_lobbying_year%5D=2022&filters%5Bc_date_end%5D=&filters%5Bc_date_start%5D=&filters%5Bc_lobbying_year%5D=&filters%5Bdate_selection%5D=Lobbying+Year&filters%5Bemployer_name%5D=&filters%5Blar_date_end%5D=&filters%5Blar_date_start%5D=&filters%5Blar_lobbying_year%5D=&filters%5Blobbying_year%5D=2022&filters%5Breport_type%5D=Activity+Reports&filters%5Breports_containing%5D=&filters%5Bsearch_query%5D=&page='
	pages = 394  # Define the number of pages you want to scrape


	links = []


	for page in range(1, pages + 1):
    url = base_url + str(page)
		
But, we want to make sure it actually grabs the links when it loops through each page. To do this, we need to investigate how the html of the page is set up. Right click on the page, select ‘Inspect’ and find the html container that the links are stored in. Once you know what you want, use BeautifulSoup to grab the links. Then, output the links to a csv. 

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = response.content


    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')


    for table in tables:
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                for link in cell.find_all('a'):
                    links.append("https://lobby-ethics.maryland.gov/" + link['href'])


	with open('./links.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Link'])
    writer.writerows([[link] for link in links])
		
Now that we have the links, ask the scraper to do the same thing - loop through the links - but this time we’re asking the scraper to go inside the links and grab the information we want. We’ll also use html parsing and the BeautifulSoup library to do this.

	data2 = []


	for link in links:
    response = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    html = response.content


	#Here I want everything in the tbody div


    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('tbody')


	#Here, I want information in the col-md-12 class, but that class appears many times in the HTML code. To help with that, I'm asking it to always grab the 18th occurance of this class. 


    div_index = 18 
    specific_divs = soup.find_all('div', class_='col-md-12')


	#And here I'm telling the code that if the 18th occurance of this class doesn't occur, to basically not freak out about it and that it's okay


    if div_index < len(specific_divs):
        specific_div = specific_divs[div_index]
        specific_text = specific_div.get_text(strip=True)
    else:
        specific_text = "Not Found" 


    #Here I'm asking the code to pull text from lists in the HTML


    ul_elements = soup.find_all('ul', class_='horizontal')
    ul_texts = [ul.get_text(strip=True) for ul in ul_elements]


	#And here I'm appending some of the text I've pulled together


    combined_data = [specific_text] + ul_texts
    for table in tables:
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                combined_data.append(cell.text.strip())


  	#Append the combined_data list to the data list
    data2.append(combined_data)
		
Once we grab everything we want from the links, we’ll attempt to clean the data using Pandas. We can make small improvements by asking that the csv output each link’s contents as a single row and to pad a column if some rows have fewer elements than others (So if some links don’t have the information that other links have we won’t have to add columns to ensure each column has uniform data). This data is still messy after using Pandas and will require significant cleaning after the fact.

	num_columns = max(len(row) for row in data2)


	#Ensure all rows have the same number of elements as the number of columns
	for i, row in enumerate(data2):
    	if len(row) < num_columns:
       	 # If the row has fewer elements, pad it with None to match the number of columns
        	data2[i] = row + [None] * (num_columns - len(row))
    	elif len(row) > num_columns:
        	# If the row has more elements, truncate it to match the number of columns
        	data2[i] = row[:num_columns]
				
I then converted the data to a dataframe and output it as a csv.

	#Print data2 to check for consistency
	print(data2)


	#Convert the data to a DataFrame
	
 		df = pd.DataFrame(data2, columns=[f"Column {i + 1}" for i in range(num_columns)])


	#Convert 'data2' to a DataFrame with appropriate column names

		num_columns = max(len(row) for row in data2)
		column_names = [f"Column {i + 1}" for i in range(num_columns)]
		df = pd.DataFrame(data2, columns=column_names)


	#Output the data to a csv

		output_file = './lobbyist_data.csv'
		df.to_csv(output_file, index=False, encoding='utf-8', escapechar='\\')


To change the session scraped, you’ll need to replace the base URL used here with the base URL of the new session. You’ll also need to adjust the number of pages to make sure you’re grabbing everything from that session. Finally, make sure you double check how the information is formatted in the links so that you can grab what you want.

# Copyright and Attribution:
Copyright 2023 Baltimore Sun. All rights reserved.

If you use this scraper or the data produced from the scraper, you must credit The Baltimore Sun and identify how you have made changes.

*Scraper built and data cleaned by Baltimore Sun data intern Victoria Stavish*
