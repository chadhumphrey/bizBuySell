import re
import time
import webbrowser
import bbsLibrary as bbsl
import sys
from sys import argv


# script, extra = argv
# Arguements
if len(sys.argv) > 1:
    script, extra = argv
else:
    extra = 'meh'
    # input("showExtra is what you are looking for..." )
import sys

sys.path.append('/home/ubuntu/code/local_utilities/db_connections/')
import db_connector as db_conn

# clear the system 
q = """
/*select * from listingsBizBuySell where id = 1074;*/
select * from listingsBizBuySell ;
"""
db_conn.load_query(q,args=None,LineNumber=27,printOutPut=False,DB="SAM")

specific_words = {"Government": 3,
                  "government": 3,
                  "military": 3,
                  "FED": 3,
                  "GOV": 3,
                  "Defense & Intelligence":3,
                  "Veteran":3,
                  "environmental consulting":3,
                  "franchise": -11,
                  "drupal":-11}

 
result_set = db_conn.results_query(q,None,98,False,"SAM")
for row in result_set:
    word_counts = bbsl.count_specific_words(row['description'], specific_words)
    total_score = sum(word_counts.values())
    
    # Store word counts for each row in a variable
    word_counts_output = ""
    for word, count in word_counts.items():
        word_counts_output += f"{word}: {count}\n"
        
    # total_score += bbsl.getBadTitlePattern(row['title'])
    # total_score += bbsl.getLameCompanies(row['company'])
    print(total_score)
                
    q = 'update listingsBizBuySell set score = %s where id = %s '
    args = [total_score,row['id']]
    db_conn.load_query(q,args,LineNumber=59,printOutPut=True,DB="SAM")    

q="""
select * from listingsBizBuySell where score > 0 
"""

# result_set = db_conn.results_query(q,None,98,True,"SAM")
# bbsl.printData(result_set,True,None,'deals.txt')
sys.exit('barfed65')
fileName = "deals.txt"
file_path = "/home/ubuntu/code/bizBuySell/" + fileName
firefox_path = "/usr/bin/firefox"
bbsl.open_urls_from_file(file_path, firefox_path)



    