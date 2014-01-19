from PIL import Image
import sendgrid
import urllib2 as urllib
import os, sys
import io
import lob
from datetime import datetime

s = sendgrid.Sendgrid('thelonelygod', '#PASSWORD#', secure=True)


class Lob_Socket(object):
  def __init__(self):  
    lob.api_key = 'test_0bead6806b12c3668ee03810cf181c78141'
    

  def CreatePostCard(self, url,toaddr, message, email):
    fd = urllib.urlopen(url)
    image_file = io.BytesIO(fd.read())
    im = Image.open(image_file)
    width,height = im.size

    size = 600, 400
    outfile = "temp.pdf"

    if height > width:
    	im = im.rotate(90)
    	width,height = im.size 

    diagonal =(1.0 *  width) / height 

    if diagonal > 1.5:
        resizewidth = (600 * height) / 400

        center =  (width - resizewidth) / 2
        im = im.crop((center,0,width - center,height))
    elif diagonal < 1.5:
        resizeheight = (400 * width) / 600
        center =  (height - resizeheight ) / 2
        im = im.crop((0,center,width,height - center))


    im.thumbnail(size, Image.ANTIALIAS)
    if im.size != size:
    	im = im.resize(size,Image.ANTIALIAS)

    im.save(outfile, "pdf", resolution=100.0)

    
    fromaddr = lob.Address.create(name="MHacks", address_line1="611 Woodward Ave", address_line2="", 
    	email="Shyamal@Ruparel.co", address_city="Detroit", address_state="MI", address_country="US", address_zip="48226").to_dict()
    PCName = str(datetime.now())
    postcard = lob.Postcard.create(name=PCName, to=toaddr,
                               message=message,
                               front= open(outfile,'rb'),
                               from_address=fromaddr).to_dict()

    print postcard
    emailMessage = sendgrid.Message("Shyamal@Ruparel.co", "PinPost Recipt", message,
    "<p>"+message+"</p>")
    emailMessage.add_to(email, "PinPost User")
    emailMessage.add_attachment("PostCard.pdf", "outfile")
    try:
        s.web.send(emailMessage)
    except Exception, e:
        print "Could not send mail with sendgrid."

def SendPostcard(url, toaddr, message, email):
  client = Lob_Socket()
  client.CreatePostCard(url,toaddr, message, email)