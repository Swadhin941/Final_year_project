
from asyncio.windows_events import NULL
import json
from unittest import removeHandler
from flask import Flask, redirect, session, render_template, url_for, request, jsonify
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from jinja2 import Environment
import csv


app = Flask(__name__)

# configure db
app.secret_key = 'your secret key'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'log'
app.config['MYSQL_HOST'] = 'localhost'
# app.config['SESSION_PERMANENT']= False
# app.config['SESSION_TYPE']='filesystem'
# Sess
mysql = MySQL(app)
books = pd.read_csv('C:/xampp/htdocs/python/Books.csv')
ratings = pd.read_csv('C:/xampp/htdocs/python/Ratings.csv')
users = pd.read_csv
('C:/xampp/htdocs/python/Users.csv')


@app.route("/")
def home():
    return render_template('home.html')


@app.route('/signup')
def signup():
    username = request.args.get('username')
    password = request.args.get('password')
    email = request.args.get('email')
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM `accounts`")
    res = cursor.fetchall()
    userid = 278859
    userid = userid + len(res)

    if email is not None:

        cursor.execute("INSERT INTO accounts (username, password, email,userid) VALUES (%s,%s,%s,%s)",
                       (username, password, email, userid))
        mysql.connection.commit()
        cursor.close()
        f = open('Users.csv', 'a', newline='')
        file = csv.writer(f)
        rec = []
        rec.append([userid, '', ''])
        file.writerows(rec)
        f.close()
        session['userid'] = userid
        session['username'] = username
        return jsonify({'msg': "done"})
    else:
        return render_template('signup.html')


@app.route('/email_check', methods=['GET'])
def em_ch():
    email = request.args.get('email')
    em_f = NULL
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM `accounts`")
    res = cursor.fetchall()
    for i in range(len(res)):
        if (res[i][3] == email):
            em_f = res[i][3]
    if em_f == 0:
        return jsonify({'email': em_f})
    else:
        return jsonify({'email': em_f})


@app.route('/login', methods=['GET', 'POST'])
def login():
    # print(session['user'])
    email = request.args.get('email')
    password = request.args.get('password')
    if email is not None:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT * FROM `accounts` where email  = %s AND password = %s", (email, password))
        res = cursor.fetchone()
        cursor.close()
        if res:
            session['username'] = res[1]
            session['userid'] = res[4]
            session['logged_in'] = True
            return jsonify({'em': 'done'})
        else:
            return jsonify({'em': 'false'})
    return render_template('login.html')


@app.route('/book', methods=['GET', "POST"])
def book():
    print(request.args.get('intro'))

    uid = (session['userid'],)
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Rating where userid = %s''', (uid))
    res = cursor.fetchall()
    # print(ratings.shape)
    # return render_template('book_page.html')
    # if len(res) >= 3:
    #     print('yes none')
    #     return render_template('book_page.html')
    # else:
    rating = ratings.drop_duplicates(['User-ID', 'ISBN'], keep='last')
    ratings_with_name = rating.merge(books, on='ISBN')
    num_rating_df = ratings_with_name.groupby(
        ['Book-Title', 'ISBN']).count()['Book-Rating'].reset_index()
    num_rating_df.rename(
        columns={'Book-Rating': 'num_ratings'}, inplace=True)
    avg_rating_df = ratings_with_name.groupby(
        ['Book-Title', 'ISBN']).mean()['Book-Rating'].reset_index()
    avg_rating_df.rename(
        columns={'Book-Rating': 'avg_rating'}, inplace=True)
    popular_df = num_rating_df.merge(
        avg_rating_df, on=['Book-Title', 'ISBN'])
    popular_df = popular_df[popular_df['num_ratings'] >= 250].sort_values(
        'avg_rating', ascending=False)
    popular_df = popular_df.merge(books, on=['Book-Title', 'ISBN'])
    popular_df = popular_df.drop_duplicates(['Book-Title', 'ISBN'])[
        ['Book-Title', 'ISBN', 'Book-Author', 'Image-URL-M', 'num_ratings', 'avg_rating']]
    book_title = list(popular_df['Book-Title'].values)
    isbn = list(popular_df['ISBN'].values)
    image = list(popular_df['Image-URL-M'].values)
    return render_template('book_page.html', book_name=book_title, isbn=isbn, image=image)

#     if(len(res)>=3):
#         # rating.drop_duplicates('User-ID',keep='last')
#         # book_with_rating=rating.merge(book, on='ISBN')
#         # x=book_with_rating.groupby('User-ID').count()['Book-Rating'] > 3
#         # special_user= x[x].index
#         # x2=book_with_rating[book_with_rating['User-ID'].isin(special_user)]
#         # y= x2.groupby('Book-Title').count()['Book-Rating'] >= 50
#         # famous_book= y[y].index
#         # final=x2[x2['Book-Title'].isin(famous_book)]
#         # test=final.pivot_table(index='User-ID', columns='Book-Title',values='Book-Rating')
#         # tes=test.copy(deep=True)
#         # test.fillna('0',inplace=True)
#         # test_dif= cosine_similarity(test)
#         # li=[]
#         # li1=[]
#         # data= 256
#         # s=np.where(test.index== data)[0][0]
#         # s1=sorted(list(enumerate(test_dif[s])),key=lambda x:x[1], reverse=True)[1:10]
#         # print(s1)
#         # for i in s1:
#         #     li1.append(i[1])
#         #     li.append(test.index[i[0]])
#         # dst=test[test.index.isin(li)]
#         # tes=tes[tes.index.isin(dst.index)]
#         # book_score={}
#         # for i in tes.columns:
#         #     book_val= tes[i]
#         #     total=0
#         #     count=0
#         #     for j in range(len(tes.index)):
#         #         if pd.isna(book_val[tes.index[j]])== False :
#         #             total+=book_val[tes.index[j]]* li1[j]
#         #             count+=1
#         #     if(total != 0):
#         #         book_score[i]=total/count
#         # #book_score.items()
#         # book_score=pd.DataFrame(book_score.items(),columns=['book_name',"total_score_of_book"])
#         # book_final_score=book_score.sort_values(by='total_score_of_book',ascending=False)
#         # final_book=book_final_score.head(10).copy(deep=True)
#         # data_book=[]
#         # for i in final_book['book_name']:
#         #     book_item=[]
#         #     temp_df=final[final['Book-Title']==i]
#         #     book_item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
#         #     book_item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
#         #     book_item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
#         #     data_book.append(book_item)
#     else:
#     return render_template('book_page.html')


@app.route('/csv')
def cs():
    f = open('Users.csv', 'r', newline='')
    res = csv.reader(f)
    for i in res:
        print(i)
    f.close()
    return redirect(url_for('signup'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/details')
def details():
    image = request.args.get('image')
    isbn = request.args.get('isbn')
    book_name = request.args.get('book_name')
    return render_template('details.html', book_name=book_name, isbn=isbn, image=image)


@app.route('/rating', methods=['GET', 'POST'])
def rating():
    rating = request.args.get('rating')
    rating = int(rating)*2
    book_name = request.args.get('book_name')
    isbn= request.args.get('isbn')
    uid = (session['userid'],isbn,)
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM Rating where userid = %s AND ISBN = %s''', (uid))
    res = cursor.fetchall()
    if len(res)>=1:
        val=(rating,session['userid'],isbn)
        cursor.execute('''UPDATE rating SET rating = %s WHERE userid = %s AND ISBN = %s''',(val))
        mysql.connection.commit()
    else:
        val=(session['userid'],isbn,rating)
        cursor.execute('''INSERT INTO rating (userid, ISBN, rating) VALUES (%s,%s,%s)''',(val))
        mysql.connection.commit()
    print(len(res))
    print(rating)
    print(isbn)
    print(book_name)
    print(session['userid'])
    return render_template('details.html')


if __name__ == '__main__':
    app.run(debug=True)
