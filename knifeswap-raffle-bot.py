# Written by: /u/uberfastman

import time
import praw
import random
import os
import datetime
import sys
import unicodedata

print "STARTING KNIFESWAP-RAFFLE-BOT..."

r = praw.Reddit(user_agent="knifeswap_raffle_automator 1.0 by /u/uberfastman")

# r.set_oauth_app_info(client_id="CLIENT_ID", client_secret="CLIENT_SECRET", redirect_uri="http://127.0.0.1:65010/authorize_callback")

r.login(os.environ["REDDIT_USER"], os.environ["REDDIT_PASS"])

subreddit = r.get_subreddit("knife_swap")
# subreddit = r.get_subreddit("bot_testing_ground")

python_mod_list = [str(mod) for mod in r.get_moderators(subreddit)]

already_parsed_comments = []


def parse_to_integer(string):

    num_slots = 0

    try:
        int(string)
        num_slots = int(string)

    except ValueError:
        pass

    return num_slots

while True:

    exception_list = []

    try:
        start_time = datetime.datetime.now() - datetime.timedelta(hours=4)

        print "Started loop to parse new posts in /r/%s at %s" % (subreddit, str(start_time))

        # limit: controls number of new comments retrieved
        for submission in subreddit.get_new(limit=50):

            # sets the submission permalink
            submission_link = unicodedata.normalize('NFKD', submission.permalink).encode('ascii', 'ignore')

            try:

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

                    comment_link = unicodedata.normalize('NFKD', comment.permalink).encode('ascii', 'ignore')

                    try:

                        comment_author = str(comment.author)

                        comment_id = str(comment.id).strip()

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

                                        message_string = "A successful raffle was drawn for submission %s from comment %s with a winning number of %d!" % (submission_link, comment_link, winner)
                                        r.send_message("uberfastman", "SUCCESSFUL RAFFLE!", message_string)

                                        print "Raffle was drawn for comment at %s" % comment_link

                                    else:
                                        comment_msg = "No number of slots for the raffle was specified. Please try again.\n\n\n&nbsp;\n\n\n[^^Contact ^^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^^| [^^Source ^^Code](https://github.com/uberfastman/knifeswap-raffle-bot)"

                                        message_string = "A raffle was attempted without included slots for submission %s from comment %s." % (submission_link, comment_link)
                                        r.send_message("uberfastman", "UNSUCCESSFUL RAFFLE ATTEMPT!", message_string)

                                        print "Raffle was attempted but needed slot number for comment at %s" % comment_link

                                    comment.reply(comment_msg)

                                # warns comment poster that they cannot call for a raffle drawing if they are not the original submission poster
                                else:
                                    comment_msg = "You are ***NOT*** the submitter of this raffle. You do ***NOT*** have permission to do the raffle drawing.\n\n\n&nbsp;\n\n\n[^^Contact ^^Creator](https://www.reddit.com/message/compose/?to=uberfastman) ^^| [^^Source ^^Code](https://github.com/uberfastman/knifeswap-raffle-bot)"

                                    message_string = "An unauthorized raffle call was made in submission %s by user %s in comment %s." % (submission_link, comment_author, comment_link)
                                    r.send_message("uberfastman", "UNAUTHORIZED RAFFLE DRAWING CALL!", message_string)

                                    print "Raffle drawing call was made by incorrect user for comment %s" % comment_link

                                    comment.reply(comment_msg)

                            already_parsed_comments.append(comment_id)

                    except Exception as e:
                        private_message = "ERROR: %s (line %s) for post %s" % (e, sys.exc_info()[-1].tb_lineno, comment_link)
                        exception_list.append(private_message)

                        print private_message
                        pass

                if already_replied_list:
                    print "/u/KNIFESWAP_RAFFLE_BOT already commented on comments with IDs %s in submission with ID '%s'." % (str(already_replied_list), submission_id)

            except Exception as e:
                private_message = "ERROR: %s (line %s) for post %s" % (e, sys.exc_info()[-1].tb_lineno, submission_link)
                exception_list.append(private_message)

                print private_message
                pass

        current_time = datetime.datetime.now() - datetime.timedelta(hours=4)

        print "The loop parsing new posts in /r/%s last executed at %s and took %s to run" % (str(subreddit), str(current_time), str(current_time - start_time))

    except Exception as e:
        private_message = "ERROR: %s (line %s)" % (e, sys.exc_info()[-1].tb_lineno)
        exception_list.append(private_message)

        print private_message
        pass

    # catches any exceptions and sends /u/uberfastman a private message with the errors
    if exception_list:

        message_string = '\n'.join(map(str, exception_list))

        r.send_message("uberfastman", "KNIFESWAP RAFFLE BOT ERROR!", message_string)

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
    time.sleep(600)
