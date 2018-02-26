"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import os
from app import app
from flask import render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename

#importing the Uploadform class from forms.py
from forms import UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Uploaded Files")


@app.route('/upload', methods=['POST', 'GET'])
def upload():

    
    if not session.get('logged_in'):
        abort(401)
    uploadform = UploadForm()
    # Instantiate your form class

    # Validate file upload on submit
    if request.method == 'POST':
        # Get file data and save to your uploads folder
        if uploadform.validate_on_submit():
            print uploadform.csrf_token
            
            photo = uploadform.photo.data
            description = uploadform.description.data
            
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            flash('File Saved', 'success')
            return redirect(url_for('home', filename=filename, description=description))
        else:
            print uploadform.errors.items()
            flash('File not Saved', 'error')
    return render_template('upload.html', form=uploadform)
    
  
    
    
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            
            flash('You were logged in', 'success')
            return redirect(url_for('upload'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect(url_for('home'))

def get_uploaded_images():
    rootdir= os.getcwd()
    print rootdir
    ls =[]
    for subdir, dirs, files in os.walk(rootdir + 'app/static/uploads'):
        for file in files:
            ls.append(os.path.join(subdir,  file).split('/')[-1])
    return ls
    
@app.route('/files')
def files():
    if not session.get('logged_in'):
        abort(401)
    files=get_uploaded_images()
    return render_template('files.html', files = files)
        
###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")