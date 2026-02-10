#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de creación de la base de datos de herramientas
Crear tablas:
- herramientas: almacena el inventario de herramientas
- herramientas_movimientos: registra asignaciones y devoluciones
"""

import sqlite3
import os

def crear_base_datos():
    # Asegurarse que existe el directorio database
    if not os.path.exists('database'):
        os.makedirs('database')
    
    # Conectar a la base de datos (la crea si no existe)
    with sqlite3.connect('database/herramientas.db') as conn:
        c = conn.cursor()
        
        # Tabla de herramientas
        c.execute('''
        CREATE TABLE IF NOT EXISTS herramientas (
            codigo TEXT PRIMARY KEY,
            descripcion TEXT NOT NULL,
            categoria TEXT DEFAULT 'General',
            estado TEXT DEFAULT 'disponible' CHECK (estado IN ('disponible', 'asignada')),
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabla de movimientos
        c.execute('''
        CREATE TABLE IF NOT EXISTS herramientas_movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            herramienta_codigo TEXT NOT NULL,
            operario_numero TEXT NOT NULL,
            accion TEXT NOT NULL CHECK (accion IN ('asignar', 'devolver')),
            fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observaciones TEXT DEFAULT '',
            realizado_por TEXT NOT NULL,
            FOREIGN KEY (herramienta_codigo) REFERENCES herramientas (codigo),
            FOREIGN KEY (operario_numero) REFERENCES operarios (numero)
        )
        ''')
        
        # Índices para optimizar búsquedas
        c.execute('CREATE INDEX IF NOT EXISTS idx_herramientas_estado ON herramientas(estado)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_movimientos_herramienta ON herramientas_movimientos(herramienta_codigo)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_movimientos_operario ON herramientas_movimientos(operario_numero)')
        
        print("✅ Base de datos herramientas.db creada exitosamente")
        
        # Datos de ejemplo
        try:
            c.execute('''
            INSERT INTO herramientas (codigo, descripcion, categoria) VALUES
            ('H001', 'Martillo de carpintero', 'Mano'),
            ('H002', 'Destornillador Phillips #2', 'Mano'),
            ('H003', 'Taladro eléctrico 1/2"', 'Eléctrica'),
            ('H004', 'Llave ajustable 12"', 'Mano'),
            ('H005', 'Nivel láser', 'Medición')
            ''')
            print("✅ Datos de ejemplo insertados")
        except sqlite3.IntegrityError:
            print("ℹ️ Los datos de ejemplo ya existían")

if __name__ == '__main__':
    crear_base_datos()