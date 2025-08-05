#!ignore
import sys
#!end-ignore

try:
    from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response, flash
    from ansi2html import Ansi2HTMLConverter
    import waitress

    import discord 
    from discord import app_commands 
    from discord.ext import tasks
    import waitress.server
    import requests

    import aiohttp

    import psutil

    from fastapi import FastAPI, HTTPException
    from fastapi.responses import StreamingResponse
    import uvicorn
    import zipstream  # pip install zipstream-ng
    from fastapi.middleware.wsgi import WSGIMiddleware
except:
    print("import error. please run 'pip install -r requirements.txt'")
    sys.exit(1)