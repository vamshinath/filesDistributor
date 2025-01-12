import os
import shutil
import face_recognition
from PIL import Image

def process_actor_images(base_dir):
    # Traverse each directory in the base folder
    for actor_dir in os.listdir(base_dir):
        actor_path = os.path.join(base_dir, actor_dir)
        if os.path.isdir(actor_path):
            print(f"Processing actor directory: {actor_path}")
            
            # Create 'toTrain' directory
            to_train_dir = os.path.join(actor_path, 'toTrain')
            os.makedirs(to_train_dir, exist_ok=True)
            
            # Process images in the actor's directory
            for image_file in os.listdir(actor_path):
                image_path = os.path.join(actor_path, image_file)
                
                # Skip directories and the 'toTrain' directory itself
                if os.path.isdir(image_path) or image_file == 'toTrain':
                    continue
                
                try:
                    # Load image and detect faces
                    image = face_recognition.load_image_file(image_path)
                    face_locations = face_recognition.face_locations(image)
                    
                    # If exactly one face is detected, copy to 'toTrain'
                    if len(face_locations) == 1:
                        print(f"Single face detected in {image_file}, copying to 'toTrain'.")
                        shutil.copy(image_path, to_train_dir)
                    else:
                        print(f"{image_file} skipped: {len(face_locations)} faces detected.")
                
                except Exception as e:
                    print(f"Error processing {image_file}: {e}")

# Replace 'base_directory' with the path to your actors' directories
base_directory = "/home/vamshi/Pictures/4K Stogram/trainData"
process_actor_images(base_directory)
