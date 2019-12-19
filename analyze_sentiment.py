api_key = 'ENTER YOUR API KEY HERE'

import os
from textblob import TextBlob
from nltk.corpus import stopwords
import string
from textblob.sentiments import NaiveBayesAnalyzer
import pandas as pd
import dateutil.parser
import matplotlib.pyplot as plt
from tqdm import tqdm
import time

from googleapiclient.discovery import build

youtube = build('youtube', 'v3', developerKey=api_key)


comment_list=[]
likes_list=[]
author_list=[]
date_list=[]

def video_details(title,videoId):	
	video = youtube.videos().list(part='snippet,contentDetails,statistics',id=videoId).execute()
	print('HERE ARE THE DETAILS OF THE VIDEO YOU REQUESTED BY YOU'.center(os.get_terminal_size().columns))
	for item in video['items']:
		date = dateutil.parser.parse(item['snippet']['publishedAt'])
		date = date.strftime('%d/%m/%Y')	
		print(' THE VIDEO WAS PUBLISHED ON --\n',date)
		print(' TOTAL VIEWS ON THE VIDEO --\n',item['statistics']['viewCount'])
		print(' TOTAL LIKES ON THE VIDEO --\n', item['statistics']['likeCount'])
		print(' TOTAL DISLIKES ON THE VIDEO --\n', item['statistics']['dislikeCount'])
		print(' TOTAL COMMENTS ON THE VIDEO --\n', item['statistics']['commentCount'])
		print('\n')
		print('-'*40)

def get_comments(title,videoId, token=''):
	comm = youtube.commentThreads().list(part="snippet",videoId=videoId,textFormat="plainText", maxResults=80).execute()
	
	for item in comm["items"]:
		comment_list.append(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
		likes_list.append(item['snippet']['topLevelComment']['snippet']['likeCount'])
		author_list.append(item['snippet']['topLevelComment']['snippet']['authorDisplayName'])
		date = dateutil.parser.parse(item['snippet']['topLevelComment']['snippet']['publishedAt'])
		date_list.append(date.strftime('%d/%m/%Y'))
	
	if "nextPageToken" in comm:
		return get_comments(title,comm["nextPageToken"])
	else:
		return {'Comments':comment_list, 'Comment By':author_list,'Total Likes':likes_list,'Date_posted':date_list}

def save_data(main_data):
	data = main_data
	df = pd.DataFrame(data)
	file_name = input('ENTER THE NAME OF THE FILE ->')
	df.to_csv(file_name+'.csv')
	print(file_name+'.csv has been saved in your present working directory')

def clean(comments,new_comments_list=[]):
	for text in comments:
		text=text.lower()
		tokens = text.split()
		table = str.maketrans('', '', string.punctuation)
		tokens = [w.translate(table) for w in tokens]
		tokens = [word for word in tokens if word.isalpha()]
		stop_words = set(stopwords.words('english'))
		tokens= [w for w in tokens if not w in stop_words]
		cleaned_text= " ".join(tokens)
		new_comments_list.append(cleaned_text)

	return new_comments_list

def analyze(comments,sent_list=[],subjective_list = []):
	comments = clean(comments)
	for text in comments:
		blob = TextBlob(text, analyzer=NaiveBayesAnalyzer())
		sent = list(blob.sentiment)
		sent_list.append(sent[0])
		res = list(TextBlob(text).sentiment)
		if res[1]>0.50:
			subjective_list.append(res)
	positive_list = [w for w in sent_list if w == 'pos']
	negative_list = [w for w in sent_list if w == 'neg']

	sub_percent  = len(subjective_list)*100/len(sent_list)
	pos_percent = len(positive_list)*100/len(sent_list)
	neg_percent = (len(negative_list)*100/len(sent_list))


	return {'Comments':comments,'Subjective_List':subjective_list,'Sub_percent':sub_percent,'Positive_List':positive_list, 'Negative_List':negative_list, 'Positive':pos_percent, 'Negative':neg_percent}	

def create_graph():
	arr = [p_percent,n_percent]
	labels = ['Positive_Reviews','Negative_Reviews']
	plt.pie(arr,labels=labels)
	plt.show()

def create_sub_graph():
	arr2 = [sub_percent,normal_comments]
	labels = ['Subjective/Suggestions On VIDEO', 'SENTIMENTAL REVIEWS']
	plt.pie(arr2,labels=labels)
	plt.show()

def save_the_graph():
	arr = [p_percent,n_percent]
	labels = ['Positive_Reviews','Negative_Reviews']
	plt.pie(arr,labels=labels)
	plt.savefig('graph.pdf')

if __name__=='__main__':

	print('-'*55,'YOUTUBE SENTIMENT ANALYSIS','-'*55,''.center(os.get_terminal_size().columns))
	print('\n')
	print('HELLO THERE! WELCOME TO YOUTUBE SENTIMENT ANALYSIS '.center(os.get_terminal_size().columns))
	print('HERE YOU CAN GATHER INFORMATION ABOUT ANY VIDEO FROM ALL OVER THE YOUTUBE '.center(os.get_terminal_size().columns))
	print('\n')
	print("SO LET'S BEGIN".center(os.get_terminal_size().columns))
	print('-'*40,'+'*40,'-'*40,''.center(os.get_terminal_size().columns))
	
	while True:
		title = input('\t ENTER THE TITILE OR URL OF THE VIDEO -\t')
		print('\n')
		print("\n ALL RIGHT!!! \t What do you wanna do know? : \n 1. GET DETAILS ABOUT THE VIDEO  \n 2. Analyze Sentiment Value For Comments \n\n")
		choice = input('\t ENTER YOUR CHOICE \t')
		print('-'*40,'+'*40,'-'*40,''.center(os.get_terminal_size().columns))
		print('\n')
		# youtube = build('youtube', 'v3', developerKey=api_key)
		res = youtube.search().list(q=title, part='snippet', type='video', maxResults=1).execute()
		results = res['items']
		videoId = results[0]['id']['videoId']

		if choice == '2':
			print('\t\tJUST A MOMENT! EXTRACTING {} COMMENTS......'.format(100).center(os.get_terminal_size().columns))

			for i in tqdm(range(),desc=" EXTRACTING COMMENTS->"):
			main_data = get_comments(title,videoId)
			comments = main_data['Comments']
			print('\nALL COMMENTS EXTRACTED !'.center(os.get_terminal_size().columns))

			print('\nCOMMENTS ARE NOW CLEANED AND READY TO BE USED !'.center(os.get_terminal_size().columns))
			print("\n ALL RIGHT!!! \t What would you like to do with it? : \n 1. RUN SENTIMENT ANALYSIS  \n 2. SAVE COMMENTS FOR FURTHER USE \n\n")
			check = input('ENTER YOUR CHOICE:-')

			if check =='1':
				analysis_data = analyze(comments)
				p_percent = analysis_data['Positive']
				n_percent = analysis_data['Negative']
				sub_percent = analysis_data['Sub_percent']
				print('ALL COMMENTS ARE NOW CATEGORIZED INTO DIFFERENT SENTIMENTS')
				print(f'TOTAL Positive Reviews On The Video {p_percent}%')
				print(f'TOTAL Negative Reviews On The Video{n_percent}%')
				print(f'TOTAL Suggestions on the Video{sub_percent}%')
				print('$'*20)
			
				print('PULLING OUT THE GRAPH FOR THIS RESULT \n')
				create_graph()
				create_sub_graph()
				save_graph = input('DO YOU WANT TO SAVE THE GRAPH - (y OR n)')
				if save_graph == 'y':
					save_the_graph()
					print('GRAPH has been saved in your present working directory')
				else:
					print('ALL RIGHT!! AS YOU WISH')	
				print('-'*40,'+'*40,'-'*40,''.center(os.get_terminal_size().columns))
			elif check == '2':
				print('SAVING ALL THE COMMENTS ...  PLEASE WAIT !!!!')
				save_data(main_data)
		
		elif choice == '1':
			video_details(title,videoId)

		else:
			print('INVALID INPUT')






