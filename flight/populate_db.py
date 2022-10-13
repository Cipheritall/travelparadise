def populate_airoprts_db():
    import pandas as pd
    tmp_data=pd.read_csv('data/EU_AIRPORTS.csv',sep=';')
    places = [
        Place(
            City = tmp_data.ix[row]['municipality'], 
            Airport = tmp_data.ix[row]['Name'],
            Code = tmp_data.ix[row]['iata_code'],
            Country = tmp_data.ix[row]['iso_country']
        )
        for row in tmp_data['ID']
    ]
    Place.objects.bulk_create(places)