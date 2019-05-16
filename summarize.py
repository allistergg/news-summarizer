import requests
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist

def soupify(url = sys.argv[1]):
    source = urlparse(url).netloc
    print(source)
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    return soup, source

def textify(soup):
    def guardian(soup): 
        text = soup.find(class_='content__article-body')
        submeta = text.findAll(class_='submeta')    
        richlink = text.findAll(class_='rich-link')
        caption = text.findAll(class_='caption')
        metaextras = text.findAll(class_='meta_extras')
        blockshare = text.findAll(class_='block-share')
        to_decompose = [submeta, richlink, caption, metaextras, blockshare]
        return text, to_decompose
    def wikipedia(soup):
        text = soup.find(class_='mw-content-ltr')
        hatnote = text.findAll(class_='hatnote')
        citation = text.findAll(class_='citation')
        infobox = text.findAll(class_='infobox')
        toc = text.findAll(class_='toc')
        reference = text.findAll(class_='reference')
        to_decompose = [hatnote, citation, infobox, toc, reference]
        return text, to_decompose
    def rt(soup):
        text = soup.find(class_='article__text')
        readmore = text.findAll(class_='read-more')
        to_decompose = [readmore]
        return text, to_decompose
    # for element in to_decompose:
    #     for match in element:
    #         match.decompose()
    
    sources = {'www.theguardian.com': guardian, 'en.wikipedia.org': wikipedia, 'www.rt.com': rt}
    text, to_decompose = sources[soup[1]](soup[0])
    [match.decompose() for element in to_decompose for match in element]
    text = text.get_text()
    return text


def tokenize(text):
    stopWords = set(stopwords.words("english"))
    word_tokens_raw = word_tokenize(text)
    # for word in word_tokens_raw:
    #     word = word.lower()
    #     if word not in stopWords and word.isalpha():
    #         word_tokens2.append(word)
    word_tokens = [word for word in word_tokens_raw if word.lower() not in stopWords and word.isalpha()]
    sent_tokens = sent_tokenize(text)
    return word_tokens, sent_tokens



def calculate_values(word_tokens, sent_tokens):
    sentenceValue = {}
    fdist = FreqDist(word_tokens)

    # print(fdist.most_common(10))

    for sentence in sent_tokens:
        for wordValue in fdist.most_common(50):
            if wordValue[0] in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += wordValue[1]
                else:
                    sentenceValue[sentence] = wordValue[1]
    return sentenceValue

def calculate_average(sentenceValue):
    sumValues = 0
    # print(sentenceValue)
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]
    # Average value of a sentence from original text
    average = sumValues / len(sentenceValue)
    return average

def summarize():
    word_tokens, sent_tokens = tokenize(textify(soupify()))
    sentenceValue = calculate_values(word_tokens, sent_tokens)
    average = calculate_average(sentenceValue)
    summary = ''
    for sentence in sent_tokens:
        if sentence in sentenceValue and sentenceValue[sentence] > (1.5 * average):
            summary +=  " " + ' '.join(sentence.split())
    return summary

if __name__ == '__main__':
   print(summarize())









