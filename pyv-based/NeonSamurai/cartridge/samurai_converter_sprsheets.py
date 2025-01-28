import os
import json

def convert_to_json_list_format(directory):
    files_changed = 0  # Counter for changed files
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        # Process only JSON files matching the specified pattern
        if filename.startswith("GreatSwordKnight_2hWalk_dir") and filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            print(f"Processing file: {filename}")
            
            # Read the original JSON file
            with open(filepath, 'r') as file:
                data = json.load(file)

            # Check if it has the problematic format
            if "frames" in data and isinstance(data["frames"], list):
                frames = data["frames"]
                # Create a proper JSON LIST format
                new_frames = []
                for index, frame_data in enumerate(frames):
                    new_frame = {
                        "filename": f"frame{index}.png",  # Use "frameN.png" naming
                        "frame": frame_data["frame"],
                        "duration": frame_data["duration"]
                    }
                    new_frames.append(new_frame)

                # Update the JSON structure
                new_data = {
                    "frames": new_frames,
                    "meta": data.get("meta", {})  # Preserve any existing metadata
                }

                # Overwrite the original JSON file
                with open(filepath, 'w') as new_file:
                    json.dump(new_data, new_file, indent=4)
                print(f"File overwritten: {filepath}")
                files_changed += 1
            else:
                print(f"File {filename} is already in a proper format or cannot be processed.")

    # Display how many files were changed
    print(f"\nTotal files changed: {files_changed}")

# Usage
input_directory = "graphics"  # Replace with the folder containing your JSON files
convert_to_json_list_format(input_directory)
