from flask import Flask,render_template,request
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))


app = Flask(__name__, static_url_path='/public', static_folder='public')


@app.route('/')
def index():
    return render_template("index.html",
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                        #    publisher=list(popular_df["Publisher"].values),
                        #    yop = list(popular_df["Year-Of-Publication"].values)           
                                               )                                           
@app.route('/browse')
def browse():
    return render_template("browse.html",
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values),
                           publisher=list(popular_df["Publisher"].values),
                           yop = list(popular_df["Year-Of-Publication"].values)           
                                               )                                           

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
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

        return render_template('recommend.html', data=data)
    except IndexError:
        return render_template('error.html',
                               book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )
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
    # Get recommendations based on the selected book index
    # selected_book = books.loc[book_name]  # Assuming 'books' is your DataFrame
    recommendations = get_recommendations_for_book(book_name)
    return render_template('recommend.html', data=recommendations)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           ), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-L'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           ), 500

if __name__ == '__main__':
    app.run(debug=True)