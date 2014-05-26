import sys,glob,os,shutil

unwanted = ['lg','4ct','xref','dvi','aux','4tc','log','tmp','idv']
tex_files = sys.argv[1:]
print tex_files
for tex in tex_files:
	if tex[0]=="-":continue
	os.system("htlatex {}".format(tex)) 
	base,ext = os.path.splitext(tex)
	for uext in unwanted: os.remove(base+"."+uext)

if "-index" in tex_files:
	f = open("index.html","w")
	f.write("<html><body>\n")
	f.write("<h1> {} </h1>\n".format("Contents:"))
	for tex in tex_files:
		if tex[0]=="-":continue
		base,ext = os.path.splitext(tex)
		f.write(r'<br><a href="{}">{}</a>'.format(base+".html",base))
		f.write('\n')
	f.write(r'</body></html>'+'\n')
	f.close()
