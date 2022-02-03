import datetime
import re
import urllib
from bs4 import BeautifulSoup
import indexer
import dbmgmt


def infinite_crawl_array(start_url):
    global crawl_queue, already_crawled, article_list, tokenized, broken_links, database
    crawl_queue = [start_url]
    already_crawled = []
    article_list = []
    tokenized = []
    broken_links = []

    while crawl_queue:
        curr = crawl_queue.pop(0)
        new_data = crawl_page(curr)
        if new_data is None:
            broken_links.append(curr)
        else:
            already_crawled.append(curr)
            article_list.append(new_data[1])

        if new_data is not None:
            for link in new_data[0]:
                if link not in already_crawled and link not in crawl_queue and link not in broken_links:
                    crawl_queue.append(link)

        if len(already_crawled) > 1000:
            print("There are still", len(crawl_queue), "items in the crawl queue!")
            return


def infinite_crawl_db(start_url):
    global crawl_queue, already_crawled, article_list, tokenized, broken_links, database
    global page_count
    crawl_queue = [start_url]
    already_crawled = []
    article_list = []
    tokenized = []
    broken_links = []
    database = dbmgmt.create_db()

    t_3 = database.broken.find_one({"Link": start_url})
    t_4 = database.visited.find_one({"Link": start_url})

    if t_3 is None and t_4 is None:
        database.crawlqueue.insert_one({"Link": start_url})

    while crawl_queue:
        curr = database.crawlqueue.find_one_and_delete({})
        curr = list(list(curr.items())[1])[1]
        dbmgmt.insert_visited(database, curr)
        new_data = crawl_page(curr)

        if new_data is None:
            dbmgmt.insert_broken(database, curr)
        else:
            dbmgmt.insert_indices(database, curr, new_data[1])
        if new_data is not None:
            for link in new_data[0]:
                t_2 = database.indices.find_one({"Link": link})
                t_3 = database.broken.find_one({"Link": link})
                t_4 = database.visited.find_one({"Link": link})
                if t_2 is None and t_3 is None and t_4 is None:
                    dbmgmt.insert_crawlqueue(database, link)

        if dbmgmt.size(database) > 100000:
            return


def infinite_crawl_db_focused(start_url):
    global crawl_queue, already_crawled, article_list, tokenized, broken_links, database
    global page_count
    crawl_queue = [start_url]
    already_crawled = []
    article_list = []
    tokenized = []
    broken_links = []
    database = dbmgmt.create_db()

    t_3 = database.broken.find_one({"Link": start_url})
    t_4 = database.visited.find_one({"Link": start_url})

    if t_3 is None and t_4 is None:
        database.crawlqueue.insert_one({"Link": start_url})

    while crawl_queue:
        curr = database.crawlqueue.find_one_and_delete({})
        curr = list(list(curr.items())[1])[1]
        # dbmgmt.insert_visited(database, curr)
        s = datetime.datetime.now()
        new_data = crawl_page(curr)
        f = datetime.datetime.now()
        seconds = f.second - s.second
        ms = f.microsecond - s.microsecond
        delta_t = seconds + .000001 * ms

        if new_data is None or not ("computing" in new_data[1] or "coc" in new_data[1] or "computer" in new_data[1] or "computer science" in new_data[1] or "computer" in new_data[1]):
            dbmgmt.insert_broken(database, curr)
        else:
            print(datetime.datetime.now(), "-- Finished crawling link #", dbmgmt.size_specialized(database)[0], "at:", curr)
            db = dbmgmt.create_db()
            db.statistics.insert_one({"Visited": dbmgmt.size_specialized(db)[0],\
                                      "Time": delta_t,\
                                      "Ratio": dbmgmt.size_specialized(db)[0] / (1 if db.crawlqueue.count_documents({}) == 0 else db.crawlqueue.count_documents({})),\
                                      "Keywords": len(new_data[1])})
            dbmgmt.insert_indices(database, curr, new_data[1])
            dbmgmt.insert_visited(database, curr)
        if new_data is not None:
            for link in new_data[0]:
                t_2 = database.indices.find_one({"Link": link})
                t_3 = database.broken.find_one({"Link": link})
                t_4 = database.visited.find_one({"Link": link})
                if t_2 is None and t_3 is None and t_4 is None:
                    dbmgmt.insert_crawlqueue(database, link)

        if dbmgmt.size_specialized(database)[0] > 100000:
            return


def crawl_page(url):
    try:
        html = urllib.request.urlopen(url, timeout=5).read()
    except:
        print("Unable to access", url)
        return None
    soup = BeautifulSoup(html, 'lxml')
    soup.find_all('a')
    all_links = clean_links(soup)

    article_content = soup.get_text()
    article_content = indexer.clean_text(article_content)

    return all_links, article_content


def clean_links(soup):
    links = soup.find_all('a', attrs={'href': re.compile("^http")})
    queue = []
    for link in links:
        queue.append(link.get('href'))
    return queue


def main(url):
    infinite_crawl_db_focused(url)


def reindex_articles():
    links = []
    articles = []

    websites = dbmgmt.create_db().indices.find({})
    websites = list(websites)
    for i in range(len(websites)):
        curr = websites[i]
        links.append(curr['Link'])
        articles.append(curr['Content'])

    tokens = indexer.index_text(articles)
    return links, articles, tokens


if __name__ == "__main__":
    main("https://cc.gatech.edu")
