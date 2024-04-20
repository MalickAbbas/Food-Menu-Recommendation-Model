import pandas as pd
import numpy as np

def load_food_data():
    return pd.read_csv('food.csv')

def generate_menus(food_data, budget, num_people, course_types, diet_preferences):
    course_types = [course.strip().lower() for course in course_types]
    diet_preferences = [diet.strip().lower() for diet in diet_preferences]

    filtered_data = food_data[
        (food_data['course'].str.lower().isin(course_types)) &
        ((food_data['diet'].str.lower().isin(diet_preferences)) | (food_data['course'].str.lower() == 'dessert'))
    ].copy()  # Ensure we are working on a copy of the data

    # Avoid SettingWithCopyWarning by using .copy() or modifying the original dataframe safely
    filtered_data.loc[:, 'Total Needed'] = np.ceil(num_people / filtered_data['No Of Peoples Can Eat']).astype(int)
    filtered_data.loc[:, 'Total Cost'] = filtered_data['Price'] * filtered_data['Total Needed']

    # Sort data by 'Total Cost' descending to try to use up the budget with fewer items
    filtered_data.sort_values(by='Total Cost', ascending=False, inplace=True)

    menus = []
    while len(menus) < 5:
        current_budget = budget
        menu = []
        for course in course_types:
            course_filtered = filtered_data[(filtered_data['course'].str.lower() == course) & (filtered_data['Total Cost'] <= current_budget)]
            if not course_filtered.empty:
                selected_dish = course_filtered.iloc[0]
                menu.append({
                    'Dish': selected_dish['name'],
                    'Course': selected_dish['course'],
                    'Diet': selected_dish['diet'],
                    'Price per Unit': selected_dish['Price'],
                    'Total Units Needed': selected_dish['Total Needed'],
                    'Total Cost': selected_dish['Total Cost'],
                    'Image Link': selected_dish['Images']
                })
                current_budget -= selected_dish['Total Cost']
        if menu and all(course in [dish['Course'] for dish in menu] for course in course_types):
            menus.append(menu)
            filtered_data = filtered_data.loc[~filtered_data.index.isin([d.index for d in course_filtered.iterrows()])]
        if len(menus) == 5 or filtered_data.empty:
            break

    return menus

def accept_user_input():
    print("Enter your budget:")
    budget = int(input())
    print("Enter the number of people:")
    num_people = int(input())
    print("Select course types (comma-separated, e.g., starter, main course, dessert):")
    course_types = input().split(',')
    print("Enter diet preferences (comma-separated, e.g., vegetarian, non vegetarian):")
    diet_preferences = input().split(',')
    return budget, num_people, course_types, diet_preferences

def print_menus(menus):
    if not menus:
        print("No menus could be generated within the given constraints.")
        return
    for index, menu in enumerate(menus, start=1):
        print(f"\nMenu {index}:")
        for item in menu:
            print(f"  Dish: {item['Dish']}")
            print(f"  Course: {item['Course']}")
            print(f"  Diet: {item['Diet']}")
            print(f"  Price per Unit: ${item['Price per Unit']}")
            print(f"  Total Units Needed: {item['Total Units Needed']}")
            print(f"  Total Cost: ${item['Total Cost']}")
            print(f"  Image Link: {item['Image Link'] or 'No image available'}")
        total_cost = sum(dish['Total Cost'] for dish in menu)
        print(f"Total Menu Cost: ${total_cost}")
        print("-" * 40)

def interactive_menu_generation():
    budget, num_people, course_types, diet_preferences = accept_user_input()
    food_data = load_food_data()
    menus = generate_menus(food_data, budget, num_people, course_types, diet_preferences)
    print_menus(menus)

# Uncomment to run the program interactively
interactive_menu_generation()
