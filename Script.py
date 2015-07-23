from math import log, sqrt
from nltk.stem.porter import PorterStemmer
import re
import sys
from nltk import pos_tag, word_tokenize
from nltk.corpus import sentiwordnet
import time

stemmer = PorterStemmer()
#read in +ve, -ve  li

stopwordsFiles = open(r"stopwords.txt", "r")
stopwords = stopwordsFiles.read().splitlines()
stopwordsFiles.close()


File = open(r'training-data1.txt',"r")		
Content = File.read().splitlines()
File.close()


#File = open(r'C:\Users\Administrator\Desktop\Testing\HackathonInput.txt',"r")		
#TestContent = File.read().splitlines()
#File.close()


PostiveLines = []
neglines = []

for line in Content:
	Token = [word.strip() for word in line.split("\t")]
	#print Token
	if (len(Token) == 2):
		Comment = re.sub(r'[^A-Za-z0-9.\s]+', '',Token[1])
		if Token[0] == '1':
			PostiveLines.append(Comment)
			#print line, "Positive"
		else:	
			neglines.append(Comment)
			#print line, "Negative"


#print len(PostiveLines), len(neglines), len(stopwords)



poslinesTrain = PostiveLines[:len(PostiveLines)]
neglinesTrain = neglines[:len(neglines)]


def CountPotentialWords(line):
	cWords = 0
	Rawtoken = word_tokenize(line)
	
	TaggedWords = pos_tag(Rawtoken)
	#print TaggedWords
	#for word in TaggedWords:
	for word in TaggedWords:	
		if "J" in word[1] or "RB" in word[1] :
			cWords = cWords + 1
	return cWords




trainset = [(x, 1) for x in poslinesTrain] + [(x, -1) for x in neglinesTrain]

#testset = [(x, 1) for x in poslinesTest] + [(x, -1) for x in neglinesTest]

#init stemmer for stemming (pruning words)
stemmer = PorterStemmer()

def getwords(sentence):

	
	w = sentence.split()
	
	#remove words which are lesser than 3 characters
	w = [ x for x in  w if len(x) > 2]
	
	#get rid of all stopwords
	w = [ x for x in w if not x in stopwords]
	
	#stem each words
	w = [stemmer.stem(x) for x in w]
	
	#add bigrams
	#w = w + [w([i] + ' ' + w[i + 1] for in in range(len(w) - 1)]
	
	#get rid of duplicates
	w = list(set(w))
	
	return w
	

freq = {}
trainfeatures = []

#for each line and label in training set
for line, label in trainset:
	words = getwords(line)
	
	#for each word in a pruned sentence
	for word in words:
		freq[word] = freq.get(word, 0) + 1
	
	trainfeatures.append((words,label))
	
#evaluate test set
#Numerator
Ntr = len(trainset)
wrong = 0 #store count of misclassifications

def GetSentiment(line):
#for line in TestContent:
		
	testwords = getwords(line)
	
	#we will store distances to all train reviews in this list as tuples of (socre, label)
	#To be sorted by score later
	
	results = []
	
	
	#compute similarity between testword and  every review/trained
	for i, (trainwords, trainlabel) in enumerate(trainfeatures):
	
		#find all common words between these two sentences
		commonwords = [x for x in trainwords if x in testwords]
		
		#accumulate score for all overlaps. Common words count for less 
		#log() function squashes things down so that infrequent words dont count for much
		
		score = 0.0
		
		for word in commonwords:
			score += log(Ntr / freq[word])
			
		#print score, trainlabel
		results.append((score, trainlabel))
		
	#sort similarity based on high scores (descending order)
	results.sort(reverse=True)
	
	#Classify based on the top 5 scores
	toplab = [x[1] for x in results[:10]]
	#number one
	numones = toplab.count(1)
	#negative number one
	numnegones = toplab.count(-1)
	prediction = 1
	
	
	flag = 0
	Sentiment = "NEUTRAL"
	
	print "================================================================"
	if (numones >= 6):
		if flag == 1:
			print "POSITIVE","+ve=%f -ve=%f %s" % ( numones, numnegones, line)
		print "Positive", line,"\n"
		Sentiment = "POSTIVE"
	elif (numones <= 4):
		if flag == 1:
			print "NEGATIVE","+ve=%f -ve=%f %s" % ( numones, numnegones, line)
		print "Negative", line,"\n"
		Sentiment = "NEGATIVE"        
	else:
		if flag == 1:	
			print "NEUTRAL","+ve=%f -ve=%f %s" % ( numones, numnegones, line)
		print "Neutral", line,"\n"
		Sentiment = "NEUTRAL"
	print "================================================================"
	return Sentiment


def SearchGoogle(query)	:
# Source: http://stackoverflow.com/questions/3898574/google-search-using-python-script
import requests
import json

#query = "cats+dogs"

#NB. add 'start=3' to the query string to move to later results
r = requests.get('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=' + query)

# JSON object
theJson = r.content
theObject = json.loads(theJson)

# Print it all out
Response = []
for index,result in enumerate(theObject['responseData']['results']):
    print str(index+1) + ") " + result['titleNoFormatting']
    print result['url']
	Response.append([result['url'], result['titleNoFormatting']])
return 	Response

	
def SaveToFile(Index, Content):
    Content = Content.replace("\"", "\'")
    Details = Content.split("class=\'breadcrumbs\'")[1].split(">")[1:14]
    Forum   = Details[1] + ">" + Details [4] + ">" + Details[6] + ">" + Details[8]
    Title = Details[11]
    AuthorName = Content.split("class=\'authorName \'")[1].split(">")[3]
    TotalComments = len(Content.replace("<br>","").split("class=\'postTimestamp \'"))
    
    NextLink = Content.split("&laquo;")[0].split("<")[-1]
    PostedTimeon = Content.split("class=\'postTimestamp \'")[1].split(">")[1]
    
    Forum = Forum.replace("</A","")
    Title = Title.replace("</A","")
    AuthorName = AuthorName.replace("</A","")
    PostedTimeon = PostedTimeon.replace("</A","")
    NextLink = r"http://www.dslreports.com/"+ NextLink.replace("</A","").replace("A HREF='","").replace("\'>","")
    PostedTimeon = PostedTimeon.replace("</p","")
    Comment = Content.replace("<br>","").split("class=\'postTimestamp \'")[1].split("</div></TD></TR><TR><TD")[0].split(">")[-1]
    
    print Forum
    print Title
    print AuthorName
    print PostedTimeon
    print TotalComments
    print Comment
    Mood = GetSentiment(Comment)
    print NextLink
    
    Comment = Comment.replace("\"","\\\"")
    #Comment = "Comments"
    
    File = open("Output.csv","a+")
    File.write("Index,Forum,Title,AuthorName,TotalComments,NextLink,PostedTimeon,Comment\n")
    #Index = 1
    File.write(str(Index)+",\"" + Forum +"\",\"" + Title +"\",\"" + AuthorName +"\",\"" + str(TotalComments)  +"\",\"" + NextLink  +"\",\"" + PostedTimeon  +"\",\""+ Mood + "\",\"" + Comment  +"\"")
    File.close()
    
    return NextLink
    
if(1):    
    import urllib2
    #url = 'http://www.dslreports.com/forum/r30174874-Channels-Fox-Channels-now-Copyright-flag'
    url = 'http://www.dslreports.com/forum/r30177321-XG2-trials-have-started'
    for i in range(100):
        print "============>Parsing" + url
        response = urllib2.urlopen(url)
        html = response.read()    
        url = SaveToFile(i+1,html)
        time.sleep(1)    