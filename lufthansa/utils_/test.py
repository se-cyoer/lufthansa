import time
from lufthansa.lufthansa.db.redisdb import RedisDB
import json


class Redis_(RedisDB):
    def add(self, table, data, prioritys):
        self.zadd(table=table, values=self.dump_data(data), prioritys=prioritys)

    def dump_data(self, data):
        return json.dumps(data)






proxyredis = Redis_(ip_ports='localhost:6379', db=0)
data = {"url": "https://mobile.lufthansa.com/rs/revenue?execution=e1s1&l=en",
        "headers": {"cache-control": "max-age=0", "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "sec-fetch-site": "same-site", "sec-fetch-mode": "navigate", "sec-fetch-user": "?1",
                    "sec-fetch-dest": "document", "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "cookie": "AKA_A2=A; bm_sz=1AC5DBE1EFC37B15DDEE5952D44F4077~YAAQPxQgFy6+8N2AAQAAV9cE+Q+j1XGfgYSuEODpVB1yciQ8lu1WBJmtJR6701QHpmw0dJnvmuORQuj53oJ8cllh1nqfOB5O8gE0Cp06R2EDfp9kiWadn123se8+x5bvUqW83jRXNBwi0ZifRiMMz+3Zm8cbX+fwpSGTrM68BYVmuXpJjg6SS/TSadd/a04liuCoxWDuBqY0pX4T6T8ZeCBtubycZ2p6SZ31vMR2mtgI+0nyHckMAyzSRSo3zwqsso9tQoOGJrnvS/reD4dzkOk4g7abytCawA4tVsDWAzkmu33mLj8=~3551811~3224624; bm_mi=BE7BF2EDA506795021730BF15A25437E~YAAQPxQgFzG+8N2AAQAAM9gE+Q/CbeiOXfb7leX6PpEczJAG+pMElp+mENIfVYBFc5wxXrPgTd3MdQkQ3xUehKPkEsos/xVEVinz3f25H4xekruX4ze6WdloIsSv3UXIa87Q6SbfQxUZK4k92D3prLTkWlDz4pfp2wyoTQL/Ef3lGwQhQa7JK6C03F7FAh0Zv0vAtLkworWrOuuf8d5jlNnwsYxZoOL5oHtD5KCmmFSLwgYVVZJV5+lXgRbtqRQpqOKkRX3NHy6o+BNmSqnqTuZU42IqTyEutZn6vRMM2Ccn9SWAf/097/qbWzqjtoCvu9JDw2sS4GTTXZ8q4TR8~1; cmv3=true; HomepageMarket=hk; mt.v=2.1560323988.1653445287461; _abck=6CE44361E531C0EB2DAC31E976638A06~0~YAAQPxQgF5e+8N2AAQAARu0E+QctPm0Pcj4/ZzkG8ezl9sXFS1uFFWJw1THkb5g+B6LGbqVlGXkcKqhuNultNasi2roUEvhaqkKeod/exGDgZv9FAmZOYropvZusQcVPEz8U6SPb8sK9WKiT2axgInATUwDnAn2Vnnf/VPzns1CuzzQHV4ukMjA9SjnpFCXcagBYQA7OtJmSlqYkx97tJk7JirpOJb7P6RTz8+cJK+Eei73wi5tg0TG4rLr/pZM/DVzla8txsCTvsoLsfxazRdCZrg61fkW0bRz/7ZHTTV9JTE97ZBsy97MxHKDcZ0/iFajROMHtEYM7jrU7YC9wtM4/OVv1A6cHpxO7Mz22CosqWKtUI7IedkfH2h5/F08rEjtoZWEdBhVjDgV0EZ0e3JRA01AZ0DiY+zEOm1oTFI7/e8wxD9xrqHLgOgbMusda72zbnMnSTYTcHx28Bg==~-1~-1~-1; ak_bmsc=540D6419B88E53DBEE460DED00CBDE38~000000000000000000000000000000~YAAQPxQgF8a+8N2AAQAAr/AE+Q/mGv6VChjNsn+Ch5jPxrfiy2JKUHp0DRILRBsJN3HX+a0BsqGg+69iLJzRp3JuqxWVEPfApQm4No3vW0f8tguGlpS5zdwIe1iNOty8qi0vVRkGDzgMHlY5dChauOjJm4WLHPzi+wLuti63n6EtgC0QJmnyYF4IYt3AyjMztGZ6nbAO2qeCjVqlGjmw9FqTCx9thLIatK9/DT0MfQ3pwpLbxKRJmoNMRRXYHIgW1I/z+3SVXPusl2ldRCL9PKDFUqECvrhSLq8kJhey4RBzL5PiOzTHGAqQ3H/rnITE4fiXpffW/5TL0LW6esjMk/8cfSbVYZj2nvHITRp6fXAGpBbOePBcjX7X4+16244O52zgFlIyTO0ASKH//YUKqm0SBZmImSqgbv9X42UTvNmBNmjCc6bgdlR7nN12aA==; _gid=GA1.2.1822556947.1653445293; _gat_main=1; _gcl_au=1.1.333748823.1653445296; _ga_EJMWHEJGLX=GS1.1.1653445294.1.0.1653445294.60; _ga=GA1.1.750699081.1653445293; da_sid=816000CD8E32AE8CBBCFAA13B4AF7CECF8|3|0|3; da_lid=B25333FE9A72EA172E9EBB99F6AD36E74B|0|0|0; da_intState=; et_uk=413d6c914a71428bbb09e30921253e41; et_gk=99fa3e3dafb443e1bceaffbf8fe945c5|24.07.2022 02:21:35; CONSENTMGR=c1:1%7Cc2:1%7Cc3:1%7Cc4:1%7Cts:1653445301675%7Cconsent:true; utag_main=v_id:0180f904dc96003f7d192809c05200087002807f004ae$_sn:1$_se:8$_ss:0$_st:1653447101677$ses_id:1653445287063%3Bexp-session$_pn:1%3Bexp-session$dc_visit:1$dc_event:4%3Bexp-session$dc_region:ap-east-1%3Bexp-session; JSESSIONID=605232BFB25D46037A658521D312B6F7.portal1; LH_USER=BFE932787A0129FC1D62304870D54B31; bm_sv=EF4B5C09187B897FFAD5ED79B80CE596~YAAQPxQgF0m/8N2AAQAA4xoF+Q8dpCMDSyuwhK7cDPSZef0si6REMzGiIZfcg/LVx8jZU5ZfCXmwxVDIccGqrJgs64qIES63RpZDuTGoh/CN4N0fQrTxqhRahqY1XtiU2ew2m9KSOG4TJffVz0rKf12D1P/k4MfRF5496ePjG3NtFXQfR4TZX4WySd5MstDZqWFiRer2/MW0SknvIyB9v+YqP9UM6PxXhR6EmUYiBe0bR0NgEd2sjvdCTJ6yt2qzlwRi~1; LH_NUI_BKG=%2Fkthj1rLg58nfivNl3kgIaCy1D4XRDPQXnSFocBBtKCkTJzuN%2F%2FmD4YhXoNzRt%2FEZRwK9lS3qA8%2F%0A2ssLOzKs042LLh6XrqDo; searchFlightHistory=%5B%7B%22departureDate%22%3A%2220220526%22%2C%22tripType%22%3A%22O%22%2C%22cabin%22%3A%22E%22%2C%22airline%22%3A%22LH%22%2C%22from%22%3A%22HKG%22%2C%22to%22%3A%22FRA%22%2C%22nbAdt%22%3A%221%22%2C%22nbInf%22%3A%220%22%2C%22nbChd%22%3A%220%22%7D%5D"}}

timestamp = time.time()
proxyredis.add(table='Lufthansa', data=data, prioritys=timestamp)

data = proxyredis.zget(table='Lufthansa', is_pop=False)
print(json.loads(data[0]))