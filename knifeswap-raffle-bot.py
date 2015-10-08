# Written by: /u/uberfastman

import time
import praw
import random
import os
import datetime
import logging
import sys

print "STARTING KNIFESWAP-RAFFLE-BOT..."

r = praw.Reddit(user_agent="knifeswap_raffle_automator 1.0 by /u/uberfastman")
r.login(os.environ["REDDIT_USER"], os.environ["REDDIT_PASS"])

# subreddit = r.get_subreddit("knife_swap")
subreddit = r.get_subreddit("bot_testing_ground")

python_mod_list = [str(mod) for mod in r.get_moderators(subreddit)]

# logging.basicConfig(filename="raffle_bot_log.txt", level=logging.INFO)

already_parsed_comments = []
# with open("saved_parsed_comments.txt", "r") as parse_history:
#     already_parsed_comments = parse_history.read().splitlines()


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
        start_time = datetime.datetime.now() - datetime.timedelta(hours=4)

        print "Started loop to parse new posts in /r/%s at %s" % (subreddit, str(start_time))

        # limit: controls number of new comments retrieved
        for submission in subreddit.get_new(limit=50):

            # sets the submission id
            submission_id = str(submission.id)

            # sets the original poster of the submission
            submission_author = str(submission.author)

            # limit: take no more than this # of requests; threshold: requests must result in this many additional comments
            submission.replace_more_comments(limit=None, threshold=1)

            # flattens the comments for easy parsing
            flat_comments = praw.helpers.flatten_tree(submission.comments)

            comment_author_parent_tuple = []
            for comment in flat_comments:

                temp_author = str(comment.author)
                comment_parent_id = str(comment.parent_id).split("_")[1]

                temp_pair = [temp_author, comment_parent_id]

                comment_author_parent_tuple.append(temp_pair)

            already_replied_list = []
            for pair in comment_author_parent_tuple:
                if pair[0] == "KNIFESWAP_RAFFLE_BOT":
                    already_replied_list.append(pair[1])

            for comment in flat_comments:

                comment_author = str(comment.author)

                comment_id = str(comment.id).strip()

                comment_link = str(comment.permalink)

                comment_body = comment.body.lower()

                krb_is_not_author = True
                if comment_author == "KNIFESWAP_RAFFLE_BOT":
                    krb_is_not_author = False

                # checks if to make sure comment has not been parsed already
                if comment_id not in already_parsed_comments and comment_id not in already_replied_list:

                    # checks /u/KNIFE_RAFFLE_BOT is not comment author and comment contains 'knifeswap', 'raffle', and 'slots'
                    if krb_is_not_author and "knifeswap" in comment_body and "raffle" in comment_body and "slots" in comment_body:

                        # checks that raffle caller is either OP or a mod of /r/Knife_Swap
                        if submission_author == comment_author or comment_author in python_mod_list:

                            comment_word_list = comment.body.split(" ")

                            total_slots = 0

                            for word in comment_word_list:

                                # parses any number strings in the comment to integers
                                slots = parse_to_integer(word)

                                if slots != 0 and total_slots == 0:
                                    total_slots = slots

                                else:
                                    pass

                            # if a slot total was included, randomly determines a winner from the slot range
                            if total_slots != 0:

                                winner = random.randint(0, total_slots)

                                comment_msg = "Thank you for hosting a raffle on /r/%s with %d slots.\n\nThe winner of the raffle is the redditor who chose raffle slot number %d!\n\n\n&nbsp;\n\n\n[^^Contact ^^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^^| [^^Source ^^Code](https://github.com/uberfastman/knifeswap-raffle-bot)" % (str(subreddit), total_slots, winner)

                                # logging.info("Raffle was drawn for comment at %s" % comment_link)
                                print "Raffle was drawn for comment at %s" % comment_link

                            else:
                                comment_msg = "No number of slots for the raffle was specified. Please try again.\n\n\n&nbsp;\n\n\n[^^Contact ^^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^^| [^^Source ^^Code](https://github.com/uberfastman/knifeswap-raffle-bot)"

                                # logging.info("Raffle was attempted but needed slot number for comment at %s" % comment_link)
                                print "Raffle was attempted but needed slot number for comment at %s" % comment_link

                            comment.reply(comment_msg)

                        # warns comment poster that they cannot call for a raffle drawing if they are not the original submission poster
                        else:
                            comment_msg = "You are ***NOT*** the submitter of this raffle. You do ***NOT*** have permission to do the raffle drawing.\n\n\n&nbsp;\n\n\n[^^Contact ^^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^^| [^^Source ^^Code](https://github.com/uberfastman/knifeswap-raffle-bot)"

                            # logging.info("Raffle drawing call was made by incorrect user for comment %s" % comment_link)
                            print "Raffle drawing call was made by incorrect user for comment %s" % comment_link

                            comment.reply(comment_msg)

                    # with open("saved_parsed_comments.txt", "a") as parse_history:
                    #     parse_history.write(comment_id + "\n")

                    already_parsed_comments.append(comment_id)
            if already_replied_list:
                print "/u/KNIFESWAP_RAFFLE_BOT already commented on comments with IDs %s in submission with ID '%s'." % (str(already_replied_list), submission_id)

        current_time = datetime.datetime.now() - datetime.timedelta(hours=4)

        # logging.info("The loop parsing new posts in /r/%s last executed at %s and took %s to run" % (str(subreddit), str(current_time), str(current_time - start_time)))
        print "The loop parsing new posts in /r/%s last executed at %s and took %s to run" % (str(subreddit), str(current_time), str(current_time - start_time))

    # catches any exceptions and sends /u/uberfastman a private message with the error
    except Exception as e:
        private_message = "ERROR: %s (line %s)" % (e, sys.exc_info()[-1].tb_lineno)
        r.send_message("uberfastman", "KNIFESWAP RAFFLE BOT ERROR!", private_message)

        # logging.error("KNIFESWAP_RAFFLE_BOT encountered error: %s (line %s)" % (e, sys.exc_info()[-1].tb_lineno))
        print "ERROR: %s (line %s)" % (e, sys.exc_info()[-1].tb_lineno)
        pass

    # time_check = datetime.datetime.now() - datetime.timedelta(hours=4)
    # midnight = time_check.replace(hour=0, minute=0, second=0, microsecond=0)
    # time_diff = time_check - midnight
    # sec_diff = time_diff.seconds

    # if 27900 < sec_diff < 85500:
        # logging.info("Starting daytime sleep at %s for 15 minutes." % str(time_check.time()))
        # print "Starting daytime sleep at %s for 15 minutes." % str(time_check.time())
        # time.sleep(900)
    # else:
        # logging.info("Starting nighttime sleep at %s and will awaken again in 8 hours." % str(time_check.time()))
        # print "Starting nighttime sleep at %s and will awaken again in 8 hours." % str(time_check.time())
        # time.sleep(28800)

    # sleep for 10 minutes between runs
    print "Starting 10 minute sleep before next run."
    time.sleep(30)
