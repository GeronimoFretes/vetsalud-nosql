SERVICES = {
    1: {
        "module": "src.services.service_01_pacientes_activos",
        "description": "Pacientes activos con datos de propietario",
    },
    2: {
        "module": "src.services.service_02_consultas_seguimiento",
        "description": "Consultas en seguimiento con veterinario asignado y costo",
    },
    3: {
        "module": "src.services.service_03_historial_paciente",
        "description": "Historial completo de paciente",
    },
    4: {
        "module": "src.services.service_04_propietarios_multiples_pacientes",
        "description": "Propietarios con más de un paciente",
    },
    5: {
        "module": "src.services.service_05_veterinarios_consultas_60_dias",
        "description": "Veterinarios activos y consultas en últimos 60 días",
    },
    6: {
        "module": "src.services.service_06_vacunas_vencidas",
        "description": "Pacientes con vacunas vencidas",
    },
    7: {
        "module": "src.services.service_07_top_diagnosticos",
        "description": "Top 5 diagnósticos más frecuentes",
    },
    8: {
        "module": "src.services.service_08_stock_bajo",
        "description": "Stock menor a 50 unidades con proveedor",
    },
    9: {
        "module": "src.services.service_09_controles_bajo_costo",
        "description": "Consultas Control con costo menor a 5000",
    },
    10: {
        "module": "src.services.service_10_pacientes_por_sucursal",
        "description": "Pacientes por sucursal a través del veterinario",
    },
    11: {
        "module": "src.services.service_11_ingresos_mes_actual",
        "description": "Ingresos totales por veterinario en el mes actual",
    },
    12: {
        "module": "src.services.service_12_propietarios_sin_consultas_anio",
        "description": "Propietarios sin consultas en el último año",
    },
    13: {
        "module": "src.services.service_13_abm_propietarios",
        "description": "ABM completo de propietarios",
    },
    14: {
        "module": "src.services.service_14_registrar_consulta",
        "description": "Registro de nueva consulta con validación",
    },
    15: {
        "module": "src.services.service_15_actualizar_stock",
        "description": "Actualización masiva de stock tras consulta",
    },
}