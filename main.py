from flask import Flask, render_template,redirect,request,flash
from PIL import Image
from werkzeug.utils import secure_filename
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter

app = Flask(__name__)
app.secret_key = 'hi'
UPLOAD_FOLDER ='static/'
ALLOWED_EXTENSIONS ={'jpg','png','jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Invalid file part. Please upload jpg, png or jpeg images.')
            return redirect(request.url)
        if request.form['NumColor'] == '':
            flash('Please enter the number of colors to extract')
            return redirect(request.url)
        if int(request.form['NumColor']) <= 0:
            flash('Please enter a positive number of colors to extract')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(app.config['UPLOAD_FOLDER'] + filename)
            filepath = app.config['UPLOAD_FOLDER']+filename
            palete = color_cluster(filepath,int(request.form['NumColor']))
            return render_template('index.html',image=filepath,uploaded=True,palete=palete)
        return render_template('index.html',uploaded=False)
    return render_template('index.html')

def color_cluster(filepath,n):
    img = Image.open(filepath)
    img = img.copy()
    img.thumbnail((100, 100))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img_new = np.reshape(img,(-1,3))
    clt = KMeans(n_clusters=n)
    clt.fit(img_new)
    rgb = clt.cluster_centers_
    n_pixels = len(clt.labels_)
    counter = Counter(clt.labels_)
    palete = {}
    for i in range(0,n):
        hex = '%02x%02x%02x' % (int(rgb[i][0]),int(rgb[i][1]),int(rgb[i][2]))
        perc = round(counter[i]/n_pixels,2)
        palete[f'{hex}'] = perc
    return {k:v for k,v in sorted(palete.items(), key = lambda item:item[1],reverse=True)}

if __name__ == "__main__":
    app.run()
