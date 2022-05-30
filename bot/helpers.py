import json
from django.conf import settings


class Data:
    def __init__(self, tg_id, product_id):
        self.tg_id = tg_id
        self.product_id = product_id
        self.fileAddress = settings.BASE_DIR / 'bot/data.json'

    @property
    def data(self):
        with open(self.fileAddress) as f:
            return json.load(f)

    def writeJson(self, basket):
        with open(self.fileAddress, 'w') as f:
            json.dump(basket, f)

    def getOrCreateObject(self) -> dict:
        basket = self.data
        for i in range(len(basket)):
            if basket[i].get('tg_id') == self.tg_id and basket[i].get('product_id') == self.product_id:
                return {'index': i, 'data': basket[i]}
        data = {"tg_id": self.tg_id, "product_id": self.product_id, "amount": 1, 'is_basket': False}
        basket.append(data)

        self.writeJson(basket)
        return {'index': len(basket), 'data': data}

    def increment(self):
        basket = self.data
        for i in range(len(basket)):
            print(i)
            if basket[i].get('tg_id') == self.tg_id and basket[i].get('product_id') == self.product_id:
                basket[i]['amount'] = basket[i]['amount'] + 1
                print(basket[i]['amount'])
        self.writeJson(basket)

    def decrement(self):
        basket = self.data
        for i in range(len(basket)):
            if basket[i].get('tg_id') == self.tg_id and basket[i].get('product_id') == self.product_id:
                if basket[i].get('is_basket') == True:
                    if basket[i]['amount'] == 1:
                        basket[i]['amount'] = basket[i]['amount'] - 1
                        del basket[i]
                    else:
                        basket[i]['amount'] = basket[i]['amount'] - 1
                else:
                    if basket[i]['amount'] != 1:
                        basket[i]['amount'] = basket[i]['amount'] - 1
        self.writeJson(basket)

    def setOne(self):
        basket = self.data
        for i in range(len(basket)):
            if basket[i].get('tg_id') == self.tg_id and basket[i].get('product_id') == self.product_id:
                basket[i]['amount'] = 1
        self.writeJson(basket)

    def delete(self):
        basket = self.data
        for i in range(len(basket)):
            if basket[i].get('tg_id') == self.tg_id and basket[i].get('product_id') == self.product_id:
                del basket[i]
        self.writeJson(basket)
