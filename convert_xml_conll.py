from bs4 import BeautifulSoup

import os, fnmatch
def convertCONLL(directory):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, "*.xml"):
            filepath = os.path.join(path, filename)
            outputpath = os.path.join(path, filename.replace(".xml", ".conll"))
            
            with open(filepath) as f:
                output = ""
                s = f.read()
                bs = BeautifulSoup(s.decode('utf-8', 'ignore'), "xml")
                mydic = {}
                for q in bs.findAll("ne"):
                    namedentities = ""
                    if q["type"]:
                        for p in q.findAll("tok"):
                            namedentities += p["form0"].replace("+", "")
                        if namedentities:
                            mydic[namedentities] = q["type"]
                   
                for q in bs.findAll("word"):
                    morph = ""
                    word = q.find("tokenized", {"scheme" : "ATB4MT"}).find("tok")["form1"]
                    if word in mydic.keys():
                        ner = mydic[word]
                    else:
                        ner = "O"
                    morph += q["id"] + "\t" + q["word"] + "\t" + q.find("tokenized", {"scheme" : "ATB4MT"}).find("tok")["form1"] + "\t" + q.find("tokenized", {"scheme" : "ATB4MT"}).find("tok")["form4"] + "\t" + ner +"\t_\t_"
                    output += "\n" + morph
                with open(outputpath, "w") as g:
                    g.write(output.encode('utf-8'))
               
                


convertCONLL("d:/phd/test")
