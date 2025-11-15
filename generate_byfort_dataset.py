# Cleaned and runnable dataset generator based on your spec
import argparse, os, numpy as np, pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
now = datetime.utcnow()

def rand_dates_vec(n, days_back=800):
    secs = np.random.randint(0, days_back*24*3600, size=n)
    base = now - timedelta(days=days_back)
    return [(base + timedelta(seconds=int(s))).isoformat() for s in secs]

def generate(outdir, config):
    os.makedirs(outdir, exist_ok=True)
    N_USERS = config['users']
    N_VIDEOS = config['videos']
    N_INTERACTIONS = config['interactions']
    N_TRANSACTIONS = config['transactions']
    N_ORDERS = config['orders']
    N_MARKET = config['market']
    N_CHATS = config['chats']
    N_WALLETS = config['wallets']
    N_MODERATION = config['moderation']

    user_idx = np.arange(N_USERS)
    user_ids = np.char.add("u", (100000 + user_idx).astype(str))
    usernames = np.char.add("user", (100000 + user_idx).astype(str))
    emails = np.char.add(usernames, "@byfort.test")
    phones = np.char.add("+6281", (10000000 + user_idx).astype(str))
    created_at = rand_dates_vec(N_USERS, days_back=1200)
    countries = np.random.choice(["ID","MY","PH","VN","US","SG"], size=N_USERS, p=[0.7,0.05,0.05,0.05,0.1,0.05])
    is_verified = np.random.choice([0,1], size=N_USERS, p=[0.45,0.55])
    roles = np.random.choice(["user","creator","admin"], size=N_USERS, p=[0.9,0.095,0.005])

    users = pd.DataFrame({
        "user_id": user_ids,
        "username": usernames,
        "email": emails,
        "phone": phones,
        "created_at": created_at,
        "country": countries,
        "is_verified": is_verified,
        "role": roles
    })
    users.to_csv(os.path.join(outdir,"users.csv"), index=False)

    # minimal videos
    video_idx = np.arange(N_VIDEOS)
    video_ids = np.char.add("v", (200000 + video_idx).astype(str))
    creator_ids = np.random.choice(user_ids, size=N_VIDEOS)
    titles = np.char.add("BYFORT Video #", (video_idx).astype(str))
    descriptions = np.char.add("Auto-generated demo video content ", (video_idx).astype(str))
    durations = np.random.randint(5,300, size=N_VIDEOS)
    uploaded_at = rand_dates_vec(N_VIDEOS, days_back=800)
    languages = np.random.choice(["id","en","mix"], size=N_VIDEOS, p=[0.75,0.2,0.05])
    visibility = np.random.choice(["public","private","unlisted"], size=N_VIDEOS, p=[0.88,0.08,0.04])

    videos = pd.DataFrame({
        "video_id": video_ids,
        "creator_id": creator_ids,
        "title": titles,
        "description": descriptions,
        "duration_seconds": durations,
        "uploaded_at": uploaded_at,
        "language": languages,
        "visibility": visibility
    })
    videos.to_csv(os.path.join(outdir,"videos.csv"), index=False)

    # interactions
    interaction_ids = np.char.add("int", (300000 + np.arange(N_INTERACTIONS)).astype(str))
    video_choices = np.random.choice(video_ids, size=N_INTERACTIONS)
    user_choices = np.random.choice(user_ids, size=N_INTERACTIONS)
    types = np.random.choice(["view","like","comment","share"], size=N_INTERACTIONS, p=[0.75,0.15,0.08,0.02])
    comments_pool = ["Great!","Nice","Loved it","Where did you get this?","Cool!","Spam?"]
    contents = np.where(types=="comment", np.random.choice(comments_pool, size=N_INTERACTIONS), "")
    timestamps = rand_dates_vec(N_INTERACTIONS, days_back=800)
    interactions = pd.DataFrame({
        "interaction_id": interaction_ids,
        "video_id": video_choices,
        "user_id": user_choices,
        "type": types,
        "content": contents,
        "timestamp": timestamps
    })
    interactions.to_csv(os.path.join(outdir,"interactions.csv"), index=False)

    print('Dataset generated at', outdir)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out','-o',default='./byfort_data')
    parser.add_argument('--scale','-s',default='small',choices=['small','medium','large'])
    args = parser.parse_args()
    presets = {
        'small': {'users':2000,'videos':5000,'interactions':20000,'transactions':5000,'orders':5000,'market':8000,'chats':10000,'wallets':4000,'moderation':2000},
        'medium': {'users':10000,'videos':30000,'interactions':150000,'transactions':30000,'orders':30000,'market':60000,'chats':80000,'wallets':20000,'moderation':15000},
        'large': {'users':50000,'videos':150000,'interactions':800000,'transactions':200000,'orders':200000,'market':400000,'chats':400000,'wallets':100000,'moderation':80000}
    }
    cfg = presets[args.scale]
    generate(args.out, cfg)
