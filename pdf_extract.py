import pdfplumber

if False:
    with pdfplumber.open("nv.pdf") as pdf:
        first_page = pdf.pages[6].find_tables()
        t1_content = first_page[0].extract(x_tolerance = 5)
        t2_content = first_page[1].extract(x_tolerance = 5)
        print(t1_content, '\n' ,t2_content)
        exit()

with pdfplumber.open(r'nv.pdf') as pdf:
    for no in [ 5, 6, 7,8,9,10,11,12,13,14,15,16]:
    #for no in [ 7,8]:
        #my_page = pdf.pages[no]
        #print(my_page.extract_text())
        #print(my_page.extract_table())
        #myTable=my_page.extract_table()
        my_page=pdf.pages[no].find_tables()
        #TODO, handle up to two tables in a page
        myTable=[]
        if len(my_page)>0:
            t1_content = my_page[0].extract(x_tolerance = 5)
            myTable=t1_content
        if len(my_page)>1:
            t2_content = my_page[1].extract(x_tolerance = 5)
            myTable=myTable+t2_content
        for row in myTable:
            id_str=row[0].replace('\n', '') if len(row) > 1 and row[0] is not None else ""
            fields=[id_str]
            if id_str.startswith("SBIOS"):
                for item in row[1:]:
                    truncated_item_str=item.replace('\n', ' ')[:40] if item is not None else False
                    fields.append(truncated_item_str) if item is not None else False

                print(f"page={no}, {fields[0]}, {fields[1]}, {fields[2]}")
                #spec_str=row[3].replace('\n', ' ') if len(row) > 6 and row[3] is not None else ""
                #description_str=row[6].replace('\n', ' ') if len(row) > 6 and row[6] is not None else ""
                #print(f"page={no}, {id_str}, {spec_str}, {description_str}, {row}")
        #im =my_page.to_image(resolution=150)
        #im.draw_rect(my_page.extract_words(), stroke_width=1)
        #im.save('a.png', format="PNG", quantize=True, colors=256, bits=8)
        #im.show()

