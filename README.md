# 💬 ChatAnalyzer

ChatAnalyzer is a simple yet insightful web app that analyzes private  chats between two individuals. It examines message patterns to reveal who initiates more, who puts in more effort (via word count), how fast each person replies, and how often certain emotional keywords like “love” or “sorry” are used. Based on this, the app generates a fun and meaningful "Love Score" — a percentage that reflects mutual texting balance and connection effort.

The Love Score is calculated using the average of three main metrics for each user:  
• **Initiation %** — how often they start conversations  
• **Effort %** — how many words they contribute  
• **Reply Speed %** — based on their average reply time (lower = better)

The formula looks like this:


The app is built with **Python and Flask**, styled with HTML/CSS, and deployed using **Render**. To use it, simply export your chat (without media) from your phone or email, and upload the `.txt` file on the site. Make sure your chat follows this format:  
`[YYYY-MM-DD HH:MM] Name: Message`  
If it doesn’t, you can reformat it using ChatGPT or check the included example file.

🔍 A working **sample chat file** is provided in the `uploads/sample_chat.txt` folder to test or understand the format better.

Whether you're a couple, best friends, or just curious about your texting style, ChatAnalyzer gives you a fun way to reflect on your conversations.

