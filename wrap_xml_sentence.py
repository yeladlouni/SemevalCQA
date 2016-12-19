import os, fnmatch
def findReplace(directory):
    templatepath = os.path.join(directory, "mytemplate.xml")
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, "*.txt"):
            filepath = os.path.join(path, filename)
            outputpath = os.path.join(path, filename.replace(".txt", ".xml"))
            
            with open(filepath) as f:
                s = f.read()
                with open(templatepath) as g:
                    t = g.read()
                    u = t.replace('<in_seg id="SENT1"></in_seg>', '<in_seg id="SENT1">'+s+'</in_seg>')
            with open(outputpath, "w") as f:
                f.write(u)


findReplace("d:/phd/test")

                
