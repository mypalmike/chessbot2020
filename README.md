# chessbot2020

## What is it?

This is a bot that enables people on twitter to play chess against each other.

## Status

"Beta". It is not yet heavily tested, so any feedback is welcome.

## How to play chess on twitter

Tweet something like "Hey @chessbot2020 please start a new game against @<opponent>". The bot is looking for the words "new game" followed by a single user mention.

The bot will show a new game board and your opponent will have the first move.

When it's your turn, just reply to the bot with a chess move. Both [Standard Algebraic Notation (SAN)](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)) and [Universal Chess Interface (UCI)](https://en.wikipedia.org/wiki/Universal_Chess_Interface) notation should work. If you're confused, just look at the grid. You can generally just type the starting and ending coordinates, like "e2e3" for moving a pawn forward.

The bot only responds to moves which are replies to board tweets (tweets with images of the board state). It will not respond if you reply to one of its error tweets. If you make a mistake, just tweet abother reply to the board tweet.

Please ♥ some of the bot's tweets while playing. This should improve the bot's reputation on twitter, which will make it less likely that twitter will consider the bot's tweets as spam, which seems to happen occasionally.

## FAQ

#### Q: What should I do if the bot doesn't respond?

A: The bot should respond to a "new game" request or a move within about a minute. If it has not responded in about 2 minutes, first go to the [bot's twitter page](https://twitter.com/chessbot2020) to see if the response is somewhere in there but didn't make it into your notifications. If you still can't find any sign that the bot responded to your move, try deleting your tweet and do the same response but with slightly different text. For example, if you tweeted "e4", try tweeting "e4 please".

#### Q: Why doesn't it always work?

A: Sometimes twitter will stop you from sending the same tweet in a relatively short amount of time. So if you tweet the same move twice, it will filter out the second tweet. There is a simple workaround. If you try to tweet "e2" twice in a row and the second one fails, try "e2 please" or "e2 anything" or "e2 is the thing I wanna do". As long as it's different, Twitter doesn't seem to consider it a duplicate.

#### Q: Why else might it not work?

A: There may be bugs in the bot code.

#### Q: Could there be any other possible reason it isn't working?

A: Twitter will sometimes filter tweets from your view and notifications because of abuse-filtering algorithms which think the bot is being an annoyance. It seems that "liking" tweets by the bot will help improve twitter's assessment of the bot as a good twitter user, making it less likely to filter out tweets. Also, it may be helpful to follow the bot. However, if you do this, it's possible you will start getting some notifications of other players' random chess games in your twitter timeline, which you may or may not be interested in. Worst case, you can try following now and then unfollow later.

#### Q: Seriously, it's not working and I'm playing an important game. What the heck?

A: The bot runs on an old Mac Mini in a basement, running an older Ubuntu. Among other possibilities, there may have been a flood.

#### Q: How can I declare a draw?

A: Just work it out with your opponent for now. The bot should handle most end of game scenarios apart from the threefold repetition rule.

#### Q: Why do some messages from the bot tweet a timestamp?

A: The bot uses this as a workaround to avoid twitter's duplicate tweet detection.

#### Q: Why can't multiple players "fork" the game off?

A: This is a feature being considered for future development. Let me know if you're interested.

#### Q: These are some nice chessboard images. What's the magic?

A: There's an excellent python library called [python-chess](https://github.com/niklasf/python-chess) which handles not only the graphics, but really everything about the chess gameplay. This bot is essentially a twitter interface to that library.

#### Q: What other non-standard code libraries are used?

A: [CairoSVG](https://github.com/Kozea/CairoSVG) for converting the svg output of python-chess, and [tweepy](https://github.com/tweepy/tweepy) for interfacing with twitter.

## TODO

* Unit tests probably.
* Verify all error handling cases.
