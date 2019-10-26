# -*- coding: UTF-8 -*-
# dnevnik ru   selenium scrape
from selenium import webdriver
import time   
import requests
import pickle
from bs4 import BeautifulSoup
#import codecs
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re


def send_email_account(body):
    remote_server = "smtp.yandex.ru"
    remote_port = 587
    username = "username"
    password = "password"
    email_from = "email_from"
    email_to = "email_to"
    subject = "Dnevnik.ru Mihas GradeBook"
    # connect to remote mail server and forward message on
    server = smtplib.SMTP(remote_server, remote_port)
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    smtp_sendmail_return = ""
    try:
        server.starttls()
        server.login(username, password)
        smtp_sendmail_return = server.sendmail(email_from, email_to, msg.as_string())
    except Exception:
        print('SMTP Exception:\n' + str( e) + '\n' + str( smtp_sendmail_return))
    finally:
        server.quit()            

def init_driver():
    #chromedriver = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe"   #home
    chromedriver = "C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe"  # work
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("headless")
    driver = webdriver.Chrome(executable_path=chromedriver,options=options)
    return driver

def init_login(login_url, login_email, login_password):
    driver = init_driver()
    driver.get(login_url)
    email = driver.find_element_by_name("login")
    password = driver.find_element_by_name("password")
    email.send_keys(login_email)
    password.send_keys(login_password)
    login = driver.find_element_by_xpath( '//*[@class="login__submit button button_light-green button_top-10 button_full-width"]' )
    login.click()    # нажатие на кнопку отправки
    current_page = driver.current_url
    #time.sleep(5) 
    #all_cookies = driver.get_cookies() # И теперь получим все доступные куки для текущего адреса URL
    #print(all_cookies)
    pickle.dump(driver.get_cookies() , open("C:\\Temp\\cookies.pkl","wb"))  # save cookies  
    #driver.delete_all_cookies()
    all_cookies = driver.get_cookies()
    #print(all_cookies)    
    #driver.get(url_parse)
        #print( driver.current_url)
        #print(driver.page_source)    
    cookies = pickle.load(open("C:\\Temp\\cookies.pkl", "rb")) # read cookies
    for cookie in cookies:
        
        if 'expiry' in cookie:
            del cookie['expiry']
        driver.add_cookie(cookie) 
    return driver
    

def parse_Gradebook(driver):

    body_Gradebook = '' 
    #all_cookies = driver.get_cookies()
    #print(all_cookies)
    #driver.get(current_page)
    gradebook = driver.find_element_by_link_text('Gradebook').click()
    by_quarter = driver.find_element_by_link_text('By quarter').click()
    #second_quarter= driver.find_element_by_link_text('2nd quarter').click()
    #gradebook = browser.find_element_by_link_text('Все оценки по предметам').click()
    
    #current_page = driver.current_url #current page
    html_source = driver.page_source
    #print('current page: ', current_page)
    #print('page_source: ', html_source)    
    #time.sleep(20)
    soup = BeautifulSoup(html_source, 'html.parser')
    trs = soup.find('table', class_="grid gridLines vam marks").find('tbody').find_all('tr')
    #print((trs))
    #print(len(trs))
    for tr in trs:    # table row, search all rows
        tds = tr.find_all('td')
        tds=[x.text.strip() for x in tds] # generate data of row to list
        if tds == []:   # delete empty brakets
            continue
        #print (str(tds[1:2:]).replace('[','').replace(']','').replace('\'','').replace(',','') + ': ' + str(tds[2:3:]).replace('[','').replace(']','').replace('\'','').replace(',',''))        
        txt_gradebook = (str(tds[1:2:]).replace('[','').replace(']','').replace('\'','').replace(',','').ljust(20) + ':   ' + str(tds[2:3:]).replace('[','').replace(']','').replace('\'','').replace(',',''))    
        
        '''
        result = ({'': txt_gradebook,
                }      )
        body_Gradebook += '\n'.join([f'{key} {value}' for key, value in result.items()]) + ('\n'+'---------------------------------------------------------'+'\n')        
        print(body_Gradebook)
        '''
        list_txt = []
        list_txt.append(txt_gradebook)
        list_txt.append('\n'+'----------------------------------------------------------'+'\n')
        body_Gradebook += ''.join(list_txt)    
        #print(body_Gradebook)
        #print(len(tds[10]))    
    send_email_account (body_Gradebook)
    
def parse_Grades_today(driver):
    #current_page = driver.current_url #current page
    #html_source = driver.page_source
    #print('current page: ', current_page)
    #print('page_source: ', html_source) 
    
    html_source = driver.page_source
    
    soup = BeautifulSoup(html_source, 'lxml')
    feed_root= soup.find('div', id="feed-root")
    feed_root2= soup.find('div', id="feed-root").find('div')
    grades_today = feed_root.find('div', class_="_29Z79")#.find_all("a", class_="_2Netl _2TgEf")    #oneday_today = feed_root.find_all('div', class_="_1950o")#.text.split()
    #grades_today = feed_root.find_all('div', class_="")#.find_all("a", class_="_2Netl _2TgEf")    #oneday_today = feed_root.find_all('div', class_="_1950o")#.text.split()
    next_element = feed_root.find_all('div')#, class_="")
    oneday_today = feed_root.find('div', class_="_1950o")
    oneday_today2 = oneday_today.find_next_sibling('div', class_="_1950o")
    result_grades = feed_root.find('div', class_="rIcvr")
    events2 = feed_root2.find('div', class_="_1ZP7y")
    #oneday_today_txt = (' '.join(oneday_today[1:]) + " " +  (' '.join(oneday_today[0:1]))).replace(',','')
    #oneday_today_without_dayweek_txt = (' '.join(oneday_today[1:]))
    #print(oneday_today_txt + '\n')
    #print(oneday_today_without_dayweek_txt)
    
    #print(oneday_today2)
    
    #print(oneday_today2.text)
    
 
    
    data = []
    for header in next_element:
        nextNode = header
        if nextNode == grades_today or nextNode == oneday_today:#is not None:
            print(oneday_today.text)
            
            if nextNode == events2:#is not None:
                #print("\n Tag Found \n")
                break        
        #print(nextNode.find_all("div", {"class": "_1950o"}))
            while True:
                nextNode = nextNode.nextSibling
               # print(nextNode)
                if nextNode is None:
                    break
                if nextNode.name is not None:
                    if nextNode.name == ('hr'):
                        break
                    
                    #if (nextNode.find(class_ == "_1950o")):
                    #if nextNode.div == find_all("div", {"class": "_1950o"}) is not None:
                    if nextNode == events2:#is not None:
                        #print("\n Tag Found \n")
                        break                
                    if nextNode == oneday_today2 :#is not None:
                        #print("\n Tag Found \n")
                        break
                        #print("\n Tag Found \n")
                    if nextNode == result_grades:
                        break
                    #data.append( nextNode.get_text(strip=True))      
                    print (nextNode.get_text(strip=True))
                    #print (nextNode.text)
                    #print(nextNode)
                             
                    #print(nextNode.parent)
                    #print(data)                           
    
    '''
    for header in oneday_today:
        nextNode = header
        while True:
            nextNode = nextNode.nextSibling
            if nextNode is None:
                break
            if nextNode.name is not None:
                if nextNode.name == ('hr'):
                    break
                print(dir(nextNode))
                #print (nextNode.get_text(strip=True))    
    '''
    
 
    '''
    data = []
    
    for div in next_element:
        #print (div)]
        #if '<' in div:
        #if div.find_all(text=("_1950o")):
            
        
        #if ('div class="_1950o"' or 'div class="_29Z79"') in div:
        try:
            oneday_today22 = div.find(class_="_1950o").text
        except:
            oneday_today22 = ''               
        data.append( oneday_today22)  
        try:
            grades_today = div.find(class_="_2TgEf").text
        except:
            grades_today = ''       
        try:
            grades_today_subject = div.find(class_="_31Whp").text
            
        except:
            grades_today_subject = ''
        try:
            grades_today_subject_participation = div.find('div',class_="_2Rj1d").text
        except:
            grades_today_subject_participation = ''
        try:
            grades_today_for_a_lesson_day = div.find(class_="_3-WPZ").text 
        except:
            grades_today_for_a_lesson_day = ''        
        
        #print(div)
            
        grades_today_txt = grades_today_subject.ljust(21) + grades_today.ljust(5) + grades_today_for_a_lesson_day[:grades_today_for_a_lesson_day.find('.')].ljust(16) + grades_today_subject_participation
        data.append( grades_today_txt)  
        #data.extend( grades_today_subject,grades_today,grades_today_for_a_lesson_day)  
        #print(grades_today_txt)                    
        
        
    print(data)
        #print( list(filter(None, grades_today_txt)))
    #mylist = [x for x in data if x is not None]
    #print(mylist)  
    print( list(filter(None, data)))
    '''
    '''
    data = []
    
    for div in next_element:
        #print (div)
        try:
            grades_today = div.find(class_="_2TgEf").text
        except:
            grades_today = ''       
        try:
            grades_today_subject = div.find(class_="_31Whp").text
            
        except:
            grades_today_subject = ''
        try:
            grades_today_subject_participation = div.find('div',class_="_2Rj1d").text
        except:
            grades_today_subject_participation = ''
        try:
            grades_today_for_a_lesson_day = div.find(class_="_3-WPZ").text 
        except:
            grades_today_for_a_lesson_day = ''        
        
            #if (class_='_1950o' or class_='_29Z79') in div:
        grades_today_txt = grades_today_subject.ljust(21) + grades_today.ljust(5) + grades_today_for_a_lesson_day[:grades_today_for_a_lesson_day.find('.')].ljust(16) + grades_today_subject_participation
        data.append( grades_today_txt)  
        #data.extend( grades_today_subject,grades_today,grades_today_for_a_lesson_day)  
        print(grades_today_txt)
    #print(data)
    '''
            
            
    '''
    oneday_today2 = oneday_today.find_next_sibling('div', class_="_1950o")
    oneday_today3 = oneday_today2.find_next_sibling('div', class_="_1950o")
    oneday_today4 = oneday_today3.find_next_sibling('div', class_="_1950o")
    oneday_today5 = oneday_today4.find_next_sibling('div', class_="_1950o")    
    
    next_element2 = next_element.find_next_sibling('div', class_="_1950o")
    #print(next_element2)

   
    #english_descriptions = [e.parent.find_next_sibling() for e in next_element.select(class_="_1950o")]
    #print(english_descriptions)

   
    
    for element in next_element:#.find_next_siblings('div', class_="_1950o"):
        oneday_today_text = element.find('div',{'class':'_1950o'})#.text.strip()
        grades_today_text = element.find('div',{'class':'_29Z79'})#.text.strip()
                
        if grades_today_text is not None:
            
            print("grades_today_text", grades_today_text.text.strip())            
        
        if oneday_today_text is not None:
            print("oneday_today_text", oneday_today_text.text.strip())
        #if oneday_today_text==oneday_today2:
            #break
        n=0
        
        grades_today_next_text = element.find_next_sibling('div', class_="_1950o") 
        if grades_today_next_text is not None:
            print (grades_today_next_text.text.strip())
            '''
   
 
     
     
     
    '''

    for oneday in oneday_today:
        
        oneday_today_date_without_dayweek = oneday.text.split()
        oneday_today_date_without_dayweek_txt = (' '.join(oneday_today_date_without_dayweek[1:]) + " " +  (' '.join(oneday_today_date_without_dayweek[0:1]))).replace(',','')
        #print(oneday_today_txt + '\n')
        print(oneday_today_date_without_dayweek_txt)        
        #print(oneday_today_date)
       '''
    #print(oneday_today2.text)
    #for tag in oneday_today.find_next_siblings('div', class_="_1950o"):
        #if tag == oneday_today4:
            #break        
        
        
    '''
        for grades in grades_today:
            
            print(grades.text)
            
           
    
            try:
                grades_today = grades.find(class_="_2TgEf").text
            except:
                grades_today = ''
            try:
                grades_today_subject = grades.find(class_="_31Whp").text
                
            except:
                grades_today_subject = ''
            try:
                grades_today_subject_participation = grades.find('div',class_="_2Rj1d").text
            except:
                grades_today_subject_participation = ''
            try:
                grades_today_for_a_lesson_day = grades.find(class_="_3-WPZ").text 
            except:
                grades_today_for_a_lesson_day = ''
             
            
            grades_today_txt = grades_today_subject.ljust(21) + grades_today.ljust(5) + grades_today_for_a_lesson_day[:grades_today_for_a_lesson_day.find('.')].ljust(16) + grades_today_subject_participation
            #print(grades_today_txt)       
            
          
        print(tag.text)
            #print(oneday_today5.text)
            #while oneday_today5 !=False:             
            '''



   
def parse_Notice(driver):
    #current_page = driver.current_url #current page
    #print('current page: ', current_page)
    html_source = driver.page_source
    
    soup = BeautifulSoup(html_source, 'lxml')
    oneday_info = soup.find('div', id="feed-root").find('div', class_="_1950o").text.split()
    #wewewewe = popular.find_all('article') # 4
    datetime_notice = (' '.join(oneday_info[1:]) + " " +  (' '.join(oneday_info[0:1]))).replace(',','')
    print(datetime_notice)
    
    
        
       

    
    
    

def main():
    login_url= 'https://login.dnevnik.ru/login/'
    login_email= 'login_email'
    login_password= 'login_password'
    #url_parse= 'https://schools.dnevnik.ru/marks.aspx?school=1000002697333&index=1&tab=period&homebasededucation=False'
    #url_parse = 'https://dnevnik.ru/feed'
    r = requests.get(login_url)
    #print (r.status_code    ) 
    if r.status_code != 200:
        raise requests.HTTPError(r.text)
        
    selen_examplar = init_login(login_url, login_email, login_password)
    
    #parse_Gradebook (selen_examplar)
    parse_Grades_today (selen_examplar)
    #parse_Notice(selen_examplar)
    
    selen_examplar.quit()
 
if __name__ == '__main__':
    main()
 


    
        
        
        
        
    
    '''
    def parse_fist_list_user(driver, url):
    
        url_list_users = []
        driver.get(url)
        # Обход проверки браузера
        time.sleep(5)
    
        # Получаем блок навигации
        div_PageNav = driver.find_element_by_class_name('PageNav')
    
        #Получаем количество страниц
        count_page = int(div_PageNav.get_attribute('data-last'))
        #Заполняем список url страниц с пользователями
        for i in range(1,count_page):
            url_list_users.append(url_main+'&page='+str(i))
            print(url+'&page='+str(i))
        return url_list_users
    
    
    def parse_list_users(driver,urls):
        users_url = []
        #Переход по очереди
        for url in urls:
    
            driver.get(url)
            print('Страница:', url)
    
            users = driver.find_elements_by_css_selector('li.memberListItem')
            for user in users:
                users_url.append(user.find_element_by_tag_name('a').get_attribute('href'))
    
        return users_url
    '''
