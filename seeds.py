import json

from models import Author, Quotes

import connect

if __name__ == "__main__":
    with open("authors.json", encoding='utf-8') as file:
        data = json.load(file)
        for el in data:
            author = Author(fullname=el.get("fullname"), born_date=el.get("born_date"),
                           born_location=el.get("born_location"), description=el.get("description"))
            author.save()


    with (open("quotes.json", encoding='utf-8') as file):
        data = json.load(file)
        for el in data:
            author, *_ = Author.objects(fullname=el.get('author'))
            quote = Quotes(quote=el.get("quote"), author=author, tags=el.get('tags'))
            quote.save()


