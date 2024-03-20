#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#:IMPORT MODULAS:
import streamlit as st
import easyocr
import io
from io import BytesIO
from streamlit_option_menu import option_menu
import psycopg2
import pandas as pd
import re
from PIL import Image
import numpy as np
import os
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#:SQL CONNECTION:

mydb=psycopg2.connect(host='localhost',user='postgres',password='password',database='bizzacard',port=5432)
cursor=mydb.cursor()

create='''create table if not exists bs(name varchar(100),
                                        designation varchar(100),
                                        company_name varchar(100),
                                        contact varchar(100),
                                        alternative varchar(100),
                                        email varchar(100),
                                        website varchar(100),
                                        street varchar(100),
                                        city varchar(100),
                                        state varchar(100),
                                        pincode varchar(100),
                                        image_byt bytea)'''
cursor.execute(create)
mydb.commit()
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#:Data extraction:
def upload_image(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    details =[]
    for i in range(len(result)):
        details.append(result[i][1])
    name = []
    designation = []
    contact =[]
    email =[]
    website = []
    street =[]
    city =[]
    state =[]
    pincode=[]
    company =[]
    
    for i in range(len(details)):
        match1 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+). ([a-zA-Z]+)',details[i])    
        match2 = re.findall('([0-9]+ [A-Z]+ [A-Za-z]+)., ([a-zA-Z]+)', details[i])
        match3 = re.findall('^[E].+[a-z]',details[i])
        match4 = re.findall('([A-Za-z]+) ([0-9]+)',details[i])
        match5 = re.findall('([0-9]+ [a-zA-z]+)',details[i])    
        match6 = re.findall('.com$' , details[i])
        match7 = re.findall('([0-9]+)',details[i])
        if details[i] == details[0]:
            name.append(details[i])        
        elif details[i] == details[1]:
            designation.append(details[i])
        elif '-' in details[i]:
            contact.append(details[i])
        elif '@' in details[i]:
            email.append(details[i])
        elif "www " in details[i].lower() or "www." in details[i].lower():
            website.append(details[i])
        elif "WWW" in details[i]:
            website.append(details[i] +"." + details[i+1])
        elif match6:
            pass
        elif match1:
            street.append(match1[0][0])
            city.append(match1[0][1])
            state.append(match1[0][2])
        elif match2:
            street.append(match2[0][0])
            city.append(match2[0][1])
        elif match3:
            city.append(match3[0])
        elif match4:
            state.append(match4[0][0])
            pincode.append(match4[0][1])
        elif match5:
            street.append(match5[0]+' St,')
        elif match7:
            pincode.append(match7[0])
        else:
            company.append(details[i])
    if len(company)>1:
        comp = company[0]+' '+company[1]
        print(comp)
    else:
        comp = company[0]
    if len(contact) >1:
        contact_number = contact[0]
        alternative_number = contact[1]
    else:
        contact_number = contact[0]
        alternative_number = None
        
    
    image_details = {'name':name[0],'designation':designation[0],'company_name':comp,
                     'contact':contact_number,'alternative':alternative_number,'email':email[0],
                     'website':website[0],'street':street[0],'city':city[0],'state':state[0],
                     'pincode':pincode[0]}
        
    return image_details
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#:PAGE STEPUP:

st.set_page_config(page_title="BUSIESS CARD EXTRACTION",
                   layout="wide",
                   page_icon="🧊",
                   initial_sidebar_state='auto'
                   )

if st.session_state.get('switch_button', False):
    st.session_state['menu_option'] = (st.session_state.get('menu_option',0) + 1) % 3
    manual_select = st.session_state['menu_option']
else:
    manual_select = None

with st.sidebar:    
    selected = option_menu("Main menu", ["Home", "Upload", 'About'], 
        icons=['house', 'cloud-upload', 'gear'], 
        manual_select=manual_select, key='menu_4')
st.button(f":red[Switch Tab] {st.session_state.get('menu_option',1)}", key='switch_button')
selected
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#:IMAGE READER/EDIT:
if selected=="Upload":
    #GET IMAGE FROM USER
    st.caption(":red[Upload the Business card]")
    bz_cd=st.file_uploader("Upload",label_visibility="collapsed",type=["png","jpg"],accept_multiple_files=False,help="Only .png & .jpg are allowed")
    #Process the image to df
    if bz_cd != None:
        image_path = os.getcwd()+ "\\"+"bizz"+"\\"+ bz_cd.name
        get_img = Image.open(bz_cd)
        st.image(get_img,width=300,caption="Uploaded Business card")
        df=upload_image(image_path)
        im_df=pd.DataFrame(df,index=np.arange(1))
        st.dataframe(im_df)

        #Image to bytes
        im_by= io.BytesIO()
        get_img.save(im_by,format="png")
        im_data=im_by.getvalue()

        dict1={"Image":[im_data]}
        im_df1=pd.DataFrame(dict1)
        Image_df=pd.concat([im_df,im_df1],axis=1)

        #Store the DF to Database
        create=st.button(":red[CREATE TABLE]")
        if create:
            with st.spinner("Kindly wait for few mins"):
                insert='''insert into bs(name,
                                        designation,
                                        company_name,
                                        contact,
                                        alternative,
                                        email,
                                        website,
                                        street,
                                        city,
                                        state,
                                        pincode,
                                        image_byt)
                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                for index,row in Image_df.iterrows():
                    values=(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11])
                    cursor.execute(insert,values)
                    mydb.commit()
                st.success("Successfully Uploaded")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#:Update/Delete:        
        selected1 = option_menu(
            menu_title="MANAGE DATA",
            options=["UPDATE", "DELETE"],
            icons=["database-add", "database-dash"],
            menu_icon="database-gear",
            default_index=0,
            orientation="horizontal")
        
        if selected1 =="UPDATE":
            cl1,cl2=st.columns(2)
            with cl1:
                edit_name=st.text_input("Name",df['name'])
                edit_des=st.text_input("Designation",df['designation'])
                edit_co=st.text_input("Company",df['company_name'])
                edit_cont=st.text_input("Contact",df['contact'])
                edit_alt=st.text_input("Alternative",df['alternative'])
                edit_em=st.text_input("Email",df['email'])
                im_df['name'],im_df['designation'],im_df['company_name'],im_df['contact'],im_df['alternative'],im_df['email']=edit_name,edit_des,edit_co,edit_cont,edit_alt,edit_em

            with cl2:
                edit_wb=st.text_input("Website",df["website"])
                edit_st=st.text_input("Street",df['street'])
                edit_ct=st.text_input("City",df['city'])
                edit_ste=st.text_input("State",df['state'])
                edit_pn=st.text_input("Pincode",df['pincode'])
                im_df['website'],im_df['street'],im_df['city'],im_df['state'],im_df['pincode']=edit_wb,edit_st,edit_ct,edit_ste,edit_pn

            update=st.button("Update")
            if update:
                st.spinner("Loading")

                qr='''update bs set name = %s,designation = %s,company_name = %s,contact = %s,alternative = %s,
                        email = %s,website = %s,street = %s,city = %s,state = %s,pincode = %s where name = %s '''
                values=(edit_name,edit_des,edit_co,edit_cont,edit_alt,edit_em,edit_wb,edit_st,edit_ct,edit_ste,edit_pn,edit_name)
                cursor.execute(qr,values)
                mydb.commit()
                mode={}
                mode=im_df.copy()
                nw_df=pd.DataFrame(mode,index=np.arange(1))
                st.dataframe(nw_df)
                st.success("Successfull updated")

        if selected1 == "DELETE":
            list=cursor.execute("select name from bs")
            all_list=cursor.fetchall()
            name=["select name"]
            for i in all_list:
                if i not in name:
                    name.append(i[0])
            select_name=st.selectbox("Select Details",options=name)
            delete=st.button("DELETE DATA")
            if select_name and delete:
                st.spinner("Loanding")
                del_Qr= f"delete from bs where name='{select_name}'"
                cursor.execute(del_Qr)
                mydb.commit()
                st.success("Deleted")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#:HOME:
if selected=="Home":
    st.subheader(":red[BUSINESS CARD TEXT EXTRACTION USING EASYOCR]")
    st.subheader(":gray[IMPORTANCE OF OCR]")

    st.write('''Text detection in images is an important technology for a variety of applications, including text processing, image search, and machine translation. 
             Advances in optical character recognition (OCR) technology have made document retrieval more accurate and efficient, allowing businesses and organizations to quickly extract useful information from images. 
             This article introduces EasyOCR, a powerful and easy-to-use OCR library that can find and extract text from a variety of formats. 
             Let's look at the features of EasyOCR, its advantages over other OCR libraries, and how it can be implemented in a real-world application.''')
    
    st.subheader(":gray[EASYOCR]")

    st.write('''Jaided AI was founded in 2020. Our goal is to distribute the benefits of AI to the world. The first project is an open source OCR library called EasyOCR. We build software with the philosophy that it has to be very easy to use while providing state-of-the-art performance. 
             This is to maximize AI accessiblity for everyone to be ready for the upcoming AI revolution.
             After the success of our open source project, we launched our professional service to organizations. This is the Enterprise version of EasyOCR. 
             Here we aim to help organizations around the world implementing AI technology according to their own need.''')
    
    image=("C:/Users/phoor/Downloads/easyocr_framework.jpeg")
    ey_image=Image.open(image)
    st.image(ey_image,caption="EASYOCR FRAMEWORK")
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    