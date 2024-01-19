
import requests
import uuid
import os
import pem
from jwcrypto import jwk, jwt
from datetime import datetime, timezone
import json
import pandas as pd

# les inn personene du skal gjøre oppslag på
df = pd.read_excel('data/synteticusers.xlsx')  

# konverter personnummer til liste
persons = df['Fnr'].tolist()

def readtxt(path):
    f = open(path)
    string = f.read()
    return string

# Parametre fra integrasjonen i Maskinporten
kid = readtxt("parameters/kid.txt") # kid i JWT-key som er lagt på integrasjonen i Maskinporten
integration_id = readtxt("parameters/integrationid.txt") # Fra integrasjon i Maskinporten
scope = "krr:global/kontaktinformasjon.read" # Fra integrasjon i Maskinporten. Forteller hvilke ressurser vi ønsker å benytte


# Environment specific variables
maskinporten_audience = "https://test.maskinporten.no/" # i produksjon: https://maskinporten.no/
maskinporten_token = "https://test.maskinporten.no/token/"
#maskinporten_token = "https://test.maskinporten.no"

timestamp = int(datetime.now(timezone.utc).timestamp())

# Hemmelig RSA-nøkkel generert i openssl (se readme.md)
secret = readtxt('../rsa_keys/test_key.pem')

key = jwk.JWK.from_pem(
  data=bytes(secret, 'ascii'),
)

# https://docs.digdir.no/docs/Maskinporten/maskinporten_protocol_jwtgrant
jwt_header = {
    'alg': 'RS256',
    'kid': kid,
}

# en dictionary som forteller hvilke forespørsler vi ønsker å gjøre i Maskinporten
jwt_claims = {
  'aud': maskinporten_audience, # autentiseringsklienten, som er maskinporten
  'iss': integration_id, 
  'scope': scope,
  'resource': 'https://test.kontaktregisteret.no/rest/v2/personer', # i produksjon: https://kontaktregisteret.no/rest/v2/personer
  'iat': timestamp, # tidsstempling. Maskinporten tillater bare +- 10 sekunders avvik fra egen klokke.  
  'exp': timestamp + 100, # utløpstidspunkt for autentiseringen. Maks 120 sekunder. 
  'jti': str(uuid.uuid4()), # unik ID for hver eneste autentisering
  "consumer_org" : readtxt("parameters/consumer.txt"), # Oslomets organisasjonsnummer
  'iss_onbehalfof': readtxt("parameters/iss_onbehalfof.txt") # Hentes fra integrasjonen i selvbetjeningsportalen. En ID som forteller Maskinporten at vi gjør dette på vegne av Oslomet. 
}

# Sammenstill dictionaries til et JWT-token
jwt_token = jwt.JWT(
  header = jwt_header,
  claims = jwt_claims,
)

# Signer JWK-token
jwt_token.make_signed_token(key)
signed_jwt = jwt_token.serialize()

# make the request body: https://docs.digdir.no/docs/Maskinporten/maskinporten_protocol_token
body = {
  'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
  'assertion': signed_jwt
}

# Send forespørsel om token
res = requests.post(maskinporten_token, data=body)
#print('Token request: ' + res)

result = json.loads(res.text)
token = result['access_token']

# Url til oppslagstjenesten
lookup_endpoint = 'https://test.kontaktregisteret.no/rest/v2/personer'

# Header i request
lookup_header = {
    'Http-metode': 'POST',
    'Authorization': 'Bearer ' + token,
}

# Data/Payload
loopup_body = {
        'personidentifikatorer' : persons,
        'inkluderIkkeRegistrerte': False    
}

# Gjør oppslag
lookup_res = requests.post(lookup_endpoint, headers = lookup_header, json = loopup_body)

print(lookup_res.text)