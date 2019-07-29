import requests
import json



url = "https://newslens.berkeley.edu/api/ruchir/save/allLogins" 
save_res = requests.post(url, data=json.dumps([]))