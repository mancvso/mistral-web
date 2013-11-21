# -*- coding: utf-8 -*-
"""
    Mistral Dance
    ~~~~~~

    Basado en el ejemplo Flaskr de Armin Ronacher de Flask 

    :copyright: (c) 2013 Datactil.
    :license: BSD, see LICENSE for more details.
"""

import sys
import json
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify, make_response


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='mistral-dance.db',
    DEBUG=True,
    SECRET_KEY='3566cbfdabc691faa046bc142e9c080a53b852c4',
    USERNAME='datactil',
    PASSWORD='datactil' #7505d64a54e061b7acd54ccd58b49dc43500b635
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
    return render_template('show_entries.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Credenciales no válidas.'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Credenciales no válidas.'
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
    cur = db.execute('select id, name, lastname, rut, email, score, played from entries where played = 1 order by score desc')
    entries = cur.fetchall()
    return render_template('scoreboard.html', data=entries)

@app.template_filter('privatize')
def privatize_filter(s):
    return "*****@" + s.split("@")[1]

# ====================
#    API Endpoints 
# ====================


"""
    Entregar lista de 10 usuarios con los más altos puntajes
"""
@app.route('/usuarios/top', methods=['GET'])
def api_users_top():
    db = get_db()
    cur = db.execute('select id, name, lastname, score, photo, rut, email, played from entries where played = 1 order by score desc limit 10')
    entries = cur.fetchall()
    return multi_output(request, entries, "users.xml")
    

"""
    Entregar siguiente usuario en la lista de espera
"""
@app.route('/usuarios/next')
def api_users_next():
    db = get_db()
    cur = db.execute('select id, name, lastname, rut, email, score, played from entries where played = 0 order by id asc limit 1')
    entry = cur.fetchall()
    return multi_output(request, entry, "user.xml")

"""
    Actualizar o entregar información del usuario pedido
"""
@app.route('/usuarios/<int:id>', methods=['GET', 'PUT'])
def api_users_update(id):
    db = get_db()
    if request.method == 'PUT':
        if request.form.has_key('photo'):
            db.execute('update entries set score=?, photo=?, played=? where id = ?',
                [request.form['score'], request.form['photo'], request.form['played'], id])
        else :
            db.execute('update entries set score=?, played=? where id = ?',
                [request.form['score'], request.form['played'], id])
        
        db.commit()
        cur = db.execute('select * from entries where id = ?', [id])

        return multi_output(request, cur.fetchall(), "user.xml")

    else : #GET
        
        cursor = db.execute('select id, name, lastname, rut, email, score from entries where id = ?', [id])
        entry = cursor.fetchall()
        return multi_output(request, entry, "user.xml")

"""
    Entregar todos los usuarios, hasta limit
"""
@app.route('/usuarios')
def api_users():
    db = get_db()
    if request.args.has_key('scope'):
        sql ='select id, name, lastname, rut, email, score, played from entries where played = 0 order by score desc'
    else :
        sql ='select id, name, lastname, rut, email, score, played from entries order by score desc'

    cur = db.execute( sql )
    entries = cur.fetchall()
    return multi_output(request, entries, "users.xml")

@app.route('/usuarios', methods=['POST'])
def api_user_add():
    #if not session.get('logged_in'):
    #    abort(401)
    db = get_db()
    db.execute('insert into entries (name, lastname, rut, email) values (?, ?, ?, ?)',
                 [request.form['name'], request.form['lastname'], request.form['rut'], request.form['email']])
    db.commit()
    return multi_output(request, [], "users.xml")

@app.route('/usuarios/<int:id>', methods=['DELETE'])
def remove_entry(id):
    #if not session.get('logged_in'):
    #    abort(401)
    db = get_db()
    cursor = db.execute('select id, name, lastname, rut, email, score from entries where id = ?', [id])
    entry = cursor.fetchall()
    db.execute('delete from entries where id = ?', [id])
    db.commit()
    return multi_output(request, entry, "user.xml")


def multi_output(request, data, xml_template):
    # JSON Response
    if request.args['json'] == "true":
        # None
        if data is None or len(data) == 0:
            resp = jsonify({'status': "EMPTY", 'data': []})
        # One
        #elif data != None:
        #    resp = jsonify({'status': "OK", 'data': data})
        # Multiple
        else:
            json_rep = json.loads( json.dumps( [dict(ix) for ix in data], sort_keys = False, indent = 4, separators=(',', ': ')) )
            resp = jsonify({'status': "OK", 'data': json_rep})
    # XML Response
    else:
        resp = make_response(render_template(xml_template, data=data), 200)
        
    if not request.args['json'] == "true":
        resp.headers['Content-Type'] = 'text/xml'

    return resp

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    init_db()

    app.run(host='0.0.0.0')
