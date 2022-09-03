# run with:
#    docker run --rm -it -v ${PWD}:/spider nmap-tor
#    cd /spider && proxychains scrapy runspider scraper.py


import scrapy

def loadTorUrls():
    urls = []
    with open('torlist.tab') as f:
        for line in f:
            line=line.rstrip()
            urls.append('http://' + line + ':80')
    return urls

class TestSpider(scrapy.Spider):
    name = "test_spider"
    # start_urls = ['http://1.43.247.217:80', 'http://192.160.102.166:80']
    start_urls = loadTorUrls()

    def parse(self, response):
        with open('torcrawl-results.tab', 'a') as g:
            line = '\001'.join([str(response.status), response.url, response.text])
            g.write(line + '\002')

