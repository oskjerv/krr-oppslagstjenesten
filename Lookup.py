

from ClaimToken import ClaimToken
import requests
import json
import pandas as pd
import collections

class Lookup(ClaimToken):
    def __init__(self):
        super().__init__()
        # Url til oppslagstjenesten
        self.endpoint = 'https://test.kontaktregisteret.no/rest/v2/personer'
        
        self.body = None
        self.header = None
        self.result = None
        self.contact_info = None
        
    def gen_lookup_request(self, personidentificator):
        if self.access_token:

            # Data/Payload
            self.body = {
                    'personidentifikatorer' : personidentificator,
                    'inkluderIkkeRegistrerte': False    
            }

                # Header i request
            self.header = {
                'Http-metode': 'POST',
                'Authorization': 'Bearer ' + self.access_token,
            }
        else:
            print('\nYou need to collect acces_token first, with method request_token()\n')

    def make_request(self):
        
        if self.body:
            res = requests.post(self.endpoint, headers = self.header, json = self.body)
            if res.status_code == 200:
                self.result = json.loads(res.text)
            else:
                print('\nThe request failed with status code ' + str(res.status_code) +'\n')            
        else:            
            print('\nself.body and self.header has to be compiled using gen_lookup_request.\n')

    def structure_result(self):
        if self.result:
            contact_info = collections.defaultdict(list)
            if 'personer' in self.result.keys():
                
                # Collect data for all persons in the result
                # Not all attributes are available for all persons
                for person in self.result['personer']:
                    #print(self.result['personer'])
                    contact_info['fnr'].append(person['personidentifikator'])
                    contact_info['status'].append(person['status'])
                    contact_info['varslingsstatus'].append(person['varslingsstatus'])

                    if 'reservasjon' in person.keys():
                        contact_info['reservasjon'].append(person['varslingsstatus'])
                    else:
                        contact_info['reservasjon'].append(person['varslingsstatus'])

                    if 'kontaktinformasjon' in person.keys():
                        
                        if 'epostadresse' in person['kontaktinformasjon'].keys():
                            contact_info['epostadresse'].append(person['kontaktinformasjon']['epostadresse'])
                        else:
                            contact_info['epostadresse'].append(None)

                        if 'mobiltelefonnummer' in person['kontaktinformasjon'].keys():
                            contact_info['mobiltelefonnummer'].append(person['kontaktinformasjon']['mobiltelefonnummer'])
                        else:
                            contact_info['mobiltelefonnummer'].append(None)
                    else:
                        contact_info['epostadresse'].append(None)
                        contact_info['mobiltelefonnummer'].append(None)

                    if 'spraak' in person.keys():
                        contact_info['spraak'].append(person['spraak'])
                    else:
                        contact_info['spraak'].append(None)

                    #contact_info['access_token'].append(self.access_token)
                    contact_info['timestamp'].append(self.timestamp)

                self.contact_info = contact_info
                #print(pd.DataFrame.from_dict(self.contact_info))
        else:
            print('\nNo resuls to. Did you remember to make the request?\n')


    

