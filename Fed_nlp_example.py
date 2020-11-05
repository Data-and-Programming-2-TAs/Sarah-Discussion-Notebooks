
''' Example from Prof. Levy
    If your HW is inspired by this, be sure to cite it
    This is equivalent to getting code from lab (which you should be citing too)

    Also note:
    that these line lengths are sometimes too long, keep an eye on that
    in your own code

    The coments are notes that I included, this is not an example of clean commenting
    which you should practice -talk to me if you want more clarity on what clean
    comments look like
'''


import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
import spacy 
             

do_download = False #don't forget to change to True for your first run-through

#path = r'c:\users\jeff levy\desktop\fomc_lecture'
path = '/Users/Sarah/Documents/GitHub/Sarah-Discussion-Notebooks/Data' 
os.chdir(path) 

urls = ['https://www.federalreserve.gov/newsevents/pressreleases/monetary20081216b.htm',
        'https://www.federalreserve.gov/newsevents/pressreleases/monetary20190918a.htm']
#press releases from the Federal Open Market Committee 
#may want to extract meaning: e.g. itterate over all the press releases from 2008 and...
#deadlock in 2008, countersiklical (Keynsian)spending is one main theory
#but also a theory: zero lower bound, which says that if at 0 interest reates printing $ wont -> inflation
#this recession bore out that argument
#Riht leaning economists sent letter that Fed needed to stop printing $
#fear of hyper inflation
#Fed trippled the monitary base durring this time
#infflation rate never went above 2%
#evedence for the zero lower bound theory
#other contries printed money and -> inflation. Inflation rate can reach million percent
#so 2008 FOMC veyr busy, lots of discussion lots of press releases

#maybe we want to see if sound pesimistic or optimistic (sentiment analysis)

def parse_fname(url):
    fname = url.split('/')[-1] #takes the end of the url

    pattern = r'monetary(\d{4})(\d{2})(\d{2})([ab]?)\.htm' #regular expression: matches the end of these urls
    #d{4} matches any 4 numbers in a row
    #[ab]? matehces an a or a b 0 or 1 times (so either an a or a b or neither)
    #\. match a literal . not as the regex period
    #? means may be in there may not be. Want it to match only what you want but all of what you want
    #use https://regex101.com to fiddle with it
    match = re.match(pattern, fname)

    year  = match.group(1) #pull out each group
    month = match.group(2)
    day   = match.group(3)

    assert(len(year) == 4 and len(month) == 2 and len(day) == 2), 'Unable to parse date from url: {}'.format(url)
    #makes srue the len of year is 4 and the len of month and day are ea 2
    return '-'.join([year, month, day]) + '.txt' #set file name you want

    #this urls

def get_statement(url): #web scrapping
    response = requests.get(url)
    fname = parse_fname(url)

    soup = BeautifulSoup(response.text, 'lxml')
    article = soup.find('div', id='article') #see on the web page
    paragraphs = article.find_all('p')

    header = paragraphs[:2] #know from exlprring it
    body = '\n\n'.join([p.text for p in paragraphs[2:]])
    body = body.replace(u'\xa0', ' ') #fix an encoding character for spaces
    #\xa0 tells webpage white space, we replace it with actual white space

    with open(os.path.join(path, fname), 'w') as ofile:
        ofile.write(body)

def load_text(fname):
    with open(os.path.join(path, fname), 'r') as ifile:
        content = ifile.read()
    return content

def span_to_index(sp, doc):
    start = sp.start
    end = sp.end
    return doc[start:end]

def process_text(text, nlp):
    doc = nlp(text)

    for kind in ['federal', 'discount', 'unemployement']:
        doc_slice = [span_to_index(nc, doc) for nc in doc.noun_chunks if 'rate' in nc.string and  kind in nc.string]
        
        rate_mentions = [t for t in doc if t.text == 'rate'] 
        rate_ancestors = [list(r.ancestors) for r in rate_mentions]  #list so we can see it

        rate_up = ['raise', 'increase', 'up'] #
        rate_down = ['lower', 'decrease', 'down']
        rate_unchanged = ['uncanged', 'same']

        up_counter = 0
        down_counter = 0
        flat_counter = 0

        for ra in rate_ancestors: #ra will be a list (it was a list in a list)
            #print(ra) #debug
            #break #so just see the first thing
            for ancestors in ra: #so we need to iterate over the list to get the tokens
                #print(ancestor) #debug
                if ancestors.text in rate_up:
                    up_counter +=1
                elif ancestors.text in rate_down:
                    down_counter +=1
                elif ancestors.text in rate_unchanged:
                    flat_counter +=1
    print('TERM\n', kind, '\nUp:', up_counter, '\nUnchanged:', flat_counter, '\nDown:', down_counter)
    

#try it with one thing, not a loop
#then we look at the doc: we caught a 'rate' that was about the discount rate! that's a different kind
#of rate than we wanted
#in another doc we got the unemployement rate in there too
#so we need to catgorized findings fo 'rate' to seek waht kind

#exicuting the code
if __name__ == '__main__':

    if do_download:
        for url in urls:
            get_statement(url)
    #call a fn in a loop, equally valid to call the loop in a fn instead

    all_files = [f for f in os.listdir(path) if f.endswith('.txt')] #list the txt docs in there
    all_text  = {datetime.datetime.strptime(fname, '%Y-%m-%d.txt'):load_text(fname) for fname in all_files}
    #dictionary comprehension; builds a dict in  one list
    #key is {...:
    #value is :...}

    nlp = spacy.load("en_core_web_sm")

    # This part is not finished: just an example of one call
    process_text(all_text[datetime.datetime(2008,12,16)],nlp)





