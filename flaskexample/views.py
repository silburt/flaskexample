from flaskexample import app
from flask import render_template, send_file
import flaskexample.python_scripts.resume2text as r2t
import flaskexample.python_scripts.gitscraper as gs
import flaskexample.python_scripts.topic_modelling as tm

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    user = { 'name': 'Miguel', 'fave_food': 'pizza' } # fake user
    return render_template("index.html", title = 'Home', user = user)

@app.route('/skills_output', methods=['GET', 'POST'])
def calc():
    git_user, packages = r2t.main()
    if git_user:
        GitProfile = gs.main(git_user, packages)
        Topics = tm.get_topics_from_corpus()
        return render_template("output.html", title='output', user = git_user,
                               skills = GitProfile.packages, topics = Topics)
