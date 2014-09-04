#encoding:utf-8
from flask import Flask, request, session, g, redirect, url_for, abort, flash
from flask import render_template
import sqlite3
from contextlib import closing
import sys
import math
import time

reload(sys)
sys.setdefaultencoding('utf8')

DATABASE = 'g:\\Me\\flask\\me.db'
DEBUG = True
SECRET_KEY = 'adp#@@#4sdf23'

app = Flask(__name__)
app.config.from_object(__name__)

def gettime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    table = ['data.sql', 'user.sql']
    with closing(connect_db()) as db:
        for t in table:
            with app.open_resource(t, mode='r') as f:
                db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/",methods=['get','post'])
def show_entries():
    row = 10
    page = request.args.get('p')
    if not page:
        page = 1
    else:
        page = int(page)

    s = request.args.get('s')
    if not s:
        sql = 'select id, name, title, text, date from data order by id desc limit ' + str((page-1) * row) +',' + str(row)
        sql2 = 'select count(*) from data'
    else:
        sql = 'select id, name, title, text, date from data where name like \'%' +s + '%\' or title like \'%' + s + '%\' or text like \'%'+ s +'%\' or date like \'%' + s + '%\' order by id desc limit ' + str((page-1) * row) +',' + str(row)
        sql2 = 'select count(*) from data where name like \'%' +s + '%\' or title like \'%' + s + '%\' or text like \'%'+ s +'%\' or date like \'%' + s + '%\''

    cur = g.db.execute(sql2)
    rows = cur.fetchall()[0][0]
    pages = int(math.ceil(float(rows)/float(row)))

    cur = g.db.execute(sql)
    entries = [dict(id=r[0], name=r[1], title=r[2], text=r[3], date=r[4]) for r in cur.fetchall()]
    
    for e in entries:
        bmore = False
        index = e['text'].find('<br>')
        if index>=0:
            e['text']=e['text'][0:index]
            bmore = True

        if len(e['text'])>30:
            e['text']=e['text'][0:30]
            bmore = True

        if bmore:
            e['text']=e['text'] + ' <a href="' + url_for('page',id=e['id'])+'" class="more"> 全文</a>'
        
    now = request.args.get('p')
    if not now:
        now = 1
    else:
        now = int(now)
    return render_template('show_entries.html', entries=entries, pages=pages, fun='show_entries', now=now)

@app.route("/page")
def page():
    sql = 'select id, name, title, text, date from data where id=\'' + request.args.get('id') + '\''
    cur = g.db.execute(sql)
    entries = [dict(id=r[0], name=r[1], title=r[2], text=r[3], date=r[4]) for r in cur.fetchall()]
    entry = entries[0]
    return render_template('page.html', entry=entry)

@app.route('/mod', methods=['GET'])
def mod():
    sql = 'select id, name, title, text, date from data where id= ' + request.args.get('id')
    cur = g.db.execute(sql)
    rows = [dict(id=r[0], name=r[1], title=r[2], text=r[3], date=r[4]) for r in cur.fetchall()]
    row =rows[0]
    index = row['text'].find('<br>')
    if index>=0:
        row['text'] = row['text'].replace('<br>','\r\n')
    return render_template('mod.html', row = row)

@app.route('/modpage', methods=['POST'])
def modpage():
    text = request.form['text']
    text = text.replace('\r\n','<br>')
    sql = 'update data set title=\'' + request.form['title'] + '\', text=\'' + text + '\', name=\'' + request.form['username'] + '\', date=\'' + request.form['date'] + '\' where id=\'' + request.form['id'] + '\'' 
    g.db.execute(sql)
    g.db.commit()
    return redirect(url_for('show_entries'))

@app.route('/moduser', methods=['GET'])
def moduser():
    sql = 'select id, name, password from users where id= ' + request.args.get('id')
    cur = g.db.execute(sql)
    rows = [dict(id=r[0], name=r[1], password=r[2]) for r in cur.fetchall()]
    row =rows[0]
    return render_template('moduser.html', row = row)

@app.route('/moduserpage', methods=['POST'])
def moduserpage():
    sql = 'update users set name=\'' + request.form['username'] + '\', password=\'' + request.form['password'] + '\'  where id=\'' + request.form['id'] + '\'' 
    g.db.execute(sql)
    g.db.commit()
    return redirect(url_for('user_manage'))

@app.route('/usermanage')
def user_manage():

    page = request.args.get('p')
    if not page:
        page = 1
    else:
        page = int(page)

    row = 10
    s = request.args.get('s')
    if not s:
        sql = 'select id, name from users order by id limit ' + str((page-1) * row) +',' + str(row)
        sql2 = 'select count(*) from users'
    else:
        sql = 'select id, name from users where name like \'%' +s + '%\' limit ' + str((page-1) * row) +',' + str(row)
        sql2 = 'select count(*) from users where name like \'%' +s + '%\''

    cur = g.db.execute(sql2)
    rows = cur.fetchall()[0][0]
    
    pages = int(math.ceil(float(rows)/float(row)))

    cur = g.db.execute(sql)
    users = [dict(id=row[0], name=row[1]) for row in cur.fetchall()]

    now = request.args.get('p')
    if not now:
        now = 1
    else:
        now = int(now)

    return render_template("show_users.html", users=users, pages=pages, now=now ,fun='user_manage')

@app.route('/del', methods=['GET'])
def delete():
    sql = 'delete from data where id=\'' + request.args.get('id') + '\'' 
    g.db.execute(sql)
    g.db.commit()
    return redirect(url_for('show_entries'))

@app.route('/deluser', methods=['GET'])
def del_user():
    sql = 'delete from users where id=\'' + request.args.get('id') + '\'' 
    g.db.execute(sql)
    g.db.commit()
    return redirect(url_for('user_manage'))

@app.route('/addpage')
def add_page():
    return render_template("add.html")

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    text = request.form['text']
    text = text.replace('\r\n','<br>')
    g.db.execute('insert into data (title, text, name, date) values (?, ?, ?, ?)',
                 [request.form['title'], text, session['username'], gettime()])
    g.db.commit()
    return redirect(url_for('show_entries'))

@app.route('/user')
def user():
    return render_template('adduser.html')

@app.route('/adduser', methods=['POST'])
def add_user():
    g.db.execute('insert into users (name, password) values (?, ?)',
                 [request.form['name'], request.form['password']])
    g.db.commit()
    flash('用户：' + request.form['name'] + " 添加成功")
    return redirect(url_for('user_manage'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        sql = 'select id, name, password from users where name=\'' + request.form['username'] + '\' and password=\'' + request.form['password'] +'\''
        cur = g.db.execute('select id, name, password from users where name=\'' + request.form['username'] + '\'and password=\'' + request.form['password'] +'\'')
        user = [dict(uid=row[0], name=row[1]) for row in cur.fetchall()]
        if not user:
            error = '用户名或密码错误'
        else:
            session['logged_in'] = True
            session['username'] = user[0]['name']
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('show_entries'))


if __name__ == "__main__":
    #init_db()
    app.run(port = 80, host = "", debug = True)
