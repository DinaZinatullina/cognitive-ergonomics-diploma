import random
from .models import EquipmentState

def tick_equipment():
    state, _ = EquipmentState.objects.get_or_create(id=1)

    # Температура растет медленнее (например, от +0.1 до +0.4 градуса за тик)
    state.temperature += random.uniform(0.1, 0.4)
    
    # Давление тоже растет медленнее
    state.pressure += random.uniform(0.01, 0.03)

    # Уровень жидкости падает
    state.tank_level -= random.uniform(0.05, 0.15)

    # Ограничения
    if state.temperature > 110: state.temperature = 110
    if state.pressure > 3.5: state.pressure = 3.5
    if state.tank_level < 10: state.tank_level = 10

    # Проверка на аварию
    state.is_temperature_critical = state.temperature >= 95.0
    state.is_pressure_critical = state.pressure >= 3.0

    state.save()
    return state