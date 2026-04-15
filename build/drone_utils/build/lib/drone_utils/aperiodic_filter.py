#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APERIODIC FILTER (First-Order Lag Element)
Апериодическое звено первой степени в дискретном виде
"""

import numpy as np
from typing import Optional


class AperiodicFilter:
    """
    Апериодическое звено первой степени (инерционное звено)
    
    Передаточная функция: W(s) = K / (T*s + 1)
    Дискретная форма: y[k] = α * x[k] + (1 - α) * y[k-1]
    где α = Δt / (T + Δt)
    
    Parameters:
    -----------
    time_constant : float
        Постоянная времени T (секунды). Определяет инерционность фильтра.
        Чем больше T, тем более сглаженный выход.
    gain : float
        Коэффициент усиления K (обычно 1.0)
    """
    
    def __init__(self, time_constant: float = 0.1, gain: float = 1.0):
        self.T = time_constant  # Постоянная времени
        self.K = gain           # Коэффициент усиления
        self.y_prev: Optional[np.ndarray] = None  # Предыдущее значение выхода
        self.initialized = False
    
    def reset(self):
        """Сброс состояния фильтра"""
        self.y_prev = None
        self.initialized = False
    
    def update(self, x: np.ndarray, dt: float) -> np.ndarray:
        """
        Обновление фильтра с новым измерением
        
        Parameters:
        -----------
        x : np.ndarray
            Входной сигнал (измерение)
        dt : float
            Временной шаг (секунды)
        
        Returns:
        --------
        y : np.ndarray
            Отфильтрованный выход
        """
        if not self.initialized:
            # Инициализация первым значением
            self.y_prev = x.copy()
            self.initialized = True
            return self.y_prev
        
        # Вычисляем коэффициент α
        alpha = dt / (self.T + dt)
        
        # Дискретное уравнение апериодического звена
        y = alpha * self.K * x + (1.0 - alpha) * self.y_prev
        
        # Сохраняем для следующей итерации
        self.y_prev = y.copy()
        
        return y
    
    def set_time_constant(self, time_constant: float):
        """Изменить постоянную времени"""
        self.T = time_constant


class AdaptiveAperiodicFilter(AperiodicFilter):
    """
    Адаптивное апериодическое звено с изменяемой постоянной времени
    в зависимости от скорости изменения сигнала
    """
    
    def __init__(self, 
                 time_constant_slow: float = 0.2,
                 time_constant_fast: float = 0.05,
                 velocity_threshold: float = 0.5,
                 gain: float = 1.0):
        """
        Parameters:
        -----------
        time_constant_slow : float
            Постоянная времени для медленных изменений (больше сглаживание)
        time_constant_fast : float
            Постоянная времени для быстрых изменений (меньше задержка)
        velocity_threshold : float
            Порог скорости для переключения режимов (м/с)
        """
        super().__init__(time_constant_slow, gain)
        self.T_slow = time_constant_slow
        self.T_fast = time_constant_fast
        self.velocity_threshold = velocity_threshold
        self.x_prev: Optional[np.ndarray] = None
    
    def update(self, x: np.ndarray, dt: float) -> np.ndarray:
        """Обновление с адаптивной постоянной времени"""
        
        if not self.initialized:
            self.x_prev = x.copy()
            self.y_prev = x.copy()
            self.initialized = True
            return self.y_prev
        
        # Оцениваем скорость изменения сигнала
        if self.x_prev is not None and dt > 0:
            velocity = np.linalg.norm(x - self.x_prev) / dt
            
            # Адаптивно выбираем постоянную времени
            if velocity > self.velocity_threshold:
                # Быстрое изменение - уменьшаем инерцию
                self.T = self.T_fast
            else:
                # Медленное изменение - увеличиваем сглаживание
                self.T = self.T_slow
        
        self.x_prev = x.copy()
        
        # Применяем базовый фильтр
        return super().update(x, dt)
