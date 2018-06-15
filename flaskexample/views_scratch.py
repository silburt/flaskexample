# https://stackoverflow.com/questions/39960942/flask-app-search-bar

from flaskexample import app
from flask import render_template, send_file
import flaskexample.python_scripts.resume2text as r2t
import flaskexample.python_scripts.gitscraper as gs
from wtforms import StringField
from wtforms.validators import DataRequired

class SearchForm(Form):
    search = StringField('search', [DataRequired()])
    submit = SubmitField('Search',
                         render_kw={'class': 'btn btn-success btn-block'})

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if request.method == 'POST' and form.validate_on_submit():
        return redirect((url_for('search_results', query=form.search.data)))  # or what you want
    return render_template('index.html', form=form)
#return render_template("index.html", title = 'Home', user = user)

def calc2(x):
    return x**2

@app.route('/skills_output', methods=['GET', 'POST'])
def calc():
    git_user, packages = r2t.main()
    if git_user:
        GitProfile = gs.main(git_user, packages)
        return render_template("output.html", title='output', user = git_user,
                               skills = GitProfile.packages)
