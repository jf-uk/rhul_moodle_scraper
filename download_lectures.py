# Imports
import getpass
import re
import requests
from bs4 import BeautifulSoup
import time
from robobrowser import RoboBrowser
from pick import pick

# Constants

def main_download():

    print('This script will download your lecture recordings from moodle.')

    url = 'https://moodle.royalholloway.ac.uk/'
    username = raw_input('Enter your moodle username: ')
    password = getpass.getpass('Enter your moodle password: ')

    browser = RoboBrowser(parser='html.parser')
    browser.open(url)

    if(browser.find('h1').string != 'E-Learning skills development sessions'):
        print('Error: Could not connect to moodle.')
        return;

    print('Connecting to moodle...')

    # Login Page
    login_form = browser.get_form(class_='navbar-form')
    login_form['username'].value = username 
    login_form['password'].value = password
    browser.submit_form(login_form)

    time.sleep(1)

    # Homepage
    courses_link = browser.find(class_='navbar-inner').find(string='My courses').find_parent()
    browser.follow_link(courses_link)

    if(browser.find('h2').string != 'Course overview'):
        print('Error: Login failed, please check your login details.')
        return;

    print('Successfully logged in to moodle...')

    time.sleep(1)

    # Courses Page
    courses_list = browser.find_all(class_='course_title')
    pick_course_names = []
    for course in courses_list:
        pick_course_names.append(course.find('a').string)

    pick_course_names.append('--Download all of them--')

    pick_title = 'Please select which course you wish to download the videos for: '
    pick_option, pick_index = pick(pick_course_names, pick_title)

    if(pick_option == '--Download all of them--'):
        return;
    else:
        browser.follow_link(browser.find(title=pick_course_names[pick_index]))

    print('Loading page: ' + browser.find('h3').string)

    # Panopto call
    panopto_url = 'https://moodle.royalholloway.ac.uk/blocks/panopto/panopto_content.php'
    course_id = browser.find(id='block_panopto_content')['courseid']
    get_sesskey = browser.find(href=re.compile("sesskey=")).get('href').split('sesskey=')
    sesskey = get_sesskey[1]
    moodle_session = browser.session.cookies['MoodleSession']

    cookies = dict([('MoodleSession', moodle_session)])
    post_data = dict([('sesskey', sesskey), ('courseid', course_id)])

    panopto_request = requests.post(panopto_url, data=post_data, cookies=cookies)

    if(panopto_request.status_code != requests.codes.ok):
        print('Error: Unable to fetch tutorials from Panopto.')
        return;

    panopto_response = BeautifulSoup(panopto_request.text, 'html.parser')
    for link in panopto_response.find_all('a'):
        lecture_href = link.get('href')
        lecture_name = link.string

        lecture_page = requests.get(lecture_href, cookies=cookies)
        lecture_html = BeautifulSoup(lecture_page.text, 'html.parser')

        #download_video_link = lecture_html.find(property='og:video:secure_url')['content']

        print(lecture_html.find_all('meta'))

        break;



    #time.sleep(2)

    #completed_recordings = browser.find(id='block_panopto_content') #.find_all(class_='listItem')

    #print(completed_recordings)
    # Chosen Course

    # Download into folder

    # Done


main_download();
