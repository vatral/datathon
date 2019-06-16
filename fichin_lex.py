#!/usr/bin/python3

# pylint: disable=bad-whitespace
# pylint: disable=missing-docstring
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-locals
# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods


# AWS Version 4 signing example

# Based on example from the source:
# http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html

# Amazon Lex API request

# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a POST request and passes request parameters
# in the body (payload) of the request. Auth information is passed in
# an Authorization header.
import datetime
import hashlib
import hmac
import sys
import os

import requests

def _sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def _getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = _sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = _sign(kDate, regionName)
    kService = _sign(kRegion, serviceName)
    kSigning = _sign(kService, 'aws4_request')
    return kSigning


class FichinLexService:
    def __init__(self):
        self.region       = 'eu-west-1'
        self.host         = 'runtime.lex.' + self.region + '.amazonaws.com'
        self.endpoint     = 'https://' + self.host
        self.bot_name     = 'fichin'
        self.bot_alias    = 'fichin'
        self.user_id      = 'myuserid'
        self.access_key   = os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key   = os.environ.get('AWS_SECRET_ACCESS_KEY')

        if self.access_key is None or self.secret_key is None:
            print('No access key is available. Please set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.')
            sys.exit()

    def make_request(self, request_text):
        method = 'POST'
        service = 'lex'
        request_parameters =  '{"inputText": "' + request_text + '", "sessionAttributes": {"attr_name" : "value"}}'
        post_action = 'text'

        content_type = 'application/json'

        # Create a date for headers and the credential string
        t = datetime.datetime.utcnow()
        amz_date = t.strftime('%Y%m%dT%H%M%SZ')#'20170714T010101Z'
        date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope  '20170714'

        canonical_uri = '/bot/' + self.bot_name + '/alias/' + self.bot_alias + '/user/' + self.user_id + '/' + post_action

        canonical_querystring = ''

        canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + self.host + '\n' + 'x-amz-date:' + amz_date + '\n'

        signed_headers = 'content-type;host;x-amz-date'

        payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()

        canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash

        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = date_stamp + '/' + self.region + '/' + service + '/' + 'aws4_request'
        string_to_sign = algorithm + '\n' +  amz_date + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()


        # Create the signing key using the function defined above.
        signing_key = _getSignatureKey(self.secret_key, date_stamp, self.region, service)

        # Sign the string_to_sign using the signing_key
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()


        # Put the signature information in a header named Authorization.
        authorization_header = algorithm + ' ' + 'Credential=' + self.access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

        # For Lex, the request can include any headers, but MUST include "host", "x-amz-date",
        # "x-amz-target", "content-type", and "Authorization". Except for the authorization
        # header, the headers must be included in the canonical_headers and signed_headers values, as
        # noted earlier. Order here is not significant.
        # # Python note: The 'host' header is added automatically by the Python 'requests' library.
        headers = {'Content-Type':content_type,
                   'X-Amz-Date':amz_date,
                   'Authorization':authorization_header}


        # ************* SEND THE REQUEST *************
        print('\nBEGIN REQUEST++++++++++++++++++++++++++++++++++++')
        print('Request URL = ' + self.endpoint)

        r = requests.post(self.endpoint + canonical_uri, data=request_parameters, headers=headers)

        print('\nRESPONSE++++++++++++++++++++++++++++++++++++')
        print('Response code: %d\n' % r.status_code)
        print(r.text)
        return r.text
