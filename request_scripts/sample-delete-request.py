#!/usr/bin/env python3

import requests
import json, jsonpickle
import os
import sys
import base64
import glob


#
# Use localhost if not specified by environment variable REST
#
REST = os.getenv("REST") or "localhost"

##
# The following routine makes a JSON REST query of the specified type
# and if a successful JSON reply is made, it pretty-prints the reply
##

def mkReq(reqmethod, endpoint, data, verbose=True):
    print(f"Response to http://{REST}/{endpoint} request is {type(data)}")
    jsonData = jsonpickle.encode(data)
    if verbose and data != None:
        print(f"Make request http://{REST}/{endpoint} with json {data.keys()}")
        print(f"mp3 is of type {type(data['mp3'])} and length {len(data['mp3'])} ")
    response = reqmethod(f"http://{REST}/{endpoint}", data=jsonData,
                         headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        jsonResponse = json.dumps(response.json(), indent=4, sort_keys=True)
        print(jsonResponse)
    else:
        print(
            f"response code is {response.status_code}, raw response is {response.text}")
    return response


if __name__ == "__main__":
    print(f"Cache from server is")
    resp = mkReq(requests.get, "apiv1/queue", data=None)
    if resp.status_code != 200: sys.exit()
    test_hash = "83abdba474adf043c6879343f3561e36d5d9b37d3dba90603b33affa2dc2a666"
    #Test Bass removal of all hashes
    resp = mkReq(requests.delete, f"apiv1/remove/{test_hash}/vocals", data=None)
    if resp.status_code != 200: sys.exit()