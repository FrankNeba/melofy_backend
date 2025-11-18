from PIL import Image, ImageDraw, ImageFont

def generate_man_with_dog_image(output_filename="man_with_dog.png"):
    # --- Image Dimensions and Colors ---
    width, height = 800, 600
    background_color = (173, 216, 230)  # Light Blue (sky)
    ground_color = (144, 238, 144)    # Light Green (grass)

    man_skin_color = (255, 224, 189)  # Peach
    man_shirt_color = (70, 130, 180)   # Steel Blue
    man_pants_color = (47, 79, 79)     # Dark Slate Grey

    dog_color = (139, 69, 19)          # Saddle Brown
    dog_ear_color = (101, 67, 33)      # Medium Taupe

    text_color = (0, 0, 0)             # Black

    # --- Create the Base Image ---
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # --- Draw the Ground ---
    draw.rectangle([0, height // 2, width, height], fill=ground_color)

    # --- Draw the Man ---
    # Man's head (circle)
    head_radius = 40
    head_center_x = width // 2
    head_center_y = height // 2 - 80 # Above the ground
    draw.ellipse(
        [head_center_x - head_radius, head_center_y - head_radius,
         head_center_x + head_radius, head_center_y + head_radius],
        fill=man_skin_color,
        outline='black', width=2
    )

    # Man's body (rectangle)
    body_width = 100
    body_height = 150
    body_x1 = head_center_x - body_width // 2
    body_y1 = head_center_y + head_radius
    body_x2 = body_x1 + body_width
    body_y2 = body_y1 + body_height
    draw.rectangle([body_x1, body_y1, body_x2, body_y2], fill=man_shirt_color, outline='black', width=2)

    # Man's arms (rectangles) - simplified, one arm holding the dog
    arm_width = 30
    arm_length = 70
    
    # Left arm (straight down)
    draw.rectangle([body_x1 - arm_width, body_y1 + 20, body_x1, body_y1 + 20 + arm_length], fill=man_shirt_color, outline='black', width=1)
    # Left hand (small circle)
    draw.ellipse([body_x1 - arm_width - 5, body_y1 + 20 + arm_length - 10, body_x1 + 5, body_y1 + 20 + arm_length + 10], fill=man_skin_color, outline='black', width=1)


    # Right arm (bent, for holding the dog)
    arm_bend_x = head_center_x + body_width // 2 # Right side of body
    arm_bend_y = body_y1 + 30
    draw.line([arm_bend_x, arm_bend_y, arm_bend_x + 30, arm_bend_y - 20], fill=man_shirt_color, width=arm_width, joint="curve") # Upper arm
    draw.line([arm_bend_x + 30, arm_bend_y - 20, arm_bend_x + 60, arm_bend_y + 10], fill=man_shirt_color, width=arm_width, joint="curve") # Forearm
    # Right hand (small circle, where the dog will be)
    man_hand_x = arm_bend_x + 60
    man_hand_y = arm_bend_y + 10
    draw.ellipse([man_hand_x - 10, man_hand_y - 10, man_hand_x + 10, man_hand_y + 10], fill=man_skin_color, outline='black', width=1)


    # Man's legs (rectangles)
    leg_width = 40
    leg_height = 100
    leg_y1 = body_y2
    leg_y2 = leg_y1 + leg_height

    # Left leg
    draw.rectangle([body_x1, leg_y1, body_x1 + leg_width, leg_y2], fill=man_pants_color, outline='black', width=2)
    # Right leg
    draw.rectangle([body_x2 - leg_width, leg_y1, body_x2, leg_y2], fill=man_pants_color, outline='black', width=2)


    # --- Draw the Dog (positioned at the man's hand) ---
    dog_body_width = 80
    dog_body_height = 40
    dog_head_radius = 20

    # Dog's position relative to the man's hand
    dog_x_offset = -10 # Move slightly to the left of the hand
    dog_y_offset = -30 # Move slightly above the hand

    dog_body_x1 = man_hand_x + dog_x_offset
    dog_body_y1 = man_hand_y + dog_y_offset
    dog_body_x2 = dog_body_x1 + dog_body_width
    dog_body_y2 = dog_body_y1 + dog_body_height

    # Dog's body (rounded rectangle for a softer look)
    draw.rounded_rectangle([dog_body_x1, dog_body_y1, dog_body_x2, dog_body_y2], 
                           radius=10, fill=dog_color, outline='black', width=2)

    # Dog's head (circle)
    dog_head_center_x = dog_body_x1 + dog_head_radius
    dog_head_center_y = dog_body_y1 + dog_head_radius
    draw.ellipse(
        [dog_head_center_x - dog_head_radius, dog_head_center_y - dog_head_radius,
         dog_head_center_x + dog_head_radius, dog_head_center_y + dog_head_radius],
        fill=dog_color,
        outline='black', width=2
    )
    
    # Dog's ears (triangles or small rounded rectangles)
    draw.polygon([dog_head_center_x - 15, dog_head_center_y - dog_head_radius + 5,
                  dog_head_center_x - 5, dog_head_center_y - dog_head_radius - 15,
                  dog_head_center_x - 5, dog_head_center_y - dog_head_radius + 5],
                 fill=dog_ear_color, outline='black', width=1)
    draw.polygon([dog_head_center_x + 15, dog_head_center_y - dog_head_radius + 5,
                  dog_head_center_x + 5, dog_head_center_y - dog_head_radius - 15,
                  dog_head_center_x + 5, dog_head_center_y - dog_head_radius + 5],
                 fill=dog_ear_color, outline='black', width=1)
                 
    # Dog's nose (small circle)
    draw.ellipse([dog_head_center_x + 5, dog_head_center_y + 5, dog_head_center_x + 15, dog_head_center_y + 15], fill='black')


    # --- Add Text ---
    try:
        # Try to load a common font. Fallback if not found.
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default() # Fallback to default PIL font

    message = "A Man and His Best Friend"
    text_bbox = draw.textbbox((0,0), message, font=font) # Get bounding box to center text
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (width - text_width) // 2
    text_y = 50 # Near the top
    draw.text((text_x, text_y), message, fill=text_color, font=font)


    # --- Save the Image ---
    img.save(output_filename)
    print(f"Image '{output_filename}' generated successfully!")

# --- Run the script ---
if __name__ == "__main__":
    generate_man_with_dog_image()

# Display the generated image if running in an environment that supports it
# try:
#     Image.open("man_with_dog.png").show()
# except Exception:
#     pass