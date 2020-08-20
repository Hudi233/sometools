import requests
import datetime
import json
import calendar
import re
import pymysql

YEAR = str(datetime.datetime.now().year)
TODAY = datetime.datetime.now().strftime('%Y-%m-%d')
MONTH_IN_SHORT_EN = calendar.month_abbr[datetime.datetime.now().month]
THIS_MONTH_ID = YEAR + "-" + MONTH_IN_SHORT_EN

base_url = "https://api.msrc.microsoft.com/"
#windows api key
api_key = ""

def get_csrf_json():
	db = pymysql.connect("localhost","admin","xxxx","win_patch_manage")
	cur = db.cursor()
	url = "{}cvrf/{}?api-Version={}".format(base_url, THIS_MONTH_ID, YEAR)
	headers = {'api-key': api_key, 'Accept': 'application/json'}
	response = requests.get(url, headers = headers)
	data = json.loads(response.content)

	for each_product in data["ProductTree"]["FullProductName"]:
		productid = each_product['ProductID']
		product_name = each_product['Value']

		search_productid_sql = "SELECT * FROM win_product_name WHERE product_id='" + str(productid) + "'"
		cur.execute(search_productid_sql)

		if cur.rowcount > 0:
			pass
		else:
			insert_product_sql = "INSERT INTO win_product_name (product_id,product_name,dt) VALUES('" + str(productid) + "','" + str(product_name) + "','" + TODAY + "')"
			cur.execute(insert_product_sql)
			db.commit()

	for each_cve in data["Vulnerability"]:
		cve = each_cve["CVE"]
		if re.search('ADV',cve):
			pass
		else:
			cve = each_cve["CVE"]
			kblist = []
			scorelist = []
			product_id_list = str(each_cve["ProductStatuses"][0]["ProductID"]).replace("'","")
			product_id_list = product_id_list.replace("[","")
			product_id_list = product_id_list.replace("]","")
			product_id_list = product_id_list.replace(" ","")

			for each_kb in each_cve["Remediations"]:
				try:
					kb_num = each_kb["Description"]["Value"]
					if re.search('Click to Run',kb_num) or re.search('Release Notes',kb_num):
						pass
					else:
						kblist.append('KB{}'.format(kb_num))
				except Exception as e:
					print("kb",e)
			kblist=list(set(kblist))
			kblist=str(kblist).replace("'","")
			kblist=kblist.replace("[","")
			kblist=kblist.replace("]","")
			kblist=kblist.replace(" ","")

			for each_score in each_cve["CVSSScoreSets"]:
				try:
					scorelist.append(each_score["BaseScore"])
				except Exception as e:
					print("score",e)

			try:
				score_mean = format(sum(scorelist)/len(scorelist),'.1f')
			except Exception as e:
				print("score_mean",e)
				score_mean = 0

			insert_cve_sql = "INSERT INTO win_cve_db (cve,score,product_id_list,kb_list,cvrf_id,dt) VALUES(\"" + str(cve) + "\",\"" + str(score_mean) + "\",\"" + str(product_id_list) + "\",\"" + str(kblist) + "\",\"" + str(THIS_MONTH_ID) + "\",\"" + TODAY + "\")"
			print(insert_cve_sql)
			cur.execute(insert_cve_sql)
			db.commit()

	db.close()

if __name__ == '__main__':
	get_csrf_json()
