"""
各種必要なパッケージを呼び出す
"""
import discord 
from discord import app_commands 
from discord.ext import tasks
import waitress.server

from enum import Enum
from datetime import datetime, timedelta
from collections import deque
import subprocess
import threading
import asyncio
import platform
import os
from shutil import copystat,Error,copy2,copytree
import sys
import logging
import requests
import json

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response, flash
from ansi2html import Ansi2HTMLConverter
import waitress
import io