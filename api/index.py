from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from the parent directory
from app import app as application

# This is the entry point for Vercel
app = application 
