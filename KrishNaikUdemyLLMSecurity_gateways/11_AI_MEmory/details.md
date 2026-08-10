### No memory

Follow up question wont be answered to the user


### Conversational Memory with Sliding Window
We keep a track of all turns of all messages. Memory will be maintained
But using this in future tokens will be huge


### Sliding Window Memory
In order to keep a track of history we set a threshold. That is after aybe 5 we keep
only the latest memory. We might lose important information

### Summary memmory
For every new message a summary is being generated in the form of history.
Problem is 2 api calls in single turn of chat message
Context Echo might happen. Context echo is if a user has mentioned football 70 times in 100 chats then
summary will have most of the words like football

### Summary and Token buffer memory
It keeps last 5 or 10 messages and beyond that it summarises.


### token buffer memory
More than a certain tokens it will forget and will rememeber only a certain numner of tokens related history