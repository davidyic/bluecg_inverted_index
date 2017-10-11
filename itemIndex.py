import http.cookiejar as cookielib
from urllib.request import Request, urlopen 
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from bs4 import ResultSet
from bs4 import CData
import inspect
import unicodedata
import threading
import time

class crawlerThread (threading.Thread):
	def __init__(self, accountName):
		threading.Thread.__init__(self)
		self.accountName = accountName
	def run(self):
		# print("Start fetching account " + self.accountName)
		self.itemPageURL = "http://www.bluecg.net/plugin.php?id=gift:guanli&zhanghao=" + self.accountName
		characters = []
		with urllib.request.urlopen(self.itemPageURL) as accountInfo:
			self.accountPage = accountInfo.read().decode("big5", "strict").encode("utf8", "strict")
			self.accountSoup = BeautifulSoup(self.accountPage, 'html.parser')
			self.petTables = self.accountSoup.find_all("table", attrs={'id':'ddd'})
			self.petList = []
			for petTable in self.petTables:
				newPet = {}
				rows = petTable.find_all('tr')
				petType = rows[0].find_all('td')[1].find('b').string
				petName = str(rows[1].find('td').string)[6:]
				petLevel = rows[2].find('b').string
				newPet['name'] = petName
				newPet['type'] = petType
				newPet['level'] = petLevel
				self.petList.append(newPet)
				
			if len(self.petList)> 0:
				petLock.acquire()
				petMap[self.accountName] = self.petList
				petLock.release()

			self.items = self.accountSoup.find_all('span', attrs={"id": "ziduan"})
			itemLock.acquire()
			# print("Item Lock acquired for account: " + self.accountName)
			add_item_to_map(self.items, itemMap, self.accountName)
			itemLock.release()
			# print("Item Lock released from account: " + self.accountName)
			
		self.bbsStorageUrlTop = "http://www.bluecg.net/plugin.php?id=gift:beibao&zhanghao=" + self.accountName + "&juexu=2&infloat=yes&handlekey=fh&inajax=1&ajaxtarget=fwin_content_fh"
		with urllib.request.urlopen(self.bbsStorageUrlTop) as bbsStorageInfo:
			self.bbsStoragePage = bbsStorageInfo.read().decode("big5", "strict").encode("utf8", "strict")
			self.bbsStorageSoup = BeautifulSoup(self.bbsStoragePage, 'html.parser')
			self.cd = self.bbsStorageSoup.find_all(text = True)[2]
			self.cdSoup = BeautifulSoup(self.cd, 'html.parser')
			self.items = self.cdSoup.find_all('span', attrs={"id": "ziduan"})
			itemLock.acquire()
			# print("Item Lock acquired for account: " + self.accountName)
			add_item_to_map(self.items, itemMap, self.accountName)
			itemLock.release()
			# print("Item Lock released from account: " + self.accountName)
			
		bbsStorageUrlBot = "http://www.bluecg.net/plugin.php?id=gift:beibao&zhanghao=" + self.accountName + "&juexu=3&infloat=yes&handlekey=fh&inajax=1&ajaxtarget=fwin_content_fh"
		with urllib.request.urlopen(bbsStorageUrlBot) as bbsStorageInfo:
			self.bbsStoragePage = bbsStorageInfo.read().decode("big5", "strict").encode("utf8", "strict")
			self.bbsStorageSoup = BeautifulSoup(self.bbsStoragePage, 'html.parser')
			self.cd = self.bbsStorageSoup.find_all(text = True)[2]
			self.cdSoup = BeautifulSoup(self.cd, 'html.parser')
			self.items = self.cdSoup.find_all('span', attrs={"id": "ziduan"})
			itemLock.acquire()
			# print("Item Lock acquired for account: " + self.accountName)
			add_item_to_map(self.items, itemMap, self.accountName)
			itemLock.release()
			# print("Item Lock released from account: " + self.accountName)

def wide_chars(s):
	return sum(unicodedata.east_asian_width(x)=='W' for x in s)

def add_item_to_map(items, itemMap, accountName):
	for item in items:
		count = 1
		itemName = item.string.replace(" ", "")
		indexRight = str(item.string).find("個")
		indexLeft = str(item.string).rfind("(", 0, indexRight)
		if indexLeft > -1 and indexRight > -1:
			count = int(str(item.string)[indexLeft+1:indexRight-1])
			itemName = str(item.string)[:indexLeft-1]
		if itemName not in itemMap:
			itemMap[itemName] = {}
		if accountName in itemMap[itemName]:
			itemMap[itemName][accountName] += count
		else:
			itemMap[itemName][accountName] = count

startTime = time.time()
loginCredentials = [{'account':'foo1', 'password':'bar1'}, {'account':'foo2', 'password':'bar2'}]

itemMap = {}
petMap = {}

itemLock = threading.Lock()
petLock = threading.Lock()

for loginCredential in loginCredentials:
	threads = []
	loginUrl = "http://www.bluecg.net/member.php?mod=logging&action=login&referer=&infloat=yes&handlekey=login&inajax=1&ajaxtarget=fwin_content_login"
	req = Request(loginUrl, headers={'User-Agent': 'Chrome/3.0'})
	loginPage = urlopen(req).read()
	start = str(loginPage).find("name=\"formhash\" value=\"") + len("name=\"formhash\" value=\"")
	formhash = str(loginPage)[start:start + 8]
	# print(formhash)

	loginHashStart = str(loginPage).find("member.php?mod=logging&amp;action=login&amp;loginsubmit=yes&amp;handlekey=login&amp;loginhash=") + len("member.php?mod=logging&amp;action=login&amp;loginsubmit=yes&amp;handlekey=login&amp;loginhash=")
	# print(loginHashStart)
	loginHash = str(loginPage)[loginHashStart : loginHashStart + 5]
	# print(loginHash)


	cj = cookielib.CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

	opener.addheaders = [('User-Agent', 'Chrome/3.0')]
	urllib.request.install_opener(opener)


	authentication_url = "http://www.bluecg.net/member.php?mod=logging&action=login&loginsubmit=yes&handlekey=login&loginhash="+loginHash+"&inajax=1"
	# print(authentication_url)
	payload = {
		'formhash': formhash,
		'referer': 'http://www.bluecg.net/forum.php',
		'username': loginCredential['account'],
		'password': loginCredential['password'],
	}

	# Use urllib to encode the payload
	data = urllib.parse.urlencode(payload)
	binary_data = data.encode('UTF-8')

	# Make the request and read the response
	resp = urllib.request.urlopen(authentication_url, binary_data)
	loginResult = resp.read()

	accountManageURL = "http://www.bluecg.net/plugin.php?id=gift:guanli"
	accountIDs = []
	with urllib.request.urlopen(accountManageURL) as response:
		html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	unorderLists = soup.find_all('ul')
	if(len(unorderLists) > 0):
		accountList = unorderLists[len(unorderLists)-1]
		accounts = accountList.find_all('li')
		for account in accounts:
			accountIDs.append(account.find("a").get("href")[35:])

	for accountName in accountIDs:
		# print(accountName)
		newThread = crawlerThread(accountName)
		threads.append(newThread)
		newThread.start()
	
	for t in threads:
		t.join()



itemFile = open('full_inverted_index_multi.txt', 'wb')
for key in sorted(itemMap.keys()):
	itemFile.write((key + " : ").encode('utf8'))
	for idKey in sorted(itemMap[key].keys()):
		itemFile.write((idKey + ":" + str(itemMap[key][idKey]) + "   ").encode('utf8'))
	itemFile.write(("\n").encode('utf8'))
itemFile.close()

petFile = open('pet_list_multi.txt', 'wb')
for account in petMap:
	petFile.write(("*************\n").encode('utf8'))
	petFile.write((account + "\n").encode('utf8'))
	petFile.write(("*************\n").encode('utf8'))
	for pet in petMap[account]:
		petFile.write(("%s%*s%*s\n" % ( pet["name"], 20-wide_chars(pet["name"])-len(pet["name"]) + len(pet["type"]), pet["type"], 24-wide_chars(pet["type"])-len(pet["type"]), pet["level"])).encode('utf8'))
petFile.close()
		
print(time.time() - startTime)

print(time.ctime())

