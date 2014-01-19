from PIL import Image
import urllib2 as urllib
import os, sys
import io
import lob
from datetime import datetime

class Lob_Socket(object):
  def __init__(self):  
    lob.api_key = 'test_0bead6806b12c3668ee03810cf181c78141'
    

  def CreatePostCard(self, url,toaddr, message):
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

def SendPostcard(url, toaddr, message):
  client = Lob_Socket()
  client.CreatePostCard(url,toaddr, message)