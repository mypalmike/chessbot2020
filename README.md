# chessbot2020

## What is it?

This is a bot that enables people on twitter to play chess against each other.

## Status

It basically works. It is not routinely running on twitter yet, so don't try to play it quite yet.

## How to play chess on twitter

Once it is live (It's not yet!), just tweet something like "Hey @chessbot2020 please start a new game against @otherUsername239814"

The bot will show a new game board and your opponent will have the first move.

When it's your turn, just reply to the bot with a chess move. Both [Standard Algebraic Notation (SAN)](https://en.wikipedia.org/wiki/Algebraic_notation_(chess)) and [Universal Chess Interface (UCI)](https://en.wikipedia.org/wiki/Universal_Chess_Interface) notation should work. If you're confused, just look at the grid. You can generally just type the starting and ending coordinates, like "e2e3" for moving a pawn forward.

## FAQ

#### Q: Why doesn't it always work?

A: There may be bugs in the bot code. Also, twitter will sometimes filter tweets from the bot because some algorithm thinks it's being an annoyance. It's not. I believe "liking" tweets by the bot will help improve twitter's assessment of the bot as a good twitter user, making it less likely to filter out tweets in your timeline from this bot that mention you.

#### Q: Why else doesn't it work?

A: Sometimes twitter will stop you from sending the same tweet in a relatively short amount of time. So if you tweet the same move twice, it will filter out the second tweet. There is a simple workaround. If you try to tweet "e2" twice in a row and the second one fails, try "e2 please" or "e2 anything" or "e2 is the thing I wanna do". As long as it's different, Twitter doesn't seem to consider it a duplicate.

#### Q: Why do some messages from the bot tweet a timestamp?

A: This is the reverse of the previous question. The bot uses this as a workaround for twitter's duplicate tweet detection.

## TODO

* Endgame checks.
* Unit tests.
* Better error handling.
