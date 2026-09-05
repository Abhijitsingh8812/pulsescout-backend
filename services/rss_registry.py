# services/rss_registry.py

# ==========================================
# GLOBAL RSS FEEDS
# ==========================================

GLOBAL_RSS = {

    # BBC
    "bbc_main":
        "https://feeds.bbci.co.uk/news/rss.xml",

    "bbc_world":
        "https://feeds.bbci.co.uk/news/world/rss.xml",

   "bbc_uk":
        "https://feeds.bbci.co.uk/news/uk/rss.xml",


    "bbc_technology":
        "https://feeds.bbci.co.uk/news/technology/rss.xml",

    "bbc_health":
        "https://feeds.bbci.co.uk/news/health/rss.xml",


    "bbc_business":
        "https://feeds.bbci.co.uk/news/business/rss.xml",

    "bbc_science":
        "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",

    # NEWSUN
    "newsun_crime":
        "https://news.un.org/feed/subscribe/en/news/topic/law-and-crime-prevention/feed/rss.xml",     


    "newsun_american":
        "https://news.un.org/feed/subscribe/en/news/region/americas/feed/rss.xml",       


    "newsun_climate":
        "https://news.un.org/feed/subscribe/en/news/topic/climate-change/feed/rss.xml",     


    "newsun_education":
        "https://news.un.org/feed/subscribe/en/news/topic/culture-and-education/feed/rss.xml",   



    # TOI
    "toi_world":
        "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",

    # NDTV
    "ndtv_world":
        "https://feeds.feedburner.com/ndtvnews-world-news",



    # GLOBAL_VOICE
    "gvoice_main":
        "https://globalvoices.org/feed",


    "gvoice_long":
        "https://globalvoices.org/feed/?cat=-28",


     "gvoice_short":
        "https://globalvoices.org/-/roundups/feed",


     # GLOBAL_NATIONAL
    "glnews_main":
        "https://globalnews.ca/us-news/feed",

    "glnews_morning":
        "https://globalnews.ca/national/program/the-morning-show/feed",


    "glnews_entertainment":
        "https://globalnews.ca/entertainment/feed",

    "glnews_us":
        "https://globalnews.ca/us-news/feed",


    # CNN
    "cnn_main":
        "http://rss.cnn.com/rss/edition.rss",

    "cnn_world":
        "http://rss.cnn.com/rss/edition_world.rss",

    "cnn_travel":
        "http://rss.cnn.com/rss/cnn_travel.rss",


    "cnn_us":
        "http://rss.cnn.com/rss/cnn_us.rss",


    "cnn_topstories":
        "http://rss.cnn.com/rss/cnn_topstories.rss",


   "cnn_business":
        "http://rss.cnn.com/rss/edition_business.rss",


   "cnn_health":
        "http://rss.cnn.com/rss/cnn_health.rss",


    "cnn_technology":
        "http://rss.cnn.com/rss/edition_technology.rss",

    "cnn_sports":
        "http://rss.cnn.com/rss/edition_sport.rss",

    # CBSN_NEWS
    "cbsn_top":
        "https://www.cbsnews.com/latest/rss/main",

    "cbsn_politics":
        "https://www.cbsnews.com/latest/rss/politics",


    "cbsn_space":
        "https://www.cbsnews.com/latest/rss/space",

    "cbsn_entertainment":
        "https://www.cbsnews.com/latest/rss/entertainment",

    "cbsn_technology":
        "https://www.cbsnews.com/latest/rss/technology",

    "cbsn_us":
        "https://www.cbsnews.com/latest/rss/us",


}


# ==========================================
# GLOBAL GOOGLE RSS
# ==========================================

GLOBAL_DYNAMIC_RSS = {

    "ai":
        "https://news.google.com/rss/search?q=Artificial+Intelligence",

    "tesla":
        "https://news.google.com/rss/search?q=Tesla",

    "startup":
        "https://news.google.com/rss/search?q=Startup+India",

    "cryptocurrency":
        "https://news.google.com/rss/search?q=Cryptocurrency",

    "defence":
        "https://news.google.com/rss/search?q=Indian+Defence",

    "elections":
        "https://news.google.com/rss/search?q=Elections",

    "trending":
        "https://news.google.com/rss/search?q=Trending",
}


# ==========================================
# INDIA RSS FEEDS
# ==========================================

INDIA_RSS = {

    "ndtv":
        "https://feeds.feedburner.com/ndtvnews-top-stories",

    "the_hindu":
        "https://www.thehindu.com/news/national/feeder/default.rss",

    "toi":
        "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",

    "india_today":
        "https://www.indiatoday.in/rss/home",

    "ani":
        "https://aninews.in/rss-feed/",

}


# ==========================================
# INDIA GOOGLE RSS
# ==========================================

INDIA_DYNAMIC_RSS = {

    "ai":
        "https://news.google.com/rss/search?q=Artificial+Intelligence",

    "politics":
        "https://news.google.com/rss/search?q=Indian+Politics",

    "ipl":
        "https://news.google.com/rss/search?q=IPL",

    "startup":
        "https://news.google.com/rss/search?q=Startup+India",

    "defence":
        "https://news.google.com/rss/search?q=Indian+Defence",

    "business":
        "https://news.google.com/rss/search?q=Indian+Business",

    "technology":
        "https://news.google.com/rss/search?q=Technology+India",

    "cricket":
        "https://news.google.com/rss/search?q=Indian+Cricket",

    "education":
        "https://news.google.com/rss/search?q=Indian+Education",

    "health":
        "https://news.google.com/rss/search?q=India+Health",

     "ebhas_cricket":
        "https://www.bhaskarenglish.in/rss-v1--category-16339.xml",

    "ebhas_science":
        "https://www.bhaskarenglish.in/rss-v1--category-16336.xml",

    "ebhas_entertainment":
        "https://www.bhaskarenglish.in/rss-v1--category-16334.xml",

    "ndtv_movies":
        "https://feeds.feedburner.com/ndtvmovies-latest",

    "ndtv_cricket":
        "https://feeds.feedburner.com/ndtvsports-cricket",

    "ndtv_health":
        "https://feeds.feedburner.com/ndtvcooks-latest",

    "ndtv_sports":
        "https://feeds.feedburner.com/ndtvsports-latest",

    "toi_business":
        "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",

    "toi_cricket":
        "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms",

    "toi_sports":
        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",

    "toi_science":
        "https://timesofindia.indiatimes.com/rssfeeds/-2128672765.cms",

    "toi_entertainment":
        "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",

    "toi_auto":
        "https://timesofindia.indiatimes.com/rssfeeds/74317216.cms",

    "toi_education":
        "https://timesofindia.indiatimes.com/rssfeeds/913168846.cms",

}