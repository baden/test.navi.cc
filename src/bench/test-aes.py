import timeit
import hashlib
import hmac
import base64

secret = "some secret"
remote_ip = "127.0.0.1"
user_agent = "User-Agent"
id = "007"
domain = "some_host_com"

from tornado.web import decode_signed_value

def decode_signed_value(self, name, value):
    from tornado.web import decode_signed_value
    return decode_signed_value(self.application.settings["cookie_secret"],
                               name, value, max_age_days=31)

def foo():
    hash = hmac.new(secret, digestmod=hashlib.sha1)
    hash.update(str(remote_ip))
    hash.update(user_agent)
    hash.update(id)
    hash.update(domain)
    identity = base64.urlsafe_b64encode(hash.digest()).rstrip('=')
    access_token = decode_signed_value("access_token", access_token)


t = timeit.timeit(foo)
print("Time = {0}".format(t))

