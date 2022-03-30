import aiohttp_session
from aiohttp.web import HTTPFound, Request, Response, RouteTableDef
from aiohttp_jinja2 import template

import discord
from discord.ext import vbu

routes = RouteTableDef()
