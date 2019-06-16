#!/usr/bin/python3

import fichin_lex
import json


srv = fichin_lex.FichinLexService()
retdata = srv.make_request(request_text='in')

ret = json.loads(retdata)

print(ret['message'])

