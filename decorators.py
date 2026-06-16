# -*- coding: utf-8 -*-
from odoo import api

def endpoint(name=None):
    def decorator(func):
        func._is_endpoint = True
        func._endpoint_name = name or func.__name__.replace('_', ' ').title()
        
        return api.model(func)
    return decorator