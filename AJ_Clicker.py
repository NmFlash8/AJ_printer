import json
import win32api, win32con
import time
import keyboard

file_path = input("file path: ")
 
with open(file_path, 'r') as json_file:
    data = json.load(json_file)

def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

# Print the loaded data
canvas_coords = data['canvas_click_coords']
palette_coords = data['palette_click_coords']

start = int(input("Enter Starting Int: "))
skip = 1
print(len(canvas_coords))
for i in range(start, len(canvas_coords), skip):
    if i % 10 == 0:
        time.sleep(.08)
        if keyboard.is_pressed('x'):
            break
    click(palette_coords[i][0], palette_coords[i][1])
    # time.sleep(0.001)
    click(canvas_coords[i][0], canvas_coords[i][1])
print(i)