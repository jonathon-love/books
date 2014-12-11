
PANDOC_CMD = "/usr/local/bin/pandoc -f markdown -t epub3 -S --toc-depth=1 -o $dest --epub-stylesheet=$stylesheet $src"
KINDLE_CMD = "/usr/local/bin/kindlegen $src"

STYLESHEET = "templates/epub.css"

import os.path as path
import os
import yaml
import json

location = path.dirname(path.abspath(__file__))

template_loc = path.join(location, STYLESHEET).replace(" ", "\\ ")
pandoc_cmd = PANDOC_CMD.replace("$stylesheet", template_loc)

source_location = path.join(location, "src-books")
output_location = path.join(location, "src-www")

def requires_build(input, output):

	if path.exists(output) == False:
		return True;

	source_time = path.getmtime(input)
	binary_time = path.getmtime(output)
	
	return source_time > binary_time

def compile_epub(input, output):

	escaped_input  = input.replace(" ", "\\ ")
	escaped_output = output.replace(" ", "\\ ")
	
	output_dir = path.dirname(output)
	if path.exists(output_dir) == False:
		os.makedirs(output_dir)
	
	exe = pandoc_cmd.replace("$src", escaped_input).replace("$dest", escaped_output)
	print("building: " + path.basename(output))
	os.system(exe)
	
def compile_mobi(input, output):

	escaped_input  = input.replace(" ", "\\ ")
	escaped_output = output.replace(" ", "\\ ")
	
	output_dir = path.dirname(output)
	if path.exists(output_dir) == False:
		os.makedirs(output_dir)
	
	exe = KINDLE_CMD.replace("$src", escaped_input).replace("$dest", escaped_output)
	print("building: " + path.basename(output))
	os.system(exe)

some_where_built = False
book_info = [ ]

for dirname, dirnames, filenames in os.walk(source_location):

    for filename in filenames:
    
		if (filename.endswith(".md")):
		
			filepath = os.path.join(dirname, filename)
			relpath = path.relpath(filepath, source_location)
			epubpath = path.join(output_location, relpath[:-3] + ".epub")
			mobipath = path.join(output_location, relpath[:-3] + ".mobi")
			
			if requires_build(filepath, epubpath):

				compile_epub(filepath, epubpath)
				some_where_built = True
				
			if requires_build(epubpath, mobipath):

				compile_mobi(epubpath, mobipath)
				some_where_built = True
				
			file = open(filepath, "r")
			loader = yaml.Loader(file)
			data = loader.get_data()

			data["paths"] = { "epub" : relpath[:-3] + ".epub", "mobi" : relpath[:-3] + ".mobi" }

			book_info.append(data)
			file.close()

if some_where_built:

	book_info_file = open("src-www/_data/books.json", "w")
	book_info_file.write(json.dumps(book_info, indent=4))
	book_info_file.close()
	
else:

	print("Nothing to do. All destination files are up to date.")
	
	