# Library import
# ===================

from timeit import default_timer as timer

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RedditScraper():

    def __init__(self, subreddit="wallstreetbets"):
        self.base_url = BASE_URL
        self.subreddit = subreddit.strip()
        self.url = BASE_URL + "/r/" + self.subreddit
        self.threads = [] # list of dicts
        self.threads_df = None # Pandas DataFrame

    # Cleanup data upon closing instance
    def cleanup(self):
        # Remove all images downloaded
        shutil.rmtree(IMAGE_DIR)
        os.makedirs(IMAGE_DIR)

    # Initiate Selenium and Chorme webdriver
    def init_selenium_driver(self):
        # restart Tor to get new proxy
        os.system('killall tor > /dev/null')
        os.system('service tor start > /dev/null')

        # Brower setup for Selenium
        service = Service(executable_path="/root/chromedriver")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent={0}'.format(random.choice(USER_AGENTS)))
        # Used proxy to avoid IP ban
        options.add_argument('--proxy-server=socks5://127.0.0.1:9050')

        driver = webdriver.Chrome(service=service, options=options)
        print("Selenium initiated.")
        return driver

    # Load page source and unfold javascript-powered elements
    def load_page_source(self, driver, url):
        driver.get(url)
        # Unlike time.sleep, continues if webpage is loaded before max time
        # driver.implicitly_wait(5)

        # Collapsed content area should be expanded to get contents
        collapsed_expand_obj = driver.find_elements(
            By.XPATH, 
            "//div[contains(@class, 'expando-button') and contains(@class, 'collapsed')]"
        );
        for expand_button in collapsed_expand_obj:
            # click to expand content area
            expand_button.click()

            # (Explicitly) wait until (javescript-based) content area is fully loaded
            post_obj = expand_button.find_element(By.XPATH, "../..") # select grandparent
            content_obj = post_obj.find_element(By.CLASS_NAME, "expando") # where content is shown
            WebDriverWait(driver, 20).until(EC.visibility_of(content_obj))

        print('BeautifulSoup: page source loaded succesfully.')
        return BeautifulSoup(driver.page_source, "html.parser")

    # Parse post element into data
    def parse_post_object(self, post):
        # Scrape post information
        post_id = post.attrs["id"]
        post_link = post.attrs["data-permalink"]
        # Datetime submitted in format yyyy-MM-ddThh:mm:ss+00:00 (UTC)
        post_time = post.find("time").attrs["datetime"]
        post_title = post.find("a", class_="title").text
        post_domain = post.find("span", class_="domain").a.text

        board_name = post.attrs['data-subreddit']
        board_id = post.attrs['data-subreddit-fullname']
        board_type = post.attrs['data-subreddit-type']

        author_name = post.find("a", class_="author").text
        author_id = post.attrs['data-author-fullname']
        # Moderator list is hard-coded for /r/wallstreetbets
        author_ismod = (author_name in LIST_MODERATORS)
        
        post_likes = post.find("div", attrs={"class": "score unvoted"})
        post_likes = 0 if post_likes.text == "•" else int(post_likes.attrs['title'])
        
        # Number of comments
        post_comments = post.find("a", class_="comments").text.split()[0]
        if post_comments == "comment":
            post_comments = 0
        post_comments = int(post_comments)

        # Flair attached to the post                
        post_flair = post.find("span", class_="linkflairlabel")
        if post_flair:
            post_flair = post_flair.text

        # Awards conveyed to the author
        author_awards = {}
        awards = post.find("span", class_="awardings-bar").find_all("a", class_="awarding-link")
        if awards:
            for award in awards:
                k = award.attrs['data-award-id']
                v = award.attrs['data-count']
                author_awards[k] = v

        # 4 types of post in terms of its content: 
        # text only, (single) video, (multiple) images, (single) image
        post_content = None
        post_media = []
        content_area = post.find("div", class_="expando")

        if content_area:
            # if content loading is not finished, mark it as ERROR
            if content_area.find("span", class_="error"):
                post_content = "ERROR"
            else:
                content_text = content_area.find("div", class_="usertext-body")
                post_content = content_text.text if content_text else None

                # Extract media from content
                is_video = content_area.find("div", class_="video-player")
                is_gallery = content_area.find("div", class_="media-gallery")
                is_image = content_area.find("div", class_="media-preview-content")

                # Skip if content is video
                if is_video:
                    pass
                # if content is multiple images
                elif is_gallery:
                    imgs = content_area.find_all("div", class_="media-preview-content")
                    for img in imgs:
                        # do not store image(file) into database
                        img_path = save_image(img.find("img")["src"])
                        # instead, store file hash as a link to saved file
                        img_hash = hash_file(img_path)
                        post_media.append(img_hash)
                # if content is single image
                elif is_image:
                    img_path = save_image(is_image.find("img")["src"])
                    img_hash = hash_file(img_path)
                    post_media.append(img_hash)

        self.threads.append({
            "post_id": post_id, 
            "link": post_link,
            "time": post_time, 
            "title": post_title, 
            "domain": post_domain,
            "board_name": board_name,
            "board_id": board_id,
            "board_type": board_type,
            "author_name": author_name, 
            "author_id": author_id, 
            "author_ismod": author_ismod,
            "likes": post_likes, 
            "comments": post_comments, 
            "flair": post_flair,
            "author_awards": author_awards,
            "content": post_content,
            "media": post_media,
        })

    # Start scraping up to designated number of items
    def scrape_threads(self, max_item=0):
        # Measures time spent
        start_time = timer()
        # Disguise headers to avoid IP ban
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"    
        }
        driver = self.init_selenium_driver()
        bs = self.load_page_source(driver, self.url)
        driver.quit() # Close browser

        # Get all threads regardless of domain direction (inbound / outbound)
        attrs = {"class": "thing", "id": True}
        page_counter = 0
        post_counter = 0

        # Loop until next page does not exists
        while True:
            page_counter += 1
            for post in bs.find_all("div", attrs=attrs):

                # Skip if the post is already collected
                if post.attrs["id"] in [p["post_id"] for p in self.threads]:
                    continue

                # Skip advertisement posts
                if post.find("span", class_="promoted-tag"):
                    continue

                # Show progress for debug
                post_counter += 1
                if post_counter % 5 == 1:
                    print("Processing post #{} from page #{}...".format(post_counter, page_counter))

                # Parse and store post object
                self.parse_post_object(post)

                # Break if reached target item count
                if (max_item > 0) and (post_counter >= max_item):
                    break

            # For every page request, pause not to reach rate limit
            rand_sleep()

            # Skipped pages afterwards due to IP ban
            if page_counter == 1:
                break

            next_button = bs.find("span", class_="next-button")
            # continue scraping only when next page exists
            if next_button:
                next_page_link = next_button.find("a").attrs['href']
                bs = self.load_page_source(driver, next_page_link)
                driver.quit() # Close browser
            # next button no longer exists after 500 newest posts
            else:
                break

        print(f'Scraping completed - collected (additional) {post_counter} post(s) from {page_counter} page(s) in {timer()-start_time:,.1f} seconds.')
        print(f'Returned {len(self.threads)} records.')
        return self.threads


if __name__ == '__main__':
    pass