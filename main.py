from Scrape import Scraper
scraper = Scraper()
scraper.close_button()
scraper.get_last_post_url()
scraper.scrape_post()
output_dir = './website' # Change to your desired output directory
scraper.export_to_html(output_dir)