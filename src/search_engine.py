import datetime
import crawler
import dbmgmt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def search(query, term_doc_matrix, articles, links):
    start_time = datetime.datetime.now()
    tokenize = TfidfVectorizer()
    tokenize.fit_transform(articles)
    vectorized_query = tokenize.transform([query]).toarray().reshape(term_doc_matrix.shape[0], )
    norm_q = np.linalg.norm(vectorized_query)

    if norm_q == 0.0:
        print()
        print("No items matched your search")
        print()
        return

    num_articles = len(articles)
    similarity_index = {}

    for curr in range(num_articles):
        vals = term_doc_matrix.loc[:, curr].values
        num = np.dot(vals, vectorized_query)
        norm_tdm = np.linalg.norm(term_doc_matrix.loc[:, curr])
        if norm_tdm == 0.0:
            similarity_index[curr] = 0
            continue
        similarity_index[curr] = num / (norm_tdm * norm_q)

    sim_sorted = sorted(similarity_index.items(), key=lambda x: x[1], reverse=True)

    similarity_list = []
    for k, v in sim_sorted:
        if v != 0.0 and not np.isnan(v):
            similarity_list.append((v, k))

    end_time = datetime.datetime.now()
    search_time = end_time - start_time
    print()
    if len(similarity_list) == 1:
        print("1 article was found in", search_time, "ms")
    else:
        print(len(similarity_list), "articles related to", query, "were found in", search_time, "seconds")

    print()
    for i in range(min(len(similarity_list), 7)):
        print("Article link:", links[similarity_list[i][1]], "----- Similarity Score:", similarity_list[i][0])
        # print(articles[i])
        print()

    if len(similarity_list) <= 0:
        print("No items matched your search")
        print()


def query():
    # should_reindex = input("Type \'Yes\' to reindex the database")
    should_reindex = 'Yes'
    if should_reindex[0] == 'y' or should_reindex[0] == 'Y':
        s = datetime.datetime.now()
        links, articles, tokenized = crawler.reindex_articles()
        f = datetime.datetime.now()
        db = dbmgmt.create_db()
        print()
        print("Reindexed", dbmgmt.size(db), "documents and", tokenized.shape[0], "words in", f - s, "seconds")
        print()
    query = input("What would you like to search?")
    while query != "Exit" and query != "exit":
        search(query, tokenized, articles, links)
        query = input("What would you like to search?")
    return tokenized


if __name__ == "__main__":
    t = query()
    print(t[4000:4050][0:10])
    # t.reset_index(inplace=True)
    # dict_t = t.to_dict("records")
    # db = dbmgmt.create_db()
    # db.tokenized.insert_one({"tokenized": dict_t})
