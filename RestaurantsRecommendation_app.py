import streamlit as st
import pandas as pd

# Set the background image using CSS
image_url = "https://cdn.vox-cdn.com/uploads/chorus_image/image/73039055/Valle_KimberlyMotos__1_of_47__websize__1_.0.jpg"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 style="font-size:35px;">Most Popular Restaurants Based on Reviews and Ratings</h1>', unsafe_allow_html=True)

# User input to select the location
place = st.selectbox("Select the state location:", 
                     ['KL', 'Ipoh', 'JB', 'Kuching', 'Langkawi', 'Melaka', 'Miri', 'Penang', 'Petaling Jaya', 'Shah Alam'])

# Load the data (ensure that the file paths are correct or files are uploaded)
google_review_data = pd.read_csv('GoogleReview_data_cleaned.csv')
tripadvisor_data = pd.read_csv('TripAdvisor_data_cleaned.csv')

# Data cleaning: removing missing values and duplicates
google_review_data.dropna(axis=0, how='any', inplace=True)
tripadvisor_data.dropna(axis=0, how='any', inplace=True)
google_review_data.drop_duplicates(inplace=True, keep=False)
tripadvisor_data.drop_duplicates(inplace=True, keep=False)

# Check if 'Number of Reviews' column exists, if not create it based on review text length
if 'Number of Reviews' not in google_review_data.columns:
    google_review_data['Number of Reviews'] = google_review_data['Review'].apply(lambda x: len(x.split()))  # Example assumption
if 'Number of Reviews' not in tripadvisor_data.columns:
    tripadvisor_data['Number of Reviews'] = tripadvisor_data['Review'].apply(lambda x: len(x.split()))  # Example assumption

# Combine the datasets on Restaurant and Location
combined_data = pd.merge(google_review_data, tripadvisor_data, on=['Restaurant', 'Location'], how='inner')

# Remove duplicates based on the restaurant name
combined_data = combined_data.drop_duplicates(subset=['Restaurant'], keep='first')

# Calculate the average rating from both sources and the total number of reviews
combined_data['Combined Rating'] = (combined_data['Rating_x'] + combined_data['Rating_y']) / 2
combined_data['Total Reviews'] = combined_data['Number of Reviews_x'] + combined_data['Number of Reviews_y']

# Filter data based on the selected location
place_df = combined_data[combined_data['Location'].str.lower().str.contains(place.lower())]

# Sort the data by total reviews and combined rating (popularity-based filtering)
sorted_data = place_df.sort_values(by=['Total Reviews', 'Combined Rating'], ascending=[False, False])

# Reset the index for cleaner display
sorted_data.reset_index(drop=True, inplace=True)

# Select top 10 popular restaurants
popular_restaurants = sorted_data[['Restaurant', 'Location', 'Total Reviews', 'Combined Rating']].head(10)

# Rename columns for better readability
popular_restaurants = popular_restaurants.rename(columns={
    'Restaurant': 'Name',
    'Total Reviews': 'Number of Reviews',
    'Combined Rating': 'Average Rating'
})

# Display the dataframe in Streamlit
st.dataframe(popular_restaurants.style.format({
    'Number of Reviews': '{:.0f}',
    'Average Rating': '{:.1f}'
}))


import pandas as pd
import ipywidgets as widgets
from IPython.display import display, HTML

# Load the GoogleReview and TripAdvisor datasets
google_review_data = pd.read_csv('GoogleReview_data_cleaned.csv')
tripadvisor_data = pd.read_csv('TripAdvisor_data_cleaned.csv')

# Clean datasets
google_review_data.dropna(axis=0, how='any', inplace=True)
tripadvisor_data.dropna(axis=0, how='any', inplace=True)
google_review_data.drop_duplicates(inplace=True, keep='first')
tripadvisor_data.drop_duplicates(inplace=True, keep='first')

# Add 'Number of Reviews' columns if not present in the datasets
if 'Number of Reviews' not in google_review_data.columns:
    google_review_data['Number of Reviews'] = google_review_data['Review'].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)
if 'Number of Reviews' not in tripadvisor_data.columns:
    tripadvisor_data['Number of Reviews'] = tripadvisor_data['Review'].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)

# Map the location to the respective CSV file
location_csv_map = {
    'Ipoh': 'Restaurants_Ipoh.csv',
    'JB': 'Restaurants_JB.csv',
    'KL': 'Restaurants_KL.csv',
    'Kuching': 'Restaurants_Kuching.csv',
    'Langkawi': 'Restaurants_Langkawi.csv',
    'Melaka': 'Restaurants_Melaka.csv',
    'Miri': 'Restaurants_Miri.csv',
    'Penang': 'Restaurants_Penang.csv',
    'Petaling Jaya': 'Restaurants_Petaling Jaya.csv',
    'Shah Alam': 'Restaurants_Shah Alam.csv'
}

# Define a function to update and display the data
def update_display(location, top_n, min_rating, max_rating):
    try:
        # Load the location-specific restaurant data
        location_file = location_csv_map.get(location)
        if not location_file:
            print("Invalid location.")
            return

        # Load the restaurant data for the selected location
        location_restaurant_data = pd.read_csv(location_file)

        # Ensure that the user input is valid
        top_n = top_n.strip()
        top_n = int(top_n) if top_n else None
        min_rating = float(min_rating)
        max_rating = float(max_rating)

        if min_rating < 0 or max_rating > 5:
            raise ValueError("Rating must be between 0 and 5.")
        if min_rating > max_rating:
            raise ValueError("Minimum rating cannot be greater than maximum rating.")

        # Merge the location restaurant data with Google and TripAdvisor data
        combined_data = pd.merge(google_review_data, tripadvisor_data, on='Restaurant', how='inner')
        combined_data = pd.merge(combined_data, location_restaurant_data[['Restaurant', 'url']], on='Restaurant', how='inner')

        # Calculate the combined rating and total number of reviews
        combined_data['Combined Rating'] = (combined_data['Rating_x'] + combined_data['Rating_y']) / 2
        combined_data['Total Reviews'] = combined_data['Number of Reviews_x'] + combined_data['Number of Reviews_y']

        # Add the location column
        combined_data['Location'] = location

        # Remove duplicates to ensure each restaurant appears only once
        combined_data = combined_data.drop_duplicates(subset=['Restaurant'], keep='first')

        # Filter by rating range
        filtered_data = combined_data[(combined_data['Combined Rating'] >= min_rating) & (combined_data['Combined Rating'] <= max_rating)]

        # Sort by combined rating and total reviews
        sorted_data = filtered_data.sort_values(by=['Combined Rating', 'Total Reviews'], ascending=[False, False])

        # If top_n is specified, select the top N results
        if top_n:
            popular_restaurants = sorted_data[['Restaurant', 'Location', 'url', 'Total Reviews', 'Combined Rating']].head(top_n)
        else:
            popular_restaurants = sorted_data[['Restaurant', 'Location', 'url', 'Total Reviews', 'Combined Rating']]

        # Rename columns
        popular_restaurants = popular_restaurants.rename(columns={
            'Restaurant': 'Name',
            'Total Reviews': 'Number of Reviews',
            'Combined Rating': 'Average Rating'
        })

        # Add a ranking column
        popular_restaurants.reset_index(drop=True, inplace=True)
        popular_restaurants.index += 1
        popular_restaurants.index.name = 'Rank'

        # Convert the restaurant name and URL to clickable links
        popular_restaurants['url'] = popular_restaurants.apply(lambda row: f'<a href="{row["url"]}" target="_blank">{row["Name"]}</a>', axis=1)

        # Display the DataFrame as an HTML table with clickable links
        display(HTML(popular_restaurants[['Name', 'Location', 'Number of Reviews', 'Average Rating', 'url']].to_html(escape=False)))

    except ValueError as e:
        print(f"Error: {e}")
    except KeyError as e:
        print(f"Error: {e}")

# Create a dropdown menu for location selection
locations = ['Ipoh', 'JB', 'KL', 'Kuching', 'Langkawi', 'Melaka', 'Miri', 'Penang', 'Petaling Jaya', 'Shah Alam']
dropdown_location = widgets.Dropdown(
    options=locations,
    value='KL',  # Default value
    description='Location:',
)

# Create a text input for number of top results
text_input_top_n = widgets.Text(
    value='',  # Default value is empty
    description='Top N:',
    style={'description_width': 'initial'}
)

# Create text inputs for rating range
text_input_min_rating = widgets.Text(
    value='0',  # Default value
    description='Min Rating:',
    style={'description_width': 'initial'}
)

text_input_max_rating = widgets.Text(
    value='5',  # Default value
    description='Max Rating:',
    style={'description_width': 'initial'}
)

# Display the widgets and link them to the update_display function
widgets.interactive(update_display, location=dropdown_location, top_n=text_input_top_n, min_rating=text_input_min_rating, max_rating=text_input_max_rating)
