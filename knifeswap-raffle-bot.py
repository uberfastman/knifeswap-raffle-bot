# Written by: /u/uberfastman

import time
import praw
import random
import os
import datetime

reddit_object = praw.Reddit(user_agent="knifeswap_raffle_bot 1.0 by /u/uberfastman")
reddit_object.login(os.environ["REDDIT_USER"], os.environ["REDDIT_PASS"])


def parseToInteger(string):

    num_slots = 0

    try:
        int(string)
        num_slots = int(string)

    except ValueError:
        pass

    return num_slots


already_parsed_comments = set()

# count = 0
# while count < 5:
while True:

    try:

        subreddit = reddit_object.get_subreddit("knife_swap")

        # for submission in subreddit.get_new(limit=10):
        for submission in subreddit.get_new(limit=25):

            submission_commentor = submission.author

            flat_comments = praw.helpers.flatten_tree(submission.comments)

            for comment in flat_comments:

                if comment.id not in already_parsed_comments and "knifeswap" in comment.body.lower() and "raffle" in comment.body.lower():

                    if submission_commentor == comment.author:

                        comment_word_list = comment.body.split(" ")

                        total_slots = 0

                        for word in comment_word_list:

                            slots = parseToInteger(word)

                            if slots != 0:
                                total_slots = slots

                            else:
                                pass

                        if total_slots != 0:

                            winner = random.randint(0, total_slots)

                            comment_msg = "Thank you for hosting a raffle on /r/Knife_Swap with %d slots.\n\nThe winner of the raffle is the redditor who chose raffle slot number %d!\n\n\n&nbsp;\n\n\n^(If you have any questions about the working of this bot, please send a private message to its creator, /u/uberfastman.)" % (total_slots, winner)

                        else:
                            comment_msg = "No number of slots for the raffle was specified. Please try again.\n\n\n&nbsp;\n\n\n^(If you have any questions about the working of this bot, please send a private message to its creator, /u/uberfastman.)"

                        # print comment_msg

                        comment.reply(comment_msg)
                        already_parsed_comments.add(comment.id)

                    else:
                        comment_msg = "You are ***NOT*** the submitter of this raffle. You do ***NOT*** have permission to do the raffle drawing.\n\n\n&nbsp;\n\n\n^(If you have any questions about the working of this bot, please send a private message to its creator, /u/uberfastman.)"
                        comment.reply(comment_msg)
                        already_parsed_comments.add(comment.id)

        # count += 1
        current_time = datetime.datetime.now()
        print "The loop parsing new posts in /r/knife_swap last executed on: " + str(current_time)

    except Exception as e:
        private_message = "Your bot /u/KNIFESWAP_RAFFLE_B0T encountered the following error: %s. Please log on to Heroku and debug it." % e
        reddit_object.send_message("uberfastman", "KNIFESWAP RAFFLE BOT ERROR!", private_message)
        break

    # sleeps for 15 minutes before repeating the loop
    time.sleep(900)
