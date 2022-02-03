from pymongo import MongoClient
import matplotlib.pyplot as plt
import numpy as np


class DB:
    def __init__(self):
        # self.client = MongoClient("mongodb+srv://admin:admin@cluster0.kvgsd.mongodb.net/test")
        self.client = MongoClient(
            "mongodb+srv://admin:admin@cluster0.kvgsd.mongodb.net/SearchEngine?retryWrites=true&w=majority")
        self.db = self.client["SpecializedSearchEngine"]
        self.indices = self.db["Indices"]
        self.crawlqueue = self.db["Crawlqueue"]
        self.broken = self.db["Broken"]
        self.visited = self.db["Visited"]
        self.statistics = self.db["Statistics"]


def create_db():
    db_ = DB()
    return db_


def size(database):
    return database.indices.count_documents({})


def size_specialized(database):
    return database.indices.count_documents({}), database.broken.count_documents({})


def insert_indices(db, link, content):
    t = db.indices.find_one({"Link": link})
    if t is None:
        db.indices.insert_one({"Link": link, "Content": content})


def insert_crawlqueue(db, link):
    t = db.crawlqueue.find_one({"Link": link})
    if t is None:
        db.crawlqueue.insert_one({"Link": link})


def insert_broken(db, link):
    t = db.broken.find_one({"Link": link})
    if t is None:
        db.broken.insert_one({"Link": link})


def insert_visited(db, link):
    t = db.visited.find_one({"Link": link})
    if t is None:
        db.visited.insert_one({"Link": link})


def clear_database(db):
    db.crawlqueue.delete_many({})
    db.broken.delete_many({})
    db.indices.delete_many({})
    db.visited.delete_many({})
    db.statistics.delete_many({})


def plot_stats():
    db = DB()
    stats = db.statistics.find({})
    count = db.statistics.count_documents({})
    visited_pages = np.zeros(count)
    crawl_time = np.zeros(count)
    ratio = np.zeros(count)
    keywords = np.zeros(count)

    for i in range(count):
        visited_pages[i] = ((stats[i])['Visited'])  # Visited Pages
        crawl_time[i] = ((stats[i])['Time'])  # Time to crawl newest page (s)
        ratio[i] = ((stats[i])['Ratio'])  # pages crawled:pages in crawl queue
        keywords[i] = ((stats[i])['Keywords'])  # Number of keywords in newest doc

    crawl_time[crawl_time > 5] = np.average(crawl_time)
    keywords = np.absolute(keywords)
    avg = np.average(keywords)
    keywords[keywords > 3 * avg] = avg

    crawl_time = 1 / crawl_time
    ratio[0] = .055

    plt.plot(visited_pages, np.absolute(crawl_time))
    plt.title('Time to crawl a new page')
    plt.xlabel('# of crawled pages')
    plt.ylabel('Pages crawled / second')
    plt.show()

    plt.plot(visited_pages, np.absolute(ratio))
    plt.title('Ratio of indexed pages to items in to be crawled list')
    plt.xlabel('# of crawled pages')
    plt.ylabel('Ratio of indexed pages to items in to be crawled list')
    plt.show()

    plt.plot(visited_pages, np.absolute(keywords / crawl_time))
    plt.title('Time to Analyze Keywords')
    plt.xlabel('# of crawled pages')
    plt.ylabel('Keywords found per second')
    plt.show()


if __name__ == "__main__":
    plot_stats()
    # db = create_db()
    # clear_database(db)
