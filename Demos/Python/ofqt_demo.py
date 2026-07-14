# -*- coding: utf-8 -*-
"""
Launches a demonstration of OpenFrames managed within a qtpy framework

Copyright (c) 2021 Emergent Space Technologies, Inc.
"""

# OS-specific modifications before importing modules
import os
import sys
import platform
import math
currpath = os.path.abspath(os.path.dirname(__file__))

# Tell OSG where to find shader files and images
shaderpath = currpath + os.sep + ".." + os.sep + "Shaders"
imagespath = currpath + os.sep + ".." + os.sep + "Images"
current_file_path = os.environ.get('OSG_FILE_PATH', '')
if current_file_path:
    os.environ['OSG_FILE_PATH'] = current_file_path + os.pathsep + shaderpath + os.pathsep + imagespath
else:
    os.environ['OSG_FILE_PATH'] = shaderpath + os.pathsep + imagespath

if platform.system() == 'Windows': # Windows
    # Python 3.8 no longer searches the topmost (bin) directory
    # when loading shared library dependencies, so we must add it explicitly
    if sys.version_info[:2] >= (3,8):
        os.add_dll_directory(currpath)
    
else: # OSX/Linux
    # Tell OSG where to find plugins
    osglibpath = currpath + os.sep + ".." + os.sep + "lib"
    os.environ['OSG_LIBRARY_PATH'] = osglibpath
        
    if platform.system() == 'Darwin':
        # On OSX 10.15+, some fonts (e.g. Arial.ttf) are moved to the Supplemental folder
        os.environ['OSG_FILE_PATH'] = os.environ['OSG_FILE_PATH'] + os.pathsep + "/System/Library/Fonts/Supplemental"

# Import modules
from qtpy.QtWidgets import *
from qtpy.QtGui import QSurfaceFormat
from qtpy.QtCore import Qt
import OFInterfaces.PyQtOF as PyQtOF
import OFInterfaces.PyOF as PyOF

from qtpy.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, QTimer)
from qtpy.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from qtpy.QtWidgets import (QApplication, QDockWidget, QMainWindow, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.dockWidget = QDockWidget(MainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
        
        self.dockWidget_2 = QDockWidget(MainWindow)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget_2)
        
        self.dockWidget_3 = QDockWidget(MainWindow)
        self.dockWidget_3.setObjectName(u"dockWidget_3")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.dockWidget_3)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi

class MacMainWindow(QMainWindow, Ui_MainWindow):
    """
    Reusable widget used to display a list of bodies and add/delete to a "selected" list.

    """

    def __init__(self):
        """
        Constructor. Calls APIs to get list of available and selected bodies.

        @param id: client using the widget.
        """
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.ofDockWidget = PyQtOF.OFDockWidget(window_type=MyOFDemoWin2)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.ofDockWidget)
        
        # Add controls to left dock widget
        layout = QVBoxLayout()
        self.dockWidgetContents.setLayout(layout)
        
        self.shaderToggleButton = QPushButton("Disable Shader")
        self.shaderToggleButton.clicked.connect(self.toggleShader)
        layout.addWidget(self.shaderToggleButton)
        
        # Add trace mode toggle button
        self.traceModeButton = QPushButton("Disable Trace Mode")
        self.traceModeButton.clicked.connect(self.toggleTraceMode)
        layout.addWidget(self.traceModeButton)
        
        # Add pause/resume button for simulation time
        self.pauseButton = QPushButton("Pause Time")
        self.pauseButton.clicked.connect(self.togglePause)
        layout.addWidget(self.pauseButton)
        
        # Add reset time button
        self.resetTimeButton = QPushButton("Reset Time")
        self.resetTimeButton.clicked.connect(self.resetTime)
        layout.addWidget(self.resetTimeButton)
        
        # Add time display label
        self.timeLabel = QLabel("Simulation Time: 0.00 s")
        self.timeLabel.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.timeLabel)
        
        layout.addStretch()
        
        # Set up timer to update time display
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.updateTimeDisplay)
        self.updateTimer.start(50)  # Update every 50ms

    def applyFont(self):
        pass
    
    def toggleShader(self):
        """Toggle shader on the first orbit"""
        # Access the OpenFrames window and toggle its shader
        ofWindow = self.ofDockWidget.ofwindow
        ofWindow.toggleShader()
        
        # Update button text
        if ofWindow.shaderEnabled:
            self.shaderToggleButton.setText("Disable Shader")
        else:
            self.shaderToggleButton.setText("Enable Shader")
    
    def toggleTraceMode(self):
        """Toggle trace mode on the third orbit"""
        ofWindow = self.ofDockWidget.ofwindow
        ofWindow.toggleTraceMode()
        
        # Update button text
        if ofWindow.traceModeEnabled:
            self.traceModeButton.setText("Disable Trace Mode")
        else:
            self.traceModeButton.setText("Enable Trace Mode")
    
    def togglePause(self):
        """Toggle pause/resume of simulation time"""
        ofWindow = self.ofDockWidget.ofwindow
        ofWindow.togglePause()
        
        # Update button text
        if ofWindow.isPaused:
            self.pauseButton.setText("Resume Time")
        else:
            self.pauseButton.setText("Pause Time")
    
    def resetTime(self):
        """Reset simulation time to zero"""
        ofWindow = self.ofDockWidget.ofwindow
        ofWindow.resetTime()
    
    def updateTimeDisplay(self):
        """Update the time display label with current simulation time"""
        try:
            ofWindow = self.ofDockWidget.ofwindow
            simTime = ofWindow.windowProxy.getTime()
            self.timeLabel.setText(f"Simulation Time: {simTime:.2f} s")
        except Exception:
            pass  # Window may not be fully initialized yet
        
    def closeEvent(self, event):
        self.updateTimer.stop()
        self.ofDockWidget.stopRendering()
        
class MyOFDemoWin1(PyQtOF.OFWindow):
    """
    Inherits PyQtOF.Window for a simple window showing only a Coordinate Axes
    This window is embedded in a tab widget (see below)

    """
    def __init__(self):
        """
        Instantiate a window
        """
        super().__init__(1, 1) # 1x1 window

        # Create scene root
        root = PyOF.CoordinateAxes("CoordinateAxes")

        # Create a manager to handle access to the scene
        fm = PyOF.FrameManager()
        fm.setFrame(root)

        # Add the scene to the window
        self.windowProxy.setScene(fm, 0, 0)

class MyOFDemoWin2(PyQtOF.OFWindow):
    """
    Inherits PyQtOF.Window for a simple standalone window showing only a Sphere
    
    """
    def __init__(self):
        """
        Instantiate a window
        """
        super().__init__(1, 1) # 1x1 window

        # Create scene root with sphere
        root = PyOF.Sphere("Sphere")
        root.setRadius(1.0)
        root.setTextureMap("EarthTexture.bmp")

        # let's also add a circular orbit around the sphere:
        # Create a trajectory with 3 DOF (x, y, z position), 0 optional parameters
        # Keep reference to prevent garbage collection
        self.traj = PyOF.Trajectory(3, 0)
        
        # Create a DrawableTrajectory to visualize the orbit
        self.drawTraj = PyOF.DrawableTrajectory("Orbit", 0.0, 1.0, 0.0, 0.9)  # Green orbit
        self.drawTraj.showAxes(PyOF.ReferenceFrame.NO_AXES)
        self.drawTraj.showAxesLabels(PyOF.ReferenceFrame.NO_AXES)
        self.drawTraj.showNameLabel(False)
        
        # Create a CurveArtist to draw the trajectory as a line
        self.curveArtist = PyOF.CurveArtist(self.traj)
        self.curveArtist.setWidth(4.0)
        self.curveArtist.setColor(0.0, 1.0, 0.0)  # Green color
        self.curveArtist.setShader("Line_Pulse_Thickness.frag")
        self.drawTraj.addArtist(self.curveArtist)
        
        # Generate circular orbit data
        numPoints = 360
        orbitRadius = 2.0  # Orbit at 2x sphere radius
        
        for i in range(numPoints + 1):
            t = (i * 2.0 * math.pi) / numPoints
            x = orbitRadius * math.cos(t)
            y = orbitRadius * math.sin(t)
            z = 0.0
            
            self.traj.addTime(t)
            self.traj.addPosition(x, y, z)
        
        # Add the drawable trajectory to the scene
        root.addChild(self.drawTraj)
        
        # Add a second orbit - smaller radius, inclined 90 degrees, no shader
        self.traj2 = PyOF.Trajectory(3, 0)
        
        self.drawTraj2 = PyOF.DrawableTrajectory("Orbit2", 1.0, 0.5, 0.0, 0.9)  # Yellow/orange orbit
        self.drawTraj2.showAxes(PyOF.ReferenceFrame.NO_AXES)
        self.drawTraj2.showAxesLabels(PyOF.ReferenceFrame.NO_AXES)
        self.drawTraj2.showNameLabel(False)
        
        self.curveArtist2 = PyOF.CurveArtist(self.traj2)
        self.curveArtist2.setWidth(3.0)
        self.curveArtist2.setColor(1.0, 0.5, 0.0)  # Orange color
        # No shader for this orbit
        self.drawTraj2.addArtist(self.curveArtist2)
        self.curveArtist2.setShader("Line_Pulse_Traveling.frag")

        # Generate circular orbit in XZ plane (90 degrees inclined from first orbit)
        orbitRadius2 = 1.5  # Smaller radius
        
        for i in range(numPoints + 1):
            t = (i * 2.0 * math.pi) / numPoints
            x = orbitRadius2 * math.cos(t)
            y = 0.0  # XZ plane instead of XY
            z = orbitRadius2 * math.sin(t)
            
            self.traj2.addTime(t)
            self.traj2.addPosition(x, y, z)
        
        root.addChild(self.drawTraj2)
        
        # Add a third orbit - helical path with trace mode enabled
        # This demonstrates drawing only the trajectory up to the current simulation time
        self.traj3 = PyOF.Trajectory(3, 0)
        
        self.drawTraj3 = PyOF.DrawableTrajectory("Trace Orbit", 1.0, 0.0, 1.0, 0.9)  # Magenta orbit
        self.drawTraj3.showAxes(PyOF.ReferenceFrame.NO_AXES)
        self.drawTraj3.showAxesLabels(PyOF.ReferenceFrame.NO_AXES)
        self.drawTraj3.showNameLabel(False)
        
        self.curveArtist3 = PyOF.CurveArtist(self.traj3)
        self.curveArtist3.setWidth(5.0)
        self.curveArtist3.setColor(1.0, 0.0, 1.0)  # Magenta color
        
        # Enable trace mode - only shows trajectory up to current simulation time
        self.curveArtist3.setTraceMode(True)
        self.traceModeEnabled = True
        
        self.drawTraj3.addArtist(self.curveArtist3)
        
        # Generate helical trajectory (spiral outward and upward)
        numPoints3 = 200
        timeSpan = 10.0  # 10 seconds of trajectory data
        
        for i in range(numPoints3 + 1):
            t = (i * timeSpan) / numPoints3  # Time from 0 to 10 seconds
            angle = (i * 4.0 * math.pi) / numPoints3  # 2 full revolutions
            radius = 1.2 + (t / timeSpan) * 0.8  # Spiral outward from 1.2 to 2.0
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = (t / timeSpan) * 1.5 - 0.75  # Rise from -0.75 to +0.75
            
            self.traj3.addTime(t)
            self.traj3.addPosition(x, y, z)
        
        root.addChild(self.drawTraj3)

        # Create a manager to handle access to the scene
        fm = PyOF.FrameManager()
        fm.setFrame(root)

        # Add the scene to the window
        self.windowProxy.setScene(fm, 0, 0)
        
        # Set black background and star map texture
        self.windowProxy.getGridPosition(0, 0).setBackgroundColor(0, 0, 0)
        self.windowProxy.getGridPosition(0, 0).setSkySphereTexture("StarMap.tif")
        
        # Track shader state for toggle button
        self.shaderEnabled = True
        
        # Set time scale for smooth playback of trace
        # self.windowProxy.setTimeScale(1.0)  # Real-time
        self.windowProxy.setTimeScale(0.2)  # slower
        self.isPaused = False
        self.windowProxy.pauseTime(False)  # Start with time running
    
    def toggleShader(self):
        """Toggle the shader on the first orbit"""
        if self.shaderEnabled:
            self.curveArtist.setShader("")  # Disable shader
        else:
            self.curveArtist.setShader("Line_Pulse_Thickness.frag")  # Enable shader
        self.shaderEnabled = not self.shaderEnabled
    
    def toggleTraceMode(self):
        """Toggle trace mode on the third orbit"""
        self.traceModeEnabled = not self.traceModeEnabled
        self.curveArtist3.setTraceMode(self.traceModeEnabled)
    
    def togglePause(self):
        """Toggle pause/resume of simulation time"""
        self.isPaused = not self.isPaused
        self.windowProxy.pauseTime(self.isPaused)
    
    def resetTime(self):
        """Reset simulation time to zero"""
        self.windowProxy.setTime(0.0)

class TabWindow(QWidget):
    """
    Inherits QWidget for a simple standalone window showing a Tab widget
    
    """
    def __init__(self):
        QWidget.__init__(self)
        layout = QGridLayout()
        self.setLayout(layout)

        label = QLabel("Widget in a Tab.")

        self.ofwidget = PyQtOF.OFWidget(MyOFDemoWin1)
        self.ofwidget.setWindowTitle('qtpy OpenFrames Window 1')
        self.ofwidget.setGeometry(50, 50, 1024, 768)

        tabwidget = QTabWidget()
        tabwidget.addTab(self.ofwidget, "OpenFrames Tab")
        tabwidget.addTab(label, "Label Tab")

        layout.addWidget(tabwidget, 0, 0)
      
    def closeEvent(self, event):
        self.ofwidget.stopRendering()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # macOS requires some OpenGL context management to be performed from the main thread
    # which means multiple threads must be using the OpenGL context.
    # See: https://codereview.qt-project.org/c/qt/qtbase/+/155170
    if platform.system() == 'Darwin': # macOS
        app.setAttribute(Qt.ApplicationAttribute.AA_DontCheckOpenGLContextThreadAffinity)

    # Set depth buffer and MSAA
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)
    
    # Create main window with docked widgets
    exMainWindow = MacMainWindow()
    exMainWindow.show()

    # Create tab window
    #exTabWindow = TabWindow()
    #exTabWindow.show()
    
    # Create standalone window
    #exStandaloneWindow = PyQtOF.OFWidget(MyOFDemoWin2)
    #exStandaloneWindow.setWindowTitle('qtpy OpenFrames Window 2')
    #exStandaloneWindow.setGeometry(100, 100, 1024, 768)
    #exStandaloneWindow.show()
    
    # Start Qt application
    ret = app.exec_()
    sys.exit(ret)
