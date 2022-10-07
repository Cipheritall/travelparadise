from amadeus import Client, ResponseError
import os

amadeus = Client(
    client_id=os.environ['AMAKEY'],
    client_secret=os.environ['AMASEC']
)