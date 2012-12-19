#
import httplib, urllib

#SERVER = "localhost"
SERVER = "point.gps.navi.cc"
SERVER_PORT = 80
#IMEI = "1234"

def rawPOST(url, body):
	http = httplib.HTTP(SERVER, SERVER_PORT)
	http.putrequest('POST', url)
	http.putheader('Content-Type', 'application/binary')
	http.putheader('Content-Length', str(len(body)))
	http.endheaders()
	http.send(body)
	code, msg, headers = http.getreply()
	result = http.file.read()

	print 'code: %s\r\nmsg:%s\r\nHeaders:\r\n%s' % (code, msg, headers)
	print 'result (%d bytes)\r\n%s' % (len(result), result)

def rawPOST2(url, body):
	# headers = {"Content-type": "application/octet-stream", "Accept": "text/plain"}
	headers = {"Accept": "text/plain"}
	conn = httplib.HTTPConnection(SERVER, SERVER_PORT)
	conn.request("POST", url, body, headers)

	response = conn.getresponse()
	print 'Status: %s\r\nReason: %s\r\nHeaders:' % (response.status, response.reason)
	for p in response.getheaders():
		print p[0], ':', p[1]
	#print '\r\nMsg:\r\n%s' % response.msg
	data = response.read()
	conn.close()
	print 'Data:\r\n%s' % data

def simpleGET(url):
	http = httplib.HTTP(SERVER, SERVER_PORT)
	http.putrequest('GET', url)
	#http.endheaders()
	http.send('')
	code, msg, headers = http.getreply()
	result = http.file.read()

	print 'code: %s\r\nmsg:%s\r\nHeaders:\r\n%s' % (code, msg, headers)
	print 'result (%d bytes)\r\n%s' % (len(result), result)

def simpleGET2(url):
	conn = httplib.HTTPConnection(SERVER, SERVER_PORT)
	conn.request("GET", url)
	response = conn.getresponse()
	print 'Status: %s\r\nReason: %s\r\nHeaders:\r\n' % (response.status, response.reason)
	for p in response.getheaders():
		print p
	#print 'Msg:\r\n%s' % response.msg
	data = response.read()
	conn.close()
	print 'Data:\r\n%s' % data

