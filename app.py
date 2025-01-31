import os,shutil,humanize,sys
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image
from datetime import datetime
sys.path.insert(1, '/home/vamshi/gitRepos/machineSetupRepoMain/')
from getImageProps import getScoreOnly 
from getScore import getScore


from filehash import FileHash
from pymongo import MongoClient
import copy
mongoClientApp = MongoClient('mongodb://localhost:27017/')
db = mongoClientApp["miniFilesLookup"]
md5hasher = FileHash('sha256')


app = Flask(__name__)
IMAGES_PER_PAGE=45
initialLoad=3000

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
    
    alreadySeen = []
    try:
        with open(root_dir+"/seen.txt") as fl:
            for ln in fl:
                alreadySeen.append(ln[:-1])
    except Exception as e:
        alreadySeen=[]

    alreadySeen = set(alreadySeen)  # Convert to set if it's not already a set

    image_files = [f for f in os.listdir(root_dir) if f not in alreadySeen and f.lower().endswith(('jpg', 'jpeg', 'png', 'bmp','webp','gif'))]
    image_files = list(map(lambda x:[x,os.path.getsize(os.path.join(root_dir, x)),os.stat(os.path.join(root_dir, x)).st_ctime],image_files))

    sortNum=1
    if sortKey == 'ctime':
        sortNum=2
    if sortKey=='name':
        image_files_sorted = sorted(image_files, key=lambda x:int(x[0].split('_')[0]),reverse=sortOrder)
    else:
        image_files_sorted = sorted(image_files, key=lambda x:x[sortNum],reverse=sortOrder)
    print('files sorted reverser',sortOrder)
    imgs_lookup = {}
    #os.path.getsize(os.path.join(root_dir, img))
    ctr=1
    for img,sz,ctime in image_files_sorted[:initialLoad]:
        
        try:
            Img = Image.open(os.path.join(root_dir, img))
            nsfw_score1=-1
            skinPer=-10
            score=-1

            if sortKey == 'skinPer':
                tmp = getScoreOnly(os.path.join(root_dir, img),False,True)
                if tmp:
                    skinPer = tmp['skinPer']

            if sortKey=='nsfw_score1':
                tmp = getScoreOnly(os.path.join(root_dir, img),True,False)
                if tmp:
                    nsfw_score1 = tmp['nsfw_score1']

            if sortKey=='score':
                try:
                    filehash = md5hasher.hash_file(os.path.join(root_dir, img))
                    exis=db['files'].find_one({'_id':filehash})
                    if exis == {} or exis == None:
                        score= getScore(os.path.join(root_dir, img))
                    else:
                        score=exis['score']
                except Exception as e:
                    print(e)
                    score=-123

                    
                nsfw_score1=score
            print(ctr)
            ctr+=1
            imgs_lookup[img] = {'dim':Img.size[0]*Img.size[1],'score':score,'flsz':sz,'w':Img.size[0],'h':Img.size[1],'ctime':ctime,'nsfw_score1':nsfw_score1,'skinPer':skinPer}
        except Exception as e:
            print(e)
            e=0
        

    print(sortKey,'reverse:',sortOrder)
    if sortKey=='name':
        imgs_lookup = sorted(imgs_lookup.items(), key=lambda x:int(x[0].split('_')[0]),reverse=sortOrder)
    else:
        imgs_lookup = sorted(imgs_lookup.items(),key=lambda x:x[1][sortKey],reverse=sortOrder)
    image_files=[]
    for img,vals in imgs_lookup:
        flsz = humanize.naturalsize(os.path.getsize(os.path.join(root_dir, img))).strip().replace('\n','')
        print(img,vals['nsfw_score1'])
        image_files.append([img,str(vals['w'])+"x"+str(vals['h']),flsz,str(vals['nsfw_score1'])+'_'+str(vals['skinPer'])])
    
    
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
                fl.write(str(datetime.now())+"----------------------------------------------------------------\n")
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
    print('http://127.0.0.1:5001/?sort=flsz&order=desc')
    print('http://127.0.0.1:5001/?sort=nsfw_score1&order=desc')
    print('http://127.0.0.1:5001/?sort=name&order=desc')

    app.run(host='0.0.0.0',port=5001)
