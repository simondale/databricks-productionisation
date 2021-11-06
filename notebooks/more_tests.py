# Databricks notebook source
import unittest

class MoreTests(unittest.TestCase):
  def test_always_succeeds(self):
    self.assertTrue(True)
  def test_always_fails(self):
    self.assertTrue(False)
