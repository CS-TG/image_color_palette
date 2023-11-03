import numpy as np 
from PIL import Image, ImageOps 
from flask import Flask, render_template, request, flash, redirect, url_for
import secrets

def rgb_to_hex(rgb): 
	return '%02x%02x%02x' % rgb 


def give_most_hex(file_path, code): 
	my_image = Image.open(file_path).convert('RGB') 
	size = my_image.size 
	if size[0] >= 400 or size[1] >= 400: 
		my_image = ImageOps.scale(image=my_image, factor=0.2) 
	elif size[0] >= 600 or size[1] >= 600: 
		my_image = ImageOps.scale(image=my_image, factor=0.4) 
	elif size[0] >= 800 or size[1] >= 800: 
		my_image = ImageOps.scale(image=my_image, factor=0.5) 
	elif size[0] >= 1200 or size[1] >= 1200: 
		my_image = ImageOps.scale(image=my_image, factor=0.6) 
	my_image = ImageOps.posterize(my_image, 2) 
	image_array = np.array(my_image) 

	# create a dictionary of unique colors with each color's count set to 0 
	# increment count by 1 if it exists in the dictionary 
	unique_colors = {} # (r, g, b): count 
	for column in image_array: 
		for rgb in column: 
			t_rgb = tuple(rgb) 
			if t_rgb not in unique_colors: 
				unique_colors[t_rgb] = 0
			if t_rgb in unique_colors: 
				unique_colors[t_rgb] += 1

	# get a list of top ten occurrences/counts of colors 
	# from unique colors dictionary 
	sorted_unique_colors = sorted( 
		unique_colors.items(), key=lambda x: x[1], 
	reverse=True) 
	converted_dict = dict(sorted_unique_colors) 
	# print(converted_dict) 

	# get only 10 highest values 
	values = list(converted_dict.keys()) 
	# print(values) 
	top_10 = values[0:10] 
	# print(top_10) 

	# code to convert rgb to hex 
	if code == 'hex': 
		hex_list = [] 
		for key in top_10: 
			hex = rgb_to_hex(key) 
			hex_list.append(hex) 
		return hex_list 
	else: 
		return top_10 


app = Flask(__name__) 
app.secret_key = secrets.token_hex(16)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    colors_list = []
    code = 'hex'  # Default value for code
    
    if request.method == 'POST':
        if 'file' not in request.files:
            error_message = "No file part."
        else:
            f = request.files['file']
            if f.filename == '':
                error_message = "No selected file."
            elif not allowed_file(f.filename):
                error_message = "Invalid file format. Please upload a valid image (PNG, JPG, JPEG, or GIF)."
                flash(error_message, "error")
                return redirect(url_for('index'))
            else:
                colour_code = request.form.get('colour_code')
                if colour_code and colour_code in ['hex', 'rgb']:
                    code = colour_code
                    colors_list = give_most_hex(f.stream, code)
                else:
                    error_message = "Please select a valid color code option ('hex' or 'rgb')."
                    flash(error_message)
                    return redirect(url_for('index'))
        if not error_message:
            flash("Colors generated successfully!", "success")

    return render_template('index.html', colors_list=colors_list, code=code, error_message=error_message)

if __name__ == '__main__': 
	app.run(debug=True) 