import os,csv
import cPickle as pickle
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
            if not b.split():
                break
            l=os.getcwd()+'/'+b[0]+'.p'
            try:
               with open(l) as f: pass
               foi=pickle.load(open(l,"rb"))
               print foi[b]
               continue
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
                        foi=pickle.load(open(l,"rb"))
                        foi.update(do)
                    except EOFError:
                        foi={}
                        pickle.dump(foi,open(l,"wb"))
                        foi=pickle.load(open(l,"rb"))
                        foi.update(do)
                    pickle.dump(foi,open(l,"wb"))
                    print "Thank you"
