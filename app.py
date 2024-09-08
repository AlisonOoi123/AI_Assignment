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
    .table-container {{
        background-color: rgba(50, 50, 50, 0.9); /* Dark grey background with slight transparency */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5); /* Shadow for better visibility */
        overflow-x: auto; /* Allows horizontal scrolling if needed */
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: auto; /* Ensures table resizes based on content */
    }}
    th, td {{
        border: 1px solid #555; /* Darker border for better visibility */
        padding: 8px;
        text-align: left;
    }}
    th {{
        background-color: #333; /* Dark grey background for header */
        color: #ffffff; /* White text for header */
    }}
    td {{
        color: #ffffff; /* White text for all columns */
    }}
    td.url {{
        color: #1a0dab; /* Blue color for URL text */
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 style="font-size:35px; color: #ffffff;">Most Popular Restaurants Based on Reviews and Ratings</h1>', unsafe_allow_html=True)

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

def update_display(location, top_n, min_rating, max_rating):
    try:
        # Load the location-specific restaurant data
        location_file = location_csv_map.get(location)
        if not location_file:
            st.error("Invalid location.")
            return

        # Load the restaurant data for the selected location
        location_restaurant_data = pd.read_csv(location_file)

        # Ensure that the user input is valid
        top_n = int(top_n) if top_n else None
        min_rating = float(min_rating)
        max_rating = float(max_rating)

        if min_rating < 0 or max_rating > 5:
            st.error("Rating must be between 0 and 5.")
            return
        if min_rating > max_rating:
            st.error("Minimum rating cannot be greater than maximum rating.")
            return

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
            'Combined Rating': 'Average Rating',
            'url': 'URL'
        })

        # Add a ranking column
        popular_restaurants.reset_index(drop=True, inplace=True)
        popular_restaurants.index += 1
        popular_restaurants.index.name = 'Rank'
        popular_restaurants['Rank'] = popular_restaurants.index

        # Convert the restaurant name and URL to clickable links
        popular_restaurants['URL'] = popular_restaurants.apply(lambda row: f'<a href="{row["URL"]}" class="url" target="_blank">{row["Name"]}</a>', axis=1)

        # Display the DataFrame with styling
        table_placeholder = st.empty()
        table_placeholder.markdown('<div class="table-container">' + popular_restaurants[['Rank', 'Name', 'Location', 'Number of Reviews', 'Average Rating', 'URL']].to_html(escape=False, index=False) + '</div>', unsafe_allow_html=True)

        # Dropdown to select restaurant
        restaurant_list = popular_restaurants['Name'].tolist()
        selected_restaurant = st.selectbox("Select a restaurant to see reviews:", restaurant_list)

        if selected_restaurant:
            # Extract reviews for the selected restaurant
            google_reviews = google_review_data[google_review_data['Restaurant'] == selected_restaurant]
            tripadvisor_reviews = tripadvisor_data[tripadvisor_data['Restaurant'] == selected_restaurant]

            # Display reviews
            st.markdown(f"### Google Reviews for {selected_restaurant}")
            if not google_reviews.empty:
                st.dataframe(google_reviews[['Author', 'Review']])

            st.markdown(f"### TripAdvisor Reviews for {selected_restaurant}")
            if not tripadvisor_reviews.empty:
                st.dataframe(tripadvisor_reviews[['Author', 'Review']])

    except ValueError as e:
        st.error(f"Error: {e}")
    except KeyError as e:
        st.error(f"Error: {e}")

# Streamlit inputs
place = st.selectbox("Select the state location:", 
                     ['KL', 'Ipoh', 'JB', 'Kuching', 'Langkawi', 'Melaka', 'Miri', 'Penang', 'Petaling Jaya', 'Shah Alam'])
top_n = st.text_input("Enter the number of top results:", "10")
min_rating = st.text_input("Minimum rating:", "0")
max_rating = st.text_input("Maximum rating:", "5")

# Run the update_display function based on user inputs
if st.button("Search"):
    update_display(place, top_n, min_rating, max_rating)