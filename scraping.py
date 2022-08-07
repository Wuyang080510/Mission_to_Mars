# import splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

executable_path = {'executable_path': ChromeDriverManager().install()}

def scrape_all():
    # set executable path, initiate headless driver for deployment
    browser = Browser('chrome', **executable_path, headless=False)
    news_title, news_paragraph = mars_news(browser)
    #run all scraping functions and store results in dictionary
    data={
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'hemisphere_info': mars_hemi(browser),
        'last_modified': dt.datetime.now()
    }
    #stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # set up the HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try: 
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')

        # use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_= 'content_title').get_text()
        news_title

        # use the parent element to find the paragraph text 
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
        news_p
    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Scrap images Featured Image

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    
    # find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # parse the resulting html with soup
    html=browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

# scrape fact table
def mars_facts():
    try:
        # use pandas read_html() function to scrape the entire table
        df = pd.read_html('https://galaxyfacts-mars.com')[0] # read_html() serachs for and returns a list of tables found in the HTML, and [0] means we let pandas pulls out the first table it encounters.
    except BaseException:
        return None
    # Assign columns and set index of dataframe
    df.columns = ['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # convert the dataframe to html, this way the data is live based on the changes happens in the original source
    # Then we can add the table to a webpage
    return df.to_html(classes='table table-striped')


def mars_hemi(browser):
    # use the browser to visit url
    url='https://marshemispheres.com/'
    browser.visit(url)

    #create a list to hold the hemisphere images and titiles
    hemisphere_image_urls = []
    
    for i in range(4):
        hemisphere_info={}
        #click the hemisphere img link
        browser.find_by_css('img.thumb')[i].click()
        # parse the resulting html with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')
        img_rel_url = img_soup.find('img', class_='wide-image').get('src')
        img_url = f'https://marshemispheres.com/{img_rel_url}'
        img_title = img_soup.find('h2', class_='title').get_text()
        hemisphere_info['image_title']=img_title
        hemisphere_info['image_url']=img_url
        hemisphere_image_urls.append(hemisphere_info)
        browser.back()
   
    return hemisphere_image_urls



if __name__ =='__main__':
    # if running as script, print scraped data
    print(scrape_all())
