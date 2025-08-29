from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from models import db, User, Collection
from flask import g

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

#@app.before_first_request
#def create_tables():
#    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            flash('Login successful.')
            return redirect(url_for('index'))
        flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/collections')
def collections():
    if 'user_id' not in session:
        flash("Login required")
        return redirect(url_for('login'))
    
    user_collections = Collection.query.filter_by(user_id=session['user_id']).all()
    return render_template('collections.html', collections=user_collections)

@app.route('/add', methods=['GET', 'POST'])
def add_collection():
    if 'user_id' not in session:
        flash("Login required")
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        new_item = Collection(item_name=item_name, description=description, user_id=session['user_id'])
        db.session.add(new_item)
        db.session.commit()
        flash("Item added to collection")
        return redirect(url_for('collections'))

    return render_template('add_collection.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_collection(id):
    item = Collection.query.get_or_404(id)

    if item.user_id != session.get('user_id'):
        flash("Unauthorized access")
        return redirect(url_for('collections'))

    if request.method == 'POST':
        item.item_name = request.form['item_name']
        item.description = request.form['description']
        db.session.commit()
        flash("Item updated")
        return redirect(url_for('collections'))

    return render_template('edit_collection.html', item=item)

@app.route('/delete/<int:id>')
def delete_collection(id):
    item = Collection.query.get_or_404(id)

    if item.user_id != session.get('user_id'):
        flash("Unauthorized")
        return redirect(url_for('collections'))

    db.session.delete(item)
    db.session.commit()
    flash("Item deleted")
    return redirect(url_for('collections'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
