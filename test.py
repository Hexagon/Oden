# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

# ------------------------------------------------------------------------------
# Execute this file to test basic functionality of ODEN
# ------------------------------------------------------------------------------

# TODO:
# Replace these tests with unittest

import config
from handlers import helper
from data import people
from data import user
from data import aspects

# Switch to database 'oden-test' while testing
config.mongo_db = "oden-test"

# Counters
success         = 0
fail            = 0

# Disable/Enable tests
teste_magicsig          = True
test_rsa                = False
test_new_people         = False
test_new_user           = False
test_new_aspect         = False
test_get_user_by_user   = False
test_get_user_by_id     = False
test_get_people_by_id   = False


# Run selected tests
# ------------------------------------
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

# MongoDB Aspect object add
if test_new_user or test_get_user_by_id or test_get_user_by_user:
    print "Creating a new aspect..."
    try:
        tmp = aspects.Aspects()
        res = tmp.new("Foo",_id)             # _id is assigned in test_new_user
        _aspect_id = tmp.object_id
        tmp_aspect = aspects.Aspects()
        tmp_aspect.get_by_id(_aspect_id)
        if res and tmp_aspect.data[u'name'] == "Foo":
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


