from flask import Flask, render_template, request, redirect, url_for, session
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.secret_key = 'secret-key'  

message_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] ([^:]+): (.*)')

love_keywords = ["love", "miss", "babe", "dear", "❤️", "💖", "💗", "😘", "😍"]
sorry_keywords = ["sorry"]

def is_valid_chat_format(chat_lines):
    valid_lines = sum(bool(message_pattern.match(line)) for line in chat_lines)
    return valid_lines / len(chat_lines) > 0.8 if chat_lines else False

def parse_chat(chat_lines):
    messages = []
    for line in chat_lines:
        match = message_pattern.match(line)
        if match:
            date_str, sender, msg = match.groups()
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            messages.append({"sender": sender.strip(), "datetime": dt, "msg": msg.strip()})
    return messages

def analyze_scores(messages):
    users = list({msg['sender'] for msg in messages})
    if len(users) != 2:
        return {}, 0, users
    user1, user2 = users[0], users[1]
    stats = {user1: defaultdict(int), user2: defaultdict(int)}
    word_counts = {user1: Counter(), user2: Counter()}

    prev_time = None
    last_sender = None

    for msg in messages:
        sender = msg['sender']
        text = msg['msg'].lower()
        stats[sender]['word_count'] += len(text.split())
        word_counts[sender].update(text.split())

        if any(word in text for word in love_keywords):
            stats[sender]['love_count'] += 1
        if any(word in text for word in sorry_keywords):
            stats[sender]['sorry_count'] += 1
        if '<media omitted>' in text:
            stats[sender]['word_count'] += 1

        if not prev_time or msg['datetime'] - prev_time > timedelta(minutes=30):
            stats[sender]['initiation_count'] += 1
        prev_time = msg['datetime']

        if last_sender and last_sender != sender:
            gap = (msg['datetime'] - last_time).total_seconds() / 60
            if 'reply_times' not in stats[sender]:
                stats[sender]['reply_times'] = []
            stats[sender]['reply_times'].append(gap)

        last_sender = sender
        last_time = msg['datetime']

    total_initiations = sum(stats[u]['initiation_count'] for u in users)
    total_words = sum(stats[u]['word_count'] for u in users)
    scores = {}

    for u in users:
        init_score = (stats[u]['initiation_count'] / total_initiations) * 100 if total_initiations else 0
        effort_score = (stats[u]['word_count'] / total_words) * 100 if total_words else 0
        reply_avg = sum(stats[u].get('reply_times', [])) / len(stats[u].get('reply_times', []) or [1])
        reply_score = max(0, 100 - (reply_avg / 720 * 100))  # Cap at 12 hrs

        scores[u] = {
            "initiation": round(init_score, 2),
            "effort": round(effort_score, 2),
            "reply": round(reply_score, 2),
            "love_count": stats[u]['love_count'],
            "sorry_count": stats[u]['sorry_count'],
            "most_used": word_counts[u].most_common(1)[0][0] if word_counts[u] else "-"
        }

    avg_score = sum([
        scores[user1]['initiation'],
        scores[user1]['effort'],
        scores[user1]['reply'],
        scores[user2]['initiation'],
        scores[user2]['effort'],
        scores[user2]['reply']
    ]) / 6

    return scores, round(avg_score, 2), [user1, user2]

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['chatfile']
        if file:
            chat_lines = file.read().decode('utf-8').splitlines()
            if not is_valid_chat_format(chat_lines):
                return render_template('upload.html', error="❌ Chat format is not valid. Expected format: [YYYY-MM-DD HH:MM] Name: Message")
            
            messages = parse_chat(chat_lines)
            session['messages'] = [dict(msg) for msg in messages]
            scores, love_score, users = analyze_scores(messages)
            session['users'] = users
            session['scores'] = scores
            session['love_score'] = love_score

            return render_template('result.html',
                                   scores=scores,
                                   love_score=love_score,
                                   person1=users[0],
                                   person2=users[1],
                                   search_term=None)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
