from amadeus import Client, ResponseError
import os

amaclient = Client(
    client_id=os.environ['AMAKEY'],
    client_secret=os.environ['AMASEC']
)