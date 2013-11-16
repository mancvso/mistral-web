# -*- coding: utf-8 -*-
"""
    Mistral Dance
    ~~~~~~

    Basado en el ejemplo Flaskr de Armin Ronacher de Flask 

    :copyright: (c) 2013 Datactil.
    :license: BSD, see LICENSE for more details.
"""

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='mistral-dance.db',
    DEBUG=True,
    SECRET_KEY='3566cbfdabc691faa046bc142e9c080a53b852c4',
    USERNAME='admin',
    PASSWORD='default' #7505d64a54e061b7acd54ccd58b49dc43500b635
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select id, name, lastname, rut, email, score from entries where played = "false" order by id asc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries, inlogin=False) #XXX: harcoded fix


@app.route('/entries', methods=['GET'])
def ajax_show_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cursor = db.execute('select id, name, lastname, rut, email, score from entries where played = "false" order by id asc')
    entries = cursor.fetchall()
    #return jsonify(dict(('entry%d' % i, entry) for i, entry in enumerate(cursor.fetchall(), start=0)))
    return render_template('table-entries.html', entries=entries)


@app.route('/entries', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    ajax = request.args.get('ajax', '')
    db = get_db()
    db.execute('insert into entries (name, lastname, rut, email) values (?, ?, ?, ?)',
                 [request.form['name'], request.form['lastname'], request.form['rut'], request.form['email']])
    db.commit()
    if(ajax != null):
        return ajax_show_entry()
    else:
        return show_entries()



@app.route('/entries/<int:entry_id>', methods=['DELETE'])
def remove_entry(entry_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from entries where id = ?',
                 [entry_id])
    db.commit()
    return ajax_show_entry()

@app.route('/entries/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('update entries set played=?, score=?, rewarded=? where id = ?',
                 [request.form['played'], request.form['score'], request.form['rewarded'], entry_id])
    db.commit()
    return ajax_show_entry()


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('Has iniciado sesión')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error, inlogin=True)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Has cerrado sesión')
    return redirect(url_for('show_entries'))

@app.route('/puntajes')
def scoreboard():
    db = get_db()
    cur = db.execute('select id, name, lastname, rut, email, score from entries where played is True order by score desc')
    entries = cur.fetchall()
    return render_template('scoreboard.html', entries=entries)

@app.template_filter('privatize')
def privatize_filter(s):
    return "*****@" + s.split("@")[1]


if __name__ == '__main__':
    init_db()
    app.run()
