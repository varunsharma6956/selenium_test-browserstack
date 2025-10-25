"""Utility modules for El País scraper."""

from .scraper import ElPaisScraper
from .translator import RapidTranslator
from .analyzer import TextAnalyzer

__all__ = ['ElPaisScraper', 'RapidTranslator', 'TextAnalyzer']