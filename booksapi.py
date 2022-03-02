import requests
from flask import Flask, request, make_response
from flask_restful import Api, Resource, abort, reqparse
from functools import wraps
import json


app = Flask(__name__)
api = Api(app)
BOOKS = {}

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def get_author_information(author):
    result =''
    if not isEnglish(author):
        parse_author = author.replace(" ", "_")
        result = f'https://he.wikipedia.org/wiki/{parse_author}'
    else:
        parse_author = author.replace(" ", "_")
        result = f'https://en.wikipedia.org/wiki/{parse_author}'
    return result


def books_structure(file_name):

    f = open(file_name,encoding="utf8")
    data = json.load(f)
    id = 0
    for book in data['books']:
        BOOKS[f'book_{id}'] = book
        id = id +1
    f.close()


parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('author')
parser.add_argument('author_information')


def abort_book_does_not_exsit(book_id):
    if book_id not in BOOKS:
        abort(404, message ='Book {} does not exist'.format(book_id))

class Book(Resource):
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
            json.dump(data, data_file, indent= 2, ensure_ascii=False)


        del BOOKS[book_id]

        return '', 204  #204 No Content

    def put(self,book_id):
        args = parser.parse_args()
        author_information = get_author_information(args['author'])
        book_information = {'title': args['title'], 'author': args['author'],'author_information':author_information}
        with open('books.json') as data_file:
            data = json.load(data_file)
            for book in data['books']:
                 if BOOKS[book_id]['title'] == book['title']:
                    book['title'] = args['title']
                    book['author'] = args['author']
                    book['author_information']= author_information
                    break
        with open('books.json', 'w') as data_file:
            json.dump(data, data_file, indent=2, ensure_ascii=False)

        BOOKS[book_id] = book_information
        return  book_information


class BookList(Resource):
    def get(self):
        return BOOKS

    def post(self):
        args = parser.parse_args()
        author_information = get_author_information(args['author'])
        current_book_id = 0
        
        if len(BOOKS) > 0:
            for book in BOOKS:
                x= int(book.split('_')[-1])
                if x > current_book_id:
                    current_book_id = x
        book_information = {'title': args['title'], 'author': args['author'],'author_information':author_information}
        BOOKS[f'book_{current_book_id +1}'] = book_information
        write_json(book_information,'books.json')
        return BOOKS[f'book_{current_book_id +1}'], 201


def write_json(new_data, filename='data.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["books"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 2, ensure_ascii=False)


api.add_resource(Book, '/books/<book_id>')
api.add_resource(BookList, '/books')

if __name__ == '__main__':
    books_structure('books.json')
    app.run(debug=True)
