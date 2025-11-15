# Single-file retrieval QA (cleaned, runnable)
import os, json, joblib, numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

DATA_DIR = 'byfort_data'
INDEX_DIR = 'byfort_index'

def ensure_dataset():
    os.makedirs(DATA_DIR, exist_ok=True)
    required = ['videos.csv','chats.csv','transactions.csv','wallets.csv']
    if all(os.path.exists(os.path.join(DATA_DIR,f)) for f in required):
        print('[OK] Dataset exists')
        return
    print('[INFO] Creating minimal dataset')
    videos = pd.DataFrame([
        {"video_id":1, "title":"Cara Withdraw DANA", "description":"Tutorial tarik dana"},
        {"video_id":2, "title":"Cara Deposit QRIS", "description":"Panduan isi saldo"}
    ])
    chats = pd.DataFrame([
        {"chat_id":1, "sender":"user","message":"Bagaimana cara withdraw ke DANA?"},
        {"chat_id":2, "sender":"user","message":"Cara deposit BYFORT gimana ya?"}
    ])
    transactions = pd.DataFrame([
        {"tx_id":101, "user_id":1, "type":"withdrawal", "asset":"IDR", "status":"completed", "amount":150000},
    ])
    wallets = pd.DataFrame([{"wallet_id":"w1","user_id":1,"asset":"IDR","balance":254000}])
    videos.to_csv(os.path.join(DATA_DIR,'videos.csv'), index=False)
    chats.to_csv(os.path.join(DATA_DIR,'chats.csv'), index=False)
    transactions.to_csv(os.path.join(DATA_DIR,'transactions.csv'), index=False)
    wallets.to_csv(os.path.join(DATA_DIR,'wallets.csv'), index=False)
    print('[OK] dataset minimal dibuat')

def load_documents():
    docs = []
    v = pd.read_csv(os.path.join(DATA_DIR,'videos.csv'))
    for _,r in v.iterrows():
        docs.append({'id':str(r['video_id']),'source':'video','text': f"{r.get('title','')} {r.get('description','')}"})
    c = pd.read_csv(os.path.join(DATA_DIR,'chats.csv'))
    for _,r in c.iterrows():
        docs.append({'id':str(r['chat_id']),'source':'chat','text':str(r.get('message',''))})
    t = pd.read_csv(os.path.join(DATA_DIR,'transactions.csv'))
    for _,r in t.iterrows():
        docs.append({'id':str(r['tx_id']),'source':'transaction','text': f"{r.get('type','')} {r.get('asset','')} status {r.get('status','')} amount {r.get('amount','')}"})
    w = pd.read_csv(os.path.join(DATA_DIR,'wallets.csv'))
    for _,r in w.iterrows():
        docs.append({'id':str(r['wallet_id']),'source':'wallet','text': f"wallet {r.get('wallet_id','')} asset {r.get('asset','')} balance {r.get('balance','')}"})
    return docs

def build_index(docs):
    print('[INFO] Building TF-IDF')
    texts = [d['text'] for d in docs]
    vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=5000)
    tfidf = vectorizer.fit_transform(texts)
    os.makedirs(INDEX_DIR, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(INDEX_DIR,'vectorizer.joblib'))
    joblib.dump(tfidf, os.path.join(INDEX_DIR,'tfidf.joblib'))
    json.dump(docs, open(os.path.join(INDEX_DIR,'docs.json'),'w',encoding='utf-8'), indent=2)
    print('[OK] index siap')


def load_index():
    vec = joblib.load(os.path.join(INDEX_DIR,'vectorizer.joblib'))
    tfidf = joblib.load(os.path.join(INDEX_DIR,'tfidf.joblib'))
    docs = json.load(open(os.path.join(INDEX_DIR,'docs.json'),'r',encoding='utf-8'))
    return vec, tfidf, docs


def retrieve(query, topk=5):
    vec, tfidf, docs = load_index()
    qv = vec.transform([query])
    sims = linear_kernel(qv, tfidf).flatten()
    idx = sims.argsort()[::-1][:topk]
    results = []
    for i in idx:
        results.append({'score':float(sims[i]), 'text':docs[i]['text'],'source':docs[i]['source'],'id':docs[i]['id']})
    return results


def answer(query):
    res = retrieve(query, topk=5)
    if not res:
        return 'Tidak ditemukan data relevan.'
    top = res[0]
    ql = query.lower()
    if 'withdraw' in ql or 'wd' in ql:
        return f"Untuk withdraw: {top['text']}"
    if 'deposit' in ql:
        return f"Deposit: {top['text']}"
    return f"Hasil relevan: {top['text']}"

if __name__=='__main__':
    ensure_dataset()
    docs = load_documents()
    build_index(docs)
    print('\n================================')
    print(' BYFORT RETRIEVAL QA READY')
    print('================================')
    while True:
        q = input('\nTanya apa saja: ')
        print('\n>> Jawaban:', answer(q))
        print('\n>> Dokumen relevan:', retrieve(q, topk=3))
