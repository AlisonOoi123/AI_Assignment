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
