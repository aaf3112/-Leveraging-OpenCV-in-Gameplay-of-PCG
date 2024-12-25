import cv2  
import numpy as np
import time
import pyautogui
import subprocess
import psutil
import os
 
# Define the background color for gap detection in RGB
background_color_rgb = (201, 160, 69)

# Create screenshots directory if it doesn't exist
os.makedirs("screenshots", exist_ok=True)

# Load Mario templates in grayscale
mario_template_paths = [
    r'player_frame_0-removebg.png',  
    r'marion_running_1-removebg.png',  
    r'mario_running-removebg-.png'   
]
mario_templates = [cv2.imread(path, 0) for path in mario_template_paths]

# Load pipe template in grayscale
pipe_template_path = r'pipeblock.png'
pipe_template = cv2.imread(pipe_template_path, 0)
pipe_template_edges = cv2.Canny(pipe_template, 100, 200)
pipe_height, pipe_width = pipe_template_edges.shape

# Load mystery block template in grayscale
mystery_block_template_path = r'MysteryBlock.png'
mystery_block_template = cv2.imread(mystery_block_template_path, 0)
mystery_block_template_edges = cv2.Canny(mystery_block_template, 100, 200)

# Initialize ground level y-coordinate
initial_ground_y = None

def adjust_brightness_contrast(image, brightness=0, contrast=1):
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    y_channel, u_channel, v_channel = cv2.split(yuv_image)
    y_channel = cv2.convertScaleAbs(y_channel, alpha=contrast, beta=brightness)
    adjusted_yuv = cv2.merge((y_channel, u_channel, v_channel))
    adjusted_image = cv2.cvtColor(adjusted_yuv, cv2.COLOR_YUV2BGR)
    return adjusted_image

def filter_mario_colors(image):
    adjusted_image = adjust_brightness_contrast(image, brightness=-50, contrast=2)
    return adjusted_image

def process_template(template):
    template_rgb = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    template_filtered = filter_mario_colors(template_rgb)
    template_edges = cv2.Canny(template_filtered, 100, 200)
    return template_edges

mario_templates_edges = [process_template(template) for template in mario_templates]
mario_height, mario_width = mario_templates_edges[0].shape

def capture_screen():
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    if screenshot.size == 0:
        raise ValueError("Screenshot is empty.")
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    screen_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    return screenshot, screen_gray

def detect_mario_with_edge_detection(screen, screenshot):
    adjusted_screen = filter_mario_colors(screen)
    screen_edges = cv2.Canny(adjusted_screen, 100, 200)

    for mario_template_edges in mario_templates_edges:
        result = cv2.matchTemplate(screen_edges, mario_template_edges, cv2.TM_CCOEFF_NORMED)
        threshold = 0.2
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            top_left = max_loc
            bottom_right = (top_left[0] + mario_width, top_left[1] + mario_height)
            cv2.rectangle(screenshot, top_left, bottom_right, (255, 0, 0), 2)
            detected_img_filename = "screenshots/detected_mario_edges.png"
            cv2.imwrite(detected_img_filename, cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
            print(f"Mario detected and saved as {detected_img_filename}")
            return top_left, screenshot

    no_detection_filename = "screenshots/no_detection_edges.png"
    cv2.imwrite(no_detection_filename, cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
    print(f"No Mario detected. Screenshot saved as {no_detection_filename}")
    return None, screenshot

enemy_template_paths = [
    r'enemy_new_1-removebg.png',
    r'enemy_new-removebg.png',
    r'koopa_trans.png',   
    r'koopa_trans1.png'  
]
enemy_templates = [cv2.imread(path, 0) for path in enemy_template_paths]
enemy_templates_edges = [process_template(template) for template in enemy_templates]
enemy_height, enemy_width = enemy_templates_edges[0].shape

def detect_pipe(screen):
    adjusted_screen = filter_mario_colors(screen)
    screen_edges = cv2.Canny(adjusted_screen, 100, 200)

    result = cv2.matchTemplate(screen_edges, pipe_template_edges, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val > threshold:
        top_left = max_loc

        # Capture screenshot if pipe is detected
        pipe_detection_screenshot_path = f"screenshots/pipe_detected_{int(time.time())}.png"
        screenshot_copy = screen.copy()
        cv2.rectangle(screenshot_copy, top_left, (top_left[0] + pipe_width, top_left[1] + pipe_height), (0, 255, 0), 2)
        cv2.imwrite(pipe_detection_screenshot_path, cv2.cvtColor(screenshot_copy, cv2.COLOR_BGR2RGB))
        print(f"Pipe detected. Screenshot saved at {pipe_detection_screenshot_path}")

        return top_left

    return None

def detect_mystery_block(screen, mario_position):
    adjusted_screen = filter_mario_colors(screen)
    screen_edges = cv2.Canny(adjusted_screen, 100, 200)
    result = cv2.matchTemplate(screen_edges, mystery_block_template_edges, cv2.TM_CCOEFF_NORMED)
    threshold = 0.2
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val > threshold:
        top_left = max_loc
        
        # Check if the detected mystery block is close to Mario's y-coordinate
        mystery_block_y = top_left[1]
        mario_y = mario_position[1]
        
        # Define a threshold for how close the mystery block should be to Mario
        if abs(mystery_block_y - mario_y) < 200 and abs(top_left[0] - mario_position[0]) < 20:  # Adjust x-coordinate tolerance
            return top_left
        
    return None

def detect_gap_below_mario(screen, mario_position):
    x_coord_check = mario_position[0] + 250
    y_coord_check = mario_position[1] + 110

    # Check if color at coordinates matches background color
    color_pixel = screen[y_coord_check, x_coord_check]
    print(f"Detected color at gap check: {color_pixel}")
    if np.allclose(color_pixel, background_color_rgb, atol=10):
        gap_check_screenshot_path = f"screenshots/gap_check_{int(time.time())}.png"
        cv2.imwrite(gap_check_screenshot_path, screen)
        print(f"Gap detection check saved at {gap_check_screenshot_path}")
        return True
    return False

# Define colors to check for in front of Mario
target_colors_bgr = [
    (12, 76, 200),  
    (0, 0, 0),      
    (12, 76, 200),  
]

def color_in_front_of_mario(screen, mario_position):
    # Define the region in front of Mario to check
    region_x_start = mario_position[0] + 50  
    region_y_start = mario_position[1] - 10  
    region_width = 20  
    region_height = mario_position[1] + 30 - region_y_start  

    # Extract the region from the screen
    region = screen[region_y_start:region_y_start + region_height, region_x_start:region_x_start + region_width]

    # Convert region to RGB format if it's not already
    region_rgb = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)

    # Check if any pixel in the region matches the target colors
    for color in target_colors_bgr:
        mask = cv2.inRange(region_rgb, np.array(color) - 10, np.array(color) + 10)  # Allow a small tolerance
        if cv2.countNonZero(mask) > 0:
            return True  # Color found

    return False  # No target color detected

def move_right(duration=0.4):
    pyautogui.keyDown('right')
    time.sleep(duration)
    pyautogui.keyUp('right')

def jump():
    pyautogui.keyDown('up')
    time.sleep(0.3)
    pyautogui.keyUp('up')

def long_jump():
    pyautogui.keyDown('right')
    pyautogui.keyDown('up')
    time.sleep(0.5)  
    pyautogui.keyUp('up')
    pyautogui.keyUp('right')

def move_right_and_jump(move_duration=0.5, jump_duration=0.5):
    print("Moving right and jumping...")
    pyautogui.keyDown('right')
    time.sleep(move_duration)
    pyautogui.keyDown('up')
    time.sleep(jump_duration)
    pyautogui.keyUp('up')
    pyautogui.keyUp('right')

def start_game(game_path):
    print("Starting the game...")
    process = subprocess.Popen(game_path)
    time.sleep(5)
    return process

def is_same_x_position(new_position, old_position, tolerance):
    return abs(new_position[0] - old_position[0]) <= tolerance

def is_game_running(process):
    return process.poll() is None

stop_distance_threshold = 200  
jump_distance_threshold = 50   

def detect_enemy(screen, mario_position):
    adjusted_screen = filter_mario_colors(screen)
    screen_edges = cv2.Canny(adjusted_screen, 100, 200)

    for enemy_template_edges in enemy_templates_edges:
        result = cv2.matchTemplate(screen_edges, enemy_template_edges, cv2.TM_CCOEFF_NORMED)
        threshold = 0.3
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > threshold:
            top_left = max_loc
            bottom_right = (top_left[0] + enemy_width, top_left[1] + enemy_height)
            cv2.rectangle(screen, top_left, bottom_right, (0, 0, 255), 2)  
            cv2.putText(screen, "Enemy", (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            # Save screenshot with enemy detection highlighted
            enemy_detected_screenshot_path = f"screenshots/enemy_detected_{int(time.time())}.png"
            cv2.imwrite(enemy_detected_screenshot_path, screen)
            print(f"Enemy detected: True at position: {top_left}. Screenshot saved as {enemy_detected_screenshot_path}")

            # Check distance between Mario and the detected enemy
            distance_to_enemy = top_left[0] - mario_position[0]
            if distance_to_enemy < stop_distance_threshold and distance_to_enemy > jump_distance_threshold:
                print("Enemy detected at a distance; Mario stops.")
                pyautogui.keyUp('right')  
            elif distance_to_enemy <= jump_distance_threshold:
                print("Enemy close to Mario; jumping.")
                jump()
            return top_left

    print("Enemy detected: False")
    return None

def main():
    global initial_ground_y  # Access initial_ground_y at global level to use for gap detection reset
    game_path = r"\path to the game.exe file"
    game_process = start_game(game_path)
    print("You have 3 seconds to switch to the game window...")
    time.sleep(3)

    previous_position = None
    same_position_count = 0
    same_position_tolerance = 50
    last_check_time = time.time()
    check_interval = 0.5
    slow_down_duration = 0.2  # Set slower speed after jumping over pipe
    slow_down_counter = 0  # Tracks how long to slow down after pipe jump
    normal_speed_duration = 0.3  # Normal move right speed

    # Variable to toggle gap detection based on Mario's y-coordinate after jumping
    enable_gap_detection = True

    while is_game_running(game_process):
        screen, screenshot = capture_screen()

        if time.time() - last_check_time >= check_interval:
            mario_position, _ = detect_mario_with_edge_detection(screen, screenshot)
            pipe_position = detect_pipe(screen)

            if pipe_position:
                print(f"Pipe detected at position: {pipe_position}")
            else:
                print("No pipe detected.")
                
            if mario_position is not None:
                # Proceed with further actions only if Mario's position is detected
                print(f"Mario detected at position: {mario_position}")

                # Detect mystery block and enemy only if Mario is detected
                mystery_block_position = detect_mystery_block(screen, mario_position)
                # In main, update the call to detect_enemy to include mario_position
                enemy_position = detect_enemy(screen, mario_position)

                # Set initial ground level once, assuming it's the y-coordinate of Mario's first detection
                if initial_ground_y is None:
                    initial_ground_y = mario_position[1]

                # Check if Mario has returned to ground level; if so, enable gap detection
                if mario_position[1] == initial_ground_y:
                    enable_gap_detection = True
                else:
                    enable_gap_detection = False

                # Perform gap detection only if enabled
                gap_detected = enable_gap_detection and detect_gap_below_mario(screen, mario_position)
                print(f"Gap detection result: {gap_detected}")  # Log the result
                
                if color_in_front_of_mario(screen, mario_position):
                    print("Obstacle color detected in front of Mario! Jumping.")
                    jump()
                else:
                    move_right()  # Move right if no obstacle detected

                if gap_detected:
                    print("Gap detected! Executing long jump.")
                    move_right(duration=0.4)
                    long_jump()
                elif pipe_position and abs(pipe_position[0] - mario_position[0]) < 150:
                    print("Pipe detected close to Mario. Moving right and jumping!")
                    print(f"Pipe position: {pipe_position}, Mario position: {mario_position}")
                    move_right_and_jump(move_duration=1, jump_duration=0.3)
                    slow_down_counter = 20  # Slow down for 20 frames after pipe jump
                elif mystery_block_position and is_same_x_position(mystery_block_position, mario_position, same_position_tolerance):
                    print(f"Mario Position: {mario_position}, Mystery Block Position: {mystery_block_position}")
                    print("Mystery block directly above Mario! Jumping!")
                    jump()  # Trigger jump when mystery block is directly above
                    move_right()
                elif enemy_position and abs(enemy_position[0] - mario_position[0]) < 150:
                    print("Enemy detected in front of Mario! Jumping to avoid it.")
                    move_right(duration=0.2)
                    jump()  # Mario jumps when enemy is detected in close proximity
                    move_right()
                else:
                    if slow_down_counter > 0:
                        print("Slowing down after jumping over pipe...")
                        move_right(duration=slow_down_duration)  # Move at slower speed after pipe jump
                        slow_down_counter -= 1  # Decrement the counter
                    else:
                        move_right(duration=normal_speed_duration)

            previous_position = mario_position
            last_check_time = time.time()

        time.sleep(0.01)

    print("Game has terminated.")
    for proc in psutil.process_iter():
        if proc.pid == game_process.pid:
            proc.kill()

if __name__ == "__main__":
    main()
