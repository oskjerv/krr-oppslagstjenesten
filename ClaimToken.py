
import requests
import uuid
import os
from jwcrypto import jwk, jwt
from datetime import datetime, timezone
import json


class ClaimToken():
  
    
    def __init__(self):
        self.timestamp = int(datetime.now(timezone.utc).timestamp())
        self.parameters = dict()
        self.request_body = None
        # Parametre fra integrasjonen i Maskinporten
        self.scope = "krr:global/kontaktinformasjon.read" 
        self.maskinporten_audience = "https://test.maskinporten.no/" # i produksjon: https://maskinporten.no/
        self.maskinporten_token = "https://test.maskinporten.no/token/"
        self.resource = 'https://test.kontaktregisteret.no/rest/v2/personer' # i produksjon: https://kontaktregisteret.no/rest/v2/personer
        self.result = None
        self.access_token = None

    def get_parameters(self, dir):
        files = os.listdir(dir)

        for file in files:
            filename = file.removesuffix(".txt")
            filename = filename.removesuffix(".pem")
            f = open(dir + file)
            string = f.read()
            self.parameters[filename] = string

    def gen_jwk_key(self):
        if 'key' in self.parameters.keys():
            self.jwk_key = jwk.JWK.from_pem(
                data = bytes(self.parameters['key'], 'ascii')
            )
        else:
            print("\nPrivate key.pem not available. Run self.get_parameters() first, and check that .pem-file is available in parameters/ directory\n")


    def gen_request(self):

        """"
        The dictionary self.parameters should contain the keys
        consumer, integrationid, iss_onbehalfof, and kid.
        """

        if all(ele in self.parameters.keys() for ele in ['consumer', 'integrationid', 'iss_onbehalfof', 'kid']):
                
            header = {
                'alg': 'RS256',
                'kid': self.parameters['kid'],
            }

            claims = {
                'aud': self.maskinporten_audience, # autentiseringsklienten, som er maskinporten
                'iss': self.parameters['integrationid'],
                'scope': self.scope, 
                'resource': self.resource, 
                'iat': self.timestamp, # tidsstempling. Maskinporten tillater bare +- 10 sekunders avvik fra egen klokke.  
                'exp': self.timestamp + 100, # utløpstidspunkt for autentiseringen. Maks 120 sekunder.
                'jti': str(uuid.uuid4()), # unik ID for hver eneste autentisering
                'consumer_org' : self.parameters['consumer'],
                'iss_onbehalfof': self.parameters['iss_onbehalfof'] # Hentes fra integrasjonen i selvbetjeningsportalen. En ID som forteller Maskinporten at vi gjør dette på vegne av Oslomet. 
            }

            token = jwt.JWT(
                header = header,
                claims = claims
                )
            
            # Signer JWK-token
            token.make_signed_token(self.jwk_key)
            signed_jwt = token.serialize()

            # make the request body: https://docs.digdir.no/docs/Maskinporten/maskinporten_protocol_token
            body = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': signed_jwt
                }
            
            self.request_body = body
        else:
            print('\nNot all parameters are available. self.parameters should contain consumer, integrationid, iss_onbehalfof, and kid.\n')

    def make_request(self):
        if self.request_body:
            self.result = requests.post(self.maskinporten_token, data = self.request_body)
            result_dict = json.loads(self.result.text)
            self.access_token = result_dict['access_token']
        else:
            print('\nThe request body is not ready. run self.gen_request first\n')


    
    


claim = ClaimToken()
claim.get_parameters("parameters/")
claim.gen_jwk_key()

claim.gen_request()
claim.make_request()
print(claim.result)
print(claim.access_token)
#print(claim.parameters)
