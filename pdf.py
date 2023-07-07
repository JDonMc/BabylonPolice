import PyPDF2
import os
#create file object variable
#opening method will be rb
from pikepdf import Pdf

def fix_file(filename, input_base_dir):
    file_basename = filename[:-4]
    original_input_file_path = path.join(input_base_dir, filename)
    tmp_output_file_path = path.join(
        input_base_dir, file_basename+".pdf.tmp"
    )
    final_input_file_path = path.join(
        input_base_dir, file_basename+".pdf.old"
    )

    pdf = Pdf.open(original_input_file_path)
    new_pdf = Pdf.new()
    for page_obj in pdf.pages:
        new_pdf.pages.append(page_obj)
    new_pdf.save(tmp_output_file_path)

    rename(original_input_file_path, final_input_file_path)
    rename(tmp_output_file_path, original_input_file_path)
    print(f"Fixed {filename}")

for (root,dirs,files) in os.walk('.', topdown=True):
	print(root)
	print(dirs)
	print(files)
	for file in files:
		if file != 'pdf.py':
			fix_file(file, '/Users/adenhandasyde/Dropbox/pdfs/')
			pdffileobj=open('/Users/adenhandasyde/Dropbox/pdfs/'+file,'rb')

			#create reader variable that will read the pdffileobj
			pdfreader=PyPDF2.PdfReader(pdffileobj, strict=False)
			 
			#This will store the number of pages of this pdf file
			x=len(pdfreader.pages)
			 
			#create a variable that will select the selected number of pages
			pageobj=pdfreader.pages[x-1]
			 
			#(x+1) because python indentation starts with 0.
			#create text variable which will store all text datafrom pdf file
			text=pageobj.extract_text()
			 
			#save the extracted data from pdf to a txt file
			#we will use file handling here
			#dont forget to put r before you put the file path
			#go to the file location copy the path by right clicking on the file
			#click properties and copy the location path and paste it here.
			#put "\\your_txtfilename"
			file1=open("/Users/adenhandasyde/Dropbox/pdf/"+file+".txt","w+")
			file1.writelines(text)

def reset_eof_of_pdf_return_stream(pdf_stream_in:list):
    # find the line position of the EOF
    for i, x in enumerate(txt[::-1]):
        if b'%%EOF' in x:
            actual_line = len(pdf_stream_in)-i
            print(f'EOF found at line position {-i} = actual {actual_line}, with value {x}')
            break

    # return the list up to that point
    return pdf_stream_in[:actual_line]

# opens the file for reading
