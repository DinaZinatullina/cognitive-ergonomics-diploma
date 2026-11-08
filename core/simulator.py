import random
from .models import EquipmentState

def tick_equipment():
    state, _ = EquipmentState.objects.get_or_create(id=1)

    # Запоминаем прошлые значения, чтобы посчитать тренд
    prev_temp = state.temperature
    prev_pressure = state.pressure

    # Температура и давление растут
    state.temperature += random.uniform(0.1, 0.4)
    state.pressure += random.uniform(0.01, 0.03)
    state.tank_level -= random.uniform(0.05, 0.15)

    # Ограничения
    if state.temperature > 110: state.temperature = 110
    if state.pressure > 3.5: state.pressure = 3.5
    if state.tank_level < 10: state.tank_level = 10

    # Считаем тренд (скорость изменения за тик)
    temp_trend = state.temperature - prev_temp
    pressure_trend = state.pressure - prev_pressure

        # Предупреждение, если температура подходит к 90, или давление к 2.8
    is_predictive_warning = (state.temperature > 90.0) or (state.pressure > 2.8)

    # Авария
    state.is_temperature_critical = state.temperature >= 95.0
    state.is_pressure_critical = state.pressure >= 3.0

    # АВТОМАТИЧЕСКАЯ ЗАЩИТА (Защита от дурака)
    # Если нагрузка оператора была высокой (мы передадим это из view), 
    # но пока симулируем: если температура > 98, а давление > 3.2, сбрасываем всё автоматически
    if state.temperature > 98.0 and state.pressure > 3.2:
        # Система берет управление на себя
        state.temperature -= 20.0
        state.pressure -= 0.8
        state.tank_level += 10.0
        # Флаг, что сработала авто-защита
        state.is_auto_protected = True 
    else:
        state.is_auto_protected = False

    state.save()
    
    return state, is_predictive_warning