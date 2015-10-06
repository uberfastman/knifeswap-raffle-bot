# Written by: /u/uberfastman

import time
import praw
import random
import os
import datetime
import logging

r = praw.Reddit(user_agent="knifeswap_raffle_automator 1.0 by /u/uberfastman")
r.login(os.environ["REDDIT_USER"], os.environ["REDDIT_PASS"])

logging.basicConfig(filename="raffle_bot_log.txt", level=logging.INFO)

saved_parsed_comments = open("saved_parsed_comments.txt", "a")
already_parsed_comments = [line.strip for line in open("saved_parsed_comments.txt", "r")]


def parse_to_integer(string):

    num_slots = 0

    try:
        int(string)
        num_slots = int(string)

    except ValueError:
        pass

    return num_slots

while True:

    try:

        subreddit = r.get_subreddit("knife_swap")

        # limit: controls number of new comments retrieved
        for submission in subreddit.get_new(limit=25):

            # sets the original poster of the submission
            submission_commentor = submission.author

            # limit: take no more than this number of requests; threshold: only make requests that will result in at least 10 additional commments
            submission.replace_more_comments(limit=None, threshold=1)

            # flattens the comments for easy parsing
            flat_comments = praw.helpers.flatten_tree(submission.comments)

            for comment in flat_comments:

                # checks if to make sure comment has not been parsed already and that it contains the words 'knifeswap' and 'raffle'
                if comment.id not in already_parsed_comments and "knifeswap" in comment.body.lower() and "raffle" in comment.body.lower() and comment.author != "KNIFESWAP_RAFFLE_BOT" and "knifeswap_raffle_bot" not in comment.body.lower():

                    # checks to make sure the poster of the comment calling for a raffle drawing was made by the submission poster
                    if submission_commentor == comment.author:

                        comment_word_list = comment.body.split(" ")

                        total_slots = 0

                        for word in comment_word_list:

                            # parses any number strings in the comment to integers
                            slots = parse_to_integer(word)

                            if slots != 0:
                                total_slots = slots

                            else:
                                pass

                        # if a slot total was included, randomly determines a winner from the slot range
                        if total_slots != 0:

                            winner = random.randint(0, total_slots)

                            comment_msg = "Thank you for hosting a raffle on /r/Knife_Swap with %d slots.\n\nThe winner of the raffle is the redditor who chose raffle slot number %d!\n\n\n&nbsp;\n\n\n[^Contact ^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^| [^Source ^Code](https://github.com/uberfastman/knifeswap-raffle-bot)" % (total_slots, winner)
                            logging.info("Raffle was drawn for comment at %s" % str(comment.permalink))

                        else:
                            comment_msg = "No number of slots for the raffle was specified. Please try again.\n\n\n&nbsp;\n\n\n[^Contact ^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^| [^Source ^Code](https://github.com/uberfastman/knifeswap-raffle-bot)"

                            logging.info("Raffle was attempted but needed slot number for comment at %s" % str(comment.permalink))

                        comment.reply(comment_msg)
                        saved_parsed_comments.write(comment.id)
                        already_parsed_comments.append(comment.id)

                    # warns comment poster that they cannot call for a raffle drawing if they are not the original submission poster
                    else:
                        comment_msg = "You are ***NOT*** the submitter of this raffle. You do ***NOT*** have permission to do the raffle drawing.\n\n\n&nbsp;\n\n\n[^Contact ^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^| [^Source ^Code](https://github.com/uberfastman/knifeswap-raffle-bot)"

                        logging.info("Raffle drawing call was made by incorrect user for comment %s" % str(comment.permalink))

                        comment.reply(comment_msg)
                        saved_parsed_comments.write(comment.id)
                        already_parsed_comments.append(comment.id)

        current_time = datetime.datetime.now() - datetime.timedelta(hours=4)
        logging.info("The loop parsing new posts in /r/knife_swap last executed on: " + str(current_time))
        print "The loop parsing new posts in /r/knife_swap last executed on: " + str(current_time)

    # catches any attribute errors and sends /u/uberfastman a private message with the error
    except AttributeError as e:
        private_message = "Your bot /u/KNIFESWAP_RAFFLE_B0T encountered the following error: %s." % e
        r.send_message("uberfastman", "KNIFESWAP RAFFLE BOT ERROR!", private_message)
        logging.error("KNIFESWAP_RAFFLE_BOT encountered error: %s" % e)
        print "ERROR: %s" % e
        saved_parsed_comments.close()
        pass

    except Exception as e:
        private_message = "Your bot /u/KNIFESWAP_RAFFLE_B0T encountered the following error: %s." % e
        r.send_message("uberfastman", "KNIFESWAP RAFFLE BOT ERROR!", private_message)
        logging.error("KNIFESWAP_RAFFLE_BOT encountered error: %s" % e)
        print "ERROR: %s" % e
        saved_parsed_comments.close()
        pass

    # sleeps for 15 minutes before repeating the loop
    time.sleep(900)
