import random
from .models import EquipmentState


def tick_equipment():
    """
    Делает один шаг симуляции. Изменяет параметры установки
    и возвращает обновленное состояние.
    """
    state, _ = EquipmentState.objects.get_or_create(id=1)

    # Температура: случайно гуляет в пределах +- 2 градуса
    # Но если она уже высокая, растет быстрее (имитация разгона)
    temp_delta = random.uniform(-1.5, 2.0)
    state.temperature += temp_delta
    
    # Давление зависит от температуры (физика)
    pressure_delta = temp_delta * 0.02 + random.uniform(-0.05, 0.06)
    state.pressure += pressure_delta

    # Уровень жидкости постепенно падает
    state.tank_level -= random.uniform(0.1, 0.5)

    # Ограничения и проверка на аварии
    state.is_temperature_critical = state.temperature >= 95.0
    state.is_pressure_critical = state.pressure >= 3.0

    # Если достигли пика, сбрасываем, чтобы не уйти в бесконечность
    if state.temperature > 110: state.temperature = 110
    if state.temperature < 50: state.temperature = 50
    
    if state.pressure > 3.5: state.pressure = 3.5
    if state.pressure < 1.0: state.pressure = 1.0
    
    if state.tank_level < 10: state.tank_level = 10
    if state.tank_level > 100: state.tank_level = 100

    state.save()
    return state