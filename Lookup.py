

from ClaimToken import ClaimToken
import requests
import json
import collections

class Lookup(ClaimToken):
    def __init__(self):
        super().__init__()
        # Url til oppslagstjenesten
        self.endpoint = 'https://test.kontaktregisteret.no/rest/v2/personer'
        
        self.body = None
        self.header = None
        self.result = None
        self.json = None
        self.contact_info = None
        self.persons = None
        self.status_code = None
        
    def gen_lookup_request(self, personidentificator):
        """
        Method for compiling the request body and header, using the generated access token
        and the batch of persons we want to lookup in the register.
        """
        if self.access_token:
            self.persons = personidentificator

            # Data/Payload
            self.body = {
                    'personidentifikatorer' : personidentificator,
                    'inkluderIkkeRegistrerte': False,

            }

                # Header i request
            self.header = {
                'Http-metode': 'POST',
                'Authorization': 'Bearer ' + self.access_token,
            }
        else:
            print('\nYou need to collect acces_token first, with method request_token()\n')

    def make_request(self):
        """
        Method for exeucuting the request, and if successfull adding the result as json
        to self.result. 
        """
        if self.body:
            try:
                
                self.result = requests.post(self.endpoint, headers = self.header, json = self.body)
                self.status_code = self.result.status_code
                self.result.raise_for_status()
            
                 
            except requests.exceptions.RequestException as e:
                
                return "Error: " + str(e)
                                      
        else:            
            print('\nself.body and self.header has to be compiled using gen_lookup_request.\n')

    def load_json(self):
        """"
        Load the result text as json if it exists. 
        If it doesnt (when status code is not 200), append the error
        to a .txt-file.
        """
        if self.status_code == 200:
                self.json = json.loads(self.result.text)
        else:
            with open('data/errors.txt', 'a') as f:
                f.write(f"{self.result.text}\n") 

               

    def structure_result(self):
        if self.json:
            contact_info = collections.defaultdict(list)
            if 'personer' in self.json.keys():
                
                # Collect data for all persons in the result 
                # Not all attributes are available for all persons

                for person in self.json['personer']:
                    #print(self.result['personer'])
                    #if person['varslingsstatus'] == "KAN_VARSLES":

                    contact_info['fnr'].append(person['personidentifikator'])
                    contact_info['status'].append(person['status'])
                    contact_info['varslingsstatus'].append(person['varslingsstatus'])

                    if 'reservasjon' in person.keys():
                        contact_info['reservasjon'].append(person['reservasjon'])
                    else:
                        contact_info['reservasjon'].append(None)

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

                    contact_info['timestamp'].append(self.timestamp)

                self.contact_info = contact_info

        else:
            print('\nNo resuls to. Did you remember to make the request?\n')

    def tally_persons(self):
        """"
        Method for tallying who data has been collected for, and for whom the request failed
        If self.contact_info still is None, it has not been collected data on the persons in self.persons.
        The persons are appended to nolookupmade.txt

        If self.contact_info is not None, check if all persons in self.persons are present in the dictionary. 
        If not, append the person to nodata.txt.
        """

        if self.contact_info:
            for person in self.persons:
                if str(person) in self.contact_info['fnr']:
                    pass
                else:
                    with open('data/nodata.txt', 'a') as f:
                        f.write(f"{person}\n") 
        else:
            with open('data/nolookupmade.txt', 'a') as f:
                    for persons in self.persons:
                        f.write(f"{persons}\n") 
        

                 


    

