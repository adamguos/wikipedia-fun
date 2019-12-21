from bs4 import BeautifulSoup
import requests
import re
import sys

class ContinueI(Exception):
	pass

continue_i = ContinueI()

pages = []
initial = sys.argv[1]
stub = "https://en.wikipedia.org"

current = initial

def trim_parentheses(para):
	left_paren = [m.start() for m in re.finditer("\(", para)]
	right_paren = [m.start() for m in re.finditer("\)", para)]
	left_angle = [m.start() for m in re.finditer("<", para)]
	right_angle = [m.start() for m in re.finditer(">", para)]

	to_cut = []

	for i in range(len(left_paren)):
		try:
			for j in range(len(left_angle)):
				if left_angle[j] > left_paren[i]:
					if j == 0 or right_angle[j-1] < left_paren[i]:
						to_cut.append([left_paren[i], right_paren[i]])
					raise continue_i
		except ContinueI:
			continue
	
	output = para

	substrs = []
	for i in to_cut:
		substrs.append(output[i[0]:i[1]+1])
	for i in substrs:
		output = output.replace(i, "")
	
	return output

while True:
	page = requests.get(current)
	soup = BeautifulSoup(page.text, "html.parser")

	if soup.h1.text in pages:
		pages.append(soup.h1.text)
		pages.append("Cyclic")
		break

	pages.append(soup.h1.text)

	for table in soup.find_all("table"):
		table.decompose()

	for span in soup.find_all("span"):
		span.decompose()
	
	next_link = ""
	for p in soup.find_all("p", class_=None):
		try:
			p = BeautifulSoup(trim_parentheses(str(p)), "html.parser")
			for a in p.find_all("a"):
				if a.get("href")[:6] == "/wiki/":
					next_link = a.get("href")
					print(next_link)
					raise continue_i
		except ContinueI:
			break

	current = stub + next_link