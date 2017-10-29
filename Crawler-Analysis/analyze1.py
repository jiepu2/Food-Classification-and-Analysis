########### Python 3.2 #############
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json

body = "{'url':'https://scontent.cdninstagram.com/t51.2885-15/s640x640/sh0.08/e35/21568762_318777815199379_3420968659881820160_n.jpg'}"

subscription_key = '619edde02d504603867b109846f68e48'



uri_base = 'westcentralus.api.cognitive.microsoft.com'

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': subscription_key,
}

params = urllib.parse.urlencode({
    # Request parameters
    'visualFeatures': 'Categories,Description',
    'language': 'en',
})

def analyze(body):
    try:
        # Execute the REST API call and get the response.
        conn = http.client.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
        conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        parsed = json.loads(data)
        print (parsed)
        if parsed.get('statusCode') == 401 or parsed.get('statusCode') == 403:
            return parsed
        print (list(parsed['description']['tags']))
        return list(parsed['description']['tags'])
        #'data' contains the JSON data. The following formats the JSON data for display.
        parsed = json.loads(data)
        # print ("Response:")
        # print (json.dumps(parsed, sort_keys=True, indent=2))
        conn.close()

    except Exception as e:
        print('Error:')
        print(e)



####################################