from PySide6.QtCore import QObject, QEvent, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QScrollArea

class SmoothScrollFilter(QObject):
    """
    A global event filter that intercepts wheel events on QScrollAreas
    and animates the scrollbar for a smooth scrolling effect.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animations = {}

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Wheel:
            # Check if the object being scrolled is inside a QScrollArea viewport
            scroll_area = None
            parent = obj
            
            # Traverse up to 5 levels to find if it's inside a QScrollArea
            for _ in range(5):
                if parent is None:
                    break
                if isinstance(parent, QScrollArea):
                    scroll_area = parent
                    break
                parent = parent.parent()
                
            if scroll_area is not None:
                vbar = scroll_area.verticalScrollBar()
                if vbar and vbar.isVisible():
                    # Calculate new value
                    delta = event.angleDelta().y()
                    if delta == 0:
                        return super().eventFilter(obj, event)
                        
                    # Standard wheel event gives 120 per notch
                    # Let's scroll 120 pixels per notch for a smooth feel
                    step = - (delta / 120.0) * 120.0
                    
                    # Stop current animation if any
                    anim = self.animations.get(id(vbar))
                    if anim:
                        current_val = anim.endValue()
                        anim.stop()
                    else:
                        current_val = vbar.value()
                        anim = QPropertyAnimation(vbar, b"value", self)
                        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                        anim.setDuration(350) # 350ms smooth decay
                        anim.finished.connect(lambda v=vbar: self.animations.pop(id(v), None))
                        self.animations[id(vbar)] = anim
                    
                    target_val = current_val + step
                    # Clamp to min/max
                    target_val = max(vbar.minimum(), min(vbar.maximum(), target_val))
                    
                    if current_val != target_val:
                        anim.setStartValue(vbar.value())
                        anim.setEndValue(target_val)
                        anim.start()
                    
                    return True # Event handled
        
        return super().eventFilter(obj, event)

def install_smooth_scrolling(app):
    """Installs the smooth scrolling filter globally on the application."""
    filter = SmoothScrollFilter(app)
    app.installEventFilter(filter)
    return filter
