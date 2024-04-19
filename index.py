from flask import Flask, render_template, request, redirect, url_for, session, flash
import pickle
import numpy as np
from flask_pymongo import PyMongo
import secrets

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__, static_url_path='/public', static_folder='public')
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabaseflask'  # Replace with your MongoDB URI
mongo = PyMongo(app)
app.secret_key = secrets.token_hex(16)  # Generate a secret key

def is_logged_in():
    return "username" in session

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user is None:
            users.insert_one({'username': request.form['username'], 'password': request.form['password']})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash('That username already exists!')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and request.form['password'] == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid username/password combination')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/contact', methods=['GET', 'POST'])
def contact_us():
    message_collection = mongo.db.message
    username = session.get("username")
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        user_message = request.form['message']  # Use a different variable name

        # Insert the message into the collection
        message_collection.insert_one({"name": name , "email": email , "message": user_message})
        # Here you can add code to send the message to your email or save it in a database
        
        # Redirect to a thank you page after submission
        return redirect('/thankyou')
    
    return render_template('contact.html' , username = username)

@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')

@app.route('/')
def index():
    username = session.get('username')
    return render_template("index.html",
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                           username=username if username is not None else None)

@app.route('/browse')
def browse():
    username = session.get("username")
    return render_template("browse.html",
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                           publisher=list(popular_df["Publisher"].values),
                           yop = list(popular_df["Year-Of-Publication"].values),
                           username = username)

@app.route('/recommend_books',methods=['POST'])
def recommend():
    if is_logged_in():
        username = session.get("username")
        user_input = request.form.get('user_input')
        try:
            index = np.where(pt.index == user_input)[0][0]
            similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[0:7]

            data = []
            for i in similar_items:
                item = []
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Year-Of-Publication'].values))
                item.extend(list(temp_df.drop_duplicates('Book-Title')['Publisher'].values))

                data.append(item)
            print(data)

            return render_template('recommend.html', data=data , username= username)
        except IndexError:
            flash('Error occurred while recommending books.')
            return redirect(url_for('internal_error'))
    return render_template("login.html")

def get_recommendations_for_book(selected_book):
    index = np.where(pt.index == selected_book)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[0:7]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-L'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Year-Of-Publication'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Publisher'].values))

        data.append(item)
    print(data)

    return data

@app.route('/recommend/<book_name>')
def get_recommendations(book_name):
    username = session.get("username")
    recommendations = get_recommendations_for_book(book_name)
    return render_template('recommend.html', data=recommendations , username = username)

@app.route('/search')
def search():
    username = session.get("username")
    return render_template('search.html' , username = username)

@app.route("/about")
def about():
    username = session.get("username")
    return render_template("about.html" , username = username)

@app.errorhandler(404)
def not_found_error(error):
    username = session.get("username")
    return render_template('error.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                           username = username
                           ), 404

@app.errorhandler(500)
def internal_error(error):
    username = session.get("username")
    return render_template('error.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                           username = username
                           ), 500

if __name__ == '__main__':
    app.run(debug=True)
