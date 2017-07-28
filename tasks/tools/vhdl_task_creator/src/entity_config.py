#!/usr/bin/env python3
from page_entity_config import PageEntityConfig

class EntityConfig:
    def __init__(self, entity_name):
        self.entity_name = entity_name
        self.inputs = []
        self.outputs = []
        self.page =  PageEntityConfig(entity_name, self)
        self.page_id = None

