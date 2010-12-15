#!/usr/bin/python2.4
#
# Copyright 2010 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Exceptions for magicsigs package."""

__author__ = 'hjfreyer@google.com (Hunter Freyer)'


class Error(Exception):
  pass

class EnvelopeFormatError(Error):
  pass

class EnvelopeProtocolError(Error):
  pass

class UnsupportedAlgorithmError(Error):
  pass

class UnsupportedEncodingError(Error):
  pass

class KeyNotFoundError(Error):
  pass

class AuthorNotFoundError(Error):
  pass
