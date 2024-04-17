import os
import keyboard
import time
import pyautogui
import pickle
import json
import shutil
from PIL import Image

def setup():
    try:
        with open('settings.pkl', 'rb') as file:
            saved_settings = pickle.load(file)
            return saved_settings
    except FileNotFoundError:
        pass

    print("Please mark the following positions:")
    positions = ["Top left of color palette", "Bottom right of color palette",
                 "Top left of canvas", "Bottom right of canvas", "Undo button"]
    marked_positions = [mark_position(pos) for pos in positions]
    with open('settings.pkl', 'wb') as file:
        pickle.dump(marked_positions, file)
    return marked_positions

def rgb_similarity(rgb1, rgb2):
    # Extracting individual components
    r1, g1, b1 = rgb1[:3]
    r2, g2, b2 = rgb2[:3]
    
    # Calculating squared Euclidean distance
    distance_sq = (r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2
    
    # Squaring the max distance for normalization
    max_distance_sq = (255**2 + 255**2 + 255**2)
    
    # Calculating similarity without taking square root
    similarity = 1 - (distance_sq / max_distance_sq)
    
    return similarity * 100

def mark_position(message):
    print(message)
    while True:
        if keyboard.is_pressed('p'):
            position = pyautogui.position()
            print(f"Position recorded: {position}")
            return position
        time.sleep(0.05)

def main():
    # Folder names
    starting_folder = "start"
    json_folder = "jsons"
    finished_folder = "finished"

    # Create folders if they don't exist
    for folder in [starting_folder, json_folder, finished_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    print("[1-5] 1 being the higest 3 being average")
    quality = int(input("Quality: "))
    starting_files = os.listdir(starting_folder)

    for filename in starting_files:
        if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_path = os.path.join(starting_folder, filename)
            image_name, image_format = os.path.splitext(filename)
            finished_path = os.path.join(finished_folder, filename)
            json_output_path = os.path.join(json_folder, f'{image_name}.json')

            image = Image.open(image_path)
            positions = setup()
            starting_x = 0
            starting_y = 0
            palette_top_left, palette_bottom_right, canvas_top_left, canvas_bottom_right, undo_button = positions

            canvas_width = canvas_bottom_right[0] - canvas_top_left[0]
            canvas_height = canvas_bottom_right[1] - canvas_top_left[1]
            image = image.resize((canvas_width, canvas_height))

            # create a list of every pixel color in the palette
            palette = Image.open("palette.png")
            palette_colors = list(palette.getdata()) 

            canvas_click_coords = []
            palette_click_coords = []

            start_time = time.time()
            drawn_pixels = 1
            total_pixels = (canvas_width / quality) * (canvas_height / quality)

            # Compare each pixel to each pixel in the color palette keep the closest quality
            # FIND A MORE EFFECIENT WAY: O(n^2)
            for y in range(starting_y, canvas_height, quality):
                for x in range(starting_x, canvas_width, quality):
                    selected_pixel = image.getpixel((x, y))[:3]
                    most_similar = 0
                    color_location = 0
                    for index, palette_pixel in enumerate(palette_colors):
                        current_score = rgb_similarity(selected_pixel, palette_pixel)
                        if current_score > most_similar:
                            most_similar = current_score
                            color_location = index

                    # Calculate the position of the color within the palette image
                    palette_columns = palette_bottom_right[0] - palette_top_left[0]
                    palette_x = color_location % palette_columns + palette_top_left[0]
                    palette_y = color_location // palette_columns + palette_top_left[1]

                    # Add locations of where to click on the canvas / the color palette to list
                    palette_click_coords.append((palette_x, palette_y))
                    canvas_click_coords.append((x + canvas_top_left[0], y + canvas_top_left[1]))
                    
                    print(f"[{(drawn_pixels / total_pixels) * 100:6.2f}%] [X:{x:>4}] [Y:{y:>4}] [{most_similar:6.2f}%] [R:{selected_pixel[0]:>3} G:{selected_pixel[1]:>3} B:{selected_pixel[2]:>3}] {image_name}{image_format} ", end="\r")
                    drawn_pixels += 1

            end_time = time.time()
            elapsed_time = end_time - start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            print()
            print(f"[{image_name}{image_format}] took {hours}h {minutes}m {seconds}s")

            # Save the coordinates as JSON
            with open(json_output_path, 'w') as json_file:
                json.dump({"canvas_click_coords": canvas_click_coords, "palette_click_coords": palette_click_coords}, json_file)

            # Move image file from start to finished folder
            shutil.move(image_path, finished_path)

if __name__ == "__main__":
    main()
