from flask import Flask, request, make_response
from flask_restful import Api, Resource, abort, reqparse
from functools import wraps
import json


app = Flask(__name__)
api = Api(app)
BOOKS = {}


def books_structure(file_name):

    f = open(file_name,)
    data = json.load(f)
    id = 0
    for book in data['books']:
        BOOKS[f'book_{id}'] = book
        id = id +1
    f.close()

def login_required(event):
    @wraps(event)
    def login(*args, **kwargs):
        if request.authorization and \
                request.authorization.username == 'Admin' and \
                request.authorization.password == 'A123456':
            return event(*args, **kwargs)

        return make_response('could not verify your credentials',
                             401,
                             {'WWW-Authenticate' : 'Basic realm="Login Realm"'})

    return login

parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('author')


def abort_book_does_not_exsit(book_id):
    if book_id not in BOOKS:
        abort(404, message ='Book {} does not exist'.format(book_id))

class Book(Resource):
    @login_required
    def get(self, book_id):
        abort_book_does_not_exsit(book_id)
        return BOOKS[book_id]

    def delete(self,book_id):
        abort_book_does_not_exsit(book_id)

        with open('books.json') as data_file:
            data = json.load(data_file)
            index = 0
            for book in data['books']:
                 if BOOKS[book_id]['title'] == book['title']:
                    del data['books'][index]
                    break
                 index = index + 1

        with open('books.json', 'w') as data_file:
            json.dump(data, data_file, indent= 2)


        del BOOKS[book_id]

        return '', 204

    def put(self,book_id):
        args = parser.parse_args()
        book_information = {'title': args['title'], 'author':args['author']}
        with open('books.json') as data_file:
            data = json.load(data_file)
            for book in data['books']:
                 if BOOKS[book_id]['title'] == book['title']:
                    book['title'] = args['title']
                    book['author'] = args['author']
                    break
        with open('books.json', 'w') as data_file:
            json.dump(data, data_file, indent=2)

        BOOKS[book_id] = book_information
        return  book_information


class BookList(Resource):
    def get(self):
        return BOOKS

    def post(self):
        args = parser.parse_args()

        current_book_id = 0

        if len(BOOKS) > 0:
            for book in BOOKS:
                x= int(book.split('_')[-1])
                if x > current_book_id:
                    current_book_id = x
        book_information = {'title': args['title'], 'author': args['author']}
        BOOKS[f'book_{current_book_id +1}'] = book_information
        write_json(book_information,'books.json')
        return BOOKS[f'book_{current_book_id +1}'], 201


def write_json(new_data, filename='data.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["books"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 2)


api.add_resource(Book, '/books/<book_id>')
api.add_resource(BookList, '/books')

if __name__ == '__main__':
    books_structure('books.json')
    app.run(debug=True)
