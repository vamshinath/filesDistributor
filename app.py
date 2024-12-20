import os,shutil,humanize
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image
from datetime import datetime
app = Flask(__name__)
IMAGES_PER_PAGE=45
Image.MAX_IMAGE_PIXELS = None
sortKey='dim'
sortOrder=False
getPropsfromDB=False
imagesAll=[]
# Route to render the index page
@app.route('/')
def index():
    global sortKey
    global sortOrder

    sortKey = request.args.get('sort','dim')
    sortOrder = request.args.get('order','desc') != 'asc'
    getPropsfromDB  = request.args.get('getFromDB','n') == 'y'


    return render_template('index.html')


def get_images_from_directory(root_dir):
    # List of common image file extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    
    alreadySeen = []
    try:
        with open(root_dir+"/seen.txt") as fl:
            for ln in fl:
                alreadySeen.append(ln[:-1])
    except Exception as e:
        alreadySeen=[]

    alreadySeen = set(alreadySeen)  # Convert to set if it's not already a set

    image_files = [f for f in os.listdir(root_dir) if f not in alreadySeen and f.lower().endswith(('jpg', 'jpeg', 'png', 'bmp','webp'))]
    #image_files_sorted = sorted(image_files, key=lambda f: os.path.getsize(os.path.join(root_dir, f)), )[:1000]
    print('files sorted')
    imgs_lookup = {}

    for img in image_files:
        try:
            Img = Image.open(os.path.join(root_dir, img))
            imgs_lookup[img] = {'dim':Img.size[0]*Img.size[1],'flsz':os.path.getsize(os.path.join(root_dir, img)),'w':Img.size[0],'h':Img.size[1]}
        except Exception as e:
            print(e)
            e=0

    print(sortKey,'reverse:',sortOrder)
    imgs_lookup = sorted(imgs_lookup.items(),key=lambda x:x[1][sortKey],reverse=sortOrder)
    image_files=[]
    for img,vals in imgs_lookup:
        flsz = humanize.naturalsize(os.path.getsize(os.path.join(root_dir, img))).strip().replace('\n','')
        image_files.append([img,str(vals['w'])+"x"+str(vals['h']),flsz])
    
    
    return image_files

@app.route('/load_images', methods=['POST'])
def load_images():
    global imagesAll
    # Get the directory path and page number from the UI
    directory = request.form.get('directory_path')
    page = int(request.form.get('page', 1))  # Default to page 1 if not provided
    firstSeen=False
    if directory:
        # Get all image filenames in the directory
        if imagesAll == []:
            firstSeen=True
            imagesAll = get_images_from_directory(directory)#[f for f in os.listdir(directory) if f.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp','webp'))]
        
        images = imagesAll[:IMAGES_PER_PAGE]
        imagesAll = imagesAll[IMAGES_PER_PAGE:]
        #print('total images:',len(images))
        # Calculate the start and end index for the current page
        start_index = (page - 1) * IMAGES_PER_PAGE
        end_index = start_index + IMAGES_PER_PAGE
        #print(start_index,end_index)
        images_on_page = images[0:IMAGES_PER_PAGE]
        # Get the images for the current page
        # if end_index >= len(images):
        #     images_on_page = images[start_index:]
        # else:
        #     images_on_page = images[start_index:end_index]
        #print('images',images_on_page)
        with open(directory+"/seen.txt",'a') as fl:
            if firstSeen:
                fl.write(str(datetime.now)+"----------------------------------------------------------------\n")
            for im in images_on_page:
                fl.write(im[0]+"\n")
        
        return jsonify({'images': images_on_page, 'page': page, 'total_images': len(images)})
    
    return jsonify({'images': []})


# Route to serve images from the specified directory
@app.route('/static/images/<filename>')
def serve_image(filename):
    # Get the directory path from the query parameters
    directory_path = request.args.get('directory_path')
    
    # Check if directory_path is valid and exists
    if directory_path and os.path.isdir(directory_path):
        return send_from_directory(directory_path, filename)
    else:
        return jsonify({'error': 'Invalid directory path'}), 400

# Route to delete an image from the given directory
@app.route('/delete_image', methods=['POST'])
def delete_image():
    image_name = request.form.get('image_name')
    directory_path = request.form.get('directory_path')  # Get directory from the request

    # Build the full path of the image
    image_path = os.path.join(directory_path, image_name)
    
    if os.path.exists(image_path):
        os.remove(image_path)  # Delete the image
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Image not found'}), 400

@app.route('/move_image', methods=['POST'])
def move_image():
    image_name = request.form.get('image_name')
    directory_path = request.form.get('directory_path')  # Get directory from the request

    # Build the full path of the image
    image_path = os.path.join(directory_path, image_name)
    
    if os.path.exists(image_path):
        shutil.move(image_path,os.path.dirname(directory_path))  # Delete the image
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Image not found'}), 400


if __name__ == '__main__':
    app.run(debug=False)
