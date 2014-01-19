import Pintrest_Socket
import Lob_Socket
import lob
import time
import sys

lob.api_key = 'test_0bead6806b12c3668ee03810cf181c78141'
print len(sys.argv)
if len(sys.argv) < 2:
	user_name = "shyruparel"
else:
	user_name = sys.argv[1]
print user_name
toName = "Shyamal Ruparel"
toaddress_line1 = '2818 Stratford Ave'
toaddress_line2 = 'Apt 2'
toemail= "Shyamal@Ruparel.co"
toaddress_city = "Cincinnati"
toaddress_state = "OH"
toaddress_country = "US"
toaddress_zip ="45520"

toaddr = lob.Address.create(name=toName, address_line1=toaddress_line1, address_line2=toaddress_line2, email=toemail, address_city=toaddress_city, address_state=toaddress_state, address_country=toaddress_country, address_zip=toaddress_zip).to_dict()

start_time = time.time()
try:
	TopPin = Pintrest_Socket.Get(user_name)
except:
	print "User DNE or has no Boards"
	sys.exit()
end_time = time.time()
print("Elapsed time was %g seconds" % (end_time - start_time))

url = TopPin["image_large_url"]
message = TopPin["description"] + "\n- " + TopPin["domain"]


print "Message: \n" + message
start_time = time.time()
try:
	Lob_Socket.SendPostcard(url,toaddr,message)
	end_time = time.time()
except:
	print "Lob Failure"
	sys.exit()
print("Elapsed time was %g seconds" % (end_time - start_time))