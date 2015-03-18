import os,csv,webbrowser,urllib,urllib2,re
from lxml import etree
from bs4 import BeautifulSoup
import cPickle as pickle
"""
Added for taking the anser in summarized form from Wikipedia .
"""
class WikipediaError(Exception):
    pass
class GrabArticle(object):
    """
    Grabbing an article from wikipedia
    """

    def __init__(self):
        self.url_random = "http://en.wikipedia.org/w/api.php?action=query&prop=revisions&grnnamespace=0&rvsection=0&generator=random&rvprop=content&format=xml"

    def __fetch(self, url):
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.0")
        try:
            result = urllib2.urlopen(request)   
        except urllib2.HTTPError, e:
            raise WikipediaError(e.code)
        except urllib2.URLError, e:
            raise WikipediaError(e.reason)
        return result
    
    def findArticle(self, article=None):
        """
        Finding a given article
        """
        if article is not None:
            title=re.sub(r"\s" ,r"%20", article)
            url = "http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvsection=0&titles=%s&rvprop=content&format=xml" % title
        else:
            url = self.url_random

        content = self.__fetch(url).read()
        tree = etree.fromstring(content)
        text=""
        try:
            text = tree.find(".//rev").text
        except:
            words=article.split()
            if words[0].islower():
                return self.findArticle(article.capitalize())
            if len(words) > 1:
                if words[0].istitle() and words[1].islower():
                    return self.findArticle(article.title())
            else:
                return 'Article "%s" cannot be found.' % article
        try:
            if '#REDIRECT' in text:
                match = re.match(r"(?i)#REDIRECT \[\[([^\[\]]+)\]\]", text)
                if match is not None:
                    return self.findArticle(match.group(1))
                raise WikipediaError("Can't find redirect article.")
            return content
        except:
            return None

    def image(self, image, thumb=None):
        """
        removing image
        """
        url = self.url_image % (image)
        result = self.__fetch(url)
        content = result.read()
        if thumb:
            url = result.geturl() + '/' + thumb + 'px-' + image
            url = url.replace('/commons/', '/commons/thumb/')
            url = url.replace('/' + self.lang + '/', '/' + self.lang + '/thumb/')
            return self.__fetch(url).read()
        return content
    
class Wiki2Plain(object):
    """
    Converting HTML to Plain Text
    """
    def __init__(self, wiki):
        self.wiki = wiki
        self.text = wiki
        self.text = self.unhtml(self.text)
        self.text = self.unwiki(self.text)
        self.text = self.punctuate(self.text)
    def __str__(self):
        return self.text
    def unwiki(self, wiki):
        """
        Remove wiki markup from the text. Hardcoded stuff.
        """
        wiki = re.sub(r'(?i)\{\{IPA(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'(?i)\{\{Lang(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\|[^\{\}]*?\|\}', '', wiki)
        wiki = re.sub(r'(?i)\[\[Category:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[Image:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[File:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'\[\[[^\[\]]*?\|([^\[\]]*?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', '', wiki)
        wiki = re.sub(r'(?i)File:[^\[\]]*?', '', wiki)
        wiki = re.sub(r'\[[^\[\]]*? ([^\[\]]*?)\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r"''+", '', wiki)
        wiki = re.sub(r"&quot;", '"', wiki)
        wiki = re.sub(r'(?m)^\*$', '', wiki)
        wiki = re.sub(r'&ndash;', '-', wiki)
        wiki = re.sub(r'&lt;ref.*?&gt;.*?&lt;/ref.*?&gt;', '', wiki, flags=re.DOTALL)
        wiki = re.sub(r'&lt;.*?&gt;', '', wiki, flags=re.DOTALL)
        wiki = re.sub(r'&\w{1,4};', '', wiki)
        return wiki
    def unhtml(self, html):
        """
        Remove HTML from the text.
        """
        html = re.sub(r'(?i)&nbsp;', ' ', html)
        html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
        html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
        html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
        html = re.sub(r'(?m)<.*?>', '', html)
        html = re.sub(r'(?i)&amp;', '&', html)
        return html
    def punctuate(self, text):
        """
        Convert every text part into well-formed one-space
        separate paragraph.
        """
        text = re.sub(r'\r\n|\n|\r', '\n', text)
        text = re.sub(r'\n\n+', '\n\n', text)
        parts = text.split('\n\n')
        partsParsed = []
        for part in parts:
            part = part.strip()
            if len(part) == 0:
                continue
            partsParsed.append(part)
        return '\n\n'.join(partsParsed)
    def image(self):
        """
        Retrieve the first image in the document.
        """
        # match = re.search(r'(?i)\|?\s*(image|img|image_flag)\s*=\s*(<!--.*-->)?\s*([^\\/:*?<>"|%]+\.[^\\/:*?<>"|%]{3,4})', self.wiki)
        match = re.search(r'(?i)([^\\/:*?<>"|% =]+)\.(gif|jpg|jpeg|png|bmp)', self.wiki)
        if match:
            return '%s.%s' % match.groups()
        return None
def getArticle(article):
    """
    Main Loop (Function) where other functions are called
    """
    wiki=GrabArticle()
    raw=wiki.findArticle(article)
    wiki2plain=Wiki2Plain(raw)
    article=wiki2plain.text
    try:
        if len(article) < 3:
            return False
        else:
            return article
    except:
        return None
    
def tts(text):      # Text to speach
    """
    Using espeak module for outputting the answer through speakers.
    """
    return os.system("espeak  -s 155 -a 200 "+text+" " )
    
while(1):           # Infinite Loop {Main for calling all other functions}
    print "Welcome to PIIOTA Answering machine"
    print "1 . Talk to PIIOTA "
    print "2 . Exit"
    ai=raw_input("")
    if len(ai)!=1:              #Added to check whether empty line inputted or not
        break
    else:
        a=int(ai)           
    if a==2:
        print "Thank you"
        tts("Thank\ you")
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
                url = "http://en.wikipedia.org/wiki/"+article   # Added to make the new Url
            ##    webbrowser.open(url,new=new)    # Opening in browser
                if __name__=="__main__":
                      print getArticle(b[2:])   # For getting summarized article
            else:
                b=b.lower()                     # converting to lower case for removing differentiation between lower case and upper case
                l=os.getcwd()+"/Data/"+b[0]+'.p' # Location of a file
                try:
                   with open(l) as f: pass
                   foi=pickle.load(open(l,"rb")) # loading file using pickel
                   if b in foi.keys():
                       print foi[b]
                       k=foi[b].replace(" ","\ ")
                       tts(k)
                   else:
                       f=open(l,'a')
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
                    print l
                    f=open(l,'w')
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
                        tts("Thank\ you")
