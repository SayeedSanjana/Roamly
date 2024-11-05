import pandas as pd
import random

# Lists of sample data for variety
names = ["John", "Jane", "Alice", "Bob", "Charlie", "Dave", "Eve", "Grace", "Hank", "Ivy", 
         "Liam", "Olivia", "Noah", "Emma", "William", "Sophia", "James", "Mia", "Benjamin", "Charlotte"]
cuisines = ["French", "Deli", "Quebecois", "Seafood", "Italian", "Japanese", "Mexican", "Chinese", 
            "Indian", "Mediterranean", "Thai", "Vegan", "Steakhouse", "Pizzeria", "Korean", "BBQ"]
outdoor_categories = ["Parks", "Beach", "Trail", "Zoo", "Lake", "Botanical Garden", "Amusement Park", "Recreational Area","Biking","Beaches","Boating"]
indoor_categories = ["Museum", "Science Center", "Planetarium", "Art Gallery", "Theater", "Bowling Alley", "Gym","Yoga","Library",
                     "Trampoline Park", "Aquarium", "Library", "Gym", "Escape Room", "Music Venue", "Pub", "Bar","Karoke"]

# Dummy places for each category
places = {
    "Restaurant": [
        {"name": "The Gourmet Bistro", "address": "123 Foodie Lane", "cuisine": random.choice(cuisines)},
        {"name": "Sushi Delight", "address": "456 Sashimi Blvd", "cuisine": random.choice(cuisines)},
        {"name": "Pasta Palace", "address": "789 Noodle St", "cuisine": random.choice(cuisines)},
        {"name": "BBQ Barn", "address": "321 Grill Ave", "cuisine": random.choice(cuisines)},
        {"name": "The Vegan Spot", "address": "654 Green Rd", "cuisine": random.choice(cuisines)}
    ],
    "Outdoor Place": [
        {"name": "Sunnyvale Park", "address": "111 Sunshine Dr", "category": random.choice(outdoor_categories)},
        {"name": "Blue Lake Retreat", "address": "222 Waterfall Way", "category": random.choice(outdoor_categories)},
        {"name": "Forest Trail Adventure", "address": "333 Pine Path", "category": random.choice(outdoor_categories)},
        {"name": "Wildlife Zoo", "address": "444 Animal Rd", "category": random.choice(outdoor_categories)},
        {"name": "Mountain Ridge", "address": "555 Summit St", "category": random.choice(outdoor_categories)}
    ],
    "Indoor Place": [
        {"name": "Tech Science Center", "address": "777 Innovation Ave", "category": random.choice(indoor_categories)},
        {"name": "Starlight Planetarium", "address": "888 Galaxy Blvd", "category": random.choice(indoor_categories)},
        {"name": "Urban Art Gallery", "address": "999 Canvas Rd", "category": random.choice(indoor_categories)},
        {"name": "Grand Theater", "address": "101 Broadway St", "category": random.choice(indoor_categories)},
        {"name": "City Escape Room", "address": "202 Puzzle Pl", "category": random.choice(indoor_categories)}
    ]
}

# Function to generate random data
def generate_dummy_data(num_entries):
    data = []
    for _ in range(num_entries):
        name = random.choice(names)
        category = random.choice(list(places.keys()))
        place_info = random.choice(places[category])
        place = place_info["name"]
        address = place_info["address"]
        if category == "Restaurant":
            detail = place_info["cuisine"]
        else:
            detail = place_info["category"]
        rating = round(random.uniform(1, 5), 1)  # Ratings between 1.0 and 5.0
        data.append([name, category, place, address, detail, rating])
    return data

# Generate 3,000 dummy entries
dummy_data = generate_dummy_data(5000)

# Create a DataFrame with the generated data
df_dummy = pd.DataFrame(dummy_data, columns=["User", "Category", "Place", "Address", "Detail", "Rating"])

# Save the DataFrame to a CSV file
df_dummy.to_csv("dummy_user_visits.csv", index=False)

# Display the first few rows of the DataFrame
print("Dummy data saved to 'dummy_user_visits.csv'. Here are the first few rows:")
print(df_dummy.head())
