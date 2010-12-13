# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

# ------------------------------------------------------------------------------
# Execute this file to test basic functionality of ODEN
# ------------------------------------------------------------------------------

# TODO:
# Replace those test with unittest or something like that whenever a lot of
# spare time time flies by

import config
from handlers import helper
from data import people
from data import user

# Switch to database 'oden-test' while testing
config.mongo_db = "oden-test"

# Counters
success         = 0
fail            = 0

# Disable/Enable tests
test_rsa                = False
test_new_people         = False
test_new_user           = False
test_get_user_by_user   = False
test_get_user_by_id     = False
test_get_people_by_id   = True

# Run selected tests
# ------------------------------------

# RSA key generation
if test_rsa:
    print "Generating 4096 bit RSA key pair..."
    try:
        res = helper.generate_rsa(4096)
        if res:
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1


# MongoDB People object add
if test_new_people or test_get_people_by_id:
    print "Creating a new people object..."
    try:
        tmp = people.People()
        res = tmp.new(1337,"handle@test.com","pubkey","podurl")
        _people_id = res
        if res:
            print " - Success"
            success += 1
        else:
            print " - Fail ( " +tmp.debug + ")"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1

# MongoDB User object add
if test_new_user or test_get_user_by_id or test_get_user_by_user:
    print "Creating a new user object..."
    try:
        tmp = user.User()
        res = tmp.new("testman","wordup","testman@testmanpod.com")
        _id = tmp.object_id
        _user = "testman"
        if res:
            print " - Success"
            success += 1
        else:
            print " - Fail (" + tmp.debug + ")"
            fail +=1
    except:
        print "Epic fail"
        fail +=1

# MongoDB Get user by id
if test_get_user_by_id:
    print "Searching for user by id..."
    try:
        tmp = user.User().get_by_id(_id)
        if tmp[u'email'] == "testman@testmanpod.com":
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print "Epic fail"
        fail +=1

# MongoDB Get user by username
if test_get_user_by_user:
    print "Searching for user by username..."
    try:
        tmp = user.User().get_by_username(_user)
        if tmp[u'email'] == "testman@testmanpod.com":
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print "Epic fail"
        fail +=1

# MongoDB Get people by id
if test_get_people_by_id:
    print "Searching for people by id..."
    #try:
    tmp = people.People().get_by_id(_people_id)
    if tmp[u'_id'] == _people_id:
        print " - Success"
        success += 1
    else:
        print " - Fail ( " + tmp.debug + ")"
        fail +=1
    #except:
    #    print "Epic fail"
    #    fail +=1

# DONE TESTING  --  PRINT RESULTS!
print "----------------------------------------------------\nTesting done\n-----------------------------------------------------------"
if fail == 0:
    print "All tests passed! (%i/%i)" % (success,success+fail)
else:
    print "Ooooooops! (%i/%i) passed" % (success,success+fail)


