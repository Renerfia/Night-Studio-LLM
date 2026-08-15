# Night-Studio's LLM

**A discord bot for Night-Studio server**

## What it does?
This bot is specially designed for forum post management. 
The special feature of this bot is **It can scans all the post from the forum and remembers them**. When someone creates a new post in the forum the agent first retrieves relevant memories from the vector db and return that if exists. The bot automatically answers the user questions.

If no relevant memories found the bot still try to give general answers.

**Note: The bot doesn't reply back any messages. It only writes a message on new thread creation.**
## Commands
| Command | Description |
|---------|-------------|
| /set_up_forum_channel   | Set up a forum channel where the forum bot will write messages |
| /scan_forum   | Scans every thread in the forum  |

## Reference images
The bot answers if relevant memories found.
![alt text](img/2.png)

The bot answers if no relevant memories found.
![alt text](img/1.png)


**Made by Renerfia!**
