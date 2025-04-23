import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import re
import io
from dotenv import load_dotenv
import os
from googleapiclient.discovery import build
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from ytmusicapi import YTMusic
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import jwt
import requests

