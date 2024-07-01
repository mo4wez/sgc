import logging
import jdatetime
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from config import SamawebGradeCheckerConfig
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from time import sleep


class SamaGradeChecker:
    def __init__(self):
        self.config = SamawebGradeCheckerConfig()
        self.driver = self._setup_driver()

    def run(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.login()

    def _setup_driver(self):
        logging.info('Setting up driver...')
        options = Options()
        options.add_argument(f"--no-proxy-server={self.config.login_url}")
        options.add_argument("--headless=new")  # run in headless mode (without gui)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        return driver
    
    def login(self):
        logging.info('login to samaweb...')
        
        try:
            self.driver.get(self.config.login_url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'Username')))
            sleep(1)
            username_field = self.driver.find_element(By.NAME, 'Username')
            username_field.send_keys(self.config.username)
            sleep(1)
            password_field = self.driver.find_element(By.NAME, 'Password')
            password_field.send_keys(self.config.password)

            sleep(1)
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-primary.btn-lg.btn-block')
            login_button.click()

            WebDriverWait(self.driver, 10).until(EC.url_changes('https://samaweb.zaums.ac.ir/CAS/'))
        
        except TimeoutException:
            logging.error('Timed out waiting for page to load')
        except NoSuchElementException as e:
            logging.error(f"Error finding element: {e}")
        except WebDriverException as e:
            logging.error(f"WebDriver error: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def check_unseen_messages(self):
        logging.info('Checking for unseen messages...')
        sleep(1)
        try:
            notification_button = self.driver.find_element(By.ID, 'notification-button')
            unseen_count_element = notification_button.find_element(By.CSS_SELECTOR, '.unSeenMessageCount')
            unseen_count = unseen_count_element.text.strip()
            
            if unseen_count != '0':
                print('in unseen count method')
                logging.info(f'There are {unseen_count} unseen messages.')
                return True
            else:
                logging.info('There are no unseen messages.')
                return False
        
        except NoSuchElementException as e:
            logging.error(f"Error finding element: {e}")
            return False

    def go_to_all_messages_page(self):
        logging.info('going to all messages page...')
        is_unseen = self.check_unseen_messages()

        if is_unseen:
            self.driver.get('https://samaweb.zaums.ac.ir/CAS/MessagingSystem/ShowAllMessages')
            sleep(1)

            try:
                message_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.row[data-messageid]'))
                )

                messages_data = []
                current_jalali_date = jdatetime.date.today()

                for message_element in message_elements:
                    try:
                        message_body = message_element.find_element(By.CSS_SELECTOR, 'div.message-body').text
                        message_date_str = message_element.find_element(By.CSS_SELECTOR, 'div[style="float: left; font-size: xx-small; color: darkgray"]').text
                        message_date = jdatetime.datetime.strptime(message_date_str, "%Y/%m/%d").date()

                        if message_date < current_jalali_date:
                            continue

                        seen_button = message_element.find_element(By.CSS_SELECTOR, 'i[title="دیدم"]')
                        seen_button_class = seen_button.get_attribute("class")

                        if 'fa-check-square-o' in seen_button_class:
                            continue

                        print(f"Message Body: {message_body}")
                        print(f"Date: {message_date_str}")

                        messages_data.append({
                            "message_body": message_body,
                            "message_date": message_date_str,
                        })

                        seen_button.click()
                        
                    except Exception as e:
                        return [{"message": f"Error: {e}"}]

                if not messages_data:
                    print("No new messages found.")
                    return [{"message": "No new messages found."}]
                
                return messages_data

            except TimeoutException:
                logging.error('Timed out waiting for messages to load')
                return [{"message": "Timed out waiting for messages to load"}]
            
            finally:
                self.driver.quit()
        else:
            self.driver.quit()
            return [{"message": "There is no notifications for new grades..."}]
            
    
        
