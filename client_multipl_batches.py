
from Lookup import Lookup
import pandas as pd
import time

# les inn personene du skal gjøre oppslag på
df = pd.read_excel('data/synteticusers.xlsx', dtype = str)  

# konverter personnummer til liste
persons = df['Fnr'].tolist()

#persons += ['99999999999']

# funksjon for å dele opp liste i n nøstede lister
def slice_per(source, step):
    return [source[i::step] for i in range(step)]

# del opp listen i nøstede lister
sliced_persons = slice_per(persons, 5) 


# Hvis programmet må kjøres på nytt, på grunn av avbrudd. 
# Sett en verdi for å fortsette fra bolk X.
continuevalue = -1

objs = [Lookup() for i in range(len(sliced_persons)- continuevalue)]

counter = continuevalue

sleep = 5

for obj in objs:
    counter += 1
    print('\nLookup number: ' + str(counter))
    obj.get_parameters("parameters/")
    obj.gen_jwk_key()
    obj.gen_token_request()
    obj.request_token()
    obj.gen_lookup_request(sliced_persons[counter])
    obj.make_request()
    obj.load_json()
    #print(obj.result)
    if obj.status_code == 200:
        obj.structure_result()
        data = pd.DataFrame.from_dict(obj.contact_info)
        data.to_excel("data/lookup_" + str(counter) + ".xlsx") 
    obj.tally_persons()

    print("Pausing for 5 seconds...")
    time.sleep(sleep)








