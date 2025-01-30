
try:
    from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response, flash
    from ansi2html import Ansi2HTMLConverter
    import waitress

    import discord 
    from discord import app_commands 
    from discord.ext import tasks
    import waitress.server
    import requests
except:
    print("import error. please run 'python3 <thisfile> -reinstall'")