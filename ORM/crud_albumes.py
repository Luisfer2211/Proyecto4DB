from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy.orm import sessionmaker
from orm_models import engine, VistaCancionesCompletas
from models import Cancion, Album, Usuario, Genero, CancionGenero
from datetime import timedelta
from sqlalchemy import select
from flask import jsonify
from collections import defaultdict
from sqlalchemy import text
from flask import send_file
import csv
import io
import json
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

@crud_canciones.route("/albumes")
def vista_albumes():
    session = Session()
    albumes = session.query(VistaAlbumesDetalles).all()
    session.close()
    return render_template("albumes/index.html", albumes=albumes)
