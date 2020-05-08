#!/usr/bin/env python

import logging
import re
import sys
import tempfile
import time
import traceback
import tweepy
import chess
import chess.svg
import cairosvg

MAX_MOVE_LENGTH = 20
IMAGE_SIZE = 600
MY_NAME = 'chessbot2020'
MY_ID = '1251065712023531520'
RE_TO_MOVE = re.compile('To move: @(.*)')
RE_LAST_MOVE = re.compile('Last: .*@(.*)')
RE_BOARD = re.compile('Board: "(.*)"')


class UntweetableException(Exception):

  def __init__(self, msg):
    super().__init__(msg)


class TweetableException(Exception):

  def __init__(self, msg):
    super().__init__(msg)


class ChessState:

  def __init__(self, state_text=None):
    self.last_move = None
    if state_text:
      self.board = chess.Board(state_text)
    else:
      self.board = chess.Board()

  def get_state_text(self):
    return self.board.fen()

  def attempt_move(self, move_text):
    logging.info('Attempting move {}'.format(move_text))
    if len(move_text) > MAX_MOVE_LENGTH:
      raise TweetableException(
          'Your tweet did not contain a legal move.\nTo try again, just reply again to my previous tweet.'
      )
    try:
      self.last_move = self.board.push_san(move_text)
      return
    except:
      pass

    try:
      self.last_move = self.board.push_uci(move_text)
      return
    except:
      raise TweetableException(
          'Your move "{}" was not a legal move.\nTo try again, just reply again to my previous tweet.'
          .format(move_text))

  def generate_png_data(self):
    boardsvg = chess.svg.board(
        self.board,
        size=IMAGE_SIZE,
        lastmove=self.last_move,
        flipped=not self.board.turn)
    return cairosvg.svg2png(boardsvg)

  def is_check(self):
    return self.board.is_check()

  def is_game_over(self):
    return self.board.is_game_over()

  def is_checkmate(self):
    return self.board.is_checkmate()

  def is_stalemate(self):
    return self.board.is_stalemate()

  def is_draw(self):
    return self.is_game_over(
    ) and not self.is_stalemate() and not self.is_checkmate()


class BotTweet:

  def __init__(self, board_state_text, last_move_text, last_move_screen_name,
               next_move_screen_name):
    self.board_state_text = board_state_text
    self.last_move_text = last_move_text
    self.last_move_screen_name = last_move_screen_name
    self.next_move_screen_name = next_move_screen_name

  @classmethod
  def parse(cls, status_text, last_move_text):
    last_move_screen_name = None
    next_move_screen_name = None
    board_state_text = None

    for line in status_text.splitlines():
      m = RE_BOARD.match(line)
      if m:
        board_state_text = m.group(1)
      else:
        m = RE_LAST_MOVE.match(line)
        if m:
          last_move_screen_name = m.group(1)
        else:
          m = RE_TO_MOVE.match(line)
          if m:
            next_move_screen_name = m.group(1)

    if not board_state_text:
      raise UntweetableException('No board_state_text parsed')

    if not last_move_screen_name:
      raise UntweetableException('No last_move_screen_name parsed')

    if not next_move_screen_name:
      raise UntweetableException('No next_move_screen_name parsed')

    return BotTweet(board_state_text, last_move_text, last_move_screen_name,
                    next_move_screen_name)

  def generate_status_text(self, is_check):
    check_text = ''
    if is_check:
      check_text = 'Check!\n'
    return '{}To move: @{}\nLast: {} by @{}\nBoard: "{}"\n'.format(
        check_text,
        self.next_move_screen_name,
        self.last_move_text,
        self.last_move_screen_name,
        self.board_state_text,
    )


class ChessBotListener(tweepy.StreamListener):

  def __init__(self, api):
    tweepy.StreamListener.__init__(self)
    self.api = api

  def fetch_previous_tweet(self, status):
    try:
      status_id = status.in_reply_to_status_id
      previous_status = self.api.get_status(status_id, tweet_mode='extended')
      previous_status.text = previous_status.full_text
      return previous_status
    except:
      pass
    return None

  def on_status(self, status):
    logging.info('Received tweet from {} text is {}.'.format(
        status.author.screen_name, status.text))

    try:
      previous_tweet = self.fetch_previous_tweet(status)

      # Asking for a new game?
      bot_tweet = None
      if 'new game' in status.text and '"new game' not in status.text and "'new game" not in status.text:
        if previous_tweet:
          raise TweetableException(
              'I do not start new games in the middle of a twitter conversation. Try a fresh tweet.'
          )
          tweet_result_no_new_game_in_reply(self)
        else:
          chess_state = ChessState()
          last_player = status.author.screen_name
          try:
            users_mentioned = extract_users_mentioned(status)
            next_player = other_player(users_mentioned, last_player)
          except UntweetableException:
            raise TweetableException(
                'To start a game with someone, please @ mention that person, and only that person, in your tweet.'
            )
          bot_tweet = BotTweet(chess_state.get_state_text(), 'New', last_player,
                               next_player)
          self.tweet_game_state(bot_tweet, chess_state, status.id)
      elif previous_tweet:
        if previous_tweet.author.screen_name != MY_NAME:
          raise UntweetableException('Not a tweet by {}'.format(MY_NAME))

        this_move_screen_name = status.author.screen_name
        this_move_text = parse_move(status.text)
        old_bot_tweet = BotTweet.parse(previous_tweet.text, None)
        if old_bot_tweet.next_move_screen_name != this_move_screen_name:
          raise UntweetableException('Response is not from next player.')

        chess_state = ChessState(old_bot_tweet.board_state_text)
        if chess_state.is_game_over():
          raise UntweetableException('Game is already over.')

        chess_state.attempt_move(this_move_text)

        bot_tweet = BotTweet(chess_state.get_state_text(), this_move_text,
                             old_bot_tweet.next_move_screen_name,
                             old_bot_tweet.last_move_screen_name)

        self.tweet_game_state(bot_tweet, chess_state, status.id)
      else:
        logging.warn(
            'Neither a new game request nor a previous tweet. Doing nothing.')

    except TweetableException as e:
      self.tweet_exception(e, status.author.screen_name, status.id)
    except UntweetableException as e:
      logging.warn('Top-level handler caught UntweetableException {}'.format(e))
    except Exception as e:
      logging.warn('Top-level handler caught unexpected Exception {}'.format(e))

    return True

  def tweet_game_state(self, bot_tweet, chess_state, in_reply_to_status_id):
    logging.info('status is {}, in_reply_to_status_id is {}'.format(
        bot_tweet.generate_status_text(chess_state.is_check()),
        in_reply_to_status_id))

    if chess_state.is_checkmate():
      status = 'Checkmate! @{} beats @{}'.format(
          bot_tweet.last_move_screen_name, bot_tweet.next_move_screen_name)
    elif chess_state.is_stalemate():
      status = '@{} @{} Game ends in a stalemate.'.format(
          bot_tweet.last_move_screen_name, bot_tweet.next_move_screen_name)
    elif chess_state.is_draw():
      status = '@{} @{} Game ends in a draw.'.format(
          bot_tweet.last_move_screen_name, bot_tweet.next_move_screen_name)
    else:
      status = bot_tweet.generate_status_text(chess_state.is_check())

    with tempfile.NamedTemporaryFile(suffix='.png') as f:
      f.write(chess_state.generate_png_data())
      self.api.update_with_media(
          f.name, status=status, in_reply_to_status_id=in_reply_to_status_id)

  def tweet_exception(self, exc, screen_name, in_reply_to_status_id):
    status = '@{} {}\nError time: {}'.format(screen_name, str(exc),
                                             str(time.time()))
    self.api.update_status(
        status=status, in_reply_to_status_id=in_reply_to_status_id)

  def on_exception(self, exc):
    traceback.print_exc(file=sys.stderr)
    return True

  def on_error(self, status_code):
    logging.error('Encountered error with status code: {}'.format(status_code))
    if status_code == 420:
      return False
    return True  # Don't kill the stream

  def on_timeout(self):
    logging.error('Timeout...')
    return True  # Don't kill the stream


def other_player(users_mentioned, player):
  users_mentioned_set = set(users_mentioned)
  if player in users_mentioned_set:
    users_mentioned_set.remove(player)
  if MY_NAME in users_mentioned_set:
    users_mentioned_set.remove(MY_NAME)
  if len(users_mentioned_set) != 1:
    raise UntweetableException(
        'Can not determine username of other player ({} remaining users)'
        .format(len(users_mentioned_set)))
  return users_mentioned_set.pop()


def extract_users_mentioned(status):
  try:
    return [u['screen_name'] for u in status.entities['user_mentions']]
  except:
    logging.info('Could not extract any user mentions due to exception: {}', e)
    return []


def parse_move(status_text):
  # Move texts will start "@mention1 @mention2". Get rid of this.
  words = [w for w in status_text.split(' ') if not w.startswith('@')]

  if words:
    return words[0].strip()
  return ''


def get_creds():
  with open('creds', 'r') as f:
    return [line.strip() for line in f]


def get_auth_api():
  k, s1, t, s2 = get_creds()
  auth = tweepy.OAuthHandler(k, s1)
  auth.set_access_token(t, s2)
  return [auth, tweepy.API(auth)]


def main(argv=sys.argv):
  logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

  logging.warn('Starting')

  auth, api = get_auth_api()
  listener = ChessBotListener(api)
  stream = tweepy.Stream(auth, listener, timeout=3600)

  logging.info('Created stream. Calling stream.filter()...')

  while True:
    try:
      stream.filter(track=['@chessbot2020'])  # follow=[MY_ID])
    except Exception as exc:
      if exc.args and 'timed out' in exc.args:
        pass
      else:
        traceback.print_exc(file=sys.stderr)


if __name__ == '__main__':
  main()
