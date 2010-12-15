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
from lib.oden import rsa_helper,aes_helper,salmon
from data import people
from data import user
from data import aspects

# Switch to database 'oden-test' while testing
config.mongo_db = "oden-test"

# Counters
success         = 0
fail            = 0

# Disable/Enable tests
test_rsa                = True
test_aes                = True
test_salmon             = True
test_new_people         = True
test_new_user           = True
test_new_aspect         = True
test_get_user_by_user   = True
test_get_user_by_id     = True
test_get_people_by_id   = True


# Run selected tests
# ------------------------------------
if test_rsa or test_salmon:
    print "Generating 4096 bit RSA key pair..."
    try:
        res = rsa_helper.generate_rsa(4096)
        if res:
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1

if test_rsa or test_salmon:
    print "Encrypting message with public key using rsa_helper..."
    try:
        plain = "Testing encryption"
        cipher = rsa_helper.encrypt(plain,res[0])
        if cipher and cipher != plain:
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1

if test_rsa or test_salmon:
    print "Decrypting message with private key using rsa_helper..."
    try:
        new_plain = rsa_helper.decrypt(cipher,res[1])
        if new_plain == plain:
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1

if test_salmon:
    print "Creating Salmon XML..."
    try:
        salmon_obj = salmon.Salmon("Robin Nilsson","robinnilsson@test.com",res[1],res[0],"Testing testing")
        if salmon_obj:
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1

if test_aes:
    print "Generating 256 bit AES key..."
    try:
        res = aes_helper.get_random_key()
        res2 = aes_helper.get_random_key()
        if res and res != res2:
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1

if test_aes:
    print "Encrypting message using aes_helper..."
    try:
        plain = "Testing encryption"
        cipher = aes_helper.encrypt(plain,res)
        if cipher and cipher != plain:
            print " - Success"
            success += 1
        else:
            print " - Fail"
            fail +=1
    except:
        print " - Epic fail"
        fail +=1

if test_aes:
    print "Decrypting message using aes_helper..."
    try:
        new_plain = aes_helper.decrypt(cipher,res)
        if new_plain.strip() == plain.strip():
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


