from crawl import selenium_crawler
import click

#http://pc26.danawa.com/bbs/?controller=boardReview&methods=reviewList
#http://pc26.danawa.com/bbs/?controller=boardReview&methods=assemblyGalleryList

@click.command()
@click.option('--url', type=click.STRING, required=True, default=None, help="Target url")
@click.option('--category', type=click.STRING, required=True, default=None, help="Target category")
def main(url, category):
    selenium_crawler(url, category)


if __name__ == "__main__":
    main()