from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

BOOKS = {
    'book_1':{'title': 'Harry Potter', 'author':'J. K. Rowling'},
    'book_2':{'title': 'Lord of the Rings', 'author':'J. R. R. Tolkien'},
    'book_3':{'title': 'In Search of Lost Time', 'author':'F. Scott Fitzgerland'},
    'book_4':{'title': 'Harry Potter', 'author':'J. K. Rowling'},
    'book_5':{'title': 'Harry Potter', 'author':'J. K. Rowling'},

}
@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
