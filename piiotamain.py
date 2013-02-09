import os,csv,webbrowser,urllib,urllib2
from bs4 import BeautifulSoup
import cPickle as pickle
def tts(text):
      return os.system("espeak  -s 155 -a 200 "+text+" " )
while(1):
    print "Welcome to PIIOTA Answering machine"
    print "1 . Talk to PIIOTA "
    print "2 . Exit"
    a=input()
    if a==2:
        break
    if a==1:
        print "Welcome... Talk to me !!"
        while(1):
            b=raw_input("")
            if not b.split():    # Checking for empty line
                break
            if b[:2]=="w:":
                article= b[2:]
                new = 2     # open in a new tab, if possible
                url = "http://en.wikipedia.org/wiki/"+article
                webbrowser.open(url,new=new)
            else:
                b=b.lower()
                l=os.getcwd()+"/Data/"+b[0]+'.p' # Location of a file
                try:
                   with open(l) as f: pass
                   foi=pickle.load(open(l,"rb")) # loading file using pickel
                   if b in foi.keys():
                       print foi[b]
                       k=foi[b].replace(" ","\ ")
                       tts(k)
                   else:
                       f=open(l,'w+')
                       print "Sorry .. Want to contribute by telling the appropriate answer"
                       print "1 . Contribute"
                       print "2 . Exit"
                       c=input()
                       if c==2:
                           break
                       else:
                           do={}
                           do[b]=raw_input("Enter your answer ")
                           try:
                               foi=pickle.load(open(l,"rb"))   # loading the file
                               foi.update(do)  # updating the dictionary
                           except EOFError:
                               foi={}
                               pickle.dump(foi,open(l,"wb"))
                               foi=pickle.load(open(l,"rb"))
                               foi.update(do)
                           pickle.dump(foi,open(l,"wb"))    # saving back in the file
                           print "Thank you"
                except IOError as e:
                    f=open(l,'w+')
                    print "Sorry .. Want to contribute by telling the appropriate answer"
                    print "1 . Contribute"
                    print "2 . Exit"
                    c=input()
                    if c==2:
                        break
                    else:
                        do={}
                        do[b]=raw_input("Enter your answer ")
                        try:
                            foi=pickle.load(open(l,"rb"))   # loading the file
                            foi.update(do)
                        except EOFError:
                            foi={}
                            pickle.dump(foi,open(l,"wb"))
                            foi=pickle.load(open(l,"rb"))
                            foi.update(do)              # updating the dictionary
                        pickle.dump(foi,open(l,"wb"))   # saving the dictionary
                        print "Thank you"
