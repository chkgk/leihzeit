from bs4 import BeautifulSoup
import urllib
import codecs
import datetime
import os

def get_next_page_url(current_page):
	# looks for an "older posts" link in the current page
	# returns URL if found and None if not.
	next_link_tag = current_page.find('div', 'nav-previous')
	if next_link_tag.a:
		return next_link_tag.a['href']
	else:
		return None

def get_info(article):
	# returns am object containing all relevant info on the article
	date_published = article.find('a', 'entry-date').time['datetime'][:19]
	title = article.find('h1', 'entry-title').a.string
	content = article.find('div', 'entry-content').get_text()
	category_entries = article.find('span', 'cat-links').find_all('a')
	categories = [unicode(cat.get_text()) for cat in category_entries]
	return {
		'published': unicode(date_published),
		'title': unicode(title),
		'content': unicode(content),
		'categories': categories
	}

def formated_date(wordpress_string):
	# create python time object from publishing date provided by wordpress
	date = datetime.datetime.strptime(wordpress_string, "%Y-%m-%dT%H:%M:%S")
	# transform into nicely formatted string:
	# ex. Tuesday, 27. December 2016 - 16:49
	print_date = datetime.datetime.strftime(date, "%A, %d. %B %Y - %H:%M")
	# remove leading 0 on days < 10
	print_date = print_date.replace(' 0', ' ')
	return print_date

def collect_articles(start_url):
	# initialize empty article list
	article_list = []
	while start_url:
		print('processing url: %s' % start_url)
		# open the website, then parse it into a convenient format
		page_source = urllib.urlopen(start_url).read()
		current_page = BeautifulSoup(page_source, "html.parser")
		
		# find all articles on current page and append them to the article list
		articles = current_page.find_all('article')
		article_list += list(articles)

		# get the next page url to continue search.
		# function returns None if there are no pages left (ends while loop)
		start_url = get_next_page_url(current_page)

	return article_list

print("starting article collection...")
article_list = collect_articles('http://leihzeit.de')

number_of_articles = len(article_list)
print('all pages processed: found %s articles' % number_of_articles)

directory = 'articles'

# check if folder exists. If not, create it.
if not os.path.exists(directory):
	os.makedirs(directory)

print('processing articles...')
# we now make one txt file for each article

with codecs.open('TextSammlung.txt', 'w', 'utf-8') as file:
	for article in article_list:

		# prepare file info and helper variables
		article_info = get_info(article)
		filename = article_info['title'] + '.txt'

		# prepare date for inclusion in the files
		article_date = formated_date(article_info['published'])
		
		# prepare list of categories
		categories = ", ".join(article_info['categories'])

		# subtitle is a combination of publishing date and categories
		subtitle = article_date + ' in ' + categories

		file.write(article_info['title']+'\n')
		file.write(subtitle)
		file.write('\n')
		file.write(article_info['content'])
		file.write('\n\n\n')

		with codecs.open(directory+'/'+filename, 'w', 'utf-8') as single_file:
			single_file.write(article_info['title']+'\n')
			single_file.write(subtitle)
			single_file.write('\n')
			single_file.write(article_info['content'])

print('done')