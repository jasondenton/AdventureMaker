from flask import Flask, render_template

from monsters import get_monster_index

app = Flask(__name__)

@app.route('/monsters')
def monster_list():
    return render_template('monsters.template.html', {'monsters':get_monster_index()})
