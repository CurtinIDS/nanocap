import os, shutil
#os.system("plastex -d {} Doc.tex ".format(os.getcwd()+"/docs"))
#os.system("plastex --renderer=XHTML --theme=python -d {} Doc.tex ".format(os.getcwd()+"/docs"))
#os.system("plastex --renderer=XHTML --theme=plain -d {} Doc.tex ".format(os.getcwd()+"/docs"))
os.system("plastex --config=config.plastex -d {} Doc.tex ".format(os.getcwd()+"/docs"))
try:
	os.makedirs("docs/styles")
except:pass
#shutil.copy("temp.css","docs/styles/style.css")
